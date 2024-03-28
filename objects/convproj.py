# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter
from functions import xtramath
from functions import data_values
from termcolor import colored, cprint
import base64
import bisect

from objects_convproj import automation
from objects_convproj import plugin
from objects_convproj import fileref
from objects_convproj import params
from objects_convproj import tracks
from objects_convproj import visual
from objects_convproj import sends
from objects_convproj import autoticks
from objects_convproj import autopoints
from objects_convproj import notelist
from objects_convproj import stretch

def autopath_encode(autol):
    return ';'.join(autol)

def vis_plugin(p_type, p_subtype):
    if p_type != None and p_subtype != None: return p_type+':'+p_subtype
    elif p_type != None and p_subtype == None: return p_type
    elif p_type == None and p_subtype == None: return 'None'

def autoloc_getname(autopath):
    if autopath[0] == 'main': autoname = 'Main'
    if autopath[0] == 'fxmixer': autoname = 'FX '+autopath[1]
    if autopath[0] == 'send': autoname = 'Send'
    if autopath[0] == 'plugin': autoname = autopath[1]
    if autopath[0] == 'track': autoname = 'Track'

plugin_id_counter = counter.counter(1000, 'plugin_')


class cvpj_timemarker:
    __slots__ = ['type','visual','position','duration']
    def __init__(self):
        self.visual = visual.cvpj_visual()
        self.type = ''
        self.position = 0
        self.duration = 0

class cvpj_fxchannel:
    def __init__(self):
        self.visual = visual.cvpj_visual()
        self.visual_ui = visual.cvpj_visual_ui()
        self.params = params.cvpj_paramset()
        self.fxslots_audio = []
        self.fxslots_mixer = []
        self.sends = sends.cvpj_sends()

class cvpj_project:
    def __init__(self):
        self.type = None
        self.time_ppq = 96
        self.time_float = False
        self.track_data = {}
        self.track_order = []
        self.track_master = tracks.cvpj_track('master', self.time_ppq, self.time_float, False, False)
        self.track_returns = {}
        self.plugins = {}
        self.instruments = {}
        self.instruments_order = []
        self.sample_index = {}
        self.notelist_index = {}
        self.params = params.cvpj_paramset()
        self.fxrack = {}
        self.playlist = {}
        self.timesig = [4,4]
        self.do_actions = []
        self.timemarkers = []
        self.metadata = visual.cvpj_metadata()
        self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
        self.loop_active = False
        self.loop_start = 0
        self.loop_end = 0
        self.filerefs = {}
        self.samplerefs = {}
        self.window_data = {}
        self.automation = automation.cvpj_automation(self.time_ppq, self.time_float)
        self.groups = {}
        self.sample_folders = []

    def sort_tracks(self):
        sortpos = {}
        for track_id, track_data in self.track_data.items():
            trackstart = track_data.placements.get_start()
            if trackstart not in sortpos: sortpos[trackstart] = []
            sortpos[trackstart].append([track_id])
        self.track_order = []
        for n in sorted(sortpos):
            for i in sortpos[n]: self.track_order += i
 
    def set_timings(self, time_ppq, time_float):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
        self.automation.time_ppq = self.time_ppq
        self.automation.time_float = self.time_float

    def change_timings(self, time_ppq, time_float):
        print('[convprov] Changing Timings from '+str(self.time_ppq)+':'+str(self.time_float)+' to '+str(time_ppq)+':'+str(time_float))
        for p in self.track_data: 
            track_data = self.track_data[p]
            track_data.change_timings(time_ppq, time_float)
            for e in track_data.notelist_index: 
                track_data.notelist_index[e].notelist.change_timings(time_ppq, time_float)
        for p in self.playlist: self.playlist[p].change_timings(time_ppq, time_float)
        for p in self.notelist_index: self.notelist_index[p].notelist.change_timings(time_ppq, time_float)
        self.loop_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_start)
        self.loop_end = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_end)
        self.timesig_auto.change_timings(time_ppq, time_float)
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.automation.change_timings(time_ppq, time_float)

    def get_dur(self):
        duration_final = 0

        for p in self.track_data: 
            track_data = self.track_data[p]
            trk_dur = track_data.placements.get_dur()
            if duration_final < trk_dur: duration_final = trk_dur
        for p in self.playlist: 
            track_data = self.track_data[p]
            trk_dur = track_data.placements.get_dur()
            if duration_final < trk_dur: duration_final = trk_dur
        return duration_final

    def add_timemarker(self):
        timemarker_obj = cvpj_timemarker()
        self.timemarkers.append(timemarker_obj)
        return timemarker_obj

    def patlenlist_to_timemarker(self, PatternLengthList, pos_loop):
        prevtimesig = self.timesig
        timemarkers = []
        currentpos = 0
        blockcount = 0
        for PatternLengthPart in PatternLengthList:
            temptimesig = xtramath.get_timesig(PatternLengthPart, self.timesig[1])
            if prevtimesig != temptimesig: self.timesig_auto.add_point(currentpos, temptimesig)
            if pos_loop == blockcount:self.loop_start = currentpos
            prevtimesig = temptimesig
            currentpos += PatternLengthPart
            blockcount += 1

    def iter_automation(self):
        for autopath in self.automation:
            yield autopath.split(';'), self.automation[autopath]





    def add_fileref(self, fileid, filepath):
        if fileid not in self.filerefs: 
            self.filerefs[fileid] = fileref.cvpj_fileref(filepath)
            cprint('[convproj] FileRef - '+fileid+' - '+filepath, 'white')
        return self.filerefs[fileid]

    def add_sampleref(self, fileid, filepath):
        if fileid not in self.samplerefs: 
            self.samplerefs[fileid] = fileref.cvpj_sampleref(filepath)
            cprint('[convproj] SampleRef - '+fileid+' - '+filepath, 'white')
        return self.samplerefs[fileid]

    def iter_samplerefs(self):
        for sampleref_id, sampleref_obj in self.samplerefs.items():
            yield sampleref_id, sampleref_obj

    def fill_samplerefs(self, filepath):
        for sampleref_id, sampleref_obj in self.samplerefs.items():
            if not sampleref_obj.found:
                isfound = sampleref_obj.fileref.find_relative(filepath)
                if isfound: sampleref_obj.get_info()

    def add_fxchan(self, fxnum):
        cprint('[convproj] FX Channel - '+str(fxnum), 'yellow')
        if fxnum not in self.fxrack: self.fxrack[fxnum] = cvpj_fxchannel()
        return self.fxrack[fxnum]

    def add_notelistindex(self, i_id):
        self.notelist_index[i_id] = tracks.cvpj_nle(self.time_ppq, self.time_float)
        return self.notelist_index[i_id]

    def iter_notelistindex(self):
        for i_id in self.notelist_index: yield i_id, self.notelist_index[i_id]

    def add_sampleindex(self, i_id):
        self.sample_index[i_id] = tracks.cvpj_sle()
        return self.sample_index[i_id]

    def iter_sampleindex(self):
        for i_id in self.sample_index: yield i_id, self.sample_index[i_id]





    def get_sampleref(self, fileid):
        if fileid in self.samplerefs: return True, self.samplerefs[fileid]
        else: return False, None

    def get_fileref(self, fileid):
        if fileid in self.filerefs: return True, self.filerefs[fileid]
        else: return False, None




    def add_timesig_lengthbeat(self, pat_len, notes_p_beat):
        self.timesig = xtramath.get_timesig(pat_len, notes_p_beat)

    def window_data_add(self, windowpath):
        windowpath = autopath_encode(windowpath)
        self.window_data[windowpath] = visual.cvpj_window_data()
        return self.window_data[windowpath]

    def window_data_get(self, windowpath):
        windowpath = autopath_encode(windowpath)
        if windowpath in self.window_data: return self.window_data[windowpath]
        else: return visual.cvpj_window_data()






    def add_playlist(self, idnum, uses_placements, is_indexed):
        if idnum not in self.playlist:
            cprint('[convproj] Playlist '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+str(idnum), 'light_blue')
            self.playlist[idnum] = tracks.cvpj_track('hybrid', self.time_ppq, self.time_float, uses_placements, is_indexed)
        return self.playlist[idnum]

    def iter_playlist(self):
        for idnum, playlist_obj in self.playlist.items():
            yield idnum, playlist_obj






    def find_track(self, trackid):
        if trackid in self.track_data: return True, self.track_data[trackid]
        else: return False, None

    def iter_track(self):
        for trackid in self.track_order:
            if trackid in self.track_data: yield trackid, self.track_data[trackid]




    def add_group(self, groupid):
        cprint('[convproj] Group - '+groupid, 'yellow')
        self.groups[groupid] = tracks.cvpj_track('group', self.time_ppq, self.time_float, False, False)
        return self.groups[groupid]

    def find_group(self, groupid):
        if groupid in self.groups: return True, self.groups[groupid]
        else: return False, None

    def iter_group(self):
        for groupid, group_obj in self.groups.items():
            yield groupid, group_obj





    def add_track(self, track_id, tracktype, uses_placements, is_indexed):
        cprint('[convproj] Track '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+track_id, 'light_blue')
        self.track_data[track_id] = tracks.cvpj_track(tracktype, self.time_ppq, self.time_float, uses_placements, is_indexed)
        self.track_order.append(track_id)
        return self.track_data[track_id]

    def add_track_midi(self, track_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed):
        plugin_obj = self.add_plugin_midi(plug_id, m_bank, m_inst, m_drum)
        cprint('[convproj] Track - '+track_id, 'light_blue')
        plugin_obj.role = 'synth'

        track_obj = self.add_track(track_id, 'instrument', uses_pl, indexed)
        track_obj.midi.out_patch = m_inst
        track_obj.midi.out_bank = m_bank
        track_obj.midi.drum_mode = m_drum
        track_obj.inst_pluginid = plug_id
        track_obj.params.add('usemasterpitch', not m_drum, 'bool')
        return track_obj, plugin_obj

    def add_track_midi_dset(self, inst_id, plug_id, m_bank, m_inst, m_drum, midi_ds, def_name, def_color, uses_pl, indexed):
        di_name, di_color = midi_ds.object_get_name_color('inst' if not m_drum else 'drums', str(m_inst) if not m_drum else str(m_bank))
        track_obj, plugin_obj = self.add_track_midi(inst_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed)
        track_obj.visual.name = data_values.list_usefirst([def_name, di_name])
        track_obj.visual.color = data_values.list_usefirst([def_color, di_color])
        return track_obj, plugin_obj

    def add_track_from_dset(self, track_id, plug_id, main_ds, midi_ds, ds_id, def_name, def_color, uses_pl, indexed):
        m_bank, m_inst, m_drum = main_ds.midito_get('inst', ds_id)
        di_name, di_color = main_ds.object_get_name_color('inst', ds_id)

        if m_inst != None:
            dm_name, dm_color = midi_ds.object_get_name_color('inst', str(m_inst))
            track_obj, plugin_obj = self.add_track_midi_dset(track_id, plug_id, m_bank, m_inst, m_drum, midi_ds, def_name, def_color, uses_pl, indexed)
            track_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            track_obj.visual.color = data_values.list_usefirst([def_color, di_color, dm_color])

        else:
            plugin_obj = self.add_plugin(plug_id, None, None)
            plugin_obj.role = 'synth'
            track_obj = self.add_track(track_id, 'instrument', uses_pl, indexed)
            track_obj.inst_pluginid = plug_id
            track_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            track_obj.visual.color = data_values.list_usefirst([def_color, di_color])

        return track_obj, plugin_obj





    def add_return(self, track_id):
        self.track_returns[track_id] = tracks.cvpj_track('return', self.time_ppq, self.time_float, False, False)
        return self.track_returns[track_id]





    def get_plugin(self, plug_id):
        if plug_id in self.plugins: return True, self.plugins[plug_id]
        else: return False, None

    def add_plugin(self, plug_id, i_type, i_subtype):
        cprint('[convproj] Plugin - '+str(plug_id)+' - '+vis_plugin(i_type, i_subtype), 'green')
        plugin_obj = plugin.cvpj_plugin()
        plugin_obj.replace(i_type, i_subtype)
        self.plugins[plug_id] = plugin_obj
        return self.plugins[plug_id]

    def add_plugin_genid(self, i_type, i_subtype):
        plug_id = plugin_id_counter.get_str_txt()
        cprint('[convproj] Plugin - '+str(plug_id)+' - '+vis_plugin(i_type, i_subtype), 'green')
        plugin_obj = plugin.cvpj_plugin()
        plugin_obj.replace(i_type, i_subtype)
        self.plugins[plug_id] = plugin_obj
        return self.plugins[plug_id], plug_id

    def add_plugin_sampler_genid(self, file_path):
        plug_id = plugin_id_counter.get_str_txt()
        plugin_obj, sampleref_obj = self.add_plugin_sampler(plug_id, file_path)
        plugin_obj.role = 'synth'
        return plugin_obj, plug_id, sampleref_obj

    def add_plugin_sampler(self, plug_id, file_path):
        sampleref_obj = self.add_sampleref(file_path, file_path)
        is_drumsynth = sampleref_obj.fileref.extension.lower() == 'ds'

        if not is_drumsynth:
            plugin_obj = self.add_plugin(plug_id, 'sampler', 'single')
            plugin_obj.role = 'synth'
            plugin_obj.samplerefs['sample'] = file_path
        else:
            plugin_obj = self.add_plugin(plug_id, 'sampler', 'drumsynth')
            plugin_obj.role = 'synth'
            plugin_obj.samplerefs['sample'] = file_path
            from objects_file import audio_drumsynth
            from functions_plugin_cvpj import params_drumsynth
            drumsynth_obj = audio_drumsynth.drumsynth_main()
            drumsynth_obj.read(file_path)
            params_drumsynth.to_cvpj(drumsynth_obj, plugin_obj)

        return plugin_obj, sampleref_obj

    def add_plugin_midi(self, plug_id, m_bank, m_inst, m_drum):
        plugin_obj = self.add_plugin(plug_id, 'midi', None)
        plugin_obj.role = 'synth'
        plugin_obj.datavals.add('bank', m_bank)
        plugin_obj.datavals.add('patch', m_inst)
        plugin_obj.datavals.add('is_drum', m_drum)
        return plugin_obj






    def add_instrument(self, inst_id):
        cprint('[convproj] Instrument - '+str(inst_id), 'cyan')
        self.instruments[inst_id] = tracks.cvpj_instrument()
        self.instruments_order.append(inst_id)
        return self.instruments[inst_id]

    def iter_instrument(self):
        for inst_id in self.instruments_order:
            if inst_id in self.instruments: yield inst_id, self.instruments[inst_id]

    def instrument_midi(self, inst_id, plug_id, m_bank, m_inst, m_drum):
        plugin_obj = self.add_plugin_midi(plug_id, m_bank, m_inst, m_drum)

        inst_obj = self.add_instrument(inst_id)
        inst_obj.midi.out_patch = m_inst
        inst_obj.midi.out_bank = m_bank
        inst_obj.midi.drum_mode = m_drum
        inst_obj.pluginid = plug_id
        inst_obj.params.add('usemasterpitch', not m_drum, 'bool')
        return inst_obj, plugin_obj

    def instrument_midi_dset(self, inst_id, plug_id, m_bank, m_inst, m_drum, midi_ds, def_name, def_color):
        di_name, di_color = midi_ds.object_get_name_color('inst' if not m_drum else 'drums', str(m_inst) if not m_drum else str(m_bank))
        inst_obj, plugin_obj = self.instrument_midi(inst_id, plug_id, m_bank, m_inst, m_drum)
        inst_obj.visual.name = data_values.list_usefirst([def_name, di_name])
        inst_obj.visual.color = data_values.list_usefirst([def_color, di_color])
        return inst_obj, plugin_obj

    def add_instrument_from_dset(self, inst_id, plug_id, main_ds, midi_ds, ds_id, def_name, def_color):
        m_bank, m_inst, m_drum = main_ds.midito_get('inst', ds_id)
        di_name, di_color = main_ds.object_get_name_color('inst', ds_id)

        if m_inst != None:
            dm_name, dm_color = midi_ds.object_get_name_color('inst', str(m_inst))
            inst_obj, plugin_obj = self.instrument_midi(inst_id, plug_id, m_bank, m_inst, bool(m_drum))
            inst_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            inst_obj.visual.color = data_values.list_usefirst([def_color, di_color, dm_color])

        else:
            inst_obj = self.add_instrument(inst_id)
            plugin_obj = self.add_plugin(plug_id, None, None)
            plugin_obj.role = 'synth'
            inst_obj.pluginid = plug_id
            inst_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            inst_obj.visual.color = data_values.list_usefirst([def_color, di_color])

        return inst_obj, plugin_obj










    def add_autopoints_twopoints(self, autopath, v_type, twopoints):
        for x in twopoints:
            self.add_autopoint(autopath, v_type, x[0], x[1], 'normal')



        
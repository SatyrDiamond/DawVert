# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import convproj_plugin
from objects import counter
from functions import xtramath
from functions import data_values
from termcolor import colored, cprint
import base64
import bisect

from objects import convproj_placements
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
        self.params = params.cvpj_paramset()
        self.fxslots_audio = []
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
        self.automation = {}
        self.params = params.cvpj_paramset()
        self.fxrack = {}
        self.playlist = {}
        self.timesig = [4,4]
        self.do_actions = []
        self.timemarkers = []
        self.metadata = visual.cvpj_metadata()
        self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
        self.loop_active = False
        self.loop_start = -1
        self.loop_end = -1
        self.filerefs = {}
        self.samplerefs = {}
        self.window_data = {}
        self.autoticks = {}
        self.autopoints = {}
        self.groups = {}
        self.sample_folders = []

    def set_timings(self, time_ppq, time_float):
        self.time_ppq = time_ppq
        self.time_float = time_float
        self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')

    def change_timings(self, time_ppq, time_float):
        for p in self.track_data: 
            track_data = self.track_data[p]
            track_data.change_timings(time_ppq, time_float)
            for e in track_data.notelist_index: 
                track_data.notelist_index[e].notelist.change_timings(time_ppq, time_float)
        for p in self.playlist: self.playlist[p].change_timings(time_ppq, time_float)
        for p in self.automation: self.automation[p].change_timings(time_ppq, time_float)
        for p in self.autopoints: self.autopoints[p].change_timings(time_ppq, time_float)
        for p in self.notelist_index: self.notelist_index[p].notelist.change_timings(time_ppq, time_float)
        self.loop_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_start)
        self.loop_end = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_end)
        self.timesig_auto.change_timings(time_ppq, time_float)
        self.time_ppq = time_ppq
        self.time_float = time_float

    def get_dur(self):
        duration_final = 0
        for p in self.track_data: 
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

    def add_automation_pl(self, autopath, valtype):
        autopath = autopath_encode(autopath)
        if autopath not in self.automation: 
            self.automation[autopath] = convproj_placements.cvpj_placements_auto(self.time_ppq, self.time_float, valtype)
        autopl_obj = self.automation[autopath].add(valtype)
        return autopl_obj


    def del_automation(self, autopath):
        autopath = autopath_encode(autopath)
        if autopath in self.automation: del self.automation[autopath]
        if autopath in self.autopoints: del self.autopoints[autopath]
        if autopath in self.autoticks: del self.autoticks[autopath]

    def move_automation(self, autopath, to_autopath):
        autopath = autopath_encode(autopath)
        to_autopath = autopath_encode(to_autopath)
        print('[convproj] Auto: Moving', autopath, 'to', to_autopath)
        if autopath in self.automation:
            self.automation[to_autopath] = self.automation[autopath]
            del self.automation[autopath]

        if autopath in self.autopoints:
            self.autopoints[to_autopath] = self.autopoints[autopath]
            del self.autopoints[autopath]

        if autopath in self.autoticks:
            self.autoticks[to_autopath] = self.autoticks[autopath]
            del self.autoticks[autopath]

    def moveg_automation(self, autopath, fval, tval):
        self.move_automation(autopath+[fval], autopath+[tval])

    def copy_automation(self, autopath, to_autopath):
        autopath = autopath_encode(autopath)
        to_autopath = autopath_encode(to_autopath)
        if autopath in self.automation: self.automation[to_autopath] = self.automation[autopath]
        if autopath in self.autopoints: self.autopoints[to_autopath] = self.autopoints[autopath]
        if autopath in self.autoticks: self.autoticks[to_autopath] = self.autoticks[autopath]

    def addmul_automation(self, autopath, addval, mulval):
        autopath = autopath_encode(autopath)
        if autopath in self.automation: self.automation[autopath].addmul(addval, mulval)
        if autopath in self.autopoints: self.autopoints[autopath].addmul(addval, mulval)
        if autopath in self.autoticks: self.autoticks[autopath].addmul(addval, mulval)

    def to_one_automation(self, autopath, i_min, i_max):
        autopath = autopath_encode(autopath)
        if autopath in self.automation: self.automation[autopath].to_one(i_min, i_max)
        if autopath in self.autopoints: self.autopoints[autopath].to_one(i_min, i_max)
        if autopath in self.autoticks: self.autoticks[autopath].to_one(i_min, i_max)

    def from_one_automation(self, autopath, i_min, i_max):
        autopath = autopath_encode(autopath)
        if autopath in self.automation: self.automation[autopath].from_one(i_min, i_max)
        if autopath in self.autopoints: self.autopoints[autopath].from_one(i_min, i_max)
        if autopath in self.autoticks: self.autoticks[autopath].from_one(i_min, i_max)

    def funcval_automation(self, autopath, function):
        autopath = autopath_encode(autopath)
        if autopath in self.automation: 
            for ap in self.automation[autopath].iter():
                ap.value = function(ap.value)

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
            track_obj, plugin_obj = self.add_track_midi(track_id, plug_id, m_bank, m_inst, bool(m_drum))
            track_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            track_obj.visual.color = data_values.list_usefirst([def_color, di_color, dm_color])

        else:
            plugin_obj = self.add_plugin(plug_id, None, None)
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
        plugin_obj = convproj_plugin.cvpj_plugin()
        plugin_obj.replace(i_type, i_subtype)
        self.plugins[plug_id] = plugin_obj
        return self.plugins[plug_id]

    def add_plugin_genid(self, i_type, i_subtype):
        plug_id = plugin_id_counter.get_str_txt()
        cprint('[convproj] Plugin - '+str(plug_id)+' - '+vis_plugin(i_type, i_subtype), 'green')
        plugin_obj = convproj_plugin.cvpj_plugin()
        plugin_obj.replace(i_type, i_subtype)
        self.plugins[plug_id] = plugin_obj
        return self.plugins[plug_id], plug_id

    def add_plugin_sampler_genid(self, file_path):
        plug_id = plugin_id_counter.get_str_txt()
        plugin_obj = self.add_plugin(plug_id, 'sampler', 'single')
        plugin_obj.samplerefs['sample'] = file_path
        sampleref_obj = self.add_sampleref(file_path, file_path)
        return plugin_obj, plug_id, sampleref_obj

    def add_plugin_sampler(self, plug_id, file_path):
        print('[convproj] Plugin - [Sampler]: '+str(plug_id))
        plugin_obj = self.add_plugin(plug_id, 'sampler', 'single')
        plugin_obj.samplerefs['sample'] = file_path
        sampleref_obj = self.add_sampleref(file_path, file_path)
        return plugin_obj, sampleref_obj

    def add_plugin_midi(self, plug_id, m_bank, m_inst, m_drum):
        plugin_obj = self.add_plugin(plug_id, 'midi', None)
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
            inst_obj.pluginid = plug_id
            inst_obj.visual.name = data_values.list_usefirst([def_name, di_name])
            inst_obj.visual.color = data_values.list_usefirst([def_color, di_color])

        return inst_obj, plugin_obj





    def add_autotick(self, autopath, p_pos, p_val):
        autopath = autopath_encode(autopath)
        if autopath not in self.autoticks: self.autoticks[autopath] = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'float')
        self.autoticks[autopath].add_point(p_pos, p_val)

    def get_paramval_autotick(self, autopath, firstnote, fallback):
        autopath = autopath_encode(autopath)
        out_val = fallback
        if autopath in self.autoticks: out_val = self.autoticks[autopath].get_paramval(firstnote, out_val)
        return out_val






    def add_autopoints_twopoints(self, autopath, v_type, twopoints):
        for x in twopoints:
            self.add_autopoint(autopath, v_type, x[0], x[1], 'normal')

    def add_autopoint(self, autopath, v_type, p_pos, p_val, p_type):
        autopath = autopath_encode(autopath)
        if autopath not in self.autopoints: self.autopoints[autopath] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, v_type)
        autopoint_obj = self.autopoints[autopath].add_point()
        autopoint_obj.pos = p_pos
        autopoint_obj.value = p_val
        autopoint_obj.type = p_type



    def autoticks_to_autopoints(self):
        for autopath, autoticks in self.autoticks.items():
            prev_val = -1000000000000000
            autotspl = []
            lastsplit = 0
            for p, v in autoticks.iter():
                normlvlspl = (p-prev_val)/(self.time_ppq*4)
                normlvl = (p-prev_val)/self.time_ppq
                normtype = normlvl<0.1
                if normlvlspl>1: 
                    lastsplit = p
                    autotspl.append([p, []])
                prev_val = p

                autotspl[-1][1].append([p-lastsplit, v, normtype])

            for d in autotspl:
                if autopath not in self.automation: self.automation[autopath] = convproj_placements.cvpj_placements_auto(self.time_ppq, self.time_float, autoticks.val_type)
                autopl_obj = self.automation[autopath].add(autoticks.val_type)
                autopl_obj.position = d[0]
                autopl_obj.duration = self.time_ppq
                for x in d[1]:
                    #print(autopath, x, autoticks.val_type)
                    autopoint_obj = autopl_obj.data.add_point()
                    autopoint_obj.pos = x[0]
                    autopoint_obj.value = x[1]
                    autopoint_obj.type = 'normal' if x[2] else 'instant'
                    if autopoint_obj.pos > self.time_ppq:
                        autopl_obj.duration = autopoint_obj.pos

        self.autoticks = {}

    def autopoints_to_pl(self):
        for autopath, autopoints in self.autopoints.items():
            if autopath not in self.automation: self.automation[autopath] = convproj_placements.cvpj_placements_auto(self.time_ppq, self.time_float, autopoints.val_type)

            prev_val = 0
            usedareas = []
            for x in autopoints.iter():
                usedareas.append((x.value != prev_val) or x.type == 'instant')
                prev_val = x.value

            cutpos = 0
            is_first = True
            out_regions = []
            for x in data_values.list_findrepeat(usedareas):
                outmin = cutpos if is_first else cutpos-1
                if x[0]: out_regions.append([outmin, cutpos+x[1]])
                cutpos += x[1]
                is_first = False

            for r in out_regions:
                autopl_obj = self.automation[autopath].add(autopoints.val_type)
                autopl_obj.position = autopoints.points[r[0]].pos
                for x in autopoints.points[r[0]:r[1]]:
                    autopoint_obj = autopl_obj.data.add_point()
                    autopoint_obj.pos = x.pos-autopoints.points[r[0]].pos
                    autopoint_obj.value = x.value
                    autopoint_obj.type = x.type
                    autopl_obj.duration = autopl_obj.data.get_dur()
                    if autopl_obj.duration < self.time_ppq: autopl_obj.duration = self.time_ppq
        self.autopoints = {}

    def autopoints_from_pl(self):
        for autopath, autopl in self.automation.items():
            self.autopoints[autopath] = autopoints.cvpj_autopoints(self.time_ppq, self.time_float, 'float')
            for x in autopl.iter():
                x.data.edit_trimmove(0, x.duration)
                for c, p in enumerate(x.data.points):
                    autopoint_obj = self.autopoints[autopath].add_point()
                    autopoint_obj.pos = p.pos+x.position
                    autopoint_obj.value = p.value
                    autopoint_obj.type = p.type if c != 0 else 'instant'

        self.automation = {}
            
    def get_autopoints(self, autoloc):
        autopath = autopath_encode(autoloc)
        if autopath in self.autopoints: return True, self.autopoints[autopath]
        else: return False, None

    def iter_autopoints(self):
        for autopath in self.autopoints:
            yield autopath.split(';'), self.autopoints[autopath]


        
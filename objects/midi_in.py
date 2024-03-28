# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from functions import midi_exdata
from functions import data_values

from objects import convproj
from objects import dv_dataset
from objects_convproj import autoticks
import bisect

dataset_midi = dv_dataset.dataset('./data_dset/midi.dset')

class midi_note_data:
    def __init__(self, song_channels):
        self.notes = [[[] for x in range(128)] for x in range(song_channels)]
        self.track_curpos = 0

    def note_on(self, channel, notenum, position, velocity):
        self.notes[channel][notenum].append([position,None,velocity,None,None,None])

    def note(self, channel, notenum, position, velocity, duration):
        self.notes[channel][notenum].append([position,self.track_curpos+duration,velocity,None,None,None])

    def note_off(self, channel, notenum, position):
        for note in self.notes[channel][notenum]:
            if note[1] == None:
                note[1] = position-note[0]
                break

    def iter(self):
        out_notes = []
        used_inst = []
        for ch_num, note_ch in enumerate(self.notes):
            for key, mnl in enumerate(note_ch):
                for sn in mnl: 
                    out_notes.append([key, ch_num]+sn)
                    inst = [ch_num, sn[3], sn[4], sn[5]]
                    if inst not in used_inst: used_inst.append(inst)
        return out_notes, used_inst


class auto_multidata:
    def __init__(self): 
        self.autodata = {}

    def add_point(self, position, value):
        if position not in self.autodata: self.autodata[position] = [value]
        else: self.autodata[position].append(value)

class autoset:
    def __init__(self, ppq):
        self.multiautodata = {}
        self.ppq = ppq

    def add_point(self, position, name, value):
        if name not in self.multiautodata: self.multiautodata[name] = autoticks.cvpj_autoticks(self.ppq, False, 'float')
        self.multiautodata[name].add_point(position, value)

    def get_points(self, name):
        if name in self.multiautodata: return True, self.multiautodata[name]
        else: return False, []

    def iter(self):
        for i, v in self.multiautodata.items():
            yield i, v


def decode_anvil_color(anvilcolordata):
    red_p1 = anvilcolordata[3] & 0x3f 
    red_p2 = anvilcolordata[2] & 0xe0
    out_red = (red_p1 << 2) + (red_p2 >> 5)

    green_p1 = anvilcolordata[2] & 0x1f
    green_p2 = anvilcolordata[1] & 0xf0
    out_green = (green_p1 << 3) + (green_p2 >> 4)

    blue_p1 = anvilcolordata[1] & 0x0f
    blue_p2 = anvilcolordata[0] & 0x0f
    out_blue = (blue_p1 << 4) + blue_p2
    return [out_red, out_green, out_blue]

def closest(i_list, i_val, i_dict, fallback):
    if i_dict: return i_dict[i_list[bisect.bisect(i_list, i_val)-1]]
    else: return fallback

def add_notedata(midi_notes, a_patch, a_bank, a_mode, isdrum):
    s_patch_list = [x for x in a_patch]
    s_bank_list = [x for x in a_bank]
    s_mode_list = [x for x in a_mode]
    for note in midi_notes:
        for subnote in note:
            subnote[3] = closest(s_patch_list, subnote[0], a_patch, 0)
            subnote[4] = closest(s_bank_list, subnote[0], a_bank, 0)
            subnote[5] = closest(s_mode_list, subnote[0], a_mode, isdrum)

def midid_to_num(i_bank, i_patch, i_isdrum): return i_bank*256 + i_patch + int(i_isdrum)*128
def midid_from_num(value): return (value>>8), (value%128), int(bool(value&0b10000000))

class midi_in:
    def song_start(self, numchannels, ppq, tempo, timesig):
        self.global_miditracks = []

        self.ppq = ppq
        self.pitch_gm = False
        self.song_channels = numchannels
        self.auto_bpm = autoticks.cvpj_autoticks(self.ppq, False, 'float')
        self.auto_timesig = autoticks.cvpj_autoticks(self.ppq, False, 'timesig')
        self.auto_markers = autoticks.cvpj_autoticks(self.ppq, False, 'text')
        self.auto_key_signature = autoticks.cvpj_autoticks(self.ppq, False, 'text')

        self.mulauto_sysex = auto_multidata()
        self.autoset_master = autoset(self.ppq)

        self.autochan_bank = [autoticks.cvpj_autoticks(self.ppq, False, 'float') for _ in range(self.song_channels)]
        self.autochan_inst = [autoticks.cvpj_autoticks(self.ppq, False, 'float') for _ in range(self.song_channels)]
        self.autochan_mode = [autoticks.cvpj_autoticks(self.ppq, False, 'float') for _ in range(self.song_channels)]

        self.first_use = [-1 for _ in range(self.song_channels)]

        self.loop_data = [None, None]

        self.chan_auto = [autoset(self.ppq) for _ in range(self.song_channels)]

    def add_track(self, startpos, midicmds):
        track_name = None
        track_color = None
        track_copyright = None
        track_mode = 0 # 0=normal 1=single

        track_curpos = startpos

        sequencer_specific = []
        track_notes = midi_note_data(self.song_channels)

        numnotes = 0

        for midicmd in midicmds:

            if midicmd[0] == 'rest': track_curpos += midicmd[1]
            elif midicmd[0] == 'track_name': track_name = midicmd[1]

            elif midicmd[0] == 'sequencer_specific':
                exdata = midi_exdata.decode_exdata(midicmd[1], True)
                
                if exdata[0] == [5]:
                    if exdata[1][0] == 15: #from Anvil Studio
                        if exdata[1][1] == 52: track_color = colors.rgb_int_to_rgb_float(decode_anvil_color(exdata[1][2:6]))
                elif exdata[0] == [83]:
                    if exdata[1][0:5] == b'ign\x01\xff': #from Signal MIDI Editor
                        track_color = colors.rgb_int_to_rgb_float(exdata[1][5:8][::-1])
                elif exdata[0] == [80]:
                    if exdata[1][0:5] == b'reS\x01\xff': #from Studio One
                        track_color = colors.rgb_int_to_rgb_float(exdata[1][5:8][::-1])
                else:
                    sequencer_specific.append(midicmd[1])

            elif midicmd[0] == 'copyright': track_copyright = midicmd[1]

            elif midicmd[0] == 'program_change': self.autochan_inst[midicmd[1]].add_point(track_curpos, midicmd[2])

            elif midicmd[0] == 'control_change': 
                if midicmd[2] == 0: self.autochan_bank[midicmd[1]].add_point(track_curpos, midicmd[3])
                elif midicmd[2] in [111, 116]: self.loop_data[0] = track_curpos
                elif midicmd[2] == 117: self.loop_data[1] = track_curpos
                else: self.chan_auto[midicmd[1]].add_point(track_curpos, midicmd[2], midicmd[3])

            elif midicmd[0] == 'pitchwheel': self.chan_auto[midicmd[1]].add_point(track_curpos, 'pitch', midicmd[2])

            elif midicmd[0] == 'tempo': self.auto_bpm.add_point(track_curpos, midicmd[1])

            elif midicmd[0] == 'timesig': self.auto_timesig.add_point(track_curpos, [midicmd[1], midicmd[2]])

            elif midicmd[0] == 'sysex': 
                sysexdata = midi_exdata.decode(midicmd[1])
                if sysexdata != None:
                    out_vendor, out_vendor_ext, out_brandname, out_device, out_model, out_command, out_data, devicename, groups, nameval = sysexdata

                    #print(out_vendor, out_vendor_ext, out_brandname, out_device, out_model, out_command, out_data, devicename, groups, nameval)

                    if [out_vendor, out_vendor_ext] == [b'\x7f', False]:
                        if groups == ['device', None]:
                            if nameval[0] == 'master_volume': self.autoset_master.add_point(track_curpos, 'volume', nameval[1][-1]/127)

                    if [out_vendor, out_vendor_ext] == [b'A', False]:
                        if groups[0] == 'patch_a':
                            if groups[1] == None:
                                if nameval[0] == 'master_volume': self.autoset_master.add_point(track_curpos, 'volume', nameval[1][0]/127)
                                if nameval[0] == 'gs_reset': self.pitch_gm = True
                            if groups[1] == 'block':
                                if nameval[0] == 'use_rhythm':
                                    self.autochan_mode[groups[2]-1].add_point(track_curpos, nameval[1])

            elif midicmd[0] == 'marker': 
                self.auto_markers.add_point(track_curpos, midicmd[1])
                if midicmd[1] == 'loopStart': self.loop_data[0] = track_curpos
                if midicmd[1] == 'loopEnd': self.loop_data[1] = track_curpos

            elif midicmd[0] == 'key_signature': self.auto_key_signature.add_point(track_curpos, midicmd[1])

            elif midicmd[0] == 'note_on': 
                track_notes.note_on(midicmd[1], midicmd[2], track_curpos, midicmd[3])
                numnotes += 1

            elif midicmd[0] == 'note': 
                track_notes.note(midicmd[1], midicmd[2], track_curpos, midicmd[3], midicmd[4])
                numnotes += 1

            elif midicmd[0] == 'note_off': track_notes.note_off(midicmd[1], midicmd[2], track_curpos)

            if midicmd[0] in ['note_on', 'note']:
                if self.first_use[midicmd[1]] > track_curpos or self.first_use[midicmd[1]] == -1:
                    self.first_use[midicmd[1]] = track_curpos

        self.global_miditracks.append([track_notes, track_name, track_copyright, sequencer_specific, track_color, track_mode, numnotes])

    def song_end(self, convproj_obj):
        fxchan_names = ['Chan #'+str(x+1) for x in range(self.song_channels)]
        fxchan_colors = [[0, 0, 0] for _ in range(self.song_channels)]

        numtracks = len(self.global_miditracks)

        for miditrack in self.global_miditracks:
            for channum in range(self.song_channels):
                midi_notes = miditrack[0].notes
                a_bank = self.autochan_bank[channum].points
                a_patch = self.autochan_inst[channum].points
                a_mode = self.autochan_mode[channum].points
                add_notedata(miditrack[0].notes[channum], a_patch, a_bank, a_mode, 1 if channum == 9 else 0)

        end_pos = 0
        used_inst_chans = [[] for _ in range(self.song_channels)]
        tracknum = 0
        for global_miditrack in self.global_miditracks:
            cvpj_trackid = 'track_'+str(tracknum)
            
            track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
            track_obj.visual.color = global_miditrack[4]

            midi_notes, n_used_inst = global_miditrack[0].iter()
            for n_inst in n_used_inst:
                ch_used_inst = [tracknum]+n_inst[1:]
                if ch_used_inst not in used_inst_chans[n_inst[0]]: used_inst_chans[n_inst[0]].append(ch_used_inst)

            for midi_note in midi_notes:
                n_key, n_ch, n_pos, n_dur, n_vol, n_inst, n_bank, n_isdrum = midi_note
                instid = '_'.join([str(n_ch), str(n_inst), str(n_bank), str(n_isdrum)])
                if n_dur != None:
                    track_obj.placements.notelist.add_m(instid, n_pos, n_dur, n_key-60, n_vol/127, {})
                    if end_pos < n_dur-n_pos: end_pos = n_dur-n_pos

            if numtracks == 1: convproj_obj.metadata.name = global_miditrack[1]
            else: track_obj.visual.name = global_miditrack[1]

            tracknum += 1

        used_insts = []
        for ch_num, ch_used_insts in enumerate(used_inst_chans):
            for used_inst in ch_used_insts:
                if used_inst[3] == 0: instname, instcolor = dataset_midi.object_get_name_color('inst', str(used_inst[1]))
                else: instname, instcolor = 'Drums', [0.81, 0.80, 0.82]
                _, groupname = dataset_midi.object_var_get('group', 'inst', str(used_inst[1]))
                used_inst += [instname,instcolor,groupname]

                all_part_inst = [ch_num]+used_inst[1:]
                if all_part_inst not in used_insts: used_insts.append(all_part_inst)

        for used_inst in used_insts:
            i_ch, i_inst, i_bank, i_isdrum, i_name, i_color, i_group = used_inst
            instid = '_'.join([str(i_ch), str(i_inst), str(i_bank), str(i_isdrum)])
            inst_obj, plugin_obj = convproj_obj.instrument_midi_dset(instid, instid, i_bank, i_inst, i_isdrum, dataset_midi, i_name, i_color)
            inst_obj.fxrack_channel = i_ch+1
            inst_obj.pluginid = instid


        for ch_num, chan_inst in enumerate(used_inst_chans):
            name_usable = []
            color_usable = []

            usedinlen = len(chan_inst)
            if usedinlen == 1:
                track_num = chan_inst[0][0]
                is_drum = chan_inst[0][3]

                if is_drum == 0:
                    track_color = self.global_miditracks[track_num][4]
                    if numtracks > 1:
                        track_name = self.global_miditracks[track_num][1]
                        if track_name: name_usable.append(track_name)
                    if track_color: color_usable.append(track_color)
                    name_usable.append(chan_inst[0][4])
                    color_usable.append(chan_inst[0][5])
                else:
                    name_usable.append('Drums')
                    color_usable.append([0.81, 0.80, 0.82])

            elif usedinlen > 1:
                ifsame_trackid = data_values.ifallsame([chan_inst[x][0] for x in range(usedinlen)])
                ifsame_instid = data_values.ifallsame([chan_inst[x][4] for x in range(usedinlen)])
                ifsame_groups = data_values.ifallsame([chan_inst[x][6] for x in range(usedinlen)])
                ifsame_drums = data_values.ifallsame([chan_inst[x][3] for x in range(usedinlen)])
                drumval = chan_inst[0][3]

                if ifsame_trackid:
                    track_num = chan_inst[0][0]
                    track_name = self.global_miditracks[track_num][1]
                    track_color = self.global_miditracks[track_num][4]
                    if track_name: name_usable.append(track_name)
                    if track_color: color_usable.append(track_color)

                if ifsame_instid and ifsame_drums and drumval == 0:
                    name_usable.append(chan_inst[0][4])
                    color_usable.append(chan_inst[0][5])

                if ifsame_groups:
                    g_name, g_color = dataset_midi.groups_get_name_color('inst', chan_inst[0][6])
                    name_usable.append(g_name)
                    color_usable.append(g_color)

                if ifsame_drums and drumval == 1:
                    name_usable.append('Drums')
                    color_usable.append([0.81, 0.80, 0.82])

                color_usable.append([0.4, 0.4, 0.4])

            out_name = data_values.list_usefirst(name_usable)
            out_color = data_values.list_usefirst(color_usable)

            if out_name != None: fxchan_names[ch_num] = out_name
            if out_color != None: fxchan_colors[ch_num] = out_color

        fxchannel_obj = convproj_obj.add_fxchan(0)
        fxchannel_obj.visual.name = "Master"
        fxchannel_obj.visual.color = [0.3, 0.3, 0.3]

        usedeffects = False

        for ch_num, chan_auto in enumerate(self.chan_auto):

            chorus_used = False

            fxchannel_obj = convproj_obj.add_fxchan(ch_num+1)
            fxchannel_obj.visual.name = fxchan_names[ch_num]
            fxchannel_obj.visual.color = fxchan_colors[ch_num]
            fxchannel_obj.sends.add(0, None, 1)
            #ae_vol, ap_vol = self.chan_auto[ch_num].get_points(7)

            mixerid = ch_num+1
            autochannum = str(mixerid)

            for a_id, a_dat in chan_auto.iter():
                a_dat.optimize()
                
                autoloc, pname, def_val, fxgrp = [], 'none', 0, 0

                if a_id in [10, 64, 65, 66, 67, 68]: a_dat.addmul(-1, 1)

                if a_id == 'pitch': autoloc, pname = ['fxmixer', autochannum], 'pitch'
                if a_id == 1: autoloc, pname = ['fxmixer', autochannum], 'modulation'
                if a_id == 7: autoloc, pname, def_val = ['fxmixer', autochannum], 'vol', 1
                #if a_id == 10: autoloc, pname = ['fxmixer', autochannum], 'pan'
                if a_id == 64: autoloc, pname = ['fxmixer', autochannum], 'damper_pedal'
                if a_id == 65: autoloc, pname = ['fxmixer', autochannum], 'portamento'
                if a_id == 66: autoloc, pname = ['fxmixer', autochannum], 'sostenuto'
                if a_id == 67: autoloc, pname = ['fxmixer', autochannum], 'soft_pedal'
                if a_id == 68: autoloc, pname = ['fxmixer', autochannum], 'legato'
                
                if a_id == 91: 
                    autoloc, pname, def_val = ['send', autochannum+'_reverb'], 'amount', 0
                    fxgrp = 1
                if a_id == 93: 
                    autoloc, pname, def_val = ['plugin', autochannum+'_chorus', 'amount'], 'amount', 0
                    fxgrp = 2

                if a_id != 'pitch': a_dat.addmul(0, 1/127)
                elif self.pitch_gm: a_dat.addmul(0, 6)

                #send

                #print(ch_num+1, a_id, len(a_dat.points), end=' ')
                if autoloc:
                    paramval = a_dat.get_paramval(self.first_use[ch_num], def_val)
                    if len(a_dat.points) > 1:
                        autopath = convproj.autopath_encode(autoloc+[pname])
                        convproj_obj.automation.create(autoloc+[pname], 'float', False)
                        convproj_obj.automation.data[autopath].nopl_ticks = a_dat
                        convproj_obj.automation.data[autopath].u_nopl_ticks = True
                    #print(autoloc, paramval, end=' ')
                    if fxgrp == 0: fxchannel_obj.params.add(pname, paramval, 'float')
                    if fxgrp == 1: 
                        usedeffects = True
                        fxchannel_obj.sends.add(self.song_channels+1, autochannum+'_reverb', paramval)

                    if fxgrp == 2: 
                        usedeffects = True
                        chorus_used = True
                        pluginid = autochannum+'_chorus'
                        plugin_obj = convproj_obj.add_plugin(pluginid, 'simple', 'chorus')
                        plugin_obj.visual.name = 'Chorus'
                        plugin_obj.params.add('amount', paramval, 'float')
                        fxchannel_obj.fxslots_audio.append(pluginid)
                #print()

        if usedeffects:
            fxchannel_obj = convproj_obj.add_fxchan(self.song_channels+1)
            fxchannel_obj.visual.name = 'Reverb'
            fxchannel_obj.visual_ui.other['docked'] = 1
            plugin_obj, pluginid = convproj_obj.add_plugin_genid('simple', 'reverb')
            plugin_obj.visual.name = 'Reverb'
            fxchannel_obj.fxslots_audio.append(pluginid)

            #fxchannel_obj = convproj_obj.add_fxchan(self.song_channels+2)
            #fxchannel_obj.visual.name = 'Chorus'
            #fxchannel_obj.visual_ui.other['docked'] = 1

        convproj_obj.automation.create(['main', 'bpm'], 'float', False)
        bpm_nopl_ticks = convproj_obj.automation.data[convproj.autopath_encode(['main', 'bpm'])]
        bpm_nopl_ticks.nopl_ticks = self.auto_bpm
        bpm_nopl_ticks.u_nopl_ticks = True
        convproj_obj.timesig_auto = self.auto_timesig

        global_first = 1000000000000000000
        for x in self.first_use:
            if x < global_first and x != -1: global_first = x

        bpm = self.auto_bpm.get_paramval(global_first, 120)

        convproj_obj.params.add('bpm', bpm, 'float')

        self.loop_active = False
        if self.loop_data != [None, None]:
            self.loop_active = True
            if self.loop_data[0] != None: self.loop_start = self.loop_data[0]
            self.loop_end = self.loop_data[1] if self.loop_data[1] else end_pos

        for p, v in self.auto_markers.iter():
            timemarker_obj = convproj_obj.add_timemarker()
            timemarker_obj.position = p
            timemarker_obj.visual.name = v
            timemarker_obj.type = 'text'

        return used_inst_chans
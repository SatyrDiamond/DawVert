# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
#import difflib
import json
import mido
from functions import xtramath
from functions import colors

unusedchannel = 0

def getunusedchannel():
    global unusedchannel
    unusedchannel += 1
    if unusedchannel == 10: unusedchannel += 1
    if unusedchannel == 16: unusedchannel = 1
    return unusedchannel

def add_cmd(i_list, i_pos, i_cmd):
    if i_pos not in i_list: i_list[i_pos] = []
    i_list[i_pos].append(i_cmd)

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'MIDI'
    def getshortname(self): return 'midi'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'MIDI'
        dawinfo_obj.file_ext = 'mid'
        dawinfo_obj.fxtype = 'rack'
        dawinfo_obj.fxrack_params = ['vol','pan','pitch']
        dawinfo_obj.auto_types = ['nopl_ticks']
        dawinfo_obj.track_nopl = True
        dawinfo_obj.plugin_included = ['midi']
    def parse(self, convproj_obj, output_file):
        convproj_obj.change_timings(384, False)
        
        midiobj = mido.MidiFile()
        midiobj.ticks_per_beat = convproj_obj.time_ppq
        multi_miditrack = []

        autotrack = mido.MidiTrack()
        midi_numerator, midi_denominator = convproj_obj.timesig
        midi_tempo = mido.bpm2tempo(convproj_obj.params.get('bpm', 120).value)
        autotrack.append(mido.MetaMessage('time_signature', numerator=midi_numerator, denominator=midi_denominator, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
        autotrack.append(mido.MetaMessage('set_tempo', tempo=midi_tempo, time=0))
        multi_miditrack.append(autotrack)

        for trackid, track_obj in convproj_obj.iter_track():
            miditrack = mido.MidiTrack()

            midi_defined = False
            midi_channel = None
            midi_bank = None
            midi_inst = None
            midi_trackname = track_obj.visual.name if track_obj.visual.name else ''
            midi_trackcolor = track_obj.visual.color

            midi_found, midi_bank, midi_inst, midi_drum = track_obj.get_midi(convproj_obj)

            if midi_channel == None: midi_channel = getunusedchannel()

            if midi_trackname != '': miditrack.append(mido.MetaMessage('track_name', name=midi_trackname, time=0))

            if midi_trackcolor != None: 
                midi_trackcolor = colors.rgb_float_to_rgb_int(midi_trackcolor)

                miditrack.append(mido.MetaMessage('sequencer_specific', data=(83, 105, 103, 110, 1, 255)+midi_trackcolor[::-1])) #from Signal MIDI Editor
                miditrack.append(mido.MetaMessage('sequencer_specific', data=(80, 114, 101, 83, 1, 255)+midi_trackcolor[::-1])) #from Studio One

                red_p1 = midi_trackcolor[0] >> 2
                red_p2 = (midi_trackcolor[0] << 5) & 0x7f
                green_p1 = midi_trackcolor[1] >> 3
                green_p2 = (midi_trackcolor[1] << 4) & 0x7f
                blue_p1 = midi_trackcolor[2] >> 4
                blue_p2 = midi_trackcolor[2] & 0x0f

                anvilcolor = [blue_p2,green_p2+blue_p1,red_p2+green_p1,red_p1]
                miditrack.append(mido.MetaMessage('sequencer_specific', data=(5, 15, 52, anvilcolor[0], anvilcolor[1], anvilcolor[2], anvilcolor[3], 0))) #from Anvil Studio

            miditrack.append(mido.Message('program_change', channel=midi_channel, program=midi_inst, time=0))

            i_list = {}

            multi_miditrack.append(miditrack)

            track_obj.placements.notelist.sort()
            for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in track_obj.placements.notelist.nl:
                for t_key in t_keys:
                    cvmi_n_pos = int(t_pos)
                    cvmi_n_dur = int(t_dur)
                    cvmi_n_key = int(t_key)+60
                    cvmi_n_vol = xtramath.clamp(int(t_vol*127), 0, 127)
                    add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
                    add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

            i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

            prevpos = 0
            for i_list_e in i_list:
                for midi_notedata in i_list[i_list_e]:
                    #print(i_list_e, i_list_e-prevpos, i_list[i_list_e])
                    if midi_notedata[0] == 'note_on': miditrack.append(mido.Message('note_on', channel=midi_channel, note=midi_notedata[1], velocity=midi_notedata[2], time=i_list_e-prevpos))
                    if midi_notedata[0] == 'note_off': miditrack.append(mido.Message('note_off', channel=midi_channel, note=midi_notedata[1], time=i_list_e-prevpos))
                    prevpos = i_list_e

            multi_miditrack.append(miditrack)

        for x in multi_miditrack: midiobj.tracks.append(x)
        midiobj.save(output_file)
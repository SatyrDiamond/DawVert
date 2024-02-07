# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
import plugin_input
import json
import os
import struct
import rpp

def reaper_color_to_cvpj_color(i_color, isreversed): 
    bytecolors = struct.pack('i', i_color)
    if bytecolors[3]:
        if isreversed == True: return colors.rgb_int_to_rgb_float([bytecolors[0],bytecolors[1],bytecolors[2]])
        else: return colors.rgb_int_to_rgb_float([bytecolors[2],bytecolors[1],bytecolors[0]])
    else:
        return [0.51, 0.54, 0.54]

class midi_notes():
    def __init__(self): 
        self.active_notes = [[[] for x in range(127)] for x in range(16)]
        self.midipos = 0
        pass

    def do_note(self, tracksource_var):
        self.midipos += int(tracksource_var[1])
        midicmd, midich = data_bytes.splitbyte(int(tracksource_var[2],16))
        midikey = int(tracksource_var[3],16)
        midivel = int(tracksource_var[4],16)
        if midicmd == 9: self.active_notes[midich][midikey].append([self.midipos, None, midivel])
        if midicmd == 8: self.active_notes[midich][midikey][-1][1] = self.midipos

    def do_output(self, cvpj_notelist):
        for c_mid_ch in range(16):
            for c_mid_key in range(127):
                if self.active_notes[c_mid_ch][c_mid_key] != []:
                    for notedurpos in self.active_notes[c_mid_ch][c_mid_key]:
                        cvpj_notelist.add_r(
                            notedurpos[0], 
                            (notedurpos[1]-notedurpos[0]), 
                            c_mid_key-60, 
                            notedurpos[2]/127, 
                            {'channel': c_mid_ch}
                            )

class input_reaper(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'reaper'
    def getname(self): return 'REAPER'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': [],
        'time_seconds': True,
        'track_hybrid': True,
        'placement_audio_stretch': ['rate']
        }
    def parse(self, convproj_obj, input_file, extra_param):
        bytestream = open(input_file, 'r')
        rpp_data = rpp.load(bytestream)

        convproj_obj.type = 'r'
        convproj_obj.set_timings(4, True)

        bpm = 120
        
        for rpp_var in rpp_data:
            if isinstance(rpp_var, list):
                if rpp_var[0] == 'TEMPO':
                    bpm = float(rpp_var[1])
                    convproj_obj.params.add('bpm', bpm, 'float')
                    tempomul = bpm/120
            else:
                if rpp_var.tag == 'TRACK':
                    cvpj_trackid = 'unknown'
                    cvpj_trackname = ''
                    cvpj_trackcolor = [0.4,0.4,0.4]
                    cvpj_trackvol = 1
                    cvpj_trackpan = 0
                    rpp_trackitems = []

                    for rpp_trackvar in rpp_var.children:
                        if isinstance(rpp_trackvar, list):
                            if rpp_trackvar[0] == 'NAME': cvpj_trackname = rpp_trackvar[1]
                            if rpp_trackvar[0] == 'PEAKCOL': cvpj_trackcolor = reaper_color_to_cvpj_color(int(rpp_trackvar[1]), True)
                            if rpp_trackvar[0] == 'VOLPAN':
                                cvpj_trackvol = float(rpp_trackvar[1])
                                cvpj_trackpan = float(rpp_trackvar[2])
                            if rpp_trackvar[0] == 'TRACKID': cvpj_trackid = rpp_trackvar[1]
                        else:
                            if rpp_trackvar.tag == 'ITEM': rpp_trackitems.append(rpp_trackvar.children)

                    track_obj = convproj_obj.add_track(cvpj_trackid, 'hybrid', 1, False)
                    track_obj.visual.name = cvpj_trackname
                    track_obj.visual.color = cvpj_trackcolor
                    track_obj.params.add('vol', cvpj_trackvol, 'float')
                    track_obj.params.add('pan', cvpj_trackpan, 'float')

                    for rpp_trackitem in rpp_trackitems:
                        cvpj_placement_type = 'notes'
                        cvpj_position = 0
                        cvpj_duration = 1
                        cvpj_offset = 0
                        cvpj_midioffset = 0
                        cvpj_vol = 1
                        cvpj_pan = 0
                        cvpj_muted = False
                        cvpj_color = None
                        cvpj_name = None

                        cvpj_audio_rate = 1
                        cvpj_audio_preserve_pitch = 0
                        cvpj_audio_pitch = 0
                        cvpj_audio_file = ''

                        midi_notes_out = midi_notes()
                        midi_ppq = 96

                        for rpp_placevar in rpp_trackitem:
                            if isinstance(rpp_placevar, list):
                                if rpp_placevar[0] == 'POSITION': cvpj_position = float(rpp_placevar[1])
                                if rpp_placevar[0] == 'LENGTH': cvpj_duration = float(rpp_placevar[1])
                                if rpp_placevar[0] == 'MUTE': cvpj_muted = bool(int(rpp_placevar[1]))
                                if rpp_placevar[0] == 'COLOR': cvpj_color = reaper_color_to_cvpj_color(int(rpp_placevar[1]), False)
                                if rpp_placevar[0] == 'VOLPAN':
                                    cvpj_vol = float(rpp_placevar[1])
                                    cvpj_pan = float(rpp_placevar[2])
                                if rpp_placevar[0] == 'NAME': cvpj_name = rpp_placevar[1]
                                if rpp_placevar[0] == 'SOFFS': cvpj_offset = float(rpp_placevar[1])
                                if rpp_placevar[0] == 'PLAYRATE':
                                    cvpj_audio_rate = float(rpp_placevar[1])
                                    cvpj_audio_preserve_pitch = float(rpp_placevar[2])
                                    cvpj_audio_pitch = float(rpp_placevar[3])

                            else:
                                if rpp_placevar.tag == 'SOURCE':

                                    if rpp_placevar.attrib[0] in ['MP3','FLAC','VORBIS','WAVE']:
                                        cvpj_placement_type = 'audio'
                                        for tracksource_var in rpp_placevar.children:
                                            if tracksource_var[0] == 'FILE':
                                                cvpj_audio_file = tracksource_var[1]

                                    if rpp_placevar.attrib[0] == 'MIDI':
                                        midinotes = [[[] for x in range(127)] for x in range(16)]
                                        midipos = 0
                                        for tracksource_var in rpp_placevar.children:
                                            if tracksource_var[0] == 'HASDATA': midi_ppq = int(tracksource_var[2])
                                            if tracksource_var[0] in ['E', 'e']: midi_notes_out.do_note(tracksource_var)

                        #print(cvpj_offset)
                        cvpj_offset_bpm = ((cvpj_offset)*8)*tempomul

                        if cvpj_placement_type == 'notes': 
                            placement_obj = track_obj.placements.add_notes()
                            placement_obj.position = cvpj_position
                            placement_obj.duration = cvpj_duration
                            placement_obj.cut_type = 'cut'
                            placement_obj.cut_data['start'] = cvpj_offset_bpm
                            midi_notes_out.do_output(placement_obj.notelist)

                        if cvpj_placement_type == 'audio': 
                            placement_obj = track_obj.placements.add_audio()
                            placement_obj.position = cvpj_position
                            placement_obj.duration = cvpj_duration
                            placement_obj.pan = cvpj_pan
                            placement_obj.pitch = cvpj_audio_pitch
                            placement_obj.vol = cvpj_vol
                            sampleref = convproj_obj.add_sampleref(cvpj_audio_file, cvpj_audio_file)
                            placement_obj.sampleref = cvpj_audio_file

                            placement_obj.stretch.algorithm = 'resample' if cvpj_audio_preserve_pitch == 0 else 'stretch'
                            placement_obj.stretch.use_tempo = False
                            placement_obj.stretch.rate = cvpj_audio_rate

                            placement_obj.cut_type = 'cut'
                            placement_obj.cut_data['start'] = cvpj_offset_bpm/cvpj_audio_rate
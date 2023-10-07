# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song
from functions import colors
from functions import note_data
from functions import notelist_data
from functions import data_values
from functions_tracks import tracks_r
import plugin_input
import json
import os
import struct
import rpp

def reaper_color_to_cvpj_color(i_color, isreversed): 
    bytecolors = struct.pack('i', i_color)
    if isreversed == True: return colors.rgb_int_to_rgb_float([bytecolors[0],bytecolors[1],bytecolors[2]])
    else: return colors.rgb_int_to_rgb_float([bytecolors[2],bytecolors[1],bytecolors[0]])

def getsamplefile(filename):
    localpath = os.path.join(projpath, filename)
    if os.path.exists(filename): return filename
    else: return localpath

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
    def parse(self, input_file, extra_param):
        global projpath
        bytestream = open(input_file, 'r')
        projpath = os.path.dirname(os.path.realpath(input_file))

        rpp_data = rpp.load(bytestream)

        cvpj_l = {}

        bpm = 120

        for rpp_var in rpp_data:
            if isinstance(rpp_var, list):
                if rpp_var[0] == 'TEMPO':
                    bpm = float(rpp_var[1])
                    song.add_param(cvpj_l, 'bpm', bpm)
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

                    tracks_r.track_create(cvpj_l, cvpj_trackid, 'hybrid')
                    tracks_r.track_visual(cvpj_l, cvpj_trackid, name=cvpj_trackname, color=cvpj_trackcolor)
                    
                    tracks_r.track_param_add(cvpj_l, cvpj_trackid, 'vol', cvpj_trackvol, 'float')
                    tracks_r.track_param_add(cvpj_l, cvpj_trackid, 'pan', cvpj_trackpan, 'float')

                    for rpp_trackitem in rpp_trackitems:
                        cvpj_placement = {}
                        cvpj_placement_type = 'notes'
                        cvpj_audio_rate = 1
                        cvpj_audio_preserve_pitch = 0
                        cvpj_audio_pitch = 0
                        cvpj_duration = 0
                        cvpj_offset = 0
                        cvpj_midioffset = 0
                        cvpj_vol = 0
                        cvpj_pan = 0
                        for rpp_placevar in rpp_trackitem:
                            if isinstance(rpp_placevar, list):
                                if rpp_placevar[0] == 'POSITION': cvpj_placement['position'] = float(rpp_placevar[1])
                                if rpp_placevar[0] == 'LENGTH': cvpj_duration = float(rpp_placevar[1])
                                if rpp_placevar[0] == 'MUTE': cvpj_placement['muted'] = bool(int(rpp_placevar[1]))
                                if rpp_placevar[0] == 'COLOR': cvpj_placement['color'] = reaper_color_to_cvpj_color(int(rpp_placevar[1]), False)
                                if rpp_placevar[0] == 'VOLPAN':
                                    cvpj_vol = float(rpp_placevar[1])
                                    cvpj_pan = float(rpp_placevar[2])
                                if rpp_placevar[0] == 'NAME': cvpj_placement['name'] = rpp_placevar[1]
                                if rpp_placevar[0] == 'SOFFS': 
                                    cvpj_offset = float(rpp_placevar[1])
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
                                                cvpj_placement['file'] = getsamplefile(tracksource_var[1])

                                    if rpp_placevar.attrib[0] == 'MIDI':
                                        cvpj_placement['notelist'] = []
                                        midinotes = [[[] for x in range(127)] for x in range(16)]
                                        midipos = 0
                                        midippq = 96
                                        for tracksource_var in rpp_placevar.children:
                                            if tracksource_var[0] == 'HASDATA': midippq = int(tracksource_var[2])
                                            if tracksource_var[0] in ['E', 'e']:
                                                midipos += int(tracksource_var[1])
                                                midicmd, midich = data_bytes.splitbyte(int(tracksource_var[2],16))
                                                midikey = int(tracksource_var[3],16)
                                                midivel = int(tracksource_var[4],16)
                                                #print(midipos, midicmd-8, midich, midikey)
                                                if midicmd == 9: midinotes[midich][midikey].append([midipos, None, midivel])
                                                if midicmd == 8: midinotes[midich][midikey][-1][1] = midipos

                                        for c_mid_ch in range(16):
                                            for c_mid_key in range(127):
                                                if midinotes[c_mid_ch][c_mid_key] != []:
                                                    for notedurpos in midinotes[c_mid_ch][c_mid_key]:
                                                        cvpj_notedata = note_data.rx_makenote(
                                                                notedurpos[0]/(midippq/4), 
                                                                (notedurpos[1]-notedurpos[0])/(midippq/4), 
                                                                c_mid_key-60, 
                                                                notedurpos[2]/127, None)
                                                        cvpj_notedata['channel'] = c_mid_ch
                                                        cvpj_placement['notelist'].append(cvpj_notedata)
                                                    #print(c_mid_ch, c_mid_key, midinotes[c_mid_ch][c_mid_key])

                        #print(cvpj_offset)
                        cvpj_offset_bpm = ((cvpj_offset)*8)*tempomul

                        if cvpj_placement_type == 'notes': 
                            cvpj_cutend = (  (cvpj_duration+cvpj_offset) *8)*tempomul
                            cvpj_placement['duration'] = cvpj_duration
                            cvpj_placement['cut'] = {'type': 'cut', 'start': cvpj_offset_bpm, 'end': cvpj_cutend}
                            tracks_r.add_pl(cvpj_l, cvpj_trackid, 'notes', cvpj_placement)

                        if cvpj_placement_type == 'audio': 
                            cvpj_offset /= cvpj_audio_rate
                            cvpj_cutend = (((cvpj_duration+cvpj_offset)*8)*tempomul)
                            cvpj_placement['duration'] = cvpj_duration
                            cvpj_placement['cut'] = {'type': 'cut', 'start': cvpj_offset_bpm/cvpj_audio_rate, 'end': cvpj_cutend}
                            cvpj_placement['vol'] = cvpj_vol
                            cvpj_placement['pan'] = cvpj_pan
                            cvpj_placement['audiomod'] = {}
                            if cvpj_audio_preserve_pitch == 0: cvpj_placement['audiomod']['stretch_algorithm'] = 'resample'
                            else: cvpj_placement['audiomod']['stretch_algorithm'] = 'stretch'
                            cvpj_placement['audiomod']['pitch'] = cvpj_audio_pitch
                            cvpj_placement['audiomod']['stretch_method'] = 'rate_speed'
                            cvpj_placement['audiomod']['stretch_data'] = {'rate': cvpj_audio_rate}
                            tracks_r.add_pl(cvpj_l, cvpj_trackid, 'audio', cvpj_placement)

                        #print(cvpj_placement['duration'], cvpj_placement['cut'])

        return json.dumps(cvpj_l)

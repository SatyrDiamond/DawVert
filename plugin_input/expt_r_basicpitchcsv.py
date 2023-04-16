# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import tracks
from functions import placements
import plugin_input
import json

class input_ex_basic_pitch(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'expt_basicpitchcsv'
    def getname(self): return 'Basic Pitch CSV'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': False,
        'placement_warp': False,
        'no_placements': False,
        'no_pl_auto': False,
        'pl_audio_events': False,
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        pitchcsv = bytestream.readlines()
        cvpj_l = {}
        cvpj_notelist = []
        linenum = 0
        for row_unsep in pitchcsv:
            #start_time_s, end_time_s, pitch_midi, velocity, pitch_bend
            if linenum != 0: 
                csvdata = [ float(x) for x in row_unsep.strip().split(',') ]
                t_autodata = csvdata[4:]
                cvpj_note = note_data.rx_makenote(
                    csvdata[0]*8, 
                    (csvdata[1]-csvdata[0])*8, 
                    int(csvdata[2]-60), 
                    csvdata[3]/128, 
                    None)
                cvpj_notemod = cvpj_note['notemod'] = {}
                cvpj_notemod['auto'] = {}
                cvpj_notemod['auto']['pitch'] = []
                autonum = 0
                for point in t_autodata:
                    cvpj_notemod['auto']['pitch'].append({'position': autonum, 'value': (point-1)/4})
                    autonum += 0.1
                cvpj_notelist.append(cvpj_note)
            linenum += 1

        tracks.r_create_inst(cvpj_l, 'basicpitch', {})
        tracks.r_pl_notes(cvpj_l, 'basicpitch', placements.nl2pl(cvpj_notelist))

        cvpj_l['bpm'] = 120
        return json.dumps(cvpj_l)
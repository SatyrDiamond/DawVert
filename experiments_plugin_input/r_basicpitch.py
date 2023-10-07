# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import placement_data
from functions_tracks import tracks_r
import experiments_plugin_input
import json

class input_ex_basic_pitch(experiments_plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'basic_pitch'
    def getname(self): return 'Basic Pitch'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': False,
        'placement_cut': False,
        'placement_loop': False,
        'track_nopl': False,
        'auto_nopl': False,
        'placement_audio_events': False,
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')

        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH

        model_output, midi_data, note_events = predict(input_file)

        cvpj_l = {}
        cvpj_notelist = []
        linenum = 0
        for note_event in note_events:
            cvpj_note = note_data.rx_makenote(
                float(note_event[0])*8, 
                float(note_event[1]-note_event[0])*8, 
                int(note_event[2]-60), 
                float(note_event[3]), 
                None)
            cvpj_notemod = cvpj_note['notemod'] = {}
            cvpj_notemod['auto'] = {}
            cvpj_notemod['auto']['pitch'] = []
            if not all(item == 0 for item in note_event[4]):
                autonum = 0
                for point in note_event[4]:
                    cvpj_notemod['auto']['pitch'].append({'position': autonum, 'value': (point-1)/4})
                    autonum += 0.1
            cvpj_notelist.append(cvpj_note)

        tracks_r.track_create(cvpj_l, 'basicpitch', 'instrument')
        tracks_r.add_pl(cvpj_l, 'basicpitch', 'notes', placement_data.nl2pl(cvpj_notelist))

        cvpj_l['bpm'] = 120
        return json.dumps(cvpj_l)
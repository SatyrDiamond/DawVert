# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json

class input_cvpj_m(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'cvpj_m'
    def getname(self): return 'cvpj_m'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def getdawcapabilities(self): 
        return {
        'fxrack': 'debug',
        'r_track_lanes': 'debug',
        'placement_cut': 'debug',
        'placement_loop': 'debug',
        'no_placements': 'debug',
        'no_pl_auto': 'debug',
        'audio_events': 'debug',
        }
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(12)
        if bytesdata == b'CONVPROJ___M': return True
        else: return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        data = ''.join(file_data.split('\n')[1:])
        return data


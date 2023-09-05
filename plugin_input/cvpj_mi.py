# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import plugin_input
import json

class input_cvpj_mi(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'cvpj_mi'
    def getname(self): return 'cvpj_mi'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return True
    def getdawcapabilities(self): 
        return {
        'fxrack': 'debug',
        'track_lanes': 'debug',
        'placement_cut': 'debug',
        'placement_loop': 'debug',
        'track_nopl': 'debug',
        'auto_nopl': 'debug',
        'placement_audio_events': 'debug',
        'placement_audio_stretch': ['warp', 'rate']
        }
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(12)
        if bytesdata == b'CONVPROJ__MI': return True
        else: return False
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        file_data = bytestream.read()
        data = ''.join(file_data.split('\n')[1:])
        return data


# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'DEBUG'
    def getshortname(self): return 'cvpj_mi'
    def gettype(self): return 'mi'
    def plugin_archs(self): return None
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
    def getsupportedplugformats(self): return ['vst2', 'vst3', 'clap', 'ladspa']
    def getsupportedplugins(self): return ['sampler:single', 'sampler:multi', 'sampler:slicer', 'soundfont2']
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)
        with open(output_file, "w") as fileout:
            fileout.write("CONVPROJ__MI\n")
            json.dump(projJ, fileout, indent=4, sort_keys=True)
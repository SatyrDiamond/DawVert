# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'DEBUG'
    def getshortname(self): return 'cvpj'
    def gettype(self): return 'debug'
    def plugin_archs(self): return None
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
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)
        with open(output_file, "w") as fileout:
            fileout.write("CONVPROJ****\n")
            json.dump(projJ, fileout, indent=4, sort_keys=True)
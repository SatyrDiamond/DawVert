# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'DEBUG'
    def getshortname(self): return 'cvpj_f'
    def gettype(self): return 'f'
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)
        with open(output_file, "w") as fileout:
            fileout.write("CONVPROJ___F\n")
            json.dump(projJ, fileout, indent=4, sort_keys=True)
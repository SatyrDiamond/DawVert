# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import png
import json

class input_color_art(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'color_art'
    def getname(self): return 'Color Art'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        reader = png.Reader(filename=input_file)
        w, h, pixels, metadata = reader.read_flat()

        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_trackplacements = {}

        cvpj_l_track_master = {}

        print(pixels)

        pcnt = 0

        if w >= 40:
            print('39 max')

        for height in range(h):
            trackid = str('track'+str(height))

            trackdata = {}
            trackdata['name'] = '.'
            trackdata['type'] = 'instrument'
            trackdata['placements'] = []
            trackdata["instdata"] = {}
            trackdata["instdata"]['plugin'] = 'none'

            cvpj_l_trackplacements[trackid] = {}
            cvpj_l_trackplacements[trackid]['notes'] = []

            for width in range(w):
                placement_pl = {}
                placement_pl['color'] = [pixels[pcnt]/255,pixels[pcnt+1]/255,pixels[pcnt+2]/255]
                placement_pl['position'] = width*16
                placement_pl['duration'] = 16
                placement_pl['notelist'] = [{}]
                placement_pl['notelist'][0]["key"] = 0
                placement_pl['notelist'][0]["position"] = 0
                placement_pl['notelist'][0]["duration"] = 0.2

                cvpj_l_trackplacements[trackid]['notes'].append(placement_pl)

                pcnt += 4

            cvpj_l_trackdata[trackid] = trackdata
            cvpj_l_trackordering.append(trackid)

        print(w, h)

        cvpj_l = {}
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        cvpj_l['bpm'] = 140
        cvpj_l['track_data'] = cvpj_l_trackdata
        cvpj_l['track_order'] = cvpj_l_trackordering
        cvpj_l['track_placements'] = cvpj_l_trackplacements
        cvpj_l['track_master'] = cvpj_l_track_master
        return json.dumps(cvpj_l)



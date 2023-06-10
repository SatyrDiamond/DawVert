# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image

import experiments_plugin_input
import json

class input_color_art(experiments_plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'color_art'
    def getname(self): return 'Color Art'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': False,
        'placement_cut': True,
        'placement_loop': True,
        'track_nopl': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        im = Image.open(input_file)
        px = im.load()

        w, h = im.size

        cvpj_l_trackdata = {}
        cvpj_l_trackordering = []
        cvpj_l_trackplacements = {}

        cvpj_l_track_master = {}

        pcnt = 0

        if h > 28:
            downsize = 28/h
            newsize = (int(im.width*downsize), int(im.height*downsize))
            im = im.resize(newsize, Image.LANCZOS)
            w, h = newsize

        for height in range(h-1):
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
                coordinate = width, height

                pixel_color = im.getpixel(coordinate)

                placement_pl = {}
                placement_pl['color'] = [pixel_color[0]/255,pixel_color[1]/255,pixel_color[2]/255]
                placement_pl['position'] = width*16
                placement_pl['duration'] = 16
                placement_pl['notelist'] = [{}]
                placement_pl['notelist'][0]["key"] = 0
                placement_pl['notelist'][0]["position"] = 0
                placement_pl['notelist'][0]["duration"] = 0.2

                cvpj_l_trackplacements[trackid]['notes'].append(placement_pl)

            cvpj_l_trackdata[trackid] = trackdata
            cvpj_l_trackordering.append(trackid)

        cvpj_l = {}
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False
        
        cvpj_l['bpm'] = 140
        cvpj_l['track_data'] = cvpj_l_trackdata
        cvpj_l['track_order'] = cvpj_l_trackordering
        cvpj_l['track_placements'] = cvpj_l_trackplacements
        cvpj_l['track_master'] = cvpj_l_track_master
        return json.dumps(cvpj_l)



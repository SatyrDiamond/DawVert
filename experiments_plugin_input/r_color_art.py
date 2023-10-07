# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image

import experiments_plugin_input
import json
from functions_tracks import tracks_r

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

        cvpj_l = {}
        
        w, h = im.size

        pcnt = 0

        if h > 28:
            downsize = 28/h
            newsize = (int(im.width*downsize), int(im.height*downsize))
            im = im.resize(newsize, Image.LANCZOS)
            w, h = newsize

        for height in range(h-1):
            trackid = str('track'+str(height))

            tracks_r.track_create(cvpj_l, trackid, 'instrument')
            tracks_r.track_visual(cvpj_l, trackid, name='.')

            for width in range(w):
                coordinate = width, height

                pixel_color = im.getpixel(coordinate)

                placement_pl = {}
                placement_pl['color'] = [pixel_color[0]/255,pixel_color[1]/255,pixel_color[2]/255]
                placement_pl['position'] = width*16
                placement_pl['duration'] = 16
                placement_pl['notelist'] = [{"key": 0, "position": 0, "duration": 0.2}]
                tracks_r.add_pl(cvpj_l, trackid, 'notes', placement_pl)

        cvpj_l['bpm'] = 140
        return json.dumps(cvpj_l)



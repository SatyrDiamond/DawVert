# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_tracks import tracks_r
from PIL import Image
import plugins

class input_color_art(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'color_art'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Color Art'
		dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, False)

		im = Image.open(input_file)

		w, h = im.size

		if h > 28:
			downsize = 28/h
			newsize = (int(im.width*downsize), int(im.height*downsize))
			im = im.resize(newsize, Image.LANCZOS)
			w, h = newsize

		for height in range(h-1):
			trackid = str('track'+str(height))
			track_obj = convproj_obj.add_track(trackid, 'instrument', 1, False)
			track_obj.visual.name = '.'
			for width in range(w):
				coordinate = width, height
				pixel_color = im.getpixel(coordinate)
				placement_obj = track_obj.placements.add_notes()
				placement_obj.visual.color.set_int([pixel_color[0],pixel_color[1],pixel_color[2]])
				placement_obj.time.position = width*16
				placement_obj.time.duration = 16
				placement_obj.notelist.add_r(0, 0.2, 0, 1, {})



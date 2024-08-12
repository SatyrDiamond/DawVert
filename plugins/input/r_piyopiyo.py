# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import struct
import os.path
from functions import colors
from objects import globalstore
from objects.file_proj import proj_piyopiyo

def parse_notes(convproj_obj, trackid, notes_data, track_obj, keyoffset):
	for pos, nd in enumerate(notes_data):
		notes, pan = nd
		track_obj.placements.notelist.add_r_multi(pos, 1, [(x+keyoffset)-20 for x in notes], 1, {})
		if pan != 0:
			convproj_obj.automation.add_autotick(['track', trackid, 'pan'], 'float', pos, (pan-4)/3)

class input_piyopiyo(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'piyopiyo'
	def gettype(self): return 'r'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'PiyoPiyo'
		dawinfo_obj.file_ext = 'pmd'
		dawinfo_obj.plugin_included = ['universal:synth-osc']
		dawinfo_obj.auto_types = ['nopl_ticks']
		dawinfo_obj.track_nopl = True
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(3)
		if bytesdata == b'PMD': return True
		else: return False

	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		project_obj = proj_piyopiyo.piyopiyo_song()
		project_obj.load_from_file(input_file)

		globalstore.dataset.load('piyopiyo', './data_main/dataset/piyopiyo.dset')
		colordata = colors.colorset.from_dataset('piyopiyo', 'inst', 'main')

		for tracknum in range(3):
			pmdtrack_obj = project_obj.tracks[tracknum]
			keyoffset = (pmdtrack_obj.octave-2)*12

			idval = str(tracknum)
			track_obj = convproj_obj.add_track(idval, 'instrument', 0, False)
			track_obj.visual.name = 'Inst #'+str(tracknum+1)
			track_obj.visual.color.set_float(colordata.getcolornum(tracknum))
			track_obj.params.add('vol', pmdtrack_obj.volume/250, 'float')

			plugin_obj, pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
			plugin_obj.role = 'synth'
			osc_data = plugin_obj.osc_add()
			osc_data.prop.type = 'wave'
			osc_data.prop.nameid = 'main'
			wave_obj = plugin_obj.wave_add('main')
			wave_obj.set_all_range(pmdtrack_obj.waveform, -128, 128)
			plugin_obj.env_blocks_add('vol', pmdtrack_obj.envelope, 1/64, 128, None, None)
			plugin_obj.env_points_from_blocks('vol')
			track_obj.inst_pluginid = pluginid
			parse_notes(convproj_obj, idval, project_obj.notes_data[tracknum], track_obj, keyoffset)

		track_obj = convproj_obj.add_track("3", 'instrument', False, False)
		track_obj.visual.name = 'Drums'
		track_obj.visual.color.set_float(colordata.getcolornum(3))
		track_obj.params.add('vol', project_obj.perc_volume/250, 'float')
		plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-piyopiyo', 'drums')
		plugin_obj.role = 'synth'
		track_obj.inst_pluginid = pluginid
		parse_notes(convproj_obj, '3', project_obj.notes_data[3], track_obj, 0)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (120/project_obj.musicwait)*120, 'float')

		convproj_obj.loop_active = True
		convproj_obj.loop_start = project_obj.loopstart
		convproj_obj.loop_end = project_obj.loopend
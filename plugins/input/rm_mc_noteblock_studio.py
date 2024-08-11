# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from objects import globalstore
from objects.file_proj import proj_nbs
import json
import math
import plugins

class input_gt_mnbs(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'mnbs'
	def gettype(self): return 'rm'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Minecraft Note Block Studio'
		dawinfo_obj.file_ext = 'nbs'
		dawinfo_obj.plugin_included = ['midi']
		dawinfo_obj.track_nopl = True
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'rm'
		convproj_obj.set_timings(4, True)
		
		nbs_file = proj_nbs.nbs_song()
		nbs_file.load_from_file(input_file)

		globalstore.dataset.load('noteblockstudio', './data_main/dataset/noteblockstudio.dset')

		convproj_obj.metadata.name = nbs_file.name
		convproj_obj.metadata.author = nbs_file.author
		convproj_obj.metadata.original_author = nbs_file.orgauthor
		convproj_obj.metadata.comment_text = nbs_file.description
		convproj_obj.params.add('bpm', (nbs_file.tempo/800)*120, 'float')
		convproj_obj.timesig = [nbs_file.numerator, 4]

		for instnum in range(16):
			instid = 'NoteBlock'+str(instnum)
			inst_obj = convproj_obj.add_instrument(instid)
			midifound = inst_obj.from_dataset('noteblockstudio', 'inst', str(instnum), True)
			if midifound: inst_obj.to_midi(convproj_obj, instid, True)

		for nbs_layer, layer_obj in enumerate(nbs_file.layers):
			cvpj_trackid = str(nbs_layer+1)
			track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 1, False)
			track_obj.visual.name = layer_obj.name if layer_obj.name else cvpj_trackid
			#track_obj.visual.color = [0.23, 0.23, 0.23]
			track_obj.params.add('vol', layer_obj.vol/100, 'float')
			track_obj.params.add('pan', (layer_obj.stereo/100)-1, 'float')
			for note_obj in layer_obj.notes: track_obj.placements.notelist.add_m('NoteBlock'+str(note_obj.inst), note_obj.pos, 2, note_obj.key-39, note_obj.vel/100, {'pan': (note_obj.pan/100)-1, 'finepitch': note_obj.pitch})

		custominstid = 16
		for custominstid, custom_obj in enumerate(nbs_file.custom):
			instid = 'NoteBlock'+str(custominstid+16)
			inst_obj = convproj_obj.add_instrument(instid)
			inst_obj.visual.name = custom_obj.name
			inst_obj.visual.color.set_hsv(custominstid*0.2, 1, 0.5)
			inst_obj.datavals.add('middlenote', -(custom_obj.key-51))
			plugin_obj, sampleref_obj, samplepart_obj = convproj_obj.add_plugin_sampler(instid, custom_obj.file)
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			inst_obj.pluginid = instid
			sampleref_obj.find_relative('../Data/Sounds')

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
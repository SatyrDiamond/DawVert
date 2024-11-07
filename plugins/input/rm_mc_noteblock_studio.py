# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import math
import plugins

from objects import globalstore

class input_gt_mnbs(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'mnbs'
	def get_name(self): return 'Minecraft Note Block Studio'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['nbs']
		in_dict['track_nopl'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single', 'universal:midi']
		in_dict['projtype'] = 'rm'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_nbs
		from objects.convproj import fileref

		convproj_obj.type = 'rm'
		convproj_obj.set_timings(4, True)
		
		fileref.filesearcher.add_searchpath_partial('mnbs_sounds', '../Data/Sounds', 'projectfile')

		project_obj = proj_nbs.nbs_song()
		if not project_obj.load_from_file(input_file): exit()

		globalstore.dataset.load('noteblockstudio', './data_main/dataset/noteblockstudio.dset')

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.author
		convproj_obj.metadata.original_author = project_obj.orgauthor
		convproj_obj.metadata.comment_text = project_obj.description
		convproj_obj.params.add('bpm', (project_obj.tempo/800)*120, 'float')
		convproj_obj.timesig = [project_obj.numerator, 4]

		for instnum in range(16):
			instid = 'NoteBlock'+str(instnum)
			inst_obj = convproj_obj.instrument__add(instid)
			midifound = inst_obj.from_dataset('noteblockstudio', 'inst', str(instnum), True)
			if midifound: inst_obj.to_midi(convproj_obj, instid, True)

		for nbs_layer, layer_obj in enumerate(project_obj.layers):
			cvpj_trackid = str(nbs_layer+1)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instruments', 1, False)
			track_obj.visual.name = layer_obj.name if layer_obj.name else cvpj_trackid
			track_obj.params.add('vol', layer_obj.vol/100, 'float')
			track_obj.params.add('pan', (layer_obj.stereo/100)-1, 'float')
			for note_obj in layer_obj.notes: track_obj.placements.notelist.add_m('NoteBlock'+str(note_obj.inst), note_obj.pos, 2, note_obj.key-39, note_obj.vel/100, {'pan': (note_obj.pan/100)-1, 'finepitch': note_obj.pitch})

		custominstid = 16
		for custominstid, custom_obj in enumerate(project_obj.custom):
			instid = 'NoteBlock'+str(custominstid+16)
			inst_obj = convproj_obj.instrument__add(instid)
			inst_obj.visual.name = custom_obj.name
			inst_obj.visual.color.set_hsv(custominstid*0.2, 1, 0.5)
			inst_obj.datavals.add('middlenote', -(custom_obj.key-51))
			plugin_obj, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler(instid, custom_obj.file, None)
			if sampleref_obj: sampleref_obj.find_relative('mnbs_sounds')
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			inst_obj.pluginid = instid

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
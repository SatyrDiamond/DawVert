# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
from objects import colors
from objects import globalstore

import logging
logger_input = logging.getLogger('input')

#try: 
#	import UnityPy
#	from UnityPy.helpers import TypeTreeHelper
#	TypeTreeHelper.read_typetree_c = False
#except: UnityPy_exists = False
#else: UnityPy_exists = True

#class onebit_external:
#	def __init__(self):
#		self.loaded = False
#		self.env = None
#		self.audiofiles = {}
#
#	def load_file(self, filepath):
#		if os.path.exists(filepath):
#			if UnityPy_exists:
#				self.env = UnityPy.load(filepath)
#				for obj in self.env.objects:
#					data = obj.read()
#					if obj.type.name == 'AudioClip': self.audiofiles[data.name] = data
#			else:
#				logger_input.warning('1bitdragon resource file found but UnityPy is missing.')
#
#	def save_audio(self, audioname, filepath):
#		if audioname in self.audiofiles:
#			data = self.audiofiles[audioname]
#			if data.samples:
#				firstname = list(data.samples)
#				with open(filepath, "wb") as f: f.write(data.samples[firstname[0]])
#				logger_input.info('extracted '+audioname+' as '+filepath)

class input_1bitdragon(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return '1bitdragon'
	def get_name(self): return '1BITDRAGON'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['1bd']
		in_dict['track_lanes'] = True
		in_dict['projtype'] = 'ms'
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_1bitdragon

		convproj_obj.set_timings(4, True)
		convproj_obj.type = 'ms'

		project_obj = proj_1bitdragon.onebitd_song()
		if not project_obj.load_from_file(input_file): exit()

		#onebit_ext = onebit_external()
		#onebit_ext.load_file(os.path.join(dv_config.path_external_data,'1bitdragon','1BITDRAGON_Data','resources.assets'))

		globalstore.dataset.load('1bitdragon', './data_main/dataset/1bitdragon.dset')
		colordata = colors.colorset.from_dataset('1bitdragon', 'track', 'main')

		onebitd_scaleId = project_obj.scaleId
		onebitd_scaletype = (onebitd_scaleId//12)
		onebitd_scalekey = onebitd_scaleId-(onebitd_scaletype*12)

		if onebitd_scaletype == 0: note_scale = [[0 ,2 ,4 ,7 ,9 ,12,14,16,19,21,24,26,28,31,33,36] ,-24]
		if onebitd_scaletype == 1: note_scale = [[0 ,3 ,5 ,7 ,10,12,15,17,19,22,24,27,29,31,34,36] ,-24]
		if onebitd_scaletype == 2: note_scale = [[0 ,2 ,4 ,5 ,7 ,9 ,11,12,14,16,17,19,21,23,24,26] ,-24]
		if onebitd_scaletype == 3: note_scale = [[0 ,2 ,3 ,4 ,7 ,8 ,10,12,14,15,16,19,20,22,24,26] ,-24]
		if onebitd_scaletype == 4: note_scale = [[0 ,2 ,3 ,5 ,7 ,9 ,10,12,14,15,17,19,21,22,24,26] ,-24]
		if onebitd_scaletype == 5: note_scale = [[0 ,1 ,4 ,5 ,6 ,9 ,10,12,13,16,17,18,21,22,24,25] ,-24]
		if onebitd_scaletype == 6: note_scale = [range(16),-12]
		note_scale = [x+note_scale[1]+onebitd_scalekey for x in note_scale[0]]

		track_data = []
		for plnum in range(9):
			track_obj = convproj_obj.track__add(str(plnum), 'instruments', 1, False)

			track_obj.visual.color.from_colorset_num(colordata, plnum)
			track_data.append(track_obj)

		instnames = []

		used_inst = {}
		used_drums = {}
		curpos = 0
		for blocknum, block_obj in enumerate(project_obj.blocks):
			convproj_obj.scene__add(str(blocknum))

			for inst in block_obj.instruments:
				instid = inst.get_instid()
				if instid not in used_inst: 
					used_inst[instid] = inst

			ids_inst = [x.get_instid() for x in block_obj.instruments]

			for instnum, instdata in enumerate(block_obj.n_inst):
				dur = max([len(x) for x in instdata])

				if dur:
					trscene_obj = convproj_obj.track__add_scene(str(instnum), str(blocknum), 'main')
					placement_obj = trscene_obj.add_notes()
					placement_obj.visual.name = block_obj.instruments[3-instnum].preset
					placement_obj.time.set_posdur(0, 128)
					for notenum, notesdata in enumerate(instdata):
						for pos, notedata in notesdata:
							dur = notedata['duration'] if 'duration' in notedata else 1
							vol = notedata['velocity'] if 'velocity' in notedata else 1
							placement_obj.notelist.add_m(ids_inst[3-instnum], pos, dur, note_scale[notenum], vol, None)

			for drum in block_obj.drums:
				instid = drum.get_instid()
				if instid not in used_drums: used_drums[instid] = drum

			ids_drums = [x.get_instid() for x in block_obj.drums]
			for drumnum, drumdata in enumerate(block_obj.n_drums):
				if drumdata:
					trscene_obj = convproj_obj.track__add_scene(str(8-drumnum), str(blocknum), 'main')
					placement_obj = trscene_obj.add_notes()
					placement_obj.visual.name = block_obj.drums[4-drumnum].preset
					placement_obj.time.set_posdur(0, 128)
					for pos, notedata in drumdata:
						dur = notedata['duration'] if 'duration' in notedata else 1
						vol = notedata['velocity'] if 'velocity' in notedata else 1
						placement_obj.notelist.add_m(ids_drums[4-drumnum], pos, dur, 0, vol, None)

			scenepl_obj = convproj_obj.scene__add_pl()
			scenepl_obj.position = curpos
			scenepl_obj.duration = curpos+128
			scenepl_obj.id = str(blocknum)

			curpos += 128

		for instid, instdata in used_inst.items():
			instname = instdata.preset
 
			inst_obj = convproj_obj.instrument__add(instid)
			inst_obj.visual.name = instname
			inst_obj.params.add('enabled', instdata.on, 'int')
			inst_obj.params.add('vol', instdata.volume, 'float')

			audiofilepath = os.path.join(dv_config.path_samples_extracted, str(instname)+'.wav')
			inst_obj.datavals.add('middlenote', -3)

			#if instname not in instnames:
			#	onebit_ext.save_audio(instname, audiofilepath)
			#	plugin_obj, inst_obj.pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(audiofilepath, None)
			#	plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			#	instnames.append(instname)

		for drumid, drumdata in used_drums.items():
			instname = drumdata.preset
			
			inst_obj = convproj_obj.instrument__add(drumid)
			inst_obj.visual.name = instname
			inst_obj.params.add('enabled', drumdata.on, 'int')
			inst_obj.params.add('vol', drumdata.volume, 'float')
			inst_obj.is_drum = True

			audiofilepath = os.path.join(dv_config.path_samples_extracted, str(instname)+'.wav')
			inst_obj.datavals.add('middlenote', -3)

			#if instname not in instnames:
			#	onebit_ext.save_audio(instname, audiofilepath)
			#	plugin_obj, inst_obj.pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(audiofilepath, None)
			#	plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 10, 1)
			#	instnames.append(instname)

		convproj_obj.do_actions.append('do_lanefit')

		convproj_obj.track_master.params.add('vol', project_obj.volume, 'float')
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')

		plugin_obj = convproj_obj.plugin__add('master-reverb', 'simple', 'reverb', None)
		plugin_obj.role = 'fx'
		plugin_obj.visual.name = 'Reverb'
		plugin_obj.fxdata_add(project_obj.reverb, 0.5)
		convproj_obj.track_master.fxslots_audio.append('master-reverb')
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import numpy as np
from objects import globalstore

class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'pixitracker'
	def get_name(self): return 'Pixitracker'
	def get_priority(self): return 0
	def supported_autodetect(self): return True
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['piximod']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'rs'
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(8)
		if bytesdata == b'PIXIMOD1': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import audio_data
		from objects import colors
		from objects.file_proj import proj_piximod

		convproj_obj.type = 'rs'
		convproj_obj.set_timings(4, False)

		globalstore.dataset.load('pixitracker', './data_main/dataset/pixitracker.dset')
		colordata = colors.colorset.from_dataset('pixitracker', 'inst', 'main')

		project_obj = proj_piximod.piximod_song()
		if not project_obj.load_from_file(input_file): exit()

		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.track_master.params.add('vol', project_obj.vol/100, 'float')

		samplefolder = dv_config.path_samples_extracted
		
		for instnum, pixi_sound in enumerate(project_obj.sounds):
			cvpj_instid = 'pixi_'+str(instnum)

			track_obj = convproj_obj.track__add(cvpj_instid, 'instrument', 1, False)
			track_obj.visual.name = 'Inst #'+str(instnum+1)
			track_obj.visual.color.set_float(colordata.getcolor())
			track_obj.params.add('pitch', (pixi_sound.fine/100)+(0.2 if pixi_sound.channels == 1 else 0.4), 'float')
			track_obj.params.add('vol', pixi_sound.volume/100, 'float')
			track_obj.datavals.add('middlenote', pixi_sound.transpose*-1)

			wave_path = samplefolder + str(instnum) + '.wav'

			audio_obj = audio_data.audio_obj()
			audio_obj.channels = pixi_sound.channels
			audio_obj.rate = pixi_sound.rate//pixi_sound.channels
			audio_obj.set_codec('int16')
			audio_obj.pcm_from_bytes(pixi_sound.data)
			audio_obj.to_file_wav(wave_path)

			plugin_obj, track_obj.inst_pluginid, sampleref_obj, samplepart_obj = convproj_obj.plugin__addspec__sampler__genid(wave_path, None)
			plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
			samplepart_obj.point_value_type = "samples"
			if pixi_sound.end != 0:
				samplepart_obj.start = pixi_sound.start
				samplepart_obj.end = pixi_sound.end
				samplepart_obj.length = len(pixi_sound.data)//pixi_sound.channels

		for pat_num, pat_data_r in project_obj.patterns.items():
			sceneid = str(pat_num)
			convproj_obj.scene__add(sceneid)

			pat_data = np.rot90(pat_data_r.data)
			numtracks = len(pat_data)

			instnotes = [[] for x in range(16)]

			for num in range(numtracks):
				c_track = (numtracks-1)-num
				s_data = pat_data[[c_track]][0]
				vol_where = np.where(s_data[:, 0]!=0)[0]

				track_data = np.zeros((len(vol_where), 6), dtype=np.uint8)

				for num, pos in enumerate(vol_where):
					track_data[num,:][0:4] = s_data[pos]
					track_data[num,:][4] = pos
					if num>0: track_data[num-1,:][5] = track_data[num,:][4]-track_data[num-1,:][4]
				if len(vol_where): track_data[-1,:][5] = len(s_data)-track_data[-1,:][4]

				for x in track_data: instnotes[x[1]].append(x)

			for instnum, instnote in enumerate(instnotes):
				if len(instnote):

					cvpj_instid = 'pixi_'+str(instnum)
					trscene_obj = convproj_obj.track__add_scene(cvpj_instid, sceneid, 'main')
					placement_obj = trscene_obj.add_notes()
					placement_obj.visual.name = 'Pat #'+str(pat_num+1)
					placement_obj.time.set_posdur(0, pat_data_r.length)

					for nnn in instnote:
						if nnn[2]: placement_obj.notelist.add_r(nnn[4], nnn[5], nnn[0]-78, nnn[2]/100, {})

		curpos = 0
		for pat_num in project_obj.order:
			size = project_obj.patterns[pat_num].length
			scenepl_obj = convproj_obj.scene__add_pl()
			scenepl_obj.position = curpos
			scenepl_obj.duration = size
			scenepl_obj.id = str(pat_num)
			curpos += size

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_lanefit')

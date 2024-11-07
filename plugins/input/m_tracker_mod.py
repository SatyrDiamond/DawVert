# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import re
import numpy as np
import math

FINETUNE = [8363, 8413, 8463, 8529, 8581, 8651, 8723, 8757, 7895, 7941, 7985, 8046, 8107, 8169, 8232, 8280]
TEXTSTART = 'MOD_Inst_'
MAINCOLOR = [0.47, 0.47, 0.47]

IGNORE_ERRORS = False

class input_mod(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'mod'
	def get_name(self): return 'Protracker Module'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mod']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'm'
	def supported_autodetect(self): return False

	def parse_bytes(self, convproj_obj, input_bytes, dv_config, input_file):
		from objects.file_proj import proj_mod
		project_obj = proj_mod.mod_song()
		if not project_obj.load_from_raw(input_bytes, IGNORE_ERRORS): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config)

	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_mod
		project_obj = proj_mod.mod_song()
		if not project_obj.load_from_file(input_file, IGNORE_ERRORS): exit()
		self.parse_internal(convproj_obj, project_obj, dv_config)

	def parse_internal(self, convproj_obj, project_obj, dv_config):
		from objects.tracker import pat_single
		from objects import audio_data
		samplefolder = dv_config.path_samples_extracted

		cvpj_bpm = 125
		current_speed = 6

		for num, sample_obj in enumerate(project_obj.samples):
			strnum = str(num+1)

			cvpj_instid = TEXTSTART + strnum

			pluginid = 'sampler_'+strnum

			inst_obj = convproj_obj.instrument__add(cvpj_instid)
			inst_obj.visual.name = sample_obj.name if not IGNORE_ERRORS else re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sample_obj.name)
			inst_obj.visual.color.set_float(MAINCOLOR)
			inst_obj.params.add('vol', 0.3, 'float')
			
			if sample_obj.length != 0 and sample_obj.length != 1:
				loopstart = sample_obj.loop_start*2
				loopend = (sample_obj.loop_start+sample_obj.loop_length)*2

				wave_path = samplefolder + strnum.zfill(2) + '.wav'

				audio_obj = audio_data.audio_obj()
				audio_obj.set_codec('int8')
				audio_obj.pcm_from_bytes(sample_obj.data)
				if not IGNORE_ERRORS: audiorate = FINETUNE[sample_obj.finetune]
				else: audiorate = FINETUNE[sample_obj.finetune%len(FINETUNE)]
				audio_obj.rate = audiorate

				if loopstart != 0 or loopend != 2: audio_obj.loop = [loopstart, loopend]

				audio_obj.pcm_change_bits(16)

				audio_obj.to_file_wav(wave_path)

				plugin_obj, inst_obj.pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(wave_path, None)
				sp_obj.point_value_type = "samples"
				sp_obj.loop_active = loopstart != 0 and loopend != 2
				sp_obj.loop_start = loopstart

		patterndata_obj = pat_single.single_patsong(project_obj.num_chans, TEXTSTART, MAINCOLOR)
		patterndata_obj.orders = project_obj.l_order

		for num_pat, pat_data in enumerate(project_obj.patterns):
			pattern_obj = patterndata_obj.pattern_add(num_pat, 64)
			for num_row, row_data in enumerate(pat_data.data):
				for num_ch, row_ch in enumerate(row_data):
					if np.any(row_ch):
						output_note = None
						output_inst = None
						cell_p1, cell_p2 = row_ch
						mod_inst_low = cell_p2 >> 12
						mod_inst_high = cell_p1 >> 12
						noteperiod = (cell_p1 & 0x0FFF) 
						if noteperiod != 0: output_note = (round(12 * math.log2((447902/(noteperiod*2)) / 440)) + 69)-72
						cell_fx_type = (cell_p2 & 0xF00) >> 8
						cell_fx_param = (cell_p2 & 0xFF) 
						cell_inst_num = mod_inst_high << 4 | mod_inst_low
						if cell_inst_num != 0: output_inst = cell_inst_num

						pattern_obj.cell_note(num_ch, num_row, output_note, output_inst)
						pattern_obj.cell_fx_mod(num_ch, num_row, cell_fx_type, cell_fx_param)

						if cell_fx_type == 12: pattern_obj.cell_param(num_ch, num_row, 'vol', cell_fx_param/64)
						else: 
							if output_inst != None:
								if output_inst < len(project_obj.samples):
									instvol = project_obj.samples[output_inst-1].default_vol
									pattern_obj.cell_param(num_ch, num_row, 'vol', instvol/64)

						if cell_fx_type == 13: pattern_obj.cell_g_param(num_ch, num_row, 'break_to_row', cell_fx_param)
						if cell_fx_type == 15: pattern_obj.cell_g_param(num_ch, num_row, 'speed' if cell_fx_param < 32 else 'tempo', cell_fx_param)

		patterndata_obj.to_cvpj(convproj_obj, TEXTSTART, cvpj_bpm, current_speed, True, MAINCOLOR)

		convproj_obj.metadata.name = project_obj.title
		
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_lanefit')

		convproj_obj.params.add('bpm', cvpj_bpm, 'float')
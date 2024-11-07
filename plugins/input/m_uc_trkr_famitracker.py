# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import plugins

dpcm_rate_arr = [4181.71,4709.93,5264.04,5593.04,6257.95,7046.35,7919.35,8363.42,9419.86,11186.1,12604.0,13982.6,16884.6,21306.8,24858.0,33143.9]

class input_famitracker_txt(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'famitracker_txt'
	def get_name(self): return 'Famitracker Text'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['txt']
		in_dict['file_ext_detect'] = False
		in_dict['track_lanes'] = True
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'm'
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_famitracker
		from objects.tracker import pat_multi
		from objects import audio_data
		project_obj = proj_famitracker.famitracker_project()
		if not project_obj.load_from_file(input_file): exit()

		convproj_obj.fxtype = 'rack'
		
		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.author: convproj_obj.metadata.author = project_obj.author
		if project_obj.copyright: 
			if project_obj.copyright.isnumeric(): convproj_obj.metadata.t_year = int(project_obj.copyright)
			else: convproj_obj.metadata.copyright = project_obj.copyright
		if project_obj.comment: convproj_obj.metadata.comment_text = '\n'.join(project_obj.comment)

		samplefolder = dv_config.path_samples_extracted

		globalstore.dataset.load('chip_nes', './data_main/dataset/chip_nes.dset')

		cur_song = project_obj.song[0]

		if cur_song.name != 'New song': convproj_obj.metadata.name = cur_song.name

		patterndata_obj = pat_multi.multi_patsong()
		patterndata_obj.num_rows = cur_song.patlen
		patterndata_obj.dataset_name = 'chip_nes'
		patterndata_obj.dataset_cat = 'chip'
		patterndata_obj.add_channel('square1')
		patterndata_obj.add_channel('square2')
		patterndata_obj.add_channel('triangle')
		patterndata_obj.add_channel('noise')
		patterndata_obj.add_channel('dpcm')

		if (1<<0 & project_obj.expansion):
			patterndata_obj.add_channel('vrc6_square')
			patterndata_obj.add_channel('vrc6_square')
			patterndata_obj.add_channel('vrc6_saw')

		if (1<<1 & project_obj.expansion):
			patterndata_obj.add_channel('vrc7_fm')
			patterndata_obj.add_channel('vrc7_fm')
			patterndata_obj.add_channel('vrc7_fm')
			patterndata_obj.add_channel('vrc7_fm')
			patterndata_obj.add_channel('vrc7_fm')
			patterndata_obj.add_channel('vrc7_fm')

		if (1<<2 & project_obj.expansion):
			patterndata_obj.add_channel('fds')

		if (1<<3 & project_obj.expansion):
			patterndata_obj.add_channel('mmc5')
			patterndata_obj.add_channel('mmc5')

		if (1<<4 & project_obj.expansion):
			for _ in range(project_obj.n163channels):
				patterndata_obj.add_channel('n163')

		for patnum, ftpatobj in cur_song.patterns.items():

			for channum, chandata in ftpatobj.patdata.items():
				pat_obj = patterndata_obj.pattern_add(channum, patnum)
				for row_num, d in chandata.items():
					ft_key, ft_inst, ft_vol, ft_fx = d
					if ft_key == '---': ft_key = 'off'
					if ft_key == '===': ft_key = 'off'

					pat_obj.cell_note(row_num, ft_key, ft_inst)
					if ft_vol != None: pat_obj.cell_param(row_num, 'vol_stay', ft_vol/15)

					for fx_type, fx_val in ft_fx:
						if fx_type == 0: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)
						if fx_type == 1: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)
						if fx_type == 2: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)
						if fx_type == 3: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)
						if fx_type == 4: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)
						if fx_type == 7: pat_obj.cell_fx_mod(row_num, fx_type, fx_val)

		for chnum, orders in cur_song.orders.items():
			patterndata_obj.orders[chnum] = orders

		used_insts = patterndata_obj.to_cvpj(convproj_obj, cur_song.tempo, cur_song.speed)

		for instname, instnums in used_insts.items():
			for chinst in instnums:
				instnum, channum = chinst
				instid = instname+'_'+str(channum)+'_'+str(instnum)

				inst_obj = convproj_obj.instrument__add(instid)
				inst_obj.fxrack_channel = channum+1

				insttype = patterndata_obj.get_channel_insttype(channum)
				inst_obj.visual.from_dset('chip_nes', 'chip', insttype, False)

				if instnum in project_obj.inst:
					ft_inst = project_obj.inst[instnum]
					inst_obj.visual.name = ft_inst.name

					#print(ft_inst.chip, insttype, instnum, channum)

					if ft_inst.chip == '2A03':

						if insttype == 'dpcm':
							inst_obj.is_drum = True
							plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
							plugin_obj.role = 'synth'
							for _, dpcm_key in ft_inst.dpcm_keys.items():
								if dpcm_key.id in project_obj.dpcm:
									filename = samplefolder+'dpcmg_'+str(dpcm_key.id)+'_'+str(dpcm_key.pitch)+'.wav'
									dkey = ((dpcm_key.octave*12) + dpcm_key.note)-36
									dpcm_data = project_obj.dpcm[dpcm_key.id]
									audio_obj = audio_data.audio_obj()
									audio_obj.decode_from_codec('dpcm', dpcm_data.data)
									audio_obj.rate = dpcm_rate_arr[dpcm_key.pitch]
									audio_obj.to_file_wav(filename)
									sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)
									sp_obj = plugin_obj.sampleregion_add(dkey, dkey, dkey, None)
									sp_obj.visual.name = dpcm_data.name
									sp_obj.sampleref = filename

						else:
							plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
							plugin_obj.role = 'synth'
							osc_data = plugin_obj.osc_add()
							if insttype in ['square1', 'square2']: osc_data.prop.shape = 'square'
							if insttype == 'triangle': osc_data.prop.shape = 'triangle'
							if insttype == 'noise': osc_data.prop.shape = 'random'

							if ft_inst.macro_vol != -1: 
								macro_vol = project_obj.macros[ft_inst.macro_vol]
								plugin_obj.env_blocks_add('vol', macro_vol.data, 0.05, 15, macro_vol.loop, macro_vol.release)
							#if ft_inst.macro_arp != -1: 
							#	macro_arp = project_obj.macros[ft_inst.macro_arp]
							if ft_inst.macro_pitch != -1: 
								macro_pitch = project_obj.macros[ft_inst.macro_pitch]
								plugin_obj.env_blocks_add('pitch', macro_pitch.data, 0.05, 15, macro_pitch.loop, macro_pitch.release)
							#if ft_inst.macro_hipitch != -1: 
							#	macro_hipitch = project_obj.macros[ft_inst.macro_hipitch]
							if ft_inst.macro_duty != -1: 
								macro_duty = project_obj.macros[ft_inst.macro_duty]
								plugin_obj.env_blocks_add('duty', macro_duty.data, 0.05, 15, macro_duty.loop, macro_duty.release)

					if ft_inst.chip == 'VRC6':

						if insttype == 'vrc6_square':
							plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
							plugin_obj.role = 'synth'
							osc_data = plugin_obj.osc_add()
							osc_data.prop.shape = 'square'

						if insttype == 'vrc6_saw':
							plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
							plugin_obj.role = 'synth'
							osc_data = plugin_obj.osc_add()
							osc_data.prop.shape = 'saw'

					if ft_inst.chip == 'FDS' and insttype == 'fds':
						plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
						osc_data = plugin_obj.osc_add()
						osc_data.prop.type = 'wave'
						osc_data.prop.nameid = 'main'
						wave_obj = plugin_obj.wave_add('main')
						wave_obj.set_all_range(ft_inst.fds_wave, 0, 64)

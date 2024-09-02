# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj import proj_famitracker
from objects.tracker import pat_multi
from objects import globalstore
from objects import audio_data
import plugins

dpcm_rate_arr = [4181.71,4709.93,5264.04,5593.04,6257.95,7046.35,7919.35,8363.42,9419.86,11186.1,12604.0,13982.6,16884.6,21306.8,24858.0,33143.9]

class input_petaporon(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'famitracker'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Famitracker'
		dawinfo_obj.file_ext = 'txt'
		dawinfo_obj.track_lanes = True
		dawinfo_obj.track_nopl = True
		dawinfo_obj.fxtype = 'rack'
	def parse(self, convproj_obj, input_file, dv_config):
		project_obj = proj_famitracker.famitracker_project()
		project_obj.load_from_file(input_file)

		samplefolder = dv_config.path_samples_extracted

		globalstore.dataset.load('chip_nes', './data_main/dataset/chip_nes.dset')

		cur_song = project_obj.song[0]

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

				inst_obj = convproj_obj.add_instrument(instid)
				inst_obj.fxrack_channel = channum+1

				insttype = patterndata_obj.get_channel_insttype(channum)
				inst_obj.visual.from_dset('chip_nes', 'chip', insttype, False)

				if instnum in project_obj.inst:
					ft_inst = project_obj.inst[instnum]
					inst_obj.visual.name = ft_inst.name

					#print(ft_inst.chip, insttype, instnum, channum)

					if ft_inst.chip == '2A03':

						if insttype == 'dpcm':
							plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('sampler', 'multi')
							plugin_obj.role = 'synth'

							for key, dpcm_key in ft_inst.dpcm_keys.items():

								if dpcm_key.id in project_obj.dpcm:
									filename = samplefolder+'dpcmg_'+str(dpcm_key.id)+'_'+str(dpcm_key.pitch)+'.wav'

									dkey = ((dpcm_key.octave*12) + dpcm_key.note)-36

									dpcm_data = project_obj.dpcm[dpcm_key.id]
									audio_obj = audio_data.audio_obj()
									audio_obj.decode_from_codec('dpcm', dpcm_data.data)
									audio_obj.rate = dpcm_rate_arr[dpcm_key.pitch]
									audio_obj.to_file_wav(filename)

									sampleref_obj = convproj_obj.add_sampleref(filename, filename, None)
									sp_obj = plugin_obj.sampleregion_add(dkey, dkey, dkey, None)
									sp_obj.visual.name = dpcm_data.name
									sp_obj.sampleref = filename

						else:
							plugin_obj, inst_obj.pluginid = convproj_obj.add_plugin_genid('universal', 'synth-osc')
							plugin_obj.role = 'synth'
							osc_data = plugin_obj.osc_add()
							if insttype in ['square1', 'square2']: osc_data.prop.shape = 'square'
							if insttype in ['triangle']: osc_data.prop.shape = 'triangle'
							if insttype in ['noise']: osc_data.prop.shape = 'random'

							if ft_inst.macro_vol != -1: 
								macro_vol = project_obj.macros[ft_inst.macro_vol]
								plugin_obj.env_blocks_add('vol', macro_vol.data, 0.05, 15, macro_vol.loop, macro_vol.release)
							#if ft_inst.macro_arp != -1: 
							#	macro_arp = project_obj.macros[ft_inst.macro_arp]
							#if ft_inst.macro_pitch != -1: 
							#	macro_pitch = project_obj.macros[ft_inst.macro_pitch]
							#if ft_inst.macro_hipitch != -1: 
							#	macro_hipitch = project_obj.macros[ft_inst.macro_hipitch]
							#if ft_inst.macro_duty != -1: 
							#	macro_duty = project_obj.macros[ft_inst.macro_duty]

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects import globalstore
import plugins

def speed_to_tempo(framerate, speed):
	return (framerate * 60.0) / (speed * 5)

def parse_fx_event(r_row, pat_obj, fx_p, fx_v):
	if fx_p == 1: pat_obj.cell_g_param(r_row, 'pattern_jump', fx_v)
	elif fx_p == 2: pat_obj.cell_g_param(r_row, 'stop', fx_v)
	elif fx_p == 3: pat_obj.cell_g_param(r_row, 'skip_pattern', fx_v)
	elif fx_p == 4: pat_obj.cell_g_param(r_row, 'tempo', speed_to_tempo(60, fx_v)*20)

	elif fx_p == 13:
		arp_params = [0,0]
		arp_params[0], arp_params[1] = data_bytes.splitbyte(fx_v)
		pat_obj.cell_param(r_row, 'arp', arp_params)
	elif fx_p == 14: pat_obj.cell_param(r_row, 'slide_up_persist', fx_v)
	elif fx_p == 15: pat_obj.cell_param(r_row, 'slide_down_persist', fx_v)
	elif fx_p == 16: pat_obj.cell_param(r_row, 'slide_to_note_persist', fx_v)
	elif fx_p == 17:
		fine_vib_sp, fine_vib_de = data_bytes.splitbyte(fx_v)
		vibrato_params = {}
		vibrato_params['speed'] = fine_vib_sp/16
		vibrato_params['depth'] = fine_vib_sp/16
		pat_obj.cell_param(r_row, 'vibrato', vibrato_params)
	elif fx_p == 18: pat_obj.cell_param(r_row, 'vibrato_delay', fx_v)

	elif fx_p == 22: 
		vol_left, vol_right = data_bytes.splitbyte(fx_v)
		if vol_left < 0: vol_left += 16
		if vol_right < 0: vol_right += 16
		global_pan, global_volume = xtramath.sep_pan_to_vol(vol_left/15, vol_right/15)
		pat_obj.cell_g_param(r_row, 'global_pan', global_pan)
		pat_obj.cell_g_param(r_row, 'global_volume', global_volume)

class input_trackerboy(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'trackerboy'
	def get_name(self): return 'Trackerboy'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['tbm']
		in_dict['track_lanes'] = True
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'm'
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_trackerboy
		from objects.tracker import pat_multi
		project_obj = proj_trackerboy.trackerboy_project()
		if not project_obj.load_from_file(input_file): exit()

		convproj_obj.fxtype = 'rack'
		
		samplefolder = dv_config.path_samples_extracted

		globalstore.dataset.load('trackerboy', './data_main/dataset/trackerboy.dset')

		tbm_cursong = project_obj.songs[dv_config.songnum-1]

		if project_obj.title: convproj_obj.metadata.name = project_obj.title
		if project_obj.artist: convproj_obj.metadata.author = project_obj.artist
		if project_obj.copyright: convproj_obj.metadata.copyright = project_obj.copyright

		patterndata_obj = pat_multi.multi_patsong()
		patterndata_obj.num_rows = tbm_cursong.rows
		patterndata_obj.dataset_name = 'trackerboy'
		patterndata_obj.dataset_cat = 'chip'
		patterndata_obj.add_channel('pulse')
		patterndata_obj.add_channel('pulse')
		patterndata_obj.add_channel('wavetable')
		patterndata_obj.add_channel('noise')

		for n, x in enumerate(tbm_cursong.orders):
			patterndata_obj.orders[n] = list(x)

		for channum, patm in tbm_cursong.patterns.items():
			for patnum, patdata in patm.items():
				#print(channum, patnum)
				pat_obj = patterndata_obj.pattern_add(channum, patnum)

				for d_pos, d_key, d_inst, d_fx in patdata:
					outkey = None
					if d_key != 0:
						if d_key == 85: outkey = 'off'
						else: outkey = d_key-25
					pat_obj.cell_note(d_pos, outkey, d_inst if d_inst else None)
					for fx_p, fx_v in d_fx:
						parse_fx_event(d_pos, pat_obj, fx_p, fx_v)

		tempo = speed_to_tempo(60, tbm_cursong.speed)*20
		convproj_obj.params.add('bpm', tempo, 'float')
		used_insts = patterndata_obj.to_cvpj(convproj_obj, tempo, 6)

		for instname, instnums in used_insts.items():
			for chinst in instnums:
				instnum, channum = chinst
				instid = instname+'_'+str(channum)+'_'+str(instnum)

				inst_obj = convproj_obj.instrument__add(instid)
				inst_obj.fxrack_channel = channum+1

				insttype = patterndata_obj.get_channel_insttype(channum)
				inst_obj.visual.from_dset('trackerboy', 'chip', insttype, False)

				plugin_obj, inst_obj.pluginid = convproj_obj.plugin__add__genid('universal', 'synth-osc', None)
				plugin_obj.role = 'synth'
				osc_data = plugin_obj.osc_add()
				if instname == 'pulse': osc_data.prop.shape = 'square'
				if instname == 'noise': 
					osc_data.prop.shape = 'random'
					inst_obj.is_drum = True
				if instname == 'wavetable': 
					osc_data.prop.type = 'wave'
					osc_data.prop.nameid = 'main'

				tbm_inst = project_obj.insts[instnum]

				if tbm_inst.envs[0]: plugin_obj.env_blocks_add('arp', tbm_inst.envs[0].values, 0.05, 1, 0, 0)
				if tbm_inst.envs[1]: plugin_obj.env_blocks_add('pan', tbm_inst.envs[1].values, 0.05, 15, 0, 0)
				if tbm_inst.envs[2]: plugin_obj.env_blocks_add('pitch', tbm_inst.envs[2].values, 0.05, 127, 0, 0)
				if tbm_inst.envs[3]: 
					if instname == 'pulse': envname, maxenv = ('duty', 4)
					if instname == 'wavetable': envname, maxenv = ('vol', 3)
					if instname == 'noise':  envname, maxenv = ('noise', 3)
					plugin_obj.env_blocks_add(envname, tbm_inst.envs[3].values, 0.05, maxenv, 0, 0)

				if instname != 'wavetable':
					env_attack = 0
					env_decay = 0
					env_sustain = 1
					env_amount = 1
					if tbm_inst.envelopeEnabled:
						instvol = tbm_inst.param1/15
						param2v = (tbm_inst.param2&7)/7
						if not tbm_inst.param2&8:
							if param2v:
								env_decay = (param2v*2)*instvol
								env_sustain = 0
								inst_obj.params.add('vol', instvol, 'float')
						else:
							if param2v:
								env_attack = (param2v*2)*(1-instvol)
								env_amount = instvol
							else:
								inst_obj.params.add('vol', instvol, 'float')
					plugin_obj.env_asdr_add('vol', 0, env_attack, 0, env_decay, env_sustain, 0, env_amount)
				else:
					wavenum = tbm_inst.param2+1
					if wavenum in project_obj.waves: 
						wave_obj = plugin_obj.wave_add('main')
						wave_obj.set_all_range(project_obj.waves[wavenum].wave, 0, 15)
					inst_obj.datavals.add('middlenote', 12)
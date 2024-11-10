# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath
from objects import globalstore
import plugins

FX_NAMES = ['delay','chorus','reverb','distortion','low_boost','compressor','high_pass']
CEOL_COLORS = [[0.23, 0.15, 0.93],[0.61, 0.04, 0.94],[0.82, 0.16, 0.23],[0.82, 0.60, 0.16],[0.21, 0.84, 0.14],[0.07, 0.56, 0.91]]

def add_master_fx(convproj_obj, fx_type, fx_value):
	if fx_type == 0: #delay
		from objects.inst_params import fx_delay
		delay_obj = fx_delay.fx_delay()
		delay_obj.feedback_first = True
		delay_obj.feedback[0] = 0.1
		timing_obj = delay_obj.timing_add(0)
		timing_obj.set_seconds(((300*fx_value)/100)/1000)
		plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, 'master-effect')
		plugin_obj.fxdata_add(1, 0.5)

	elif fx_type == 1: #chorus
		plugin_obj = convproj_obj.plugin__add('master-effect', 'simple', 'chorus', None)
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 2: #reverb
		plugin_obj = convproj_obj.plugin__add('master-effect', 'simple', 'reverb', None)
		plugin_obj.fxdata_add(1, (0.3)*(fx_value/100))

	elif fx_type == 3: #distortion
		plugin_obj = convproj_obj.plugin__add('master-effect', 'simple', 'distortion', None)
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 4: #low_boost
		plugin_obj = convproj_obj.plugin__add('master-effect', 'simple', 'bassboost', None)
		plugin_obj.fxdata_add(1, fx_value/100)

	elif fx_type == 5: #compressor
		plugin_obj = convproj_obj.plugin__add('master-effect', 'universal', 'compressor', None)
		plugin_obj.params.add('attack', 0.1, 'float')
		plugin_obj.params.add('pregain', 0, 'float')
		plugin_obj.params.add('knee', 6, 'float')
		plugin_obj.params.add('postgain', 0, 'float')
		plugin_obj.params.add('ratio', 4, 'float')
		plugin_obj.params.add('release', 0.5, 'float')
		plugin_obj.params.add('threshold', -20, 'float')

	elif fx_type == 6: #high_pass
		plugin_obj = convproj_obj.plugin__add('master-effect', 'universal', 'filter', None)
		plugin_obj.filter.on = True
		plugin_obj.filter.type.set('high_pass', None)
		plugin_obj.filter.freq = xtramath.midi_filter(fx_value/100)
		
	plugin_obj.role = 'fx'

	plugin_obj.visual.from_dset('boscaceoil', 'fx', FX_NAMES[fx_type], True)
	convproj_obj.track_master.fxslots_audio.append('master-effect')

def add_filter(convproj_obj, instnum, cutoff, resonance):
	cvpj_instid = 'ceol_'+str(instnum).zfill(2)
	fx_id = cvpj_instid+'_filter'
	plugin_obj = convproj_obj.plugin__add(fx_id, 'universal', 'filter', None)
	plugin_obj.filter.on = True
	plugin_obj.filter.type.set('low_pass', None)
	plugin_obj.filter.freq = xtramath.midi_filter(cutoff/100)
	plugin_obj.filter.q = resonance+1
	plugin_obj.role = 'effect'
	return fx_id

class input_ceol(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'ceol'
	def get_name(self): return 'Bosca Ceoil'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['ceol']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = []
		in_dict['plugin_included'] = ['simple:chorus','simple:reverb','simple:distortion','simple:bassboost','universal:compressor','universal:filter','chip:fm:opm','universal:filter','universal:midi']
		in_dict['projtype'] = 'mi'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_boscaceoil
		from objects.inst_params import fm_opm
		global ceol_data
		
		project_obj = proj_boscaceoil.ceol_song()
		if not project_obj.load_from_file(input_file): exit()

		# ---------- CVPJ Start ----------
		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4, False)

		globalstore.dataset.load('boscaceoil', './data_main/dataset/boscaceoil.dset')
		globalstore.idvals.load('boscaceoil', './data_main/idvals/boscaceoil_inst.csv')

		# ---------- Master FX ----------
		convproj_obj.track_master.params.add('vol', 1, 'float')
		convproj_obj.track_master.visual.color.set_float([0.31373, 0.39608, 0.41569])

		add_master_fx(convproj_obj, project_obj.effect_type, project_obj.effect_value)

		# ---------- Instruments ----------

		t_key_offset = []
		inst_filters = {}
		inst_objs = {}

		for instnum, ceol_inst_obj in enumerate(project_obj.instruments):
			cvpj_instid = 'ceol_'+str(instnum).zfill(2)

			cvpj_instcolor = data_values.list__optionalindex(ceol_inst_obj.palette, [0.55, 0.55, 0.55], CEOL_COLORS)

			if ceol_inst_obj.inst <= 127:
				inst_obj = convproj_obj.instrument__add(cvpj_instid)
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.midi.out_inst.patch = ceol_inst_obj.inst
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)

			elif ceol_inst_obj.inst == 365: 
				inst_obj = convproj_obj.instrument__add(cvpj_instid)
				inst_obj.visual.name = 'MIDI Drums'
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.midi.out_inst.drum = True
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)

			else: 
				inst_obj = convproj_obj.instrument__add(cvpj_instid)
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.from_dataset("boscaceoil", 'inst', str(ceol_inst_obj.inst), False)

				idval_inst = globalstore.idvals.get('boscaceoil')
				opm_obj = fm_opm.opm_inst()
				if idval_inst: valsoundid = idval_inst.get_idval(str(ceol_inst_obj.inst), 'valsoundid')
				opm_obj.from_valsound(valsoundid)

				plugin_obj, inst_obj.pluginid = opm_obj.to_cvpj_genid(convproj_obj)
			
			inst_objs[ceol_inst_obj.inst] = inst_obj
			if ceol_inst_obj.inst == 363: t_key_offset.append(60)
			elif ceol_inst_obj.inst == 364: t_key_offset.append(48)
			elif ceol_inst_obj.inst == 365: t_key_offset.append(24)
			else: t_key_offset.append(0)

			inst_obj.params.add('vol', ceol_inst_obj.volume/256, 'float')

			if ceol_inst_obj.cutoff < 110:
				inst_filters[instnum] = add_filter(convproj_obj, instnum, ceol_inst_obj.cutoff, ceol_inst_obj.resonance)
				inst_obj.fxslots_audio.append(inst_filters[instnum])

		# ---------- Patterns ----------
		for patnum, ceol_pat_obj in enumerate(project_obj.patterns):
			cvpj_pat_id = 'ceol_'+str(patnum).zfill(3)

			patinstid = 'ceol_'+str(ceol_pat_obj.inst).zfill(2)

			notevols = {}
			if ceol_pat_obj.recordfilter is not None:
				for n, x in enumerate(ceol_pat_obj.recordfilter[:,0]):
					notevols[n] = x/256

			nle_obj = convproj_obj.notelistindex__add(cvpj_pat_id)
			for ceol_note_obj in ceol_pat_obj.notes: nle_obj.notelist.add_m(patinstid, ceol_note_obj.pos, ceol_note_obj.len, (ceol_note_obj.key-60)+t_key_offset[ceol_pat_obj.inst], notevols[ceol_note_obj.pos] if ceol_note_obj.pos in notevols else 1, {})
			nle_obj.visual.name = str(patnum)
			nle_obj.visual.color.set_float(data_values.list__optionalindex(ceol_pat_obj.palette, [0.55, 0.55, 0.55], CEOL_COLORS))

		for num in range(8):
			playlist_obj = convproj_obj.playlist__add(num, 1, True)
			playlist_obj.visual.color.set_float([0.43, 0.52, 0.55] if (num % 2) == 0 else [0.31, 0.40, 0.42])

		# ---------- Placement ----------

		prev_pl = None
		for plpos, row_data in enumerate(project_obj.spots):
			after_filter = [[-1, -1] for x in range(8)]
			for plnum, plpatnum in enumerate(row_data):

				if plpatnum != -1:
					cvpj_placement = convproj_obj.playlist[plnum].placements.add_notes_indexed()
					cvpj_placement.fromindex = 'ceol_'+str(plpatnum).zfill(3)
					cvpj_placement.time.set_block_posdur(plpos, project_obj.pattern_length)

					ceol_pat_obj = project_obj.patterns[plpatnum]
					recordfilter = ceol_pat_obj.recordfilter

					if recordfilter is not None:
						after_filter[plnum][0] = plpos
						after_filter[plnum][1] = ceol_pat_obj.inst
						if ceol_pat_obj.inst not in inst_filters: 
							inst_filters[ceol_pat_obj.inst] = add_filter(convproj_obj, ceol_pat_obj.inst, ceol_inst_obj.cutoff, ceol_inst_obj.resonance)
							inst_objs[ceol_pat_obj.inst].fxslots_audio.append(inst_filters[ceol_pat_obj.inst])

						patinstid = 'ceol_'+str(ceol_pat_obj.inst).zfill(2)

						autofilterfxid = patinstid+'_filter'
						recordfilter_freq = [xtramath.midi_filter(x/100) for x in recordfilter[:,1]]

						f_autopl_obj = convproj_obj.automation.add_pl_points(['filter', autofilterfxid, 'freq'], 'float')
						f_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						for n, x in enumerate(recordfilter_freq):
							autopoint_obj = f_autopl_obj.data.add_point()
							autopoint_obj.pos = n
							autopoint_obj.value = x

						recordfilter_reso = [x+1 for x in recordfilter[:,2]]
						q_autopl_obj = convproj_obj.automation.add_pl_points(['filter', autofilterfxid, 'q'], 'float')
						q_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						for n, x in enumerate(recordfilter_reso):
							autopoint_obj = q_autopl_obj.data.add_point()
							autopoint_obj.pos = n
							autopoint_obj.value = x

			if prev_pl != None:
				for n in range(8):
					if prev_pl[n][0] != -1 and after_filter[n][0] == -1:
						instnum = prev_pl[n][1]
						patinstid = 'ceol_'+str(instnum).zfill(2)
						autofilterfxid = patinstid+'_filter'

						ceol_inst_obj = project_obj.instruments[instnum]

						f_autopl_obj = convproj_obj.automation.add_pl_points(['filter', autofilterfxid, 'freq'], 'float')
						f_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						autopoint_obj = f_autopl_obj.data.add_point()
						autopoint_obj.value = xtramath.midi_filter(ceol_inst_obj.cutoff)

						q_autopl_obj = convproj_obj.automation.add_pl_points(['filter', autofilterfxid, 'q'], 'float')
						q_autopl_obj.time.set_block_posdur(plpos, project_obj.pattern_length)
						autopoint_obj = q_autopl_obj.data.add_point()
						autopoint_obj.value = ceol_inst_obj.resonance+1

			prev_pl = after_filter

		# ---------- Output ----------
		convproj_obj.add_timesig_lengthbeat(project_obj.pattern_length, project_obj.bar_length)
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')
		convproj_obj.do_actions.append('do_addloop')
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath
from functions_plugin_cvpj import params_fm
from objects import globalstore
from objects.convproj import project as convproj
from objects.file_proj import proj_boscaceoil
from objects.inst_params import fm_opm
from objects.inst_params import fx_delay
import plugins
import json

FX_NAMES = ['delay','chorus','reverb','distortion','low_boost','compressor','high_pass']
CEOL_COLORS = [[0.23, 0.15, 0.93],[0.61, 0.04, 0.94],[0.82, 0.16, 0.23],[0.82, 0.60, 0.16],[0.21, 0.84, 0.14],[0.07, 0.56, 0.91]]

def add_master_fx(convproj_obj, fx_type, fx_value):
	if fx_type == 0: #delay
		delay_obj = fx_delay.fx_delay()
		delay_obj.feedback_first = True
		delay_obj.feedback[0] = 0.1
		timing_obj = delay_obj.timing_add(0)
		timing_obj.set_seconds(((300*fx_value)/100)/1000)
		plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, 'master-effect')
		plugin_obj.fxdata_add(1, 0.5)

	elif fx_type == 1: #chorus
		plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'chorus')
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 2: #reverb
		plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'reverb')
		plugin_obj.fxdata_add(1, (0.3)*(fx_value/100))

	elif fx_type == 3: #distortion
		plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'distortion')
		plugin_obj.params.add('amount', fx_value/100, 'float')

	elif fx_type == 4: #low_boost
		plugin_obj = convproj_obj.add_plugin('master-effect', 'simple', 'bassboost')
		plugin_obj.fxdata_add(1, fx_value/100)

	elif fx_type == 5: #compressor
		plugin_obj = convproj_obj.add_plugin('master-effect', 'universal', 'compressor')
		plugin_obj.params.add('attack', 0.1, 'float')
		plugin_obj.params.add('pregain', 0, 'float')
		plugin_obj.params.add('knee', 6, 'float')
		plugin_obj.params.add('postgain', 0, 'float')
		plugin_obj.params.add('ratio', 4, 'float')
		plugin_obj.params.add('release', 0.5, 'float')
		plugin_obj.params.add('threshold', -20, 'float')

	elif fx_type == 6: #high_pass
		plugin_obj = convproj_obj.add_plugin('master-effect', 'universal', 'filter')
		plugin_obj.filter.on = True
		plugin_obj.filter.type.set('high_pass', None)
		plugin_obj.filter.freq = xtramath.midi_filter(fx_value/100)
		
	plugin_obj.role = 'effect'

	plugin_obj.visual.from_dset('boscaceoil', 'fx', FX_NAMES[fx_type], True)
	convproj_obj.track_master.fxslots_audio.append('master-effect')

class input_ceol(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'ceol'
	def gettype(self): return 'mi'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Bosca Ceoil'
		dawinfo_obj.file_ext = 'ceol'
		dawinfo_obj.track_lanes = True
		dawinfo_obj.audio_filetypes = []
		dawinfo_obj.plugin_included = ['simple:chorus','simple:reverb','simple:distortion','simple:bassboost','universal:compressor','universal:filter','fm:opm','native-boscaceoil','universal:filter','midi']
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		global ceol_data
		
		ceol_obj = proj_boscaceoil.ceol_song()
		ceol_obj.load_from_file(input_file)

		# ---------- CVPJ Start ----------
		convproj_obj.type = 'mi'
		convproj_obj.set_timings(4, False)

		globalstore.dataset.load('boscaceoil', './data_main/dataset/boscaceoil.dset')
		globalstore.idvals.load('boscaceoil', './data_main/idvals/boscaceoil_inst.csv')

		# ---------- Master FX ----------
		convproj_obj.track_master.params.add('vol', 1, 'float')
		convproj_obj.track_master.visual.color.set_float([0.31373, 0.39608, 0.41569])

		add_master_fx(convproj_obj, ceol_obj.effect_type, ceol_obj.effect_value)

		# ---------- Instruments ----------

		t_key_offset = []

		for instnum, ceol_inst_obj in enumerate(ceol_obj.instruments):
			cvpj_instid = 'ceol_'+str(instnum).zfill(2)

			cvpj_instcolor = data_values.list__optionalindex(ceol_inst_obj.palette, [0.55, 0.55, 0.55], CEOL_COLORS)

			if ceol_inst_obj.inst <= 127:
				inst_obj = convproj_obj.add_instrument(cvpj_instid)
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.midi.out_inst.patch = ceol_inst_obj.inst
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)

			elif ceol_inst_obj.inst == 365: 
				inst_obj = convproj_obj.add_instrument(cvpj_instid)
				inst_obj.visual.name = 'MIDI Drums'
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.midi.out_inst.drum = True
				inst_obj.to_midi(convproj_obj, cvpj_instid, True)

			else: 
				inst_obj = convproj_obj.add_instrument(cvpj_instid)
				inst_obj.visual.color.set_float(cvpj_instcolor)
				inst_obj.from_dataset("boscaceoil", 'inst', str(ceol_inst_obj.inst), False)

				idval_inst = globalstore.idvals.get('boscaceoil')
				opm_obj = fm_opm.opm_inst()
				if idval_inst: valsoundid = idval_inst.get_idval(str(ceol_inst_obj.inst), 'valsoundid')
				opm_obj.from_valsound(valsoundid)

				plugin_obj, inst_obj.pluginid = opm_obj.to_cvpj_genid(convproj_obj)
			
			if ceol_inst_obj.inst == 363: t_key_offset.append(60)
			elif ceol_inst_obj.inst == 364: t_key_offset.append(48)
			elif ceol_inst_obj.inst == 365: t_key_offset.append(24)
			else: t_key_offset.append(0)

			inst_obj.params.add('vol', ceol_inst_obj.volume/256, 'float')

			if ceol_inst_obj.cutoff < 110:
				fx_id = cvpj_instid+'_filter'
				plugin_obj = convproj_obj.add_plugin(fx_id, 'universal', 'filter')
				plugin_obj.filter.on = True
				plugin_obj.filter.type.set('low_pass', None)
				plugin_obj.filter.freq = xtramath.midi_filter(ceol_inst_obj.cutoff/100)
				plugin_obj.filter.q = ceol_inst_obj.resonance+1
				plugin_obj.role = 'effect'
				inst_obj.fxslots_audio.append(fx_id)

		# ---------- Patterns ----------
		for patnum, ceol_pat_obj in enumerate(ceol_obj.patterns):
			cvpj_pat_id = 'ceol_'+str(patnum).zfill(3)

			nle_obj = convproj_obj.add_notelistindex(cvpj_pat_id)
			for ceol_note_obj in ceol_pat_obj.notes:
				nle_obj.notelist.add_m('ceol_'+str(ceol_pat_obj.inst).zfill(2), ceol_note_obj.pos, ceol_note_obj.len, (ceol_note_obj.key-60)+t_key_offset[ceol_pat_obj.inst], 1, {})
			nle_obj.visual.name = str(patnum)
			nle_obj.visual.color.set_float(data_values.list__optionalindex(ceol_pat_obj.palette, [0.55, 0.55, 0.55], CEOL_COLORS))

		for num in range(8):
			playlist_obj = convproj_obj.add_playlist(num, 1, True)
			playlist_obj.visual.color.set_float([0.43, 0.52, 0.55] if (num % 2) == 0 else [0.31, 0.40, 0.42])

		# ---------- Placement ----------

		for plpos, row_data in enumerate(ceol_obj.spots):
			for plnum, plpatnum in enumerate(row_data):
				if plpatnum != -1:
					cvpj_placement = convproj_obj.playlist[plnum].placements.add_notes_indexed()
					cvpj_placement.fromindex = 'ceol_'+str(plpatnum).zfill(3)
					cvpj_placement.position = plpos*ceol_obj.pattern_length
					cvpj_placement.duration = ceol_obj.pattern_length

		# ---------- Output ----------
		convproj_obj.add_timesig_lengthbeat(ceol_obj.pattern_length, ceol_obj.bar_length)
		convproj_obj.params.add('bpm', ceol_obj.bpm, 'float')
		convproj_obj.do_actions.append('do_addloop')
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import data_values
from functions import plugin_vst2
from functions import plugins

from functions_plugparams import params_various_inst
from functions_plugparams import params_kickmess
from functions_plugparams import params_various_fx
from functions_plugparams import params_vital
from functions_plugparams import wave
from functions_plugparams import data_nullbytegroup

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def simsynth_time(value): return pow(value*2, 3)
def simsynth_2time(value): return pow(value*2, 3)

def getparam(paramname):
	global pluginid_g
	global cvpj_l_g
	paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
	return paramval[0]

def getparam_old(paramname):
	global pluginid_g
	global cvpj_l_g
	paramval = plugins.get_plug_oldparam(cvpj_l_g, pluginid_g, paramname, 0)
	return paramval[0]

def convert(cvpj_l, pluginid, plugintype):
	global pluginid_g
	global cvpj_l_g
	pluginid_g = pluginid
	cvpj_l_g = cvpj_l

	#---------------------------------------- Fruit Kick ----------------------------------------
	if plugintype[1].lower() == 'fruit kick':
		max_freq = note_data.note_to_freq((getparam('max_freq')/100)+12) #1000
		min_freq = note_data.note_to_freq((getparam('min_freq')/100)-36) #130.8128
		decay_freq = getparam('decay_freq')/256
		decay_vol = getparam('decay_vol')/256
		osc_click = getparam('osc_click')/64
		osc_dist = getparam('osc_dist')/128
		#print(fkp, max_freq, min_freq, decay_freq, decay_vol, osc_click, osc_dist  )
		params_kickmess.initparams()
		params_kickmess.setvalue('pub', 'freq_start', max_freq)
		params_kickmess.setvalue('pub', 'freq_end', min_freq)
		params_kickmess.setvalue('pub', 'env_slope', decay_vol)
		params_kickmess.setvalue('pub', 'freq_slope', 0.5)
		params_kickmess.setvalue('pub', 'f_env_release', decay_freq*150)
		params_kickmess.setvalue('pub', 'phase_offs', osc_click)
		if osc_dist != 0:
			params_kickmess.setvalue('pub', 'dist_on', 1)
			params_kickmess.setvalue('pub', 'dist_start', osc_dist*0.1)
			params_kickmess.setvalue('pub', 'dist_end', osc_dist*0.1)
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Kickmess (VST)', 'chunk', params_kickmess.getparams(), None)
		plugins.add_plug_data(cvpj_l, pluginid, 'middlenotefix', -12)
		return True

	# ---------------------------------------- DX10 ----------------------------------------
	elif plugintype[1].lower() == 'fruity dx10':

		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'DX10', 'param', None, 16)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', getparam_old('amp_att')/65536, 'float', "Attack  ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', getparam_old('amp_dec')/65536, 'float', "Decay   ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', getparam_old('amp_rel')/65536, 'float', "Release ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', getparam_old('mod_course')/65536, 'float', "Coarse  ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', getparam_old('mod_fine')/65536, 'float', "Fine    ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', getparam_old('mod_init')/65536, 'float', "Mod Init", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_6', getparam_old('mod_time')/65536, 'float', "Mod Dec ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_7', getparam_old('mod_sus')/65536, 'float', "Mod Sus ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_8', getparam_old('mod_rel')/65536, 'float', "Mod Rel ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_9', getparam_old('velsen')/65536, 'float', "Mod Vel ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_10', getparam_old('vibrato')/65536, 'float', "Vibrato ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_11', (getparam_old('octave')+2)/5, 'float', "Octave  ", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_12', 0.5, 'float', "FineTune", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_13', getparam_old('waveform')/65536, 'float', "Waveform", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_14', getparam_old('mod_thru')/65536, 'float', "Mod Thru", )
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_15', getparam_old('lforate')/65536, 'float', "LFO Rate", )
		return True

	# ---------------------------------------- SimSynth ----------------------------------------
	elif plugintype[1].lower() == 'simsynth':
		params_vital.create()

		for oscnum in range(3):
			starttextparam = 'osc'+str(oscnum+1)
			starttextparam_vital = 'osc_'+str(oscnum+1)
			osc_shape = getparam(starttextparam+'_shape')
			osc_pw = getparam(starttextparam+'_pw')
			osc_o1 = int(getparam(starttextparam+'_o1'))
			osc_o2 = int(getparam(starttextparam+'_o2'))
			osc_on = float(getparam(starttextparam+'_on'))
			osc_crs = getparam(starttextparam+'_crs')
			osc_fine = getparam(starttextparam+'_fine')
			osc_lvl = getparam(starttextparam+'_lvl')
			osc_warm = int(getparam(starttextparam+'_warm'))

			vital_osc_shape = []
			for num in range(2048): 
				vital_osc_shape.append(
					wave.tripleoct(num/2048, simsynth_shapes[osc_shape], osc_pw, osc_o1, osc_o2)
					)
			params_vital.replacewave(oscnum, vital_osc_shape)
			params_vital.setvalue(starttextparam_vital+'_on', osc_on)
			params_vital.setvalue(starttextparam_vital+'_transpose', (osc_crs-0.5)*48)
			params_vital.setvalue(starttextparam_vital+'_tune', (osc_fine-0.5)*2)
			params_vital.setvalue(starttextparam_vital+'_level', osc_lvl)
			if osc_warm == 1:
				params_vital.setvalue(starttextparam_vital+'_unison_detune', 2.2)
				params_vital.setvalue(starttextparam_vital+'_unison_voices', 6)

		# ------------ AMP ------------
		params_vital.setvalue_timed('env_1_attack', simsynth_time(getparam('amp_att'))*3.5)
		params_vital.setvalue_timed('env_1_decay', simsynth_2time(getparam('amp_dec'))*3.5)
		params_vital.setvalue('env_1_sustain', getparam('amp_sus'))
		params_vital.setvalue_timed('env_1_release', simsynth_2time(getparam('amp_rel'))*3.5)

		# ------------ SVF ------------
		params_vital.setvalue_timed('env_2_attack', simsynth_time(getparam('svf_att'))*7)
		params_vital.setvalue_timed('env_2_decay', simsynth_2time(getparam('svf_dec'))*7)
		params_vital.setvalue('env_2_sustain', getparam('svf_sus'))
		params_vital.setvalue_timed('env_2_release', simsynth_2time(getparam('svf_rel'))*7)

		outfilter = 100
		outfilter += (getparam('svf_cut')-0.5)*40
		outfilter += (getparam('svf_kb')-0.5)*10

		params_vital.setvalue('filter_fx_resonance', getparam('svf_emph')*0.8)
		params_vital.setvalue('filter_fx_cutoff', outfilter)
		params_vital.setvalue('filter_fx_on', 1)
		params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', getparam('svf_env')*0.6, 0, 0, 0, 0)

		# ------------ Chorus ------------
		params_vital.setvalue('chorus_mod_depth', 0.35)
		params_vital.setvalue('chorus_delay_1', -9.5)
		params_vital.setvalue('chorus_delay_2', -9.0)
		if getparam('chorus_on') == True: params_vital.setvalue('chorus_on', 1.0)
		
		vitaldata = params_vital.getdata()
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
		return True

	elif plugintype[1].lower() == 'fruity bass boost':
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Weight', 'param', None, 2)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', (getparam_old('freq')/1024)*0.8, 'float', "Freq")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', (getparam_old('amount')/1024)*0.8, 'float', "Weight")
		return True

	elif plugintype[1].lower() == 'fruity phaser':
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'SupaPhaser', 'param', None, 16)
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_0', 0, 'float', "attack")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_1', 0, 'float', "release")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_2', 0, 'float', "min env")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_3', 0, 'float', "max env")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_4', 0, 'float', "env-lfo mixture")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_5', getparam_old('sweep_freq')/5000, 'float', "sweep freq.")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_6', getparam_old('depth_min')/1000, 'float', "min. depth")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_7', getparam_old('depth_max')/1000, 'float', "max. depth")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_8', getparam_old('freq_range')/1024, 'float', "freq. range")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_9', getparam_old('stereo')/1024, 'float', "stereo")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_10', getparam_old('num_stages')/22, 'float', "nr. stages")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_11', 0, 'float', "distortion")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_12', getparam_old('feedback')/1000, 'float', "feedback")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_13', getparam_old('drywet')/1024, 'float', "dry-wet")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_14', getparam_old('gain')/5000, 'float', "out gain")
		plugins.add_plug_param(cvpj_l, pluginid, 'vst_param_15', 0, 'float', "invert")
		return True

	elif plugintype[1].lower() == 'fruity spectroman':
		spectroman_mode = getparam_old('outputmode')
		x_spectrumanalyzer = ET.Element("state")
		x_spectrumanalyzer.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
		x_spectrumanalyzer.set('program', '0')
		params_various_inst.socalabs_addparam(x_spectrumanalyzer, "mode", float(spectroman_mode))
		params_various_inst.socalabs_addparam(x_spectrumanalyzer, "log", 1.0)
		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'SpectrumAnalyzer', 'chunk', ET.tostring(x_spectrumanalyzer, encoding='utf-8'), None)
		return True

	if plugintype[1].lower() == 'fruity waveshaper':
		params_various_fx.wolfshaper_init()
		params_various_fx.wolfshaper_setvalue('pregain', ((getparam('preamp')/128)-0.5)*2)
		params_various_fx.wolfshaper_setvalue('wet', getparam('wet')/128)
		params_various_fx.wolfshaper_setvalue('postgain', getparam('postgain')/128)
		params_various_fx.wolfshaper_setvalue('bipolarmode', float(getparam('bipolarmode')))
		params_various_fx.wolfshaper_setvalue('removedc', float(getparam('removedc')))

		shapeenv = plugins.get_env_points(cvpj_l, pluginid, 'shape')
		if shapeenv != None:
			params_various_fx.wolfshaper_addshape(shapeenv)

		plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'Wolf Shaper', 'chunk', data_nullbytegroup.make(params_various_fx.wolfshaper_get()), None)
		return True
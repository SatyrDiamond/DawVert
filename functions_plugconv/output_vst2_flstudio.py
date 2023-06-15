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
from functions import params_vst

from functions_plugconv import input_flstudio_wrapper

from functions_plugparams import params_various_inst
from functions_plugparams import params_kickmess
from functions_plugparams import params_various_fx
from functions_plugparams import params_vital
from functions_plugparams import params_vital_wavetable
from functions_plugparams import data_nullbytegroup

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def simsynth_time(value): return pow(value*2, 3)
def simsynth_2time(value): return pow(value*2, 3)

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.to_bytesio(fl_plugdata)

	# ---------------------------------------- 3xOsc ----------------------------------------
	if plugindata['name'].lower() == '3x osc':
		fl_plugstr.read(4)
		osc1_pan, osc1_shape, osc1_chorse, osc1_fine, osc1_ofs, osc1_detune, osc1_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc2_pan, osc2_shape, osc2_chorse, osc2_fine, osc2_ofs, osc2_detune, osc2_mixlevel = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc3_pan, osc3_shape, osc3_chorse, osc3_fine, osc3_ofs, osc3_detune, phaseband = struct.unpack('iiiiiii', fl_plugstr.read(28))
		osc1_invert, osc2_invert, osc3_invert, osc3_am = struct.unpack('bbbb', fl_plugstr.read(4))

	#---------------------------------------- Fruit Kick ----------------------------------------
	elif plugindata['name'].lower() == 'fruit kick':
		fkp = struct.unpack('iiiiiiii', fl_plugdata)
		max_freq = note_data.note_to_freq((fkp[1]/100)+12) #1000
		min_freq = note_data.note_to_freq((fkp[2]/100)-36) #130.8128
		decay_freq = fkp[3]/256
		decay_vol = fkp[4]/256
		osc_click = fkp[5]/64
		osc_dist = fkp[6]/128
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
		plugin_vst2.replace_data(instdata, 'any', 'Kickmess (VST)', 'chunk', params_kickmess.getparams(), None)
		if 'middlenote' in instdata: instdata['middlenote'] -= 12
		else: instdata['middlenote'] = -12

	# ---------------------------------------- Wasp ----------------------------------------
	elif plugindata['name'].lower() == 'wasp':
		wasp_unk = int.from_bytes(fl_plugstr.read(4), "little")
		wasp_1_shape, wasp_1_crs, wasp_1_fine, wasp_2_shape, wasp_2_crs, wasp_2_fine = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_3_shape, wasp_3_amt, wasp_12_fade, wasp_pw, wasp_fm, wasp_ringmod = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_amp_A, wasp_amp_S, wasp_amp_D, wasp_amp_R, wasp_fil_A, wasp_fil_S, wasp_fil_D, wasp_fil_R = struct.unpack('iiiiiiii', fl_plugstr.read(32))
		wasp_fil_kbtrack, wasp_fil_qtype, wasp_fil_cut, wasp_fil_res, wasp_fil_env = struct.unpack('iiiii', fl_plugstr.read(20))
		wasp_l1_shape, wasp_l1_target, wasp_l1_amt, wasp_l1_spd, wasp_l1_sync, wasp_l1_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_l2_shape, wasp_l2_target, wasp_l2_amt, wasp_l2_spd, wasp_l2_sync, wasp_l2_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_dist_on, wasp_dist_drv, wasp_dist_tone, wasp_dualvoice = struct.unpack('iiii', fl_plugstr.read(16))

	# ---------------------------------------- Wasp XT ----------------------------------------
	elif plugindata['name'].lower() == 'wasp xt':
		wasp_unk = int.from_bytes(fl_plugstr.read(4), "little")
		wasp_1_shape, wasp_1_crs, wasp_1_fine, wasp_2_shape, wasp_2_crs, wasp_2_fine = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_3_shape, wasp_3_amt, wasp_12_fade, wasp_pw, wasp_fm, wasp_ringmod = struct.unpack('iiiiii', fl_plugstr.read(24))
		wasp_amp_A, wasp_amp_S, wasp_amp_D, wasp_amp_R, wasp_fil_A, wasp_fil_S, wasp_fil_D, wasp_fil_R = struct.unpack('iiiiiiii', fl_plugstr.read(32))
		wasp_fil_kbtrack, wasp_fil_qtype, wasp_fil_cut, wasp_fil_res, wasp_fil_env = struct.unpack('iiiii', fl_plugstr.read(20))
		wasp_l1_shape, wasp_l1_target, wasp_l1_amt, wasp_l1_spd, wasp_l1_sync, wasp_l1_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_l2_shape, wasp_l2_target, wasp_l2_amt, wasp_l2_spd, wasp_l2_sync, wasp_l2_reset = struct.unpack('i'*6, fl_plugstr.read(24))
		wasp_dist_on, wasp_dist_drv, wasp_dist_tone, wasp_dualvoice = struct.unpack('iiii', fl_plugstr.read(16))

		waspxt_amp, waspxt_analog, waspxt_me_atk, waspxt_me_dec = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_amt, waspxt_me_1lvl, waspxt_me_2pitch, waspxt_me_1ami = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_pw, waspxt_vol, waspxt_lfo1_delay, waspxt_lfo2_delay = struct.unpack('i'*4, fl_plugstr.read(16))
		waspxt_me_filter, waspxt_wnoise = struct.unpack('i'*2, fl_plugstr.read(8))

	# ---------------------------------------- DX10 ----------------------------------------
	elif plugindata['name'].lower() == 'fruity dx10':
		int.from_bytes(fl_plugstr.read(4), "little")
		fldx_amp_att, fldx_amp_dec, fldx_amp_rel, fldx_mod_course = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_fine, fldx_mod_init, fldx_mod_time, fldx_mod_sus = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_rel, fldx_mod_velsen, fldx_vibrato, fldx_waveform = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod_thru, fldx_lforate, fldx_mod2_course, fldx_mod2_fine = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod2_init, fldx_mod2_time, fldx_mod2_sus, fldx_mod2_rel = struct.unpack('iiii', fl_plugstr.read(16))
		fldx_mod2_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
		fldx_octave = (int.from_bytes(fl_plugstr.read(4), "little", signed="True")/6)+0.5

		vstdxparams = {}
		params_vst.add_param(vstdxparams, 0, "Attack  ", fldx_amp_att/65536)
		params_vst.add_param(vstdxparams, 1, "Decay   ", fldx_amp_dec/65536)
		params_vst.add_param(vstdxparams, 2, "Release ", fldx_amp_rel/65536)
		params_vst.add_param(vstdxparams, 3, "Coarse  ", fldx_mod_course/65536)
		params_vst.add_param(vstdxparams, 4, "Fine    ", fldx_mod_fine/65536)
		params_vst.add_param(vstdxparams, 5, "Mod Init", fldx_mod_init/65536)
		params_vst.add_param(vstdxparams, 6, "Mod Dec ", fldx_mod_time/65536)
		params_vst.add_param(vstdxparams, 7, "Mod Sus ", fldx_mod_sus/65536)
		params_vst.add_param(vstdxparams, 8, "Mod Rel ", fldx_mod_rel/65536)
		params_vst.add_param(vstdxparams, 9, "Mod Vel ", fldx_mod_velsen/65536)
		params_vst.add_param(vstdxparams, 10, "Vibrato ", fldx_vibrato/65536)
		params_vst.add_param(vstdxparams, 11, "Octave  ", fldx_octave)
		params_vst.add_param(vstdxparams, 12, "FineTune", 0.5)
		params_vst.add_param(vstdxparams, 13, "Waveform", fldx_waveform/65536)
		params_vst.add_param(vstdxparams, 14, "Mod Thru", fldx_mod_thru/65536)
		params_vst.add_param(vstdxparams, 15, "LFO Rate", fldx_lforate/65536)
		plugin_vst2.replace_data(instdata, 'any', 'DX10', 'param', vstdxparams, 16)

	# ---------------------------------------- SimSynth ----------------------------------------
	elif plugindata['name'].lower() == 'simsynth':
		osc1_pw, osc1_crs, osc1_fine, osc1_lvl, osc1_lfo, osc1_env, osc1_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		osc2_pw, osc2_crs, osc2_fine, osc2_lvl, osc2_lfo, osc2_env, osc2_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		osc3_pw, osc3_crs, osc3_fine, osc3_lvl, osc3_lfo, osc3_env, osc3_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
		lfo_del, lfo_rate, unused, lfo_shape = struct.unpack('dddd', fl_plugstr.read(32))
		UNK1, svf_cut, svf_emph, svf_env = struct.unpack('dddd', fl_plugstr.read(32))
		svf_lfo, svf_kb, UNK2, svf_high = struct.unpack('dddd', fl_plugstr.read(32))
		svf_band, UNK3, amp_att, amp_dec = struct.unpack('dddd', fl_plugstr.read(32))
		amp_sus, amp_rel, amp_lvl, UNK4 = struct.unpack('dddd', fl_plugstr.read(32))
		svf_att, svf_dec, svf_sus, svf_rel = struct.unpack('dddd', fl_plugstr.read(32))
		fl_plugstr.read(64)
		fl_plugstr.read(12)
		osc1_on, osc1_o1, osc1_o2, osc1_warm = struct.unpack('IIII', fl_plugstr.read(16))
		osc2_on, osc2_o1, osc2_o2, osc2_warm = struct.unpack('IIII', fl_plugstr.read(16))
		osc3_on, osc3_o1, osc3_o2, osc3_warm = struct.unpack('IIII', fl_plugstr.read(16))
		lfo_on, lfo_retrugger, svf_on, UNK5 = struct.unpack('IIII', fl_plugstr.read(16))
		lfo_trackamp, UNK6, chorus_on, UNK7 = struct.unpack('IIII', fl_plugstr.read(16))

		params_vital.create()

		# ------------ OSC 1 ------------
		vital_osc1_shape = []
		for num in range(2048): vital_osc1_shape.append(params_vital_wavetable.tripleoct(num/2048, simsynth_shapes[osc1_shape], osc1_pw, osc1_o1, osc1_o2))
		params_vital.replacewave(0, vital_osc1_shape)
		params_vital.setvalue('osc_1_on', osc1_on)
		params_vital.setvalue('osc_1_transpose', (osc1_crs-0.5)*48)
		params_vital.setvalue('osc_1_tune', (osc1_fine-0.5)*2)
		params_vital.setvalue('osc_1_level', osc1_lvl)
		if osc1_warm == 1:
			params_vital.setvalue('osc_1_unison_detune', 2.2)
			params_vital.setvalue('osc_1_unison_voices', 6)

		# ------------ OSC 2 ------------
		vital_osc2_shape = []
		for num in range(2048): vital_osc2_shape.append(params_vital_wavetable.tripleoct(num/2048, simsynth_shapes[osc2_shape], osc2_pw, osc2_o1, osc2_o2))
		params_vital.replacewave(1, vital_osc2_shape)
		params_vital.setvalue('osc_2_on', osc2_on)
		params_vital.setvalue('osc_2_transpose', (osc2_crs-0.5)*48)
		params_vital.setvalue('osc_2_tune', (osc2_fine-0.5)*2)
		params_vital.setvalue('osc_2_level', osc2_lvl)
		if osc2_warm == 1:
			params_vital.setvalue('osc_2_unison_detune', 2.2)
			params_vital.setvalue('osc_2_unison_voices', 6)

		# ------------ OSC 3 ------------
		vital_osc3_shape = []
		for num in range(2048): vital_osc3_shape.append(params_vital_wavetable.tripleoct(num/2048, simsynth_shapes[osc3_shape], osc3_pw, osc3_o1, osc3_o2))
		params_vital.replacewave(2, vital_osc3_shape)
		params_vital.setvalue('osc_3_on', osc3_on)
		params_vital.setvalue('osc_3_transpose', (osc3_crs-0.5)*48)
		params_vital.setvalue('osc_3_tune', (osc3_fine-0.5)*2)
		params_vital.setvalue('osc_3_level', osc3_lvl)
		if osc3_warm == 1:
			params_vital.setvalue('osc_3_unison_detune', 2.2)
			params_vital.setvalue('osc_3_unison_voices', 6)

		# ------------ AMP ------------
		params_vital.setvalue_timed('env_1_attack', simsynth_time(amp_att)*3.5)
		params_vital.setvalue_timed('env_1_decay', simsynth_2time(amp_dec)*3.5)
		params_vital.setvalue('env_1_sustain', amp_sus)
		params_vital.setvalue_timed('env_1_release', simsynth_2time(amp_rel)*3.5)

		# ------------ SVF ------------
		params_vital.setvalue_timed('env_2_attack', simsynth_time(svf_att)*7)
		params_vital.setvalue_timed('env_2_decay', simsynth_2time(svf_dec)*7)
		params_vital.setvalue('env_2_sustain', svf_sus)
		params_vital.setvalue_timed('env_2_release', simsynth_2time(svf_rel)*7)

		outfilter = 100
		outfilter += (svf_cut-0.5)*40
		outfilter += (svf_kb-0.5)*10

		params_vital.setvalue('filter_fx_resonance', svf_emph*0.8)
		params_vital.setvalue('filter_fx_cutoff', outfilter)
		params_vital.setvalue('filter_fx_on', 1)
		params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', svf_env*0.6, 0, 0, 0, 0)

		# ------------ Chorus ------------
		params_vital.setvalue('chorus_mod_depth', 0.35)
		params_vital.setvalue('chorus_delay_1', -9.5)
		params_vital.setvalue('chorus_delay_2', -9.0)
		if chorus_on == 1: params_vital.setvalue('chorus_on', 1.0)
		
		vitaldata = params_vital.getdata()
		plugin_vst2.replace_data(instdata, 'any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)





def decode_pointdata(fl_plugstr):
	autoheader = struct.unpack('bii', fl_plugstr.read(12))
	pointdata_table = []

	positionlen = 0
	for num in range(autoheader[2]):
		chunkdata = struct.unpack('ddfbbbb', fl_plugstr.read(24))
		positionlen += round(chunkdata[0], 6)
		pointdata_table.append( [positionlen, chunkdata[1:], 0.0, 0] )
		if num != 0:
			pointdata_table[num-1][2] = chunkdata[2]
			pointdata_table[num-1][3] = chunkdata[3]

	fl_plugstr.read(20).hex()
	return pointdata_table

def convert_fx(fxdata):
	global temp_count
	pluginname = fxdata['plugin']
	plugindata = fxdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.to_bytesio(fl_plugdata)

	pluginname = plugindata['plugin'].lower()

	print('----------------------', pluginname)

	if pluginname == 'fruity bass boost':
		flpbb = struct.unpack('III', fl_plugdata)
		airwindowparams = {}
		params_vst.add_param(airwindowparams, 0, "Freq", (flpbb[1]/1024)*0.8)
		params_vst.add_param(airwindowparams, 1, "Weight", (flpbb[2]/1024)*0.8)
		plugin_vst2.replace_data(fxdata, 'any', 'Weight', 'param', airwindowparams, 2)

	#if pluginname == 'fruity convolver':
	#	print(fl_plugstr.read(21))
	#	stringlen = fl_plugstr.read(1)[0]
	#	filename = fl_plugstr.read(stringlen)
	#	print(fl_plugstr.read(36))
	#	instdata['plugin'] = 'convolver'
	#	plugindata = instdata['plugindata'] = {}
	#	autodata = {}
	#	for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
	#		autoheader = struct.unpack('bii', fl_plugstr.read(12))
	#		for _ in range(autoheader[2]):
	#			autodata_table = []
	#			autodata_table.append( struct.unpack('ddfbbbb', fl_plugstr.read(24)) )
	#		fl_plugstr.read(20).hex()
	#		autodata[autoname] = autodata_table
	#	print(autodata)
	#	print(   fl_plugstr.read(20).hex()   )

	#if pluginname == 'fruity delay':
	#	flpdel = struct.unpack('bIIIIII', fl_plugdata)
	#	print(flpdel)


	if pluginname == 'fruity spectroman':
		#print(len(fl_plugdata))
		spectroman_data = struct.unpack('bIIIbbb', fl_plugdata)
		x_spectrumanalyzer = ET.Element("state")
		x_spectrumanalyzer.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state width="400" height="328"/>')
		x_spectrumanalyzer.set('program', '0')
		params_various_inst.socalabs_addparam(x_spectrumanalyzer, "mode", float(spectroman_data[1]))
		params_various_inst.socalabs_addparam(x_spectrumanalyzer, "log", 1.0)
		plugin_vst2.replace_data(fxdata, 'any', 'SpectrumAnalyzer', 'chunk', ET.tostring(x_spectrumanalyzer, encoding='utf-8'), None)

	if pluginname == 'fruity waveshaper':
		headerdata = fl_plugstr.read(22)
		headerdata_ints = struct.unpack('bHHIIbbbbbb', headerdata)
		
		pointsdata = decode_pointdata(fl_plugstr)

		params_various_fx.wolfshaper_init()

		t_pointdata = []
		for pointdata in pointsdata:
			t_pointdata.append({
				'position': pointdata[0], 'data':pointdata[1], 
				'tens':pointdata[2], 'shape':pointdata[3]
				})
		t_pointdata = data_values.sort_pos(t_pointdata)
		for t_point in t_pointdata:
			wpointtype = 0
			wtens = t_point['tens']*-100

			if t_point['shape'] == 0: wpointtype = 0
			if t_point['shape'] == 1: wpointtype = 1
			if t_point['shape'] == 3: 
				wpointtype = 2
				wtens *= -1
			if t_point['shape'] == 6: 
				wpointtype = 3
				wtens = ((abs(wtens)*-1)+100)*0.2

			params_various_fx.wolfshaper_addpoint(
				t_point['position'],
				t_point['data'][0],
				wtens,
				wpointtype
				)

		params_various_fx.wolfshaper_setvalue('pregain', ((headerdata_ints[2]/128)-0.5)*2)
		params_various_fx.wolfshaper_setvalue('wet', headerdata_ints[3]/128)
		params_various_fx.wolfshaper_setvalue('postgain', headerdata_ints[4]/128)
		params_various_fx.wolfshaper_setvalue('bipolarmode', float(headerdata_ints[5]))
		params_various_fx.wolfshaper_setvalue('removedc', float(headerdata_ints[6]))

		plugin_vst2.replace_data(fxdata, 'any', 'Wolf Shaper', 'chunk', data_nullbytegroup.make(params_various_fx.wolfshaper_get()), None)
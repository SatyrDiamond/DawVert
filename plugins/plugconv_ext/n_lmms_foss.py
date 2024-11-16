# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import math
import base64
import struct
import lxml.etree as ET

from functions import extpluglog
from functions_plugin_ext import data_nullbytegroup
from functions_plugin_ext import params_os_kickmess
from functions_plugin_ext import plugin_vst2
from objects.convproj import wave

def sid_shape(lmms_sid_shape):
	if lmms_sid_shape == 0: return 3 #squ
	if lmms_sid_shape == 1: return 1 #tri
	if lmms_sid_shape == 2: return 2 #saw
	if lmms_sid_shape == 3: return 4 #noise

def mooglike(x, i_var):
	return (x*2) if x<0.5 else ((1-x)*2)**2

def exp_curve(x, i_var):
	return ((abs(x%(2)-1)-0.5)*2)**2

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'lmms', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):

		if plugin_obj.type.subtype == 'bitinvader':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'BitInvader')
				interpolation = bool(plugin_obj.params.get('interpolation', 0).value)

				plugin_obj.replace('user', 'matt_tytel', 'vital')
				plugin_obj.env_asdr_copy('vol', 'vital_env_2')
				plugin_obj.env_asdr_copy('cutoff', 'vital_env_3')
				plugin_obj.env_asdr_copy('reso', 'vital_env_4')
				env_data = plugin_obj.env_asdr_get('vital_env_2')
				filt_env_data = plugin_obj.env_asdr_get('vital_env_3')
				vollvl = abs(env_data.amount)
				osclvl = 1-vollvl

				plugin_obj.params.add('osc_1_on', 1, 'float')
				plugin_obj.params.add('osc_1_level', osclvl, 'float')
				plugin_obj.params.add('osc_1_transpose', 0, 'float')
				plugin_obj.params.add('osc_1_wave_frame', int(interpolation)*256, 'float')

				modulation_obj = plugin_obj.modulation_add_native('env_2', 'osc_1_level')
				modulation_obj.amount = vollvl

				modulation_obj = plugin_obj.modulation_add_native('env_3', 'filter_fx_cutoff')
				modulation_obj.amount = abs(filt_env_data.amount)/7000

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'tripleoscillator':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'Oscillator')

				oscdata = []
				for oscnum in range(3):
					str_oscnum = str(oscnum)
					v_vol = plugin_obj.params.get('vol'+str_oscnum, 0).value
					v_coarse = plugin_obj.params.get('coarse'+str_oscnum, 0).value
					v_pan = plugin_obj.params.get('pan'+str_oscnum, 0).value
					v_finel = plugin_obj.params.get('finel'+str_oscnum, 0).value
					v_finer = plugin_obj.params.get('finer'+str_oscnum, 0).value
					v_wave = int(plugin_obj.params.get('wavetype'+str_oscnum, 0).value)
					v_phoffset = plugin_obj.params.get('phoffset'+str_oscnum, 0).value
					oscdata.append([v_vol,v_coarse,v_pan,v_finel,v_finer,v_wave,v_phoffset])

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				plugin_obj.env_asdr_copy('vol', 'vital_env_2')
				plugin_obj.env_asdr_copy('cutoff', 'vital_env_3')
				plugin_obj.env_asdr_copy('reso', 'vital_env_4')

				env_data = plugin_obj.env_asdr_get('vital_env_2')

				vollvl = abs(env_data.amount)
				osclvl = 1-vollvl
				noiselvl = 0

				for oscnum, oscdata in enumerate(oscdata):
					v_vol,v_coarse,v_pan,v_finel,v_finer,v_wave,v_phoffset = oscdata 
					vital_oscnum = 'osc_'+str(oscnum+1)

					finetune = (v_finel+v_finer)/2
					unison_detune = abs(v_finel)+abs(v_finer)

					plugin_obj.params.add(vital_oscnum+'_on', 1, 'float')
					plugin_obj.params.add(vital_oscnum+'_level', (v_vol/100)*osclvl, 'float')
					plugin_obj.params.add(vital_oscnum+'_transpose', v_coarse, 'float')
					plugin_obj.params.add(vital_oscnum+'_pan', v_pan/100, 'float')
					plugin_obj.params.add(vital_oscnum+'_tune', finetune/100 , 'float')
					plugin_obj.params.add(vital_oscnum+'_unison_detune', (unison_detune*3.5)/50, 'float')
					plugin_obj.params.add(vital_oscnum+'_unison_voices', 2, 'float')
					plugin_obj.params.add(vital_oscnum+'_phase', int(v_phoffset)/360, 'float')

					modulation_obj = plugin_obj.modulation_add_native('env_2',  vital_oscnum+'_level')
					modulation_obj.amount = (v_vol/100)*vollvl

					osc_obj = plugin_obj.osc_add()
					osc_obj.prop.type = 'wave'
					osc_obj.prop.nameid = vital_oscnum

					wave_obj = plugin_obj.wave_add(vital_oscnum)
					wave_obj.set_numpoints(2048)
					if v_wave == 0: wave_obj.add_wave('sine', 0, 1, 1)
					if v_wave == 1: wave_obj.add_wave('triangle', 0, 1, 1)
					if v_wave == 2: wave_obj.add_wave('saw', 0, 1, 1)
					if v_wave == 3: wave_obj.add_wave('square', 0, 1, 1)
					if v_wave == 4: wave_obj.add_wave_func(mooglike, 0, 1, 1)
					if v_wave == 5: wave_obj.add_wave_func(exp_curve, 0, 1, 1)
					if v_wave == 6: 
						noiselvl += (v_vol/100)
						plugin_obj.datavals.add('sample_generate_noise', True)
						plugin_obj.params.add('sample_on', 1, 'float')
						plugin_obj.params.add(vital_oscnum+'_on', 0, 'float')

				plugin_obj.params.add('sample_level', min(noiselvl, 1), 'float')
				
				modulation_obj = plugin_obj.modulation_add_native('env_2', 'sample_level')
				modulation_obj.amount = vollvl

				filt_env_data = plugin_obj.env_asdr_get('vital_env_3')

				modulation_obj = plugin_obj.modulation_add_native('env_3', 'filter_fx_cutoff')
				modulation_obj.amount = abs(filt_env_data.amount)/7000

				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'papu':
			extpluglog.extpluglist.add('FOSS', 'VST', 'PAPU', 'SocaLabs')
			exttype = plugins.base.extplug_exists('socalabs', extplugtype, 'papu')
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'Freeboy')

				papu_ch1so1 = plugin_obj.params.get('ch1so1', 0).value
				papu_ch1so2 = plugin_obj.params.get('ch1so2', 0).value
				papu_ch1wpd = plugin_obj.params.get('ch1wpd', 0).value
				papu_ch1vsd = plugin_obj.params.get('ch1vsd', 0).value
				papu_ch1ssl = plugin_obj.params.get('ch1ssl', 0).value

				papu_st = plugin_obj.params.get('st', 0).value
				papu_sd = plugin_obj.params.get('sd', 0).value
				if papu_sd: papu_st = -papu_st

				papu_srs = plugin_obj.params.get('srs', 0).value

				papu_ch2so1 = plugin_obj.params.get('ch2so1', 0).value
				papu_ch2so2 = plugin_obj.params.get('ch2so2', 0).value
				papu_ch2wpd = plugin_obj.params.get('ch2wpd', 0).value
				papu_ch2vsd = plugin_obj.params.get('ch2vsd', 0).value
				papu_ch2ssl = plugin_obj.params.get('ch2ssl', 0).value

				papu_ch4so1 = plugin_obj.params.get('ch4so1', 0).value
				papu_ch4so2 = plugin_obj.params.get('ch4so2', 0).value
				papu_ch4vsd = plugin_obj.params.get('ch4vsd', 0).value
				papu_ch4ssl = plugin_obj.params.get('ch4ssl', 0).value
				papu_ch2ssl = plugin_obj.params.get('ch2ssl', 0).value

				papu_srw = plugin_obj.params.get('srw', 0).value

				plugin_obj.replace('user', 'socalabs', 'papu')

				# Channel 1
				plugin_obj.params.add("ol1", int(papu_ch1so1), 'float')
				plugin_obj.params.add("or1", int(papu_ch1so2), 'float')
				plugin_obj.params.add("duty1", papu_ch1wpd, 'float')
				if papu_ch1vsd:
					plugin_obj.params.add("a1", papu_ch1ssl, 'float')
					plugin_obj.params.add("r1", 0.0, 'float')
				else:
					plugin_obj.params.add("a1", 0.0, 'float')
					plugin_obj.params.add("r1", papu_ch1ssl, 'float')
				plugin_obj.params.add("tune1", 12.0, 'float')
				plugin_obj.params.add("fine1", 0.0, 'float')
				plugin_obj.params.add("sweep1", papu_st, 'float')
				plugin_obj.params.add("shift1", papu_srs, 'float')

				# Channel 2
				plugin_obj.params.add("ol2", int(papu_ch2so1), 'float')
				plugin_obj.params.add("or2", int(papu_ch2so2), 'float')
				plugin_obj.params.add("duty2", papu_ch2wpd, 'float')
				if papu_ch2vsd:
					plugin_obj.params.add("a2", papu_ch2ssl, 'float')
					plugin_obj.params.add("r2", 0.0, 'float')
				else:
					plugin_obj.params.add("a2", 0.0, 'float')
					plugin_obj.params.add("r2", papu_ch2ssl, 'float')
				plugin_obj.params.add("tune2", 12.0, 'float')
				plugin_obj.params.add("fine2", 0.0, 'float')

				# Channel 4
				plugin_obj.params.add("oln", int(papu_ch4so1), 'float')
				plugin_obj.params.add("orl", int(papu_ch4so2), 'float')
				if papu_ch4vsd:
					plugin_obj.params.add("an", papu_ch4ssl, 'float')
					plugin_obj.params.add("ar", 0.0, 'float')
				else:
					plugin_obj.params.add("an", 0.0, 'float')
					plugin_obj.params.add("ar", papu_ch4ssl, 'float')
				plugin_obj.params.add("shiftn", 10, 'float')
				plugin_obj.params.add("stepn", int(papu_srw), 'float')
				plugin_obj.params.add("ration", 0.0, 'float')

				plugin_obj.params.add("output", 7.0, 'float')
				plugin_obj.params.add("param", 8.0, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True
#
		#if plugin_obj.type.subtype == 'sid':
		#	extpluglog.extpluglist.add('FOSS', 'VST2', 'SID', 'SocaLabs')
		#	if plugin_vst2.check_exists('id', 1399415908):
		#		extpluglog.extpluglist.success('LMMS', 'SID')
		#		plugtransform.transform('./data_ext/plugts/lmms_vst2.pltr', 'vst2_sid', convproj_obj, plugin_obj, pluginid, dv_config)
		#		data_socalabs = params_os_socalabs.socalabs_data()
		#		plugin_obj.params.add("a1", plugtransform.get_storedval('a1'))
		#		plugin_obj.params.add("a2", plugtransform.get_storedval('a2'))
		#		plugin_obj.params.add("a3", plugtransform.get_storedval('a3'))
		#		plugin_obj.params.add("cutoff", plugtransform.get_storedval('cutoff'))
		#		plugin_obj.params.add("d1", plugtransform.get_storedval('d1'))
		#		plugin_obj.params.add("d2", plugtransform.get_storedval('d2'))
		#		plugin_obj.params.add("d3", plugtransform.get_storedval('d3'))
		#		plugin_obj.params.add("f1", int(plugtransform.get_storedval('f1')))
		#		plugin_obj.params.add("f2", int(plugtransform.get_storedval('f2')))
		#		plugin_obj.params.add("f3", int(plugtransform.get_storedval('f3')))
		#		plugin_obj.params.add("fine1", 0.0)
		#		plugin_obj.params.add("fine2", 0.0)
		#		plugin_obj.params.add("fine3", 0.0)
		#		filterMode = int(plugtransform.get_storedval('filterMode'))
		#		plugin_obj.params.add("highpass", 1.0 if filterMode == 0 else 0.0)
		#		plugin_obj.params.add("bandpass", 1.0 if filterMode == 1 else 0.0)
		#		plugin_obj.params.add("lowpass", 1.0 if filterMode == 2 else 0.0)
		#		plugin_obj.params.add("output3", plugtransform.get_storedval('output3'))
		#		plugin_obj.params.add("pw1", plugtransform.get_storedval('pw1'))
		#		plugin_obj.params.add("pw2", plugtransform.get_storedval('pw2'))
		#		plugin_obj.params.add("pw3", plugtransform.get_storedval('pw3'))
		#		plugin_obj.params.add("r1", plugtransform.get_storedval('r1'))
		#		plugin_obj.params.add("r2", plugtransform.get_storedval('r2'))
		#		plugin_obj.params.add("r3", plugtransform.get_storedval('r3'))
		#		plugin_obj.params.add("reso", plugtransform.get_storedval('reso'))
		#		plugin_obj.params.add("ring1", int(plugtransform.get_storedval('ring1')))
		#		plugin_obj.params.add("ring2", int(plugtransform.get_storedval('ring2')))
		#		plugin_obj.params.add("ring3", int(plugtransform.get_storedval('ring3')))
		#		plugin_obj.params.add("s1", plugtransform.get_storedval('s1'))
		#		plugin_obj.params.add("s2", plugtransform.get_storedval('s2'))
		#		plugin_obj.params.add("s3", plugtransform.get_storedval('s3'))
		#		plugin_obj.params.add("sync1", int(plugtransform.get_storedval('sync1')))
		#		plugin_obj.params.add("sync2", int(plugtransform.get_storedval('sync2')))
		#		plugin_obj.params.add("sync3", int(plugtransform.get_storedval('sync3')))
		#		plugin_obj.params.add("tune1", plugtransform.get_storedval('tune1'))
		#		plugin_obj.params.add("tune2", plugtransform.get_storedval('tune2'))
		#		plugin_obj.params.add("tune3", plugtransform.get_storedval('tune3'))
		#		plugin_obj.params.add("voices", 8.0)
		#		plugin_obj.params.add("vol", plugtransform.get_storedval('vol'))
		#		plugin_obj.params.add("w1", sid_shape(plugtransform.get_storedval('w1')))
		#		plugin_obj.params.add("w2", sid_shape(plugtransform.get_storedval('w2')))
		#		plugin_obj.params.add("w3", sid_shape(plugtransform.get_storedval('w3')))
		#		data_socalabs.to_cvpj_vst2(convproj_obj, plugin_obj, 1399415908)
		#		return True
#
		if plugin_obj.type.subtype == 'kicker':
			extpluglog.extpluglist.add('FOSS', 'VST2', 'Kickmess', '')
			exttype = plugins.base.extplug_exists('kickmess', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'Kicker')
				startnote = plugin_obj.params.get('startnote', False).value
				endnote = plugin_obj.params.get('endnote', False).value
				plugin_obj.plugts_transform('./data_ext/plugts/lmms_vst2.pltr', 'kickmess', convproj_obj, pluginid)
				if startnote: plugin_obj.params.add('freq_note_start', 0.5, 'float')
				if endnote: plugin_obj.params.add('freq_note_end', 0.5, 'float')
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'lb302':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Vital', '')
			exttype = plugins.base.extplug_exists('vital', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'LB302')

				lb_db24 = plugin_obj.params.get('db24', 0).value
				lb_dead = plugin_obj.params.get('dead', 0).value
				lb_shape = plugin_obj.params.get('shape', 0).value
				lb_slide = plugin_obj.params.get('slide', 0).value
				lb_slide_dec = plugin_obj.params.get('slide_dec', 0).value
				lb_vcf_cut = plugin_obj.params.get('vcf_cut', 0).value
				lb_vcf_dec = plugin_obj.params.get('vcf_dec', 0).value
				lb_vcf_mod = plugin_obj.params.get('vcf_mod', 0).value
				lb_vcf_res = plugin_obj.params.get('vcf_res', 0).value

				plugin_obj.replace('user', 'matt_tytel', 'vital')

				osc_obj = plugin_obj.osc_add()
				osc_obj.prop.type = 'wave'
				osc_obj.prop.nameid = 'main'

				wave_obj = plugin_obj.wave_add('main')
				wave_obj.set_numpoints(2048)
				if lb_shape == 0: wave_obj.add_wave('saw', 0, 1, 1)
				if lb_shape == 1: wave_obj.add_wave('triangle', 0, 1, 1)
				if lb_shape == 2: wave_obj.add_wave('square', 0.5, 1, 1)
				if lb_shape == 3: wave_obj.add_wave('square', 0.5, 1, 1) #square_roundend
				if lb_shape == 4: wave_obj.add_wave_func(mooglike, 0, 1, 1)
				if lb_shape == 5: wave_obj.add_wave('sine', 0, 1, 1)
				if lb_shape == 6: wave_obj.add_wave_func(exp_curve, 0, 1, 1)
				if lb_shape == 8: wave_obj.add_wave('saw', 0, 1, 1)
				if lb_shape == 9: wave_obj.add_wave('square', 0.5, 1, 1)
				if lb_shape == 10: wave_obj.add_wave('triangle', 0, 1, 1)
				if lb_shape == 11: wave_obj.add_wave_func(mooglike, 0, 1, 1)
				if lb_shape != 7:  plugin_obj.params.add('osc_1_on', 1, 'float')
				else: 
					plugin_obj.datavals.add('sample_generate_noise', True)
					plugin_obj.params.add('sample_on', 1)
				plugin_obj.params.add('osc_1_level', 1, 'float')
				plugin_obj.params.add('osc_1_transpose', 12, 'float')
				plugin_obj.params.add('sample_level', 1, 'float')

				if lb_db24 == 0:
					vitalcutoff_first = (lb_vcf_cut*40)+50
					vitalcutoff_minus = (lb_vcf_mod*16)
					vcfamt = (lb_vcf_mod+0.5)*0.25
				else:
					vitalcutoff_first = (lb_vcf_cut*60)+20
					vitalcutoff_minus = (lb_vcf_mod*20)
					vcfamt = (lb_vcf_mod+0.2)*0.5

				modulation_obj = plugin_obj.modulation_add_native('env_2', 'filter_2_cutoff')
				modulation_obj.amount = vcfamt

				plugin_obj.params.add('polyphony', 1, 'float')
				if lb_slide == 1:
					plugin_obj.params.add('portamento_force', 1, 'float')
					plugin_obj.params.add('portamento_slope', 5, 'float')
					plugin_obj.params.add('portamento_time', (-5)+(pow(lb_slide_dec*2, 2.5)), 'float')

				plugin_obj.params.add('osc_1_destination', 2, 'float')
				plugin_obj.params.add('filter_2_on', 1, 'float')
				plugin_obj.params.add('filter_2_cutoff', vitalcutoff_first-vitalcutoff_minus, 'float')
				plugin_obj.params.add('filter_2_resonance', lb_vcf_res/1.7, 'float')
				plugin_obj.env_asdr_add('vital_env_2', 0, 0, 0, 0.4+(lb_vcf_dec*3) if lb_dead == 0 else 0, 0, 0, 1)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'zynaddsubfx' and 'vst2' in extplugtype:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'ZynAddSubFX/Zyn-Fusion', '')
			if plugin_vst2.check_exists('id', 1514230598):
				extpluglog.extpluglist.success('LMMS', 'ZynAddSubFX')
				zasfxdata = plugin_obj.rawdata_get('data')
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + zasfxdata
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', 1514230598, 'chunk', zasfxdatafixed, None)
				return True

		if plugin_obj.type.subtype == 'reverbsc':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Castello Reverb', '')
			exttype = plugins.base.extplug_exists('castello', extplugtype, 'castello')
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'ReverbSC')
				plugin_obj.plugts_transform('./data_ext/plugts/lmms_vst2.pltr', 'castello_reverbsc', convproj_obj, pluginid)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'stereoenhancer':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Wider', 'Airwindows')
			exttype = plugins.base.extplug_exists('airwindows', extplugtype, 'Wider')
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'Stereo Enhancer')
				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
				manu_obj.from_param('width', 'width', 1)
				manu_obj.calc('width', 'div', 180, 0, 0, 0)
				manu_obj.calc('width', 'to_one', -1, 1, 0, 0)
				plugin_obj.replace('user', 'airwindows', 'Wider')
				manu_obj.to_param('width', 'width', None)
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

		if plugin_obj.type.subtype == 'waveshaper':
			extpluglog.extpluglist.add('FOSS', 'VST', 'Wolf Shaper', '')
			exttype = plugins.base.extplug_exists('wolfshaper', extplugtype, None)
			if exttype:
				extpluglog.extpluglist.success('LMMS', 'Wave Shaper')
				waveshapebytes = base64.b64decode(plugin_obj.datavals.get('waveShape', ''))
				waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4])[0] for i in range(0, len(waveshapebytes), 4)]

				manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

				manu_obj.from_param('inputGain', 'inputGain', 1)
				manu_obj.from_param('outputGain', 'outputGain', 1)
				manu_obj.calc_clamp('inputGain', 0, 2)
				manu_obj.calc_clamp('outputGain', 0, 1)
				plugin_obj.replace('user', 'wolf-plugins', 'wolfshaper')
				manu_obj.to_param('inputGain', 'pregain', None)
				manu_obj.to_param('outputGain', 'postgain', None)

				autopoints_obj = plugin_obj.env_points_add('shape', 1, True, 'float')
				for pointnum in range(50): 
					autopoint_obj = autopoints_obj.add_point()
					autopoint_obj.pos = pointnum/49
					autopoint_obj.value = waveshapepoints[pointnum*4]
				plugin_obj.user_to_external(convproj_obj, pluginid, exttype, 'any')
				return True

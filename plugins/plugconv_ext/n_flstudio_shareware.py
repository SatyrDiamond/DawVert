# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import struct
import os
import math
import lxml.etree as ET

from functions import note_data
from functions import data_bytes
from functions import xtramath
from functions import extpluglog
from objects import globalstore
from objects.data_bytes import bytereader
from objects.convproj import wave

from functions_plugin_ext import plugin_vst2

from functions_plugin_ext_nonfree import params_nf_image_line

def il_vst_chunk(i_type, i_data): 
	if i_type != 'name':
		if i_type != 0: return struct.pack('iii', i_type, len(i_data), 0)+i_data
		else: return bytes([0x00, 0x00, 0x00, 0x00])+i_data
	else:
		return bytes([0x01, 0x00, 0x00, 0x00])+data_bytes.makestring_fixedlen(i_data, 24)


def il_headersize(i_data): 
	return struct.pack('i', len(i_data))+i_data

def make_flvst1(plugin_obj):
	fldata = params_nf_image_line.imageline_vststate()
	fldata.state_data = plugin_obj.rawdata_get('fl')
	fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	return fldata.write()

def make_flvst2(plugin_obj):
	fldata = params_nf_image_line.imageline_vststate()
	fldata.state_data = plugin_obj.rawdata_get('fl')
	fldata.otherp1_data[1] = 54
	fldata.otherp2_data = [41 for _ in range(16)]
	fldata.otherp3_data = [41 for _ in range(16)]
	fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xffg\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00P\x03\x00\x009\x02\x00\x00h\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	fldata.headertype = 1
	return fldata.write()

def make_sslf(plugin_obj):
	ilchunk = plugin_obj.rawdata_get('fl')
	dataout = b''
	if ilchunk:
		sslf_data = bytereader.bytereader()
		sslf_data.load_raw(ilchunk)
		main_iff_obj = sslf_data.chunk_objmake()
		tlvfound = False
		for chunk_obj in main_iff_obj.iter(0, sslf_data.end):
			if chunk_obj.id == b'SSLF': dataout = sslf_data.raw(chunk_obj.size)
	return dataout

def param_auto(convproj_obj, pluginid, plugin_obj, name):
	globalstore.paramremap.load(name, '.\\data_ext\\remap\\imageline\\'+name+'.csv')
	manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
	manu_obj.remap_cvpj_to_ext_opt(name, 'vst2')

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['native', 'flstudio', None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['shareware']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		flpluginname = plugin_obj.type.subtype.lower()

		use_vst2 = 'vst2' in extplugtype

		# ---------------------------------------- Drumaxx ----------------------------------------
		if flpluginname == 'drumaxx' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Drumaxx', 'Image-Line')
			if plugin_vst2.check_exists('id', 1145918257):
				extpluglog.extpluglist.success('FL Studio', 'Drumaxx')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1145918257, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Drumaxx')
				return True

		# ---------------------------------------- FL Slayer ----------------------------------------
		elif flpluginname == 'fl slayer' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Slayer 2', 'ReFX')

			if plugin_vst2.check_exists('id', 1397512498):
				extpluglog.extpluglist.success('FL Studio', 'FL Slayer')
				amp_type = plugin_obj.params.get('amp_type', 0).value
				cabinet = plugin_obj.params.get('cabinet', 0).value
				coil_type = plugin_obj.params.get('coil_type', 0).value
				damp = plugin_obj.params.get('damp', 0).value
				damp_vel = plugin_obj.params.get('damp_vel', 0).value
				drive = plugin_obj.params.get('drive', 0).value
				eq_high = plugin_obj.params.get('eq_high', 0).value
				eq_low = plugin_obj.params.get('eq_low', 0).value
				eq_mid = plugin_obj.params.get('eq_mid', 0).value
				feedback = plugin_obj.params.get('feedback', 0).value
				fret = plugin_obj.params.get('fret', 0).value
				fx_param1 = plugin_obj.params.get('fx_param1', 0).value
				fx_param2 = plugin_obj.params.get('fx_param2', 0).value
				fx_type = plugin_obj.params.get('fx_type', 0).value
				glissando = plugin_obj.params.get('glissando', 0).value
				harmonic = plugin_obj.params.get('harmonic', 0).value
				harmonic_vel = plugin_obj.params.get('harmonic_vel', 0).value
				hold = plugin_obj.params.get('hold', 0).value
				mode = plugin_obj.params.get('mode', 0).value
				pickup_position = plugin_obj.params.get('pickup_position', 0).value
				pitch_bend = plugin_obj.params.get('pitch_bend', 0).value
				presence = plugin_obj.params.get('presence', 0).value
				slap = plugin_obj.params.get('slap', 0).value
				string_type = plugin_obj.params.get('string_type', 0).value
				timing = plugin_obj.params.get('timing', 0).value
				tone = plugin_obj.params.get('tone', 0).value

				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1397512498, 'param', None, 118)

				plugin_obj.params.add_named('ext_param_12', amp_type/5, 'float', 'Amp type')
				plugin_obj.params.add_named('ext_param_20', cabinet/5, 'float', 'Cab type')
				plugin_obj.params.add_named('ext_param_1', coil_type/2, 'float', 'Coils')
				plugin_obj.params.add_named('ext_param_115', damp/65535, 'float', 'Damping')
				plugin_obj.params.add_named('ext_param_116', damp_vel/65535, 'float', 'Vel->Damping')
				plugin_obj.params.add_named('ext_param_13', drive/65535, 'float', 'Drive')
				plugin_obj.params.add_named('ext_param_16', eq_low/65535, 'float', 'EQ low')
				plugin_obj.params.add_named('ext_param_17', eq_mid/65535, 'float', 'EQ mid')
				plugin_obj.params.add_named('ext_param_18', eq_high/65535, 'float', 'EQ high')
				plugin_obj.params.add_named('ext_param_15', feedback/65535, 'float', 'feedback')
				#fret
				#fx_param1
				#fx_param2
				#fx_type
				plugin_obj.params.add_named('ext_param_24', glissando, 'float', 'PB mode')
				plugin_obj.params.add_named('ext_param_23', pitch_bend/127, 'float', 'PB range')
				#harmonic
				#harmonic_vel
				#hold
				#mode
				plugin_obj.params.add_named('ext_param_2', pickup_position/65535, 'float', 'Pick pos')
				plugin_obj.params.add_named('ext_param_14', presence/65535, 'float', 'Presence')
				plugin_obj.params.add_named('ext_param_4', slap/65535, 'float', 'Slap lvl')
				plugin_obj.params.add_named('ext_param_0', string_type/8, 'float', 'String')
				plugin_obj.params.add_named('ext_param_22', timing/65535, 'float', 'timing')
				plugin_obj.params.add_named('ext_param_3', tone/65535, 'float', 'Tone')

				plugin_obj.params.add_named('ext_param_109', 1, 'float', 'dummy')
				plugin_obj.params.add_named('ext_param_110', 0, 'float', 'dummy')
				plugin_obj.params.add_named('ext_param_111', 1, 'float', 'dummy')
				plugin_obj.params.add_named('ext_param_112', 1, 'float', 'dummy')
				plugin_obj.params.add_named('ext_param_113', 1, 'float', 'dummy')
				plugin_obj.params.add_named('ext_param_25', 0.5, 'float', 'Gain')
				plugin_obj.params.add_named('ext_param_114', 0.5, 'float', 'Mst Vol')
				plugin_obj.params.add_named('ext_param_6', 0.75, 'float', 'Decay')
				plugin_obj.params.add_named('ext_param_7', 0, 'float', 'Release')
				plugin_obj.params.add_named('ext_param_26', 0.63, 'float', 'Body hue')
				return True

		# ---------------------------------------- Harmless ----------------------------------------
		elif flpluginname == 'harmless' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Harmless', 'Image-Line')
			if plugin_vst2.check_exists('id', 1229484653):
				extpluglog.extpluglist.success('FL Studio', 'Harmless')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229484653, 'chunk', make_flvst2(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Harmless')
				param_auto(convproj_obj, pluginid, plugin_obj, 'harmless')
				return True

		# ---------------------------------------- Harmor ----------------------------------------
		elif flpluginname == 'harmor' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Harmor', 'Image-Line')
			if plugin_vst2.check_exists('id', 1229483375):
				extpluglog.extpluglist.success('FL Studio', 'Harmor')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229483375, 'chunk', make_flvst2(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Harmor')
				return True

		# ---------------------------------------- morphine ----------------------------------------
		elif flpluginname == 'morphine' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Morphine', 'Image-Line')
			if plugin_vst2.check_exists('id', 1299149382):
				extpluglog.extpluglist.success('FL Studio', 'Morphine')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1299149382, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Morphine')
				return True

		# ---------------------------------------- poizone ----------------------------------------
		elif flpluginname == 'poizone' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'PoiZone', 'Image-Line')
			if plugin_vst2.check_exists('id', 1398893394):
				extpluglog.extpluglist.success('FL Studio', 'PoiZone')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398896471, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'PoiZone')
				return True

		# ---------------------------------------- sakura ----------------------------------------
		elif flpluginname == 'sakura' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Sakura', 'Image-Line')
			if plugin_vst2.check_exists('id', 1398893394):
				extpluglog.extpluglist.success('FL Studio', 'Sakura')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398893394, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Sakura')
				return True

		# ---------------------------------------- sawer ----------------------------------------
		elif flpluginname == 'sawer' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Sawer', 'Image-Line')
			if plugin_vst2.check_exists('id', 1398888274):
				extpluglog.extpluglist.success('FL Studio', 'Sawer')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1398888274, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Sawer')
				return True

		# ---------------------------------------- Sytrus ----------------------------------------
		elif flpluginname == 'sytrus' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Sytrus', 'Image-Line')
			if plugin_vst2.check_exists('id', 1400468594):
				extpluglog.extpluglist.success('FL Studio', 'Sytrus')
				fldata = params_nf_image_line.imageline_vststate()
				fldata.state_data = plugin_obj.rawdata_get('fl')
				fldata.otherp1_data[1] = 19
				fldata.otherp1_data[1] = 18
				fldata.startchunk_data = b'd\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xffg\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00M\x03\x00\x00\xc2\x01\x00\x00h\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
				fldata.headertype = 4

				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1400468594, 'chunk', fldata.write(), None)
				plugin_obj.datavals_global.add('name', 'Sytrus')

				param_auto(convproj_obj, pluginid, plugin_obj, 'sytrus')
				return True

		# ---------------------------------------- Toxic Biohazard ----------------------------------------
		elif flpluginname == 'toxic biohazard' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Toxic Biohazard', 'Image-Line')
			if plugin_vst2.check_exists('id', 1416591412):
				extpluglog.extpluglist.success('FL Studio', 'Toxic Biohazard')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1416591412, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'Toxic Biohazard')
				return True

		# ---------------------------------------- equo ----------------------------------------
		elif flpluginname == 'equo' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL EQUO', 'Image-Line')
			if plugin_vst2.check_exists('id', 1162958159):
				extpluglog.extpluglist.success('FL Studio', 'EQUO')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1162958159, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL EQUO')
				return True

		# ---------------------------------------- fruity delay 2 ----------------------------------------
		elif flpluginname == 'fruity delay 2' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Delay', 'Image-Line')
			if plugin_vst2.check_exists('id', 1178874454):
				extpluglog.extpluglist.success('FL Studio', 'Delay')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1178874454, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Delay')
				param_auto(convproj_obj, pluginid, plugin_obj, 'fruity delay 2')
				return True

		# ---------------------------------------- fruity delay bank ----------------------------------------
		elif flpluginname == 'fruity delay bank' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Delay Bank', 'Image-Line')
			if plugin_vst2.check_exists('id', 1147945582):
				extpluglog.extpluglist.success('FL Studio', 'Delay Bank')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1147945582, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Delay Bank')
				return True

		# ---------------------------------------- fruity delay 2 ----------------------------------------
		elif flpluginname == 'fruity flangus' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Flangus', 'Image-Line')
			if plugin_vst2.check_exists('id', 1181509491):
				extpluglog.extpluglist.success('FL Studio', 'Flangus')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1181509491, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Flangus')
				param_auto(convproj_obj, pluginid, plugin_obj, 'flangus')
				return True

		# ---------------------------------------- fruity love philter ----------------------------------------
		elif flpluginname == 'fruity love philter' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Love Philter', 'Image-Line')
			if plugin_vst2.check_exists('id', 1229737040):
				extpluglog.extpluglist.success('FL Studio', 'Love Philter')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229737040, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Love Philter')
				return True

		# ---------------------------------------- multiband compressor ----------------------------------------
		elif flpluginname == 'fruity multiband compressor' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Multiband Compressor', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179476547):
				extpluglog.extpluglist.success('FL Studio', 'Multiband Compressor')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179476547, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Multiband Compressor')
				return True

		# ---------------------------------------- gross beat ----------------------------------------
		elif flpluginname == 'gross beat' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Gross Beat', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179545410):
				extpluglog.extpluglist.success('FL Studio', 'Gross Beat')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229406821, 'chunk', make_flvst2(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Gross Beat')
				param_auto(convproj_obj, pluginid, plugin_obj, 'gross beat')
				return True

		# ---------------------------------------- hardcore ----------------------------------------
		elif flpluginname == 'hardcore' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Hardcore', 'Image-Line')
			if plugin_vst2.check_exists('id', 1212371505):
				extpluglog.extpluglist.success('FL Studio', 'Hardcore')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1212371505, 'chunk', make_sslf(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Hardcore')
				param_auto(convproj_obj, pluginid, plugin_obj, 'hardcore')
				return True

		# ---------------------------------------- maximus ----------------------------------------
		elif flpluginname == 'maximus' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Maximus', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179545410):
				extpluglog.extpluglist.success('FL Studio', 'Maximus')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229807992, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Maximus')
				param_auto(convproj_obj, pluginid, plugin_obj, 'maximus')
				return True

		# ---------------------------------------- notebook ----------------------------------------
		elif flpluginname == 'fruity notebook' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Notebook', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179545410):
				extpluglog.extpluglist.success('FL Studio', 'Notebook')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179545410, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Notebook')
				return True

		# ---------------------------------------- parametric eq ----------------------------------------
		elif flpluginname == 'fruity parametric eq' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Parametric EQ', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179665750):
				extpluglog.extpluglist.success('FL Studio', 'Parametric EQ')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179665750, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Parametric EQ')
				return True

		# ---------------------------------------- parametric eq 2 ----------------------------------------
		elif flpluginname == 'fruity parametric eq 2' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Parametric EQ 2', 'Image-Line')
			if plugin_vst2.check_exists('id', 1346720050):
				extpluglog.extpluglist.success('FL Studio', 'Parametric EQ 2')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1346720050, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Parametric EQ 2')
				return True

		# ---------------------------------------- fruity spectroman ----------------------------------------
		elif flpluginname == 'fruity spectroman' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Spectroman', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179873357):
				extpluglog.extpluglist.success('FL Studio', 'Spectroman')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179873357, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Spectroman')
				return True

		# ---------------------------------------- fruity stereo enhancer ----------------------------------------
		elif flpluginname == 'fruity stereo enhancer' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Stereo Enhancer', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179862358):
				extpluglog.extpluglist.success('FL Studio', 'Stereo Enhancer')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179862358, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Stereo Enhancer')
				return True

		# ---------------------------------------- fruity vocoder ----------------------------------------
		elif flpluginname == 'fruity vocoder' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Vocoder', 'Image-Line')
			if plugin_vst2.check_exists('id', 1179407983):
				extpluglog.extpluglist.success('FL Studio', 'Vocoder')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1179407983, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Vocoder')
				return True

		# ---------------------------------------- fruity waveshaper ----------------------------------------
		#elif flpluginname == 'fruity waveshaper':
		#	if plugin_vst2.check_exists('id', 1229739891):
		#		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229739891, 'chunk', make_flvst1(plugin_obj), None)
		#	else: 
		#		extpluglog.printerr('ext_notfound', ['Shareware VST2', 'IL Waveshaper'])

		# ---------------------------------------- wave candy ----------------------------------------
		elif flpluginname == 'wave candy' and use_vst2:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'IL Wave Candy', 'Image-Line')
			if plugin_vst2.check_exists('id', 1229748067):
				extpluglog.extpluglist.success('FL Studio', 'Wave Candy')
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', 1229748067, 'chunk', make_flvst1(plugin_obj), None)
				plugin_obj.datavals_global.add('name', 'IL Wave Candy')
				param_auto(convproj_obj, pluginid, plugin_obj, 'wave candy')
				return True
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import base64
from functions import data_bytes
from functions import data_values
from objects.data_bytes import bytewriter

import logging
logger_output = logging.getLogger('output')

def wrapper_addchunk(wrapper_data, chunkid, chunkdata):
	wrapper_data.uint32(chunkid)
	wrapper_data.uint32(len(chunkdata))
	wrapper_data.uint32(0)
	wrapper_data.raw(chunkdata)

def wrapper_addchunk_plugtype(wrapper_data, chunkid, plugtype, chunkdata):
	wrapper_data.uint32(chunkid)
	wrapper_data.uint32(len(chunkdata)+4)
	wrapper_data.uint32(0)
	wrapper_data.uint32(plugtype)
	wrapper_data.raw(chunkdata)

	#print('O< ', chunkid, chunkdata[0:100])

def setparams(convproj_obj, plugin_obj):
	fl_plugin = None
	fl_pluginparams = None
	plug_type = plugin_obj.type_get()

	bytesout = bytewriter.bytewriter()

	if plugin_obj.check_wildmatch('universal', 'sampler', 'slicer'):
		fl_plugin = 'fruity slicer'

		sre_obj = plugin_obj.samplepart_get('sample')
		ref_found, sampleref_obj = convproj_obj.sampleref__get(sre_obj.sampleref)

		slicer_beats = plugin_obj.datavals.get('beats', 4)
		slicer_bpm = plugin_obj.datavals.get('bpm', 4)
		slicer_pitch = int(sre_obj.pitch*100)
		slicer_fitlen = int(math.log2(1/sre_obj.stretch.calc_real_speed)*10000)
		slicer_att = plugin_obj.datavals.get('fade_in', 4)
		slicer_dec = plugin_obj.datavals.get('fade_out', 4)
		
		if sre_obj.stretch.algorithm == 'elastique_pro': 
			if sre_obj.stretch.algorithm_mode == 'transient': slicer_stretchtype = 3
			else: slicer_stretchtype = 2
		elif sre_obj.stretch.algorithm == 'elastique_v2': 
			if sre_obj.stretch.algorithm_mode == 'tonal': slicer_stretchtype = 5
			elif sre_obj.stretch.algorithm_mode == 'mono': slicer_stretchtype = 6
			elif sre_obj.stretch.algorithm_mode == 'speech': slicer_stretchtype = 7
			else: slicer_stretchtype = 4
		else:
			slicer_stretchtype = 0

		bytesout.int32(15)
		bytesout.float(slicer_beats)
		bytesout.float(slicer_bpm)
		bytesout.int32(slicer_pitch)
		bytesout.int32(slicer_fitlen)
		bytesout.int32(slicer_stretchtype)
		bytesout.int32(slicer_att)
		bytesout.int32(slicer_dec)
		bytesout.c_string__int8__nonull(sre_obj.get_filepath(convproj_obj, 'win'))

		bytesout.uint32(len(sre_obj.slicer_slices))
		for slice_obj in sre_obj.slicer_slices:
			bytesout.c_string__int8__nonull(slice_obj.name)
			bytesout.uint32(int(slice_obj.start//(sampleref_obj.channels/2)))
			bytesout.int32(slice_obj.custom_key+60 if slice_obj.is_custom_key else -1)
			bytesout.uint16(0)
			bytesout.uint8(128)
			bytesout.uint8(191)
			bytesout.bool8(slice_obj.reverse)

		slicer_animate = plugin_obj.viscustom_get('animate', False)
		slicer_starting_key = sre_obj.slicer_start_key+60
		slicer_play_to_end = plugin_obj.datavals.get('play_to_end', 0)
		slicer_bitrate = 44100
		slicer_auto_dump = plugin_obj.datavals.get('auto_dump', 0)
		slicer_declick = plugin_obj.datavals.get('declick', 0)
		slicer_auto_fit = plugin_obj.datavals.get('auto_fit', 0)
		slicer_view_spectrum = plugin_obj.viscustom_get('spectrum', False)

		bytesout.bool8(slicer_animate)
		bytesout.uint32(slicer_starting_key)
		bytesout.bool8(slicer_play_to_end)
		bytesout.uint32(slicer_bitrate)
		bytesout.bool8(slicer_auto_dump)
		bytesout.bool8(slicer_declick)
		bytesout.bool8(slicer_auto_fit)
		bytesout.bool32(slicer_view_spectrum)

		fl_pluginparams = bytesout.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity html notebook'):
		fl_plugin = 'fruity html notebook'
		bytesout.uint32(1)
		bytesout.c_string__int8__nonull(plugin_obj.datavals.get('url', ''))
		fl_pluginparams = bytesout.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity notebook'):
		fl_plugin = 'fruity notebook'
		bytesout.uint32(1000)
		bytesout.uint32(plugin_obj.datavals.get('currentpage', 0))
		pagedata = plugin_obj.datavals.get('pages', {})
		for pagenum, pagebin in pagedata.items():
			bytesout.int32(pagenum)
			bytesout.c_string__int32__nonull(pagebin)
		bytesout.int32(-1)
		bytesout.int8(plugin_obj.datavals.get('editing_enabled', 0))
		fl_pluginparams = bytesout.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity notebook 2'):
		fl_plugin = 'fruity notebook 2'
		bytesout.uint32(0)
		bytesout.uint32(plugin_obj.datavals.get('currentpage', 0))
		pagedata = plugin_obj.datavals.get('pages', {})
		for pagenum, pagebin in pagedata.items():
			bytesout.int32(pagenum)
			bytesout.varint(len(pagebin*2))
			bytesout.c_string__varint__nonull(pagebin, encoding='utf-16le')
		bytesout.int32(-1)
		bytesout.int8(plugin_obj.datavals.get('editing_enabled', 0))
		fl_pluginparams = bytesout.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', 'fruity vocoder'):
		fl_plugin = 'fruity vocoder'
		p_bands = plugin_obj.array_get('bands', 4)
		p_filter = plugin_obj.datavals.get('filter', 2)
		p_left_right = plugin_obj.datavals.get('left_right', 0)

		p_freq_min = plugin_obj.params.get('freq_min', 0).value
		p_freq_max = plugin_obj.params.get('freq_max', 65536).value
		p_freq_scale = plugin_obj.params.get('freq_scale', 64).value
		p_freq_invert = int(plugin_obj.params.get('freq_invert', 0).value)
		p_freq_formant = plugin_obj.params.get('freq_formant', 0).value
		p_freq_bandwidth = plugin_obj.params.get('freq_bandwidth', 50).value
		p_env_att = plugin_obj.params.get('env_att', 1000).value
		p_env_rel = plugin_obj.params.get('env_rel', 100).value
		p_mix_mod = plugin_obj.params.get('mix_mod', 0).value
		p_mix_car = plugin_obj.params.get('mix_car', 0).value
		p_mix_wet = plugin_obj.params.get('mix_wet', 128).value

		bytesout.uint32(2)
		bytesout.uint32(len(p_bands))
		bytesout.uint32(p_filter)
		bytesout.uint32(2)
		bytesout.uint8(p_left_right)

		bytesout.l_float(p_bands, len(p_bands))
		
		bytesout.uint32(p_freq_min)
		bytesout.uint32(p_freq_max)
		bytesout.uint32(p_freq_scale)
		bytesout.uint32(p_freq_invert)
		bytesout.uint32(p_freq_formant)
		bytesout.uint32(p_freq_bandwidth)

		bytesout.uint32(p_env_att)
		bytesout.uint32(p_env_rel)
		bytesout.uint32(0)
		bytesout.uint32(p_mix_mod)
		bytesout.uint32(p_mix_car)
		bytesout.uint32(p_mix_wet)

		fl_pluginparams = bytesout.getvalue()

	if plugin_obj.check_wildmatch('native', 'flstudio', None):
		outbytes = plugin_obj.to_bytes('fl_studio', 'fl_studio', 'plugin', plug_type[1], None)

		if outbytes:
			fl_plugin = plug_type[1]
			fl_pluginparams = outbytes
		else:
			fl_pluginparams = plugin_obj.rawdata_get('fl')

	if plugin_obj.check_wildmatch('universal', 'soundfont2', None):
		fl_plugin = 'fruity soundfont player'

		asdr_vol = plugin_obj.env_asdr_get('vol')
		lfo_pitch = plugin_obj.lfo_get('pitch')

		ref_found, fileref_obj = plugin_obj.fileref__get('file', convproj_obj)
		sf2_file = fileref_obj.get_path('win', False) if ref_found else ''
		sf2_bank, sf2_patch = plugin_obj.midi.to_sf2()

		flsf_lfo_predelay = int(lfo_pitch.predelay*256) if lfo_pitch.predelay != 0 else -1
		flsf_lfo_amount = int(lfo_pitch.amount*128) if lfo_pitch.amount != 0 else -1
		flsf_lfo_speed = int(6/lfo_pitch.time.speed_seconds)

		if asdr_vol.amount == 0: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = -1, -1, -1, -1
		else: flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = int(asdr_vol.attack/1024), int(asdr_vol.decay/1024), int(asdr_vol.sustain/127), int(asdr_vol.release/1024)

		fl_pluginparams = b''
		fl_pluginparams += struct.pack('iiiiii', *(2, sf2_patch+1, sf2_bank, 128, 128, 0) )
		fl_pluginparams += struct.pack('iiii', *(flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R) )
		fl_pluginparams += struct.pack('iiii', *(flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, -1) )
		fl_pluginparams += len(sf2_file).to_bytes(1, "little")
		fl_pluginparams += sf2_file.encode('utf-8')
		fl_pluginparams += b'\xff\xff\xff\xff\x00\xff\xff\xff\xff\x00\x00'

	if plugin_obj.check_wildmatch('external', 'vst2', None):
		vst_numparams = plugin_obj.datavals_global.get('numparams', 0)
		vst_current_program = plugin_obj.current_program
		vst_use_program = plugin_obj.program_used
		vst_datatype = plugin_obj.datavals_global.get('datatype', 'chunk')
		vst_fourid = plugin_obj.datavals_global.get('fourid', 0)
		vst_name = plugin_obj.datavals_global.get('name', None)

		ref_found, fileref_obj = plugin_obj.fileref__get_global('plugin', convproj_obj)
		vst_path = fileref_obj.get_path('win', False) if ref_found else None

		isvalid = True
		if vst_fourid:
			if vst_name or vst_path:
				if vst_datatype in ['chunk', 'param']:
					isvalid = True
				else:
					logger_output.warning('VST2 plugin not placed: unknown datatype:', vst_datatype)
			else:
				logger_output.warning('VST2 plugin not placed: name or file path not found.')
		else:
			logger_output.warning('VST2 plugin not placed: no ID '+('for "'+vst_name+'" found.' if vst_name else "found."))

		if isvalid:
			vstdata_bytes = plugin_obj.rawdata_get('chunk')

			wrapper_state = bytewriter.bytewriter()

			if vst_datatype == 'chunk':
				if vst_use_program:
					wrapper_state.raw(b'\xf7\xff\xff\xff\r\xfe\xff\xff\xff')
					wrapper_state.uint32(len(vstdata_bytes))
					wrapper_state.raw(b'\x00\x00\x00\x00')
					wrapper_state.uint32(vst_current_program)
					wrapper_state.raw(vstdata_bytes)
				else:
					wrapper_state.raw(b'\xf7\xff\xff\xff\x0c\xfe\xff\xff\xff')
					wrapper_state.uint32(len(vstdata_bytes))
					wrapper_state.raw(b'\x00\x00\x00\x00\x00\x00\x00\x00')
					wrapper_state.raw(vstdata_bytes)

			if vst_datatype == 'param':
				prognums = list(plugin_obj.programs)
				prognum = prognums.index(plugin_obj.current_program) if plugin_obj.current_program in prognums else 0
	
				wrapper_state.raw(b'\xf7\xff\xff\xff\x05\xfe\xff\xff\xff')
				wrapper_state.raw(b'\x00\x00\x00\x00')
				wrapper_state.raw(b'\x00\x00\x00\x00')
				wrapper_state.uint32(prognum)
	
				vst_total_params = 0
				vst_num_names = len(plugin_obj.programs)
				vst_params_data = bytewriter.bytewriter()
				vst_names = bytewriter.bytewriter()
	
				for _, progstate in plugin_obj.programs.items():
					vst_total_params += vst_numparams
					for num in range(vst_numparams):
						paramval = progstate.params.get('ext_param_'+str(num), 0).value
						vst_params_data.float(paramval)
					vst_names.string(progstate.preset.name, 25)
	
				wrapper_state.uint32(vst_total_params)
				wrapper_state.raw(vst_params_data.getvalue())
				wrapper_state.uint32(vst_num_names)
				wrapper_state.raw(vst_names.getvalue())
	
			wrapper_data = bytewriter.bytewriter()
			wrapper_data.raw(b'\n\x00\x00\x00')
			wrapper_addchunk_plugtype(wrapper_data, 50, 4 if plugin_obj.role == 'synth' else 0, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
			if vst_fourid != None: wrapper_addchunk(wrapper_data, 51, vst_fourid.to_bytes(4, "little") )
			wrapper_addchunk(wrapper_data, 57, b'`\t\x00\x00' )
			if vst_name != None: wrapper_addchunk(wrapper_data, 54, vst_name.encode() )
			if vst_path != None: wrapper_addchunk(wrapper_data, 55, vst_path.encode() )

			wrapper_addchunk(wrapper_data, 53, wrapper_state.getvalue())
			fl_plugin = 'fruity wrapper'
			fl_pluginparams = wrapper_data.getvalue()

	#if plug_type[0] == 'vst3':
	#	vst_chunk = plugin_obj.rawdata_get('chunk')
	#	vst_id = plugin_obj.datavals.get('id', None)
	#	vst_name = plugin_obj.datavals.get('name', None)
	#	vst_path = plugin_obj.datavals.get('path', None)
	#	vst_numparams = plugin_obj.datavals.get('numparams', None)

	#	if vst_numparams != None:
	#		wrapper_state = b'\x01\x00\x00\x00\x01\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	#		wrapper_state += wrapper_addchunk(3, vst_chunk)

	#		fourchunkdata = vst_numparams.to_bytes(4, "little")
	#		for paramnum in range(vst_numparams):
	#			fourchunkdata += paramnum.to_bytes(4, "little")

	#		wrapper_state += wrapper_addchunk(4, fourchunkdata)
	#		wrapper_data = b'\n\x00\x00\x00'

	##		print(54, vst_name.encode())
	##		print(55, vst_path.encode())

	#		if vst_name != None: wrapper_data += wrapper_addchunk(54, vst_name.encode() )
	#		if vst_path != None: wrapper_data += wrapper_addchunk(55, vst_path.encode() )

	#		wrapper_data += wrapper_addchunk(53, wrapper_state )
	#		#print(wrapper_state.hex())
	#		fl_plugin = 'fruity wrapper'
	#		fl_pluginparams = wrapper_data

	#print(fl_pluginparams)

	return fl_plugin, fl_pluginparams
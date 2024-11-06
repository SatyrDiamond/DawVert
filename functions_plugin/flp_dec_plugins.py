# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math
import varint
from functions import data_values
from objects import globalstore
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_clap
from functions_plugin_ext import plugin_vst3
from io import BytesIO
from objects.file import audio_wav
from objects.data_bytes import bytereader

DEBUGSTUFF = False

def get_sample(i_value):
	if i_value != None:
		if i_value[0:21] == "%FLStudioFactoryData%":
			restpath = i_value[21:]
			return restpath
		elif i_value[0:18] == "%FLStudioUserData%":
			restpath = i_value[18:]
			return restpath
		elif i_value[0:13] == "%USERPROFILE%":
			restpath = i_value[13:]
			return restpath
		else:
			return i_value
	else:
		return ''

def decode_sslf(fl_plugstr):
	header = fl_plugstr.read(4)
	out = b''
	if header == b'SSLF':
		size = fl_plugstr.uint32()
		out = fl_plugstr.read(size)
	return out

def simsynth_time(value): return pow(value*2, 3)/2

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

ss_envvol_mul = 7
ss_envsvf_mul = 7

envshapes = {
	0: 'normal',
	1: 'doublecurve',
	2: 'instant',
	3: 'stairs',
	4: 'smooth_stairs',
	5: 'pulse',
	6: 'wave',
	7: 'curve2',
	8: 'doublecurve2',
	9: 'halfsine',
	10: 'smooth',
	11: 'curve3',
	12: 'doublecurve3',
}

def getparams(convproj_obj, pluginid, flplugin, foldername, zipfile):
	fl_plugstr = bytereader.bytereader()
	fl_plugstr.load_raw(flplugin.params if flplugin.params else b'')
	flplugin.name = flplugin.name.lower()

	plugin_obj = convproj_obj.add_plugin(pluginid, 'native', 'flstudio', flplugin.name)

	windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
	windata_obj.pos_x = flplugin.window_p_x
	windata_obj.pos_y = flplugin.window_p_y
	windata_obj.size_x = flplugin.window_s_x
	windata_obj.size_y = flplugin.window_s_y
	windata_obj.open = bool(flplugin.visible)
	windata_obj.detatched = bool(flplugin.detached)

	# ------------------------------------------------------------------------------------------- VST
	if flplugin.name == 'fruity wrapper':
		fl_plugstr.skip(4)

		wrapperdata = {}
		while fl_plugstr.tell() < fl_plugstr.end:
			chunktype = fl_plugstr.uint32()
			chunksize = fl_plugstr.uint32()
			fl_plugstr.skip(4)

			if chunktype == 50: 
				wrapperdata['plugin_info'] = [fl_plugstr.uint32(), fl_plugstr.raw(chunksize-4)]
			else:
				chunkdata = fl_plugstr.raw(chunksize)
				if chunktype == 1: wrapperdata['midi'] = chunkdata
				elif chunktype == 2: wrapperdata['flags'] = chunkdata
				elif chunktype == 30: wrapperdata['io'] = chunkdata
				elif chunktype == 32: wrapperdata['outputs'] = chunkdata
				elif chunktype == 51: wrapperdata['fourid'] = int.from_bytes(chunkdata, "little")
				elif chunktype == 52: wrapperdata['16id'] = chunkdata
				elif chunktype == 53: wrapperdata['state'] = chunkdata
				elif chunktype == 54: wrapperdata['name'] = chunkdata.decode()
				elif chunktype == 55: wrapperdata['file'] = chunkdata.decode()
				elif chunktype == 56: wrapperdata['vendor'] = chunkdata.decode()
				elif chunktype == 57: wrapperdata['57'] = chunkdata
				elif chunktype == 58: wrapperdata['clapid'] = chunkdata.decode()
				#else: print(chunktype, chunkdata)

			#print(' >I', chunktype, chunkdata[0:100])

		if 'plugin_info' in wrapperdata:

			wrapper_vsttype = wrapperdata['plugin_info'][0]

			#print(wrapper_vsttype, wrapperdata['name'])

			if wrapper_vsttype in [4,0]:
				if wrapper_vsttype == 0: plugin_obj.role == 'fx'
				if wrapper_vsttype == 4: plugin_obj.role == 'synth'
				plugin_obj.type_set('external', 'vst2', 'win')
				pluginstate = wrapperdata['state']
				wrapper_vststate = pluginstate[0:9]
				wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
				wrapper_vstpad = pluginstate[13:17]
				wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
				wrapper_vstdata = pluginstate[21:]
				if 'fourid' in wrapperdata: plugin_obj.datavals_global.add('id', wrapperdata['fourid'])
				if 'name' in wrapperdata: plugin_obj.datavals_global.add('name', wrapperdata['name'])

				if wrapper_vststate[0:4] == b'\xf7\xff\xff\xff' and wrapper_vststate[5:9] == b'\xfe\xff\xff\xff':

					if wrapper_vststate[4] in [13, 12]:
						plugin_obj.clear_prog_keep(wrapper_vstprogram)
						plugin_obj.rawdata_add('chunk', wrapper_vstdata)

						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id' ,'win', wrapperdata['fourid'], 'chunk', wrapper_vstdata, None)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name' ,'win', wrapperdata['name'], 'chunk', wrapper_vstdata, None)

						numparams = plugin_obj.datavals_global.get('numparams', -1) 

						plugin_obj.datavals_global.add('all_params_used', False)

					if wrapper_vststate[4] in [5, 4]:
						stream_data = bytereader.bytereader()
						stream_data.load_raw(wrapper_vstdata)
						vst_total_params = stream_data.uint32()
						vst_params_data = stream_data.l_float(vst_total_params)
						vst_num_names = stream_data.uint32()
						vst_names = []
						for _ in range(vst_num_names):
							vst_names.append(stream_data.string(25, encoding='utf-8'))

						numparamseach = vst_total_params//vst_num_names
						bankparams = data_values.list__chunks(vst_params_data, numparamseach)

						plugin_obj.clear_prog_keep(0)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id' ,'win', wrapperdata['fourid'], 'param', None, numparamseach)

						for num in range(vst_num_names):
							plugin_obj.set_program(num)
							plugin_obj.preset.name = vst_names[num]
							for paramnum in range(numparamseach): 
								plugin_obj.params.add('ext_param_'+str(paramnum), bankparams[num][paramnum], 'float')

						plugin_obj.datavals_global.add('all_params_used', True)
						plugin_obj.set_program(wrapper_vstprogram)

			if wrapper_vsttype in [12,11] and 'state' in wrapperdata:
				plugin_obj.type_set('external', 'clap', 'win')
				pluginstate = wrapperdata['state']

				if wrapper_vsttype == 11: plugin_obj.role == 'fx'
				if wrapper_vsttype == 12: plugin_obj.role == 'synth'

				wrapper_vstdata = pluginstate[4:]

				if 'clapid' in wrapperdata: 
					plugin_clap.replace_data(convproj_obj, plugin_obj, 'id', None, wrapperdata['clapid'], wrapper_vstdata)
					if 'name' in wrapperdata: plugin_obj.datavals_global.add('name', wrapperdata['name'])
				elif 'name' in wrapperdata: 
					plugin_clap.replace_data(convproj_obj, plugin_obj, 'name', None, wrapperdata['name'], wrapper_vstdata)

			#if wrapper_vsttype in [8,7] and 'state' in wrapperdata:
			#	plugin_obj.type_set('external', 'vst3', 'win')
			#	pluginstate = wrapperdata['state']
#
			#	if wrapper_vsttype == 7: plugin_obj.role == 'fx'
			#	if wrapper_vsttype == 8: plugin_obj.role == 'synth'
#
			#	if 'name' in wrapperdata: 
			#		#plugin_vst3.replace_data(convproj_obj, plugin_obj, 'name', None, wrapperdata['name'], wrapper_vstdata)
#
			#		pluginstate_str = BytesIO(pluginstate)
			#		vststatedata = {}
#
			#		while pluginstate_str.tell() < len(pluginstate):
			#			chunktype = int.from_bytes(pluginstate_str.read(4), 'little')
			#			chunksize = int.from_bytes(pluginstate_str.read(4), 'little')
			#			pluginstate_str.read(4)
			#			chunkdata = pluginstate_str.read(chunksize)
			#			vststatedata[chunktype] = chunkdata
#
			#		print(vststatedata)

					#somedata = BytesIO(vststatedata[4])
					#somedata_num = int.from_bytes(somedata.read(4), 'little')

	# ------------------------------------------------------------------------------------------- Inst

	elif flplugin.name in ['fruity soundfont player', 'soundfont player']:
		flsf_vers = fl_plugstr.uint32()
		flsf_patch = fl_plugstr.uint32()
		flsf_bank = fl_plugstr.uint32()
		flsf_reverb_sendlvl = fl_plugstr.uint32()
		flsf_chorus_sendlvl = fl_plugstr.uint32()
		flsf_mod = fl_plugstr.uint32()

		flsf_asdf_A = fl_plugstr.uint32()
		flsf_asdf_D = fl_plugstr.uint32()
		flsf_asdf_S = fl_plugstr.uint32()
		flsf_asdf_R = fl_plugstr.uint32()

		flsf_lfo_predelay = fl_plugstr.int32()
		flsf_lfo_amount = fl_plugstr.int32()
		flsf_lfo_speed = fl_plugstr.int32()
		flsf_cutoff = fl_plugstr.uint32()

		flsf_filename = fl_plugstr.c_string__int8(encoding='utf-8')

		flsf_filename = get_sample(flsf_filename)

		flsf_reverb_sendto = fl_plugstr.uint32()
		flsf_reverb_builtin = fl_plugstr.uint8()
		flsf_chorus_sendto = fl_plugstr.uint32()
		flsf_chorus_builtin = fl_plugstr.uint8()

		flsf_hqrender = fl_plugstr.uint8()

		plugin_obj.type_set('universal', 'soundfont2', None)

		asdflfo_att = flsf_asdf_A/1024 if flsf_asdf_A != -1 else 0
		asdflfo_dec = flsf_asdf_D/1024 if flsf_asdf_D != -1 else 0
		asdflfo_sus = flsf_asdf_S/127 if flsf_asdf_S != -1 else 1
		asdflfo_rel = flsf_asdf_R/1024 if flsf_asdf_R != -1 else 0
		asdflfo_amt = int( (flsf_asdf_A == flsf_asdf_D == flsf_asdf_S == flsf_asdf_R == -1) == False )

		fileref_obj = convproj_obj.add_fileref(flsf_filename, flsf_filename, 'win')
		
		if zipfile:
			foundnames = [x for x in zipfile.namelist() if fileref_obj.file.basename in x]
			if foundnames:
				zipfile.extract(foundnames[0], path=foldername, pwd=None)
				fileref_obj.set_folder(None, os.path.join(foldername, foundnames[0]), False)

		fileref_obj.search('extracted')
		fileref_obj.search('projectfile')
		fileref_obj.search('factorysamples')

		#print(fileref_obj.get_path('win', False))

		plugin_obj.filerefs['file'] = flsf_filename

		plugin_obj.env_asdr_add('vol', 0, asdflfo_att, 0, asdflfo_dec, asdflfo_sus, asdflfo_rel, asdflfo_amt)
		plugin_obj.midi.from_sf2(flsf_bank, flsf_patch)
		
		pitch_amount = flsf_lfo_amount/128 if flsf_lfo_amount != -128 else 0
		pitch_predelay = flsf_lfo_predelay/256 if flsf_lfo_predelay != -1 else 0
		pitch_speed = 1/(flsf_lfo_speed/6) if flsf_lfo_speed != -1 else 1

		lfo_obj = plugin_obj.lfo_add('pitch')
		lfo_obj.predelay = pitch_predelay
		lfo_obj.time.set_seconds(pitch_speed)
		lfo_obj.amount = pitch_amount

	elif flplugin.name == 'fruity slicer':
		plugin_obj.type_set('universal', 'sampler', 'slicer')
		slicer_version = fl_plugstr.int32()
		slicer_beats = fl_plugstr.float()
		slicer_bpm = fl_plugstr.float()
		slicer_pitch = fl_plugstr.int32()
		slicer_fitlen = fl_plugstr.int32()
		slicer_stretchtype = fl_plugstr.int32()
		slicer_att = fl_plugstr.int32()
		slicer_dec = fl_plugstr.int32()

		slicer_filename = fl_plugstr.c_string__int8(encoding='utf-8')
		slicechannels = 2

		slicer_filename = get_sample(slicer_filename)

		stretch_multiplier = pow(2, slicer_fitlen/10000)

		sre_obj = plugin_obj.samplepart_add('sample')

		if slicer_filename != "": 
			sampleref_obj = convproj_obj.add_sampleref(slicer_filename, slicer_filename, 'win')
			if zipfile: sampleref_obj.find_relative('extracted')
			sampleref_obj.find_relative('projectfile')
			sampleref_obj.find_relative('factorysamples')
			slicechannels = sampleref_obj.channels
			sre_obj.from_sampleref(convproj_obj, slicer_filename)

		if slicer_bpm: sre_obj.stretch.set_rate_speed(slicer_bpm, 1/stretch_multiplier, False)
		sre_obj.pitch = slicer_pitch/100

		slicer_numslices = fl_plugstr.uint32()

		for _ in range(slicer_numslices):
			slice_obj = sre_obj.add_slice()
			slice_obj.name = fl_plugstr.c_string__int8(encoding='utf-8')
			slice_obj.start = fl_plugstr.uint32()
			slice_obj.start *= (slicechannels/2)
			custom_key = fl_plugstr.int32()
			if custom_key != -1:
				slice_obj.is_custom_key = True
				slice_obj.custom_key = custom_key-60
			fl_plugstr.skip(4)
			slice_obj.reverse = fl_plugstr.bool8()

		plugin_obj.datavals.add('bpm', slicer_bpm)
		plugin_obj.datavals.add('beats', slicer_beats)
		plugin_obj.datavals.add('fade_in', slicer_att)
		plugin_obj.datavals.add('fade_out', slicer_dec)
		
		if slicer_stretchtype == 2: 
			sre_obj.stretch.algorithm = 'elastique_pro'

		if slicer_stretchtype == 3: 
			sre_obj.stretch.algorithm = 'elastique_pro'
			sre_obj.stretch.algorithm_mode = 'transient'

		if slicer_stretchtype == 4: 
			sre_obj.stretch.algorithm = 'elastique_v2'
			sre_obj.stretch.algorithm_mode = 'transient'

		if slicer_stretchtype == 5: 
			sre_obj.stretch.algorithm = 'elastique_v2'
			sre_obj.stretch.algorithm_mode = 'tonal'

		if slicer_stretchtype == 6: 
			sre_obj.stretch.algorithm = 'elastique_v2'
			sre_obj.stretch.algorithm_mode = 'mono'

		if slicer_stretchtype == 7: 
			sre_obj.stretch.algorithm = 'elastique_v2'
			sre_obj.stretch.algorithm_mode = 'speech'

		slicer_animate = fl_plugstr.bool8()
		slicer_starting_key = fl_plugstr.uint32()
		slicer_play_to_end = fl_plugstr.bool8()
		slicer_bitrate = fl_plugstr.uint32()
		slicer_auto_dump = fl_plugstr.bool8()
		slicer_declick = fl_plugstr.bool8()
		slicer_auto_fit = fl_plugstr.bool8()
		slicer_view_spectrum = fl_plugstr.bool32()

		plugin_obj.viscustom_add('animate', slicer_animate)
		sre_obj.slicer_start_key = slicer_starting_key-60
		plugin_obj.datavals.add('play_to_end', slicer_play_to_end)
		plugin_obj.datavals.add('auto_dump', slicer_auto_dump)
		plugin_obj.datavals.add('declick', slicer_declick)
		plugin_obj.datavals.add('auto_fit', slicer_auto_fit)
		plugin_obj.viscustom_add('spectrum', slicer_view_spectrum)

	# ------------------------------------------------------------------------------------------- FX

	#elif flplugin.name == 'fruity convolver':
	#	try:
	#		fl_plugstr.read(20)
	#		fromstorage = fl_plugstr.int8()
	#		filename = data_bytes.readstring_lenbyte(fl_plugstr, 1, 'little', None)
	#		if fromstorage == 0:
	#			audiosize = fl_plugstr.uint32()
	#			filename = os.path.join(foldername, pluginid+'_custom_audio.wav')
	#			with open(filename, "wb") as customconvolverfile:
	#				customconvolverfile.write(fl_plugstr.read(audiosize))
	#		plugin_obj.type_set('native', 'flstudio', flplugin.name)
	#		plugin_obj.datavals.add('file', filename.decode())
	#		fl_plugstr.read(36)
	#		autodata = {}
	#		for autoname in ['pan', 'vol', 'stereo', 'allpurpose', 'eq']:
	#			autodata_table = decode_pointdata(fl_plugstr)
	#			autopoints_obj = plugin_obj.env_points_add(autoname, 4, True, 'float')
	#			for point in autodata_table:
	#				autopoint_obj = autopoints_obj.add_point()
	#				autopoint_obj.pos = point[0]
	#				autopoint_obj.value = point[1][0]
	#				autopoint_obj.type = envshapes[point[3]]
	#				autopoint_obj.tension = point[2]
	#			autodata[autoname] = autodata_table
	#	except:
	#		pass
		


	elif flplugin.name == 'fruity html notebook':
		plugin_obj.type_set('native', 'flstudio', flplugin.name)
		version = fl_plugstr.uint32()
		if version == 1: plugin_obj.datavals.add('url', fl_plugstr.c_string__int8(encoding='utf-8'))
		

	elif flplugin.name in ['fruity notebook 2', 'fruity notebook']:
		plugin_obj.type_set('native', 'flstudio', flplugin.name)
		version = fl_plugstr.uint32()
		if (version == 0 and flplugin.name == 'fruity notebook 2') or (version == 1000 and flplugin.name == 'fruity notebook'): 
			plugin_obj.datavals.add('currentpage', fl_plugstr.uint32())
			pagesdata = {}
			while True:
				pagenum = fl_plugstr.uint32()
				if pagenum == 0 or pagenum > 100: break
				if flplugin.name == 'fruity notebook 2': 
					length = fl_plugstr.varint()
					text = fl_plugstr.read(length*2).decode('utf-16le')
				if flplugin.name == 'fruity notebook': 
					length = fl_plugstr.uint32()
					text = fl_plugstr.read(length).decode('ascii')
				pagesdata[pagenum] = text
			plugin_obj.datavals.add('pages', pagesdata)
			plugin_obj.datavals.add('editing_enabled', fl_plugstr.int8())
		

	elif flplugin.name == 'fruity vocoder':
		plugin_obj.type_set('native', 'flstudio', flplugin.name)
		voc_version = fl_plugstr.uint32()
		voc_num_bands = fl_plugstr.uint32()
		voc_filter = fl_plugstr.uint32()
		fl_plugstr.skip(4)
		voc_left_right = fl_plugstr.uint8()
		voc_bands = fl_plugstr.l_float(voc_num_bands)

		plugin_obj.array_add('bands', voc_bands)
		plugin_obj.datavals.add('filter', voc_filter)
		plugin_obj.datavals.add('left_right', voc_left_right)

		plugin_obj.params.add_named('freq_min', fl_plugstr.uint32(), 'int', "Freq Min")
		plugin_obj.params.add_named('freq_max', fl_plugstr.uint32(), 'int', "Freq Max")
		plugin_obj.params.add_named('freq_scale', fl_plugstr.uint32(), 'int', "Freq Scale")
		plugin_obj.params.add_named('freq_invert', fl_plugstr.uint32(), 'bool', "Freq Invert")
		plugin_obj.params.add_named('freq_formant', fl_plugstr.uint32(), 'int', "Freq Formant")
		plugin_obj.params.add_named('freq_bandwidth', fl_plugstr.uint32(), 'int', "Freq BandWidth")
		plugin_obj.params.add_named('env_att', fl_plugstr.uint32(), 'int', "Env Att")
		plugin_obj.params.add_named('env_rel', fl_plugstr.uint32(), 'int', "Env Rel")
		fl_plugstr.skip(4)
		plugin_obj.params.add_named('mix_mod', fl_plugstr.uint32(), 'int', "Mix Mod")
		plugin_obj.params.add_named('mix_car', fl_plugstr.uint32(), 'int', "Mix Car")
		plugin_obj.params.add_named('mix_wet', fl_plugstr.uint32(), 'int', "Mix Wet")

	elif flplugin.name == 'fruity waveshaper':
		plugin_obj.type_set('native', 'flstudio', flplugin.name)
		flplugvals = struct.unpack('bHHIIbbbbbb', fl_plugstr.read(22))
		#print(flplugvals)
		plugin_obj.params.add_named('preamp', flplugvals[2], 'int', "Pre Amp")
		plugin_obj.params.add_named('wet', flplugvals[3], 'int', "Wet")
		plugin_obj.params.add_named('postgain', flplugvals[4], 'int', "Post Gain")
		plugin_obj.params.add_named('bipolarmode', flplugvals[5], 'bool', "Bi-polar Mode")
		plugin_obj.params.add_named('removedc', flplugvals[6], 'bool', "Remove DC")

		autodata_table = decode_pointdata(fl_plugstr)

		autopoints_obj = plugin_obj.env_points_add('shape', 4, True, 'float')
		for point in autodata_table:
			autopoint_obj = autopoints_obj.add_point()
			autopoint_obj.pos = point[0]
			autopoint_obj.value = point[1][0]
			autopoint_obj.type = envshapes[point[3]]
			autopoint_obj.tension = point[2]
	
	elif flplugin.name in ['bassdrum', 'pitcher']:
		sslfdata = decode_sslf(fl_plugstr)

		if flplugin.name == 'bassdrum': 
			plugin_obj.type_set('native', 'flstudio', flplugin.name)
			plugin_obj.from_bytes(sslfdata, 'fl_studio', 'fl_studio', 'plugin', flplugin.name, 'sslf_bassdrum')

		if flplugin.name == 'pitcher': 
			plugin_obj.type_set('native', 'flstudio', flplugin.name)
			plugin_obj.from_bytes(sslfdata, 'fl_studio', 'fl_studio', 'plugin', flplugin.name, 'sslf_pitcher')

	elif flplugin.name == 'slicex':
		version = fl_plugstr.l_uint16(2)
		plugin_obj.datavals.add('version', version)
		plugin_obj.params.add('play_pause', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('live_selection', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('master_level', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('master_random_level', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('master_lfo_level', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('master_pitch', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('mod_x', fl_plugstr.int32(), 'int')
		plugin_obj.params.add('mod_y', fl_plugstr.int32(), 'int')
		plugin_obj.datavals.add('layering', fl_plugstr.int32())
		plugin_obj.datavals.add('crossfade', fl_plugstr.int32())
		fl_plugstr.skip(4*11 + 1)
		data_exists = fl_plugstr.int8()
		fl_plugstr.skip(2)
		rawdata = fl_plugstr.raw(4)

		slicex_filename = get_sample(fl_plugstr.c_string__int8())
		wavedata_size = fl_plugstr.int32()
		wavedata = fl_plugstr.raw(wavedata_size)

		plugin_obj.type_set('universal', 'sampler', 'slicer')

		sre_obj = plugin_obj.samplepart_add('sample')

		if not os.path.exists(slicex_filename):
			outfilename = os.path.join(foldername, pluginid+'_custom_audio.wav')
			try:
				with open(outfilename, "wb") as slicexfile: slicexfile.write(wavedata)
			except PermissionError: pass
			sampleref_obj = convproj_obj.add_sampleref(outfilename, outfilename, 'win')
			sre_obj.from_sampleref(convproj_obj, outfilename)
		else:
			sampleref_obj = convproj_obj.add_sampleref(slicex_filename, slicex_filename, 'win')
			sre_obj.from_sampleref(convproj_obj, slicex_filename)

		sampleref_obj.find_relative('extracted')
		sampleref_obj.find_relative('projectfile')
		sampleref_obj.find_relative('factorysamples')

		if not wavedata: 
			if sampleref_obj.fileref.exists(None):
				f = open(sre_obj.get_filepath(convproj_obj, 'win'))
				wavedata = f.read()

		if wavedata:
			wave_obj = audio_wav.wav_main()
			wave_obj.read_bytes(wavedata)
			for num, enudata in enumerate(wave_obj.markers.items()):
				_, marker_obj = enudata
				slice_obj = sre_obj.add_slice()
				slice_obj.start = marker_obj.sampleoffset

	else:
		plugin_obj.type_set('native', 'flstudio', flplugin.name)

		if DEBUGSTUFF:
			print(flplugin.name, flplugin.params.hex())
			fldf = globalstore.datadef.get('fl_studio')
			dfdict = fldf.parse(flplugin.name, flplugin.params)
			for x in dfdict.items():
				print(x)

		dfdict = plugin_obj.from_bytes(flplugin.params, 'fl_studio', 'fl_studio', 'plugin', flplugin.name, None)

		if DEBUGSTUFF:
			plugin_obj.params.debugtxt()

		if dfdict and flplugin.name == 'simsynth':
			try:
				if not False in [(x in dfdict) for x in ('amp_att','amp_dec','amp_sus','amp_rel')]:
					plugin_obj.env_asdr_add('vol', 0, 
						simsynth_time(dfdict['amp_att']), 0, 
						simsynth_time(dfdict['amp_dec']), dfdict['amp_sus'], 
						simsynth_time(dfdict['amp_rel']), 1)

				if not False in [(x in dfdict) for x in ('svf_att','svf_dec','svf_sus','svf_rel')]:
					plugin_obj.env_asdr_add('cutoff', 0, 
						simsynth_time(dfdict['svf_att']), 0, 
						simsynth_time(dfdict['svf_dec']), dfdict['svf_sus'], 
						simsynth_time(dfdict['svf_rel']), 0)
			except:
				pass

		fldso = globalstore.dataset.get_obj('fl_studio', 'plugin', flplugin.name)
		if fldso:
			for param_id, dset_param in fldso.params.iter():
				if dset_param.num != -1:
					#print('FS', flplugin.name, dset_param.num, param_id, dset_param, pluginid)
					convproj_obj.automation.calc(['id_plug_points', pluginid, str(dset_param.num)], 'from_one', dset_param.min, dset_param.max, 0, 0)

					convproj_obj.automation.move(['id_plug', pluginid, str(dset_param.num)], ['plugin',pluginid,param_id])
					convproj_obj.automation.move(['id_plug_points', pluginid, str(dset_param.num)], ['plugin',pluginid,param_id])

		#plugin_obj.params.debugtxt()
		#exit()
	# ------------------------------------------------------------------------------------------- Other

	if plugin_obj.type.type != 'fruity wrapper': plugin_obj.rawdata_add('fl', flplugin.params)
	return plugin_obj
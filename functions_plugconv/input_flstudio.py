# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import os
import math

from functions import note_data
from functions import data_bytes
from functions import plugin_vst2

from functions_plugconv import input_flstudio_wrapper

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def simsynth_time(value): return pow(value*2, 3)
def simsynth_2time(value): return pow(value*2, 3)

temp_count = 0

def convert_inst(instdata):
	global temp_count
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
	fl_plugdata = base64.b64decode(plugindata['data'])
	fl_plugstr = data_bytes.to_bytesio(fl_plugdata)

	# ---------------------------------------- Fruity Slicer ----------------------------------------
	if plugindata['name'].lower() == 'fruity slicer':
		fl_plugstr.read(4)
		slicer_beats = struct.unpack('f', fl_plugstr.read(4))[0]
		slicer_bpm = struct.unpack('f', fl_plugstr.read(4))[0]
		slicer_pitch, slicer_fitlen, slicer_unk1, slicer_att, slicer_dec = struct.unpack('iiiii', fl_plugstr.read(20))

		instdata['plugin'] = "sampler-slicer"
		instdata['plugindata'] = {}

		slicer_filelen = int.from_bytes(fl_plugstr.read(1), "little")
		slicer_filename = fl_plugstr.read(slicer_filelen).decode('utf-8')
		if slicer_filename != "": instdata['plugindata']['file'] = slicer_filename

		slicer_numslices = int.from_bytes(fl_plugstr.read(4), "little")

		cvpj_slices = []
		for _ in range(slicer_numslices):
			sd = {}
			slicer_slicenamelen = int.from_bytes(fl_plugstr.read(1), "little")
			slicer_slicename = fl_plugstr.read(slicer_slicenamelen).decode('utf-8')
			slicer_s_slice = struct.unpack('iihBBB', fl_plugstr.read(13))
			if slicer_slicename != "": sd['file'] = slicer_slicename
			sd['pos'] = slicer_s_slice[0]
			if slicer_s_slice[1] != -1: sd['note'] = slicer_s_slice[1]
			sd['reverse'] = slicer_s_slice[5]
			cvpj_slices.append(sd)

		for slicenum in range(len(cvpj_slices)):
			if slicenum-1 >= 0 and slicenum != len(cvpj_slices): cvpj_slices[slicenum-1]['end'] = cvpj_slices[slicenum]['pos']-1
			if slicenum == len(cvpj_slices)-1: cvpj_slices[slicenum]['end'] = cvpj_slices[slicenum]['pos']+100000000

		instdata['plugindata']['trigger'] = 'oneshot'
		instdata['plugindata']['bpm'] = slicer_bpm
		instdata['plugindata']['beats'] = slicer_beats
		instdata['plugindata']['slices'] = cvpj_slices

	# ---------------------------------------- slicex ----------------------------------------
	#elif plugindata['name'].lower() == 'slicex':
	#	f = open("slicex"+str(temp_count)+".bin", "wb")
	#	f.write(fl_plugstr.read())
	#	temp_count += 1

	# ---------------------------------------- Soundfont Player ----------------------------------------
	elif plugindata['name'].lower() == 'fruity soundfont player':
		# flsf_asdf_A max 5940 - flsf_asdf_D max 5940 - flsf_asdf_S max 127 - flsf_asdf_R max 5940
		# flsf_lfo_predelay max 5900 - flsf_lfo_amount max 127 - flsf_lfo_speed max 127 - flsf_cutoff max 127
		flsf_unk, flsf_patch, flsf_bank, flsf_reverb_sendlvl, flsf_chorus_sendlvl, flsf_mod = struct.unpack('iiiiii', fl_plugstr.read(24))
		flsf_asdf_A, flsf_asdf_D, flsf_asdf_S, flsf_asdf_R = struct.unpack('iiii', fl_plugstr.read(16))
		flsf_lfo_predelay, flsf_lfo_amount, flsf_lfo_speed, flsf_cutoff = struct.unpack('iiii', fl_plugstr.read(16))

		flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
		flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')

		flsf_reverb_sendto, flsf_reverb_builtin = struct.unpack('ib', fl_plugstr.read(5))
		flsf_chorus_sendto, flsf_chorus_builtin = struct.unpack('ib', fl_plugstr.read(5))

		flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

		flsf_patch -= 1

		instdata['plugin'] = "soundfont2"
		instdata['plugindata'] = {}
		if flsf_asdf_A != -1: instdata['plugindata']['attack'] = flsf_asdf_A/1024
		if flsf_asdf_D != -1: instdata['plugindata']['decay'] = flsf_asdf_D/1024
		if flsf_asdf_S != -1: instdata['plugindata']['sustain'] = flsf_asdf_S/127
		if flsf_asdf_R != -1: instdata['plugindata']['release'] = flsf_asdf_R/1024
		instdata['plugindata']['file'] = flsf_filename
		if flsf_patch > 127:
			instdata['plugindata']['bank'] = 128
			instdata['plugindata']['patch'] = flsf_patch-128
		else:
			instdata['plugindata']['bank'] = flsf_bank
			instdata['plugindata']['patch'] = flsf_patch
		
		instdata['plugindata']['asdrlfo'] = {}
		instdata['plugindata']['asdrlfo']['pitch'] = {}
		if flsf_lfo_amount != -128: instdata['plugindata']['asdrlfo']['pitch']['amount'] = flsf_lfo_amount/128
		if flsf_lfo_predelay != -1: instdata['plugindata']['asdrlfo']['pitch']['predelay'] = flsf_lfo_predelay/256
		if flsf_lfo_speed != -1: instdata['plugindata']['asdrlfo']['pitch']['speed'] = 1/(flsf_lfo_speed/6)

	# ---------------------------------------- Wrapper ----------------------------------------
	elif plugindata['name'].lower() == 'fruity wrapper':

		wrapperdata = input_flstudio_wrapper.decode_wrapper(fl_plugstr)

		if 'plugin_info' in wrapperdata:
			wrapper_vsttype = int.from_bytes(wrapperdata['plugin_info'][0:4], "little")

			pluginstate = wrapperdata['state']

			if wrapper_vsttype == 4:
				wrapper_vststate = pluginstate[0:9]
				wrapper_vstsize = int.from_bytes(pluginstate[9:13], "little")
				wrapper_vstpad = pluginstate[13:17]
				wrapper_vstprogram = int.from_bytes(pluginstate[17:21], "little")
				wrapper_vstdata = pluginstate[21:]

				#print(wrapperdata)

				if os.path.exists(wrapperdata['file']):
					instdata['plugin'] = 'vst2-dll'
					instdata['plugindata'] = {}
					instdata['plugindata']['current_program'] = wrapper_vstprogram
					instdata['plugindata']['plugin'] = {}
					instdata['plugindata']['plugin']['name'] = wrapperdata['name']
					instdata['plugindata']['plugin']['path'] = wrapperdata['file']
					instdata['plugindata']['datatype'] = 'chunk'
					instdata['plugindata']['data'] = base64.b64encode(wrapper_vstdata).decode('ascii')
				else:
					plugin_vst2.replace_data(instdata, 'any', wrapperdata['name'], 'chunk', wrapper_vstdata, None)

			#if wrapper_vsttype == 8:
				#wrapper_vststate = pluginstate[0:9]
				#wrapper_vstpad = pluginstate[9:84]
				#wrapper_vstsize = pluginstate[84:92]
				#wrapper_vstdata = pluginstate[92:]
				#print(wrapper_vststate)
				#print(wrapper_vstpad)
				#print(wrapper_vstsize)
				#print(wrapper_vstdata)
				#list_vst.replace_data(instdata, 3, 'any', wrapperdata['name'], 'chunk', wrapper_vstdata, None)

		#fl_plugstr.seek(0)

		#wrapperdata = fl_plugstr.read()

		#temp_count += 1
		#f=open("dataout"+str(temp_count)+".bin", "wb")
		#f.write(wrapperdata)
		#exit()



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

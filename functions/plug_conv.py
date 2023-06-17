# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import struct
import math
import base64
from functions import data_values
from functions import plugin_vst2

from functions_plugparams import params_vital
from functions_plugparams import data_vc2xml
from functions_plugparams import params_various_fx
from functions_plugparams import params_various_inst

from functions_plugconv import input_flstudio
from functions_plugconv import input_pxtone
from functions_plugconv import input_jummbox
from functions_plugconv import input_soundchip
from functions_plugconv import input_audiosauna

from functions_plugconv import output_vst2_simple
from functions_plugconv import output_vst2_sampler
from functions_plugconv import output_vst2_multisampler
from functions_plugconv import output_vst2_slicer

from functions_plugconv import output_vst2_retro
from functions_plugconv import output_vst2_soundchip

from functions_plugconv import output_vst2_flstudio
from functions_plugconv import output_vst2_lmms
from functions_plugconv import output_vst2_onlineseq
from functions_plugconv import output_vst2_piyopiyo
from functions_plugconv import output_vst2_namco163_famistudio

# -------------------- Instruments --------------------
def convplug_inst(instdata, in_daw, out_daw, extra_json, nameid, platform_id):
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			nonfree_flag = data_values.get_value(extra_json, 'nonfree-plugins', '')

			# ---------------------------------------- input ----------------------------------------
			input_soundchip.convert_inst(instdata)
			if pluginname == 'native-fl': input_flstudio.convert_inst(instdata)
			if pluginname == 'native-pxtone': input_pxtone.convert_inst(instdata)
			if pluginname == 'native-jummbox': input_jummbox.convert_inst(instdata)
			if pluginname == 'native-audiosauna': input_audiosauna.convert_inst(instdata)

			# ---------- from general-midi
			elif pluginname == 'general-midi':
				if 'soundfont' in extra_json:
					sffile = extra_json['soundfont']
					gmdata = instdata['plugindata']
					instdata['plugin'] = "soundfont2"
					instdata['plugindata'] = {}
					instdata['plugindata']['bank'] = gmdata['bank']
					instdata['plugindata']['patch'] = gmdata['inst']
					instdata['plugindata']['file'] = sffile
					print('[plug-conv] GM MIDI > soundfont2')
				else:
					print('[plug-conv] Soundfont argument not defined.')

			# ---------------------------------------- output ----------------------------------------
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			replacingdone = None

			if 'vst2' in supportedplugins:
				if pluginname == 'sampler' and 'sampler' not in supportedplugins: 
					replacingdone = output_vst2_sampler.convert_inst(instdata, platform_id)

				if replacingdone == None and pluginname == 'sampler-multi' and 'sampler-multi' not in supportedplugins: 
					replacingdone = output_vst2_multisampler.convert_inst(instdata, platform_id)

				if replacingdone == None and pluginname == 'sampler-slicer' and 'sampler-slicer' not in supportedplugins: 
					replacingdone = output_vst2_slicer.convert_inst(instdata)

				if replacingdone == None and (pluginname == 'native-lmms' or pluginname == 'zynaddsubfx-lmms') and out_daw != 'lmms':
					replacingdone = output_vst2_lmms.convert_inst(instdata) 

				if replacingdone == None and pluginname == 'native-fl':
					replacingdone = output_vst2_flstudio.convert_inst(instdata)

				if replacingdone == None and pluginname == 'native-piyopiyo':
					replacingdone = output_vst2_piyopiyo.convert_inst(instdata)

				if replacingdone == None and pluginname == 'namco163_famistudio':
					replacingdone = output_vst2_namco163_famistudio.convert_inst(instdata)

				if replacingdone == None:
					replacingdone = output_vst2_soundchip.convert_inst(instdata, out_daw)

			# -------------------- vst2 (juicysfplugin) --------------------

			# ---------- from native soundfont2
			elif pluginname == 'soundfont2' and 'sf2' not in supportedplugins:
				sf2data = instdata['plugindata']
				sf2_bank = data_values.get_value(sf2data, 'bank', 0)
				sf2_patch = data_values.get_value(sf2data, 'patch', 0)
				sf2_filename = data_values.get_value(sf2data, 'file', '')
				jsfp_xml = params_various_inst.juicysfplugin_create(sf2_bank, sf2_patch, sf2_filename)
				plugin_vst2.replace_data(instdata, 'any', 'juicysfplugin', 'chunk', data_vc2xml.make(jsfp_xml), None)

# -------------------- FX --------------------
def convplug_fx(fxdata, in_daw, out_daw, extra_json):
	global supportedplugins
	if 'plugin' in fxdata:
		if 'plugindata' in fxdata:
			pluginname = fxdata['plugin']
			plugindata = fxdata['plugindata']

			# ---------------------------------------- input ----------------------------------------
			
			if in_daw == 'flp' and pluginname == 'native-fl': 
				input_flstudio.convert_fx(fxdata)

			# ---------------------------------------- output ----------------------------------------

			replacingdone = None

			if 'vst2' in supportedplugins:
				if pluginname == 'native-simple': 
					replacingdone = output_vst2_simple.convert_fx(fxdata)

				if replacingdone == None and in_daw == 'lmms' and pluginname == 'native-lmms': 
					replacingdone = output_vst2_lmms.convert_fx(fxdata)

				if replacingdone == None and in_daw == 'flp' and pluginname == 'native-fl':
					replacingdone = output_vst2_flstudio.convert_fx(fxdata)

				if replacingdone == None and in_daw == 'onlineseq' and pluginname == 'native-onlineseq':
					replacingdone = output_vst2_onlineseq.convert_fx(fxdata)

			#elif in_daw == 'audiosauna' and pluginname == 'native-audiosauna':
			#	output_audiosauna_vst2.convert_fx(fxdata)



# -------------------- convproj --------------------

def do_inst(track_data, in_daw, out_daw, extra_json, nameid, platform_id):
	if 'instdata' in track_data:
		instdata = track_data['instdata']
		print('[plug-conv] --- Inst: '+nameid)
		convplug_inst(instdata, in_daw, out_daw, extra_json, nameid, platform_id)

def do_fxchain_audio(fxdata, in_daw, out_daw, extra_json, textin):
	if 'chain_fx_audio' in fxdata:
		for fxslot in fxdata['chain_fx_audio']:
			print('[plug-conv] --- FX ('+textin+')')
			convplug_fx(fxslot, in_daw, out_daw, extra_json)

def do_sends(master_data, in_daw, out_daw, extra_json, platform_id, intext):
	if 'sends_audio' in master_data:
		mastersends = master_data['sends_audio']
		for sendid in mastersends:
			do_fxchain_audio(mastersends[sendid], in_daw, out_daw, extra_json,intext+' Send: '+sendid)

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, out_supportedplugins, extra_json):
	global supportedplugins
	supportedplugins = out_supportedplugins
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if 'track_master' in cvpj_l:
			do_sends(cvpj_l['track_master'], in_daw, out_daw, extra_json, platform_id, 'Master')
		if in_type == 'r' or in_type == 'ri':
			if 'track_data' in cvpj_l:
				for track in cvpj_l['track_data']:
					track_data = cvpj_l['track_data'][track]
					if 'type' in track_data:
						if track_data['type'] == 'instrument':
							do_inst(track_data, in_daw, out_daw, extra_json, track, platform_id)
					do_fxchain_audio(track_data, in_daw, out_daw, extra_json,'Track: '+track)
		if in_type == 'm' or in_type == 'mi':
			if 'instruments_data' in cvpj_l:
				for track in cvpj_l['instruments_data']:
					track_data = cvpj_l['instruments_data'][track]
					do_inst(track_data, in_daw, out_daw, extra_json, track, platform_id)
		if 'fxrack' in cvpj_l:
			for fxid in cvpj_l['fxrack']:
				fxiddata = cvpj_l['fxrack'][fxid]
				do_fxchain_audio(fxiddata, in_daw, out_daw, extra_json, 'Send: '+fxid)
		return json.dumps(cvpj_l, indent=2)
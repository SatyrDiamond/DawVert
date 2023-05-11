# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import struct
import math
import base64
from functions import plugin_vst2

from functions_plugparams import params_vital
from functions_plugparams import data_vc2xml
from functions_plugparams import params_various_fx
from functions_plugparams import params_various_inst

from functions_plugconv import input_flstudio
from functions_plugconv import input_pxtone
from functions_plugconv import input_jummbox

from functions_plugconv import output_flstudio_vst2
from functions_plugconv import output_sampler_vst2
from functions_plugconv import output_multisampler_vst2
from functions_plugconv import output_slicer_vst2
from functions_plugconv import output_lmms_vst2
from functions_plugconv import output_retro_vst2
from functions_plugconv import output_onlineseq_vst2
from functions_plugconv import output_soundchip_vst2

# -------------------- Instruments --------------------
def convplug_inst(instdata, in_daw, out_daw, extra_json, nameid, platform_id):
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# ---------------------------------------- input ----------------------------------------
			if in_daw == 'flp' and pluginname == 'native-fl': input_flstudio.convert_inst(instdata)
			if in_daw == 'ptcop' and pluginname == 'native-pxtone': input_pxtone.convert_inst(instdata)
			if in_daw == 'jummbox' and pluginname == 'native-jummbox': input_jummbox.convert_inst(instdata)

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

			output_soundchip_vst2.convert_inst(instdata, out_daw)
			output_retro_vst2.convert_inst(instdata, out_daw)

			if pluginname == 'sampler' and out_daw not in supportedplugins['sampler']: 
				output_sampler_vst2.convert_inst(instdata, platform_id)

			elif pluginname == 'sampler-multi' and out_daw not in supportedplugins['sampler-multi']: 
				output_multisampler_vst2.convert_inst(instdata, platform_id)

			elif pluginname == 'sampler-slicer' and out_daw not in supportedplugins['sampler-slicer']: 
				output_slicer_vst2.convert_inst(instdata)

			elif (pluginname == 'native-lmms' or pluginname == 'zynaddsubfx-lmms') and out_daw != 'lmms':
				output_lmms_vst2.convert_inst(instdata)

			elif pluginname == 'native-fl':
				output_flstudio_vst2.convert_inst(instdata)

			# -------------------- vst2 (juicysfplugin) --------------------

			# ---------- from native soundfont2
			elif pluginname == 'soundfont2' and out_daw not in supportedplugins['sf2']:
				sf2data = instdata['plugindata']
				if 'bank' in sf2data: sf2_bank = sf2data['bank']
				else: sf2_bank = 0
				if 'patch' in sf2data: sf2_patch = sf2data['patch']
				else: sf2_params = 0
				if 'file' in sf2data: sf2_filename = sf2data['file']
				else: sf2_filename = 0
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

			if in_daw == 'lmms' and pluginname == 'native-lmms': 
				output_lmms_vst2.convert_fx(fxdata)

			elif in_daw == 'flp' and pluginname == 'native-fl':
				output_flstudio_vst2.convert_fx(fxdata)

			elif in_daw == 'onlineseq' and pluginname == 'native-onlineseq':
				output_onlineseq_vst2.convert_fx(fxdata)



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

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, extra_json):
	global supportedplugins
	plugin_vst2.listinit()
	supportedplugins = {}
	supportedplugins['sf2'] =             ['lmms','flp',                       'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler'] =         ['lmms','flp','ableton',             'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler-multi'] =   ['ableton',                          'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler-slicer'] =  ['ableton',                          'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['vst2'] =            ['lmms','ableton','flp','muse',      'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['vst3'] =            ['ableton','flp',                    'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['clap'] =            [                                    'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['ladspa'] =          ['lmms',                             'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
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
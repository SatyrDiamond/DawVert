# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import xml.etree.ElementTree as ET
import os
import struct
import math
import base64
from functions import list_vst
from functions import vst_fx
from functions import vst_inst
from functions import params_vst
from functions import params_vital

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

from functions_plugconv import input_flstudio
from functions_plugconv import input_pxtone
from functions_plugconv import input_jummbox

from functions_plugconv import output_sampler_vst2
from functions_plugconv import output_multisampler_vst2
from functions_plugconv import output_slicer_vst2
from functions_plugconv import output_lmms_vst2

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

			if pluginname == 'sampler' and out_daw not in supportedplugins['sampler']: 
				output_sampler_vst2.convert_inst(instdata, platform_id)

			if pluginname == 'sampler-multi' and out_daw not in supportedplugins['sampler-multi']: 
				output_multisampler_vst2.convert_inst(instdata, platform_id)

			if pluginname == 'sampler-slicer' and out_daw not in supportedplugins['sampler-slicer']: 
				output_slicer_vst2.convert_inst(instdata)

			elif (pluginname == 'native-lmms' or pluginname == 'zynaddsubfx-lmms') and out_daw != 'lmms':
				output_lmms_vst2.convert_inst(instdata)

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
				jsfp_xml = vst_inst.juicysfplugin_create(sf2_bank, sf2_patch, sf2_filename)
				list_vst.replace_data(instdata, 2, 'any', 'juicysfplugin', 'raw', params_vst.vc2xml_make(jsfp_xml), None)

			# -------------------- vst2 (magical8bitplug) --------------------

			elif pluginname == 'retro':
				fsd_data = instdata['plugindata']
				m8p_root = ET.Element("root")
				m8p_params = ET.SubElement(m8p_root, "Params")
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioDirection", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioTime", 0.02999999932944775)
				if 'attack' in fsd_data: vst_inst.m8bp_addvalue(m8p_params, "attack", fsd_data['attack'])
				else: vst_inst.m8bp_addvalue(m8p_params, "attack", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "bendRange", 12.0)
				vst_inst.m8bp_addvalue(m8p_params, "colorScheme", 1.0)
				if 'decay' in fsd_data: vst_inst.m8bp_addvalue(m8p_params, "decay", fsd_data['decay'])
				else: vst_inst.m8bp_addvalue(m8p_params, "decay", 0.0)
				
				duty = 2
				if 'duty' in fsd_data: 
					if fsd_data['duty'] == 0: duty = 2
					if fsd_data['duty'] == 1: duty = 1
					if fsd_data['duty'] == 2: duty = 0
				else: duty = 2
				if 'type' in fsd_data:
					if fsd_data['type'] == '1bit_short': duty = 0
					if fsd_data['type'] == '4bit': duty = 1

				vst_inst.m8bp_addvalue(m8p_params, "duty", float(duty))
				vst_inst.m8bp_addvalue(m8p_params, "gain", 0.5)
				vst_inst.m8bp_addvalue(m8p_params, "isAdvancedPanelOpen_raw", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "isArpeggioEnabled_raw", 0.0)

				m8p_dutyEnv = ET.SubElement(m8p_root, "dutyEnv")
				m8p_pitchEnv = ET.SubElement(m8p_root, "pitchEnv")
				m8p_volumeEnv = ET.SubElement(m8p_root, "volumeEnv")

				if 'env_arp' in fsd_data:
					vst_inst.m8bp_addvalue(m8p_params, "isPitchSequenceEnabled_raw", 1.0)
					m8p_pitchEnv.text = ','.join(str(item) for item in fsd_data['env_arp']['values'])
				else: vst_inst.m8bp_addvalue(m8p_params, "isPitchSequenceEnabled_raw", 0.0)

				if 'env_duty' in fsd_data:
					vst_inst.m8bp_addvalue(m8p_params, "isDutySequenceEnabled_raw", 1.0)
					m8p_dutyEnv.text = ','.join(str(item) for item in fsd_data['env_duty']['values'])
				else: vst_inst.m8bp_addvalue(m8p_params, "isDutySequenceEnabled_raw", 0.0)

				if 'env_vol' in fsd_data:
					vst_inst.m8bp_addvalue(m8p_params, "isVolumeSequenceEnabled_raw", 1.0)
					m8p_volumeEnv.text = ','.join(str(item) for item in fsd_data['env_vol']['values'])
				else: vst_inst.m8bp_addvalue(m8p_params, "isVolumeSequenceEnabled_raw", 0.0)

				vst_inst.m8bp_addvalue(m8p_params, "maxPoly", 8.0)
				vst_inst.m8bp_addvalue(m8p_params, "noiseAlgorithm_raw", 0.0)
				if fsd_data['wave'] == 'square': vst_inst.m8bp_addvalue(m8p_params, "osc", 0.0)
				if fsd_data['wave'] == 'triangle': vst_inst.m8bp_addvalue(m8p_params, "osc", 1.0)
				if fsd_data['wave'] == 'noise': vst_inst.m8bp_addvalue(m8p_params, "osc", 2.0)
				if 'release' in fsd_data: vst_inst.m8bp_addvalue(m8p_params, "release", fsd_data['release'])
				else: vst_inst.m8bp_addvalue(m8p_params, "release", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "restrictsToNESFrequency_raw", 0.0)
				if 'sustain' in fsd_data: vst_inst.m8bp_addvalue(m8p_params, "suslevel", fsd_data['sustain'])
				else: vst_inst.m8bp_addvalue(m8p_params, "suslevel", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepInitialPitch", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepTime", 0.1000000014901161)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDelay", 0.2999999821186066)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDepth", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoIgnoresWheel_raw", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoRate", 0.1500000059604645)
				list_vst.replace_data(instdata, 2, 'any', 'Magical 8bit Plug 2', 'raw', params_vst.vc2xml_make(m8p_root), None)

			# -------------------- opn2 > OPNplug --------------------
			elif pluginname == 'opn2':
				xmlout = vst_inst.opnplug_convert(instdata['plugindata'])
				list_vst.replace_data(instdata, 2, 'any', 'OPNplug', 'raw', params_vst.vc2xml_make(xmlout), None)


# -------------------- FX --------------------
def convplug_fx(fxdata, in_daw, out_daw, extra_json, nameid):
	global supportedplugins
	if 'plugin' in fxdata:
		if 'plugindata' in fxdata:
			pluginname = fxdata['plugin']
			plugindata = fxdata['plugindata']
			if pluginname == 'native-lmms':
				mmp_plugname = plugindata['name']
				mmp_plugdata = plugindata['data']
				# -------------------- waveshaper > vst2 (Wolf Shaper) - from lmms --------------------
				if mmp_plugname == 'waveshaper':
					waveshapebytes = base64.b64decode(plugindata['data']['waveShape'])
					waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4]) for i in range(0, len(waveshapebytes), 4)]
					vst_fx.wolfshaper_init()
					for pointnum in range(50):
						pointdata = waveshapepoints[pointnum*4][0]
						vst_fx.wolfshaper_addpoint(pointnum/49,pointdata,0.5,0)
					list_vst.replace_data(fxdata, 2, 'any', 'Wolf Shaper', 'raw', params_vst.nullbytegroup_make(vst_fx.wolfshaper_get()), None)
			else:
				print('[plug-conv] Unchanged')

# -------------------- convproj --------------------
def do_fxchain_audio(fxchain_audio, in_daw, out_daw, extra_json, nameid):
	for fxslot in fxchain_audio:
		convplug_fx(fxslot, in_daw, out_daw, extra_json, nameid)

def do_inst(track_data, in_daw, out_daw, extra_json, nameid, platform_id):
	if 'instdata' in track_data:
		instdata = track_data['instdata']
		print('[plug-conv] --- Inst: '+nameid)
		convplug_inst(instdata, in_daw, out_daw, extra_json, nameid, platform_id)

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, extra_json):
	global supportedplugins
	list_vst.listinit()
	supportedplugins = {}
	supportedplugins['sf2'] =           ['lmms','flp',                       'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler'] =       ['lmms','flp','ableton',             'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler-multi'] = ['ableton',                          'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['sampler-slicer']= ['ableton',                          'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['vst2'] =          ['lmms','ableton','flp','muse',      'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['vst3'] =          ['lmms','ableton','flp',             'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['clap'] =          [                                    'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	supportedplugins['ladspa'] =        ['lmms',                             'cvpj', 'cvpj_r', 'cvpj_m', 'cvpj_mi']
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if in_type == 'r' or in_type == 'ri':
			if 'track_data' in cvpj_l:
				for track in cvpj_l['track_data']:
					track_data = cvpj_l['track_data'][track]
					if 'type' in track_data:
						if track_data['type'] == 'instrument':
							do_inst(track_data, in_daw, out_daw, extra_json, track, platform_id)
		if in_type == 'm' or in_type == 'mi':
			if 'instruments_data' in cvpj_l:
				for track in cvpj_l['instruments_data']:
					track_data = cvpj_l['instruments_data'][track]
					do_inst(track_data, in_daw, out_daw, extra_json, track, platform_id)
		if 'fxrack' in cvpj_l:
			for fxid in cvpj_l['fxrack']:
				fxiddata = cvpj_l['fxrack'][fxid]
				if 'fxchain_audio' in fxiddata:
					fxchain_audio = fxiddata['fxchain_audio']
					print('[plug-conv] --- FX: '+fxid)
					do_fxchain_audio(fxchain_audio, in_daw, out_daw, extra_json, fxid)
		return json.dumps(cvpj_l, indent=2)
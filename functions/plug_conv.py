# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import xml.etree.ElementTree as ET
import pathlib
import os
import struct
import math
import base64
from functions import audio_wav
from functions import list_vst
from functions import vst_fx
from functions import vst_inst
from functions import params_vst
from functions import params_vital
from functions import plug_in_fl
from functions import plug_in_pxtone
from functions import plug_in_jummbox

# -------------------- Instruments --------------------
def convplug_inst(instdata, dawname, extra_json, nameid):
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# ---------------------------------------- 1 ----------------------------------------
			if pluginname == 'native-fl':
				plug_in_fl.convert(instdata)

			# ---------- from pxtone
			elif pluginname == 'native-pxtone':
				plug_in_pxtone.convert(instdata)

			# ---------- from jummbox
			elif pluginname == 'native-jummbox':
				plug_in_jummbox.convert(instdata)

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

			# ---------------------------------------- 2 ----------------------------------------
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# -------------------- sampler > vst2 (Grace) --------------------
			if pluginname == 'sampler' and dawname not in supportedplugins['sampler']:
				sampler_data = instdata
				sampler_file_data = instdata['plugindata']
				wireturn = audio_wav.complete_wav_info(sampler_file_data)
				if list_vst.vst2path_loaded == True:
					if list_vst.ifexists_vst2('Grace') == True:
						if 'file' in sampler_file_data and wireturn != None and wireturn == 1:
							file_extension = pathlib.Path(sampler_file_data['file']).suffix
							if file_extension == '.wav':
								gx_root = vst_inst.grace_create_main()
								regionparams = {}
								regionparams['file'] = sampler_file_data['file']
								regionparams['length'] = sampler_file_data['length']
								regionparams['start'] = 0
								if 'loop' in sampler_file_data:
									regionparams['loop'] = sampler_file_data['loop']
								regionparams['end'] = sampler_file_data['length']
								vst_inst.grace_create_region(gx_root, regionparams)
								xmlout = ET.tostring(gx_root, encoding='utf-8')
								list_vst.replace_data(instdata, 'Grace', xmlout)
						else:
							print("[plug-conv] Unchanged, Grace (VST2) only supports Format 1 .WAV")
					else:
						print('[plug-conv] Unchanged, Plugin Grace not Found')
				else:
					print('[plug-conv] Unchanged, VST2 list not found')

			# -------------------- sampler-multi > vst2 (Grace) --------------------

			elif pluginname == 'sampler-multi' and dawname not in supportedplugins['sampler-multi']:
				msmpl_data = instdata
				msmpl_p_data = instdata['plugindata']
				if list_vst.vst2path_loaded == True:
					if list_vst.ifexists_vst2('Grace') == True:
						regions = msmpl_p_data['regions']
						gx_root = vst_inst.grace_create_main()
						for regionparams in regions:
							vst_inst.grace_create_region(gx_root, regionparams)
						xmlout = ET.tostring(gx_root, encoding='utf-8')
						list_vst.replace_data(instdata, 'Grace', xmlout)
					else:
						print('[plug-conv] Unchanged, Plugin Grace not Found')
				else:
					print('[plug-conv] Unchanged, VST2 list not found')

			# -------------------- vst2 (juicysfplugin) --------------------

			# ---------- from native soundfont2
			elif pluginname == 'soundfont2' and dawname not in supportedplugins['sf2']:
				sf2data = instdata['plugindata']
				if 'bank' in sf2data: sf2_bank = sf2data['bank']
				else: sf2_bank = 0
				if 'patch' in sf2data: sf2_patch = sf2data['patch']
				else: sf2_params = 0
				if 'file' in sf2data: sf2_filename = sf2data['file']
				else: sf2_filename = 0
				jsfp_xml = vst_inst.juicysfplugin_create(sf2_bank, sf2_patch, sf2_filename)
				list_vst.replace_data(instdata, 'juicysfplugin', params_vst.vc2xml_make(jsfp_xml))

			# -------------------- vst2 (ninjas2) --------------------
			elif pluginname == 'slicer':
				slicerdata = instdata['plugindata']
				vst_inst.ninjas2_init()
				vst_inst.ninjas2_slicerdata(slicerdata)
				ninjas2out = vst_inst.ninjas2_get()
				list_vst.replace_data(instdata, 'Ninjas 2', params_vst.nullbytegroup_make(ninjas2out))

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
				list_vst.replace_data(instdata, 'Magical 8bit Plug 2', params_vst.vc2xml_make(m8p_root))

			# -------------------- opn2 > OPNplug --------------------
			elif pluginname == 'opn2':
				xmlout = vst_inst.opnplug_convert(instdata['plugindata'])
				list_vst.replace_data(instdata, 'OPNplug', params_vst.vc2xml_make(xmlout))

			# -------------------- zynaddsubfx > vst2 (Zyn-Fusion) - from lmms --------------------
			elif pluginname == 'zynaddsubfx-lmms' and dawname != 'lmms':
				zasfxdata = instdata['plugindata']['data']
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
				list_vst.replace_data(instdata, 'ZynAddSubFX', zasfxdatafixed)

# -------------------- FX --------------------
def convplug_fx(fxdata, dawname, extra_json, nameid):
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
					vst_fx.wolfshaper_get()
					list_vst.replace_data(fxdata, 'Wolf Shaper', params_vst.nullbytegroup_make(vst_fx.wolfshaper_get()))
			else:
				print('[plug-conv] Unchanged')

# -------------------- convproj --------------------
def do_fxchain_audio(fxchain_audio, dawname, extra_json, nameid):
	for fxslot in fxchain_audio:
		convplug_fx(fxslot, dawname, extra_json, nameid)

def do_inst(track_data, dawname, extra_json, nameid):
	if 'instdata' in track_data:
		instdata = track_data['instdata']
		print('[plug-conv] --- Inst: '+nameid)
		convplug_inst(instdata, dawname, extra_json, nameid)
	if 'chain_inst' in track_data:
		print('[plug-conv] --- InstChain: '+nameid)
		for trackid in track_data['chain_inst']:
			convplug_inst(trackid, dawname, extra_json, nameid)

def convproj(cvpjdata, in_type, out_type, dawname, extra_json):
	global supportedplugins
	list_vst.listinit('windows')
	supportedplugins = {}
	supportedplugins['sf2'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp', 'ableton']
	supportedplugins['sampler-multi'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'ableton']
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if in_type == 'r' or in_type == 'ri':
			if 'track_data' in cvpj_l:
				for track in cvpj_l['track_data']:
					track_data = cvpj_l['track_data'][track]
					if 'type' in track_data:
						if track_data['type'] == 'instrument':
							do_inst(track_data, dawname, extra_json, track)
		if in_type == 'm' or in_type == 'mi':
			if 'instruments_data' in cvpj_l:
				for track in cvpj_l['instruments_data']:
					track_data = cvpj_l['instruments_data'][track]
					do_inst(track_data, dawname, extra_json, track)
		if 'fxrack' in cvpj_l:
			for fxid in cvpj_l['fxrack']:
				fxiddata = cvpj_l['fxrack'][fxid]
				if 'fxchain_audio' in fxiddata:
					fxchain_audio = fxiddata['fxchain_audio']
					print('[plug-conv] --- FX: '+fxid)
					do_fxchain_audio(fxchain_audio, dawname, extra_json, fxid)
		return json.dumps(cvpj_l, indent=2)
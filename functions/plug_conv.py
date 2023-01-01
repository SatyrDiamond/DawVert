# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import base64
import xml.etree.ElementTree as ET
import pathlib
import os
import struct
import math
from functions import audio_wav
from functions import data_bytes
from functions import list_vst
from functions import vst_fx
from functions import vst_inst
from functions import vst_params
from functions import vst_inst_vital

simsynth_shapes = {0.4: 'noise', 0.3: 'sine', 0.2: 'square', 0.1: 'saw', 0.0: 'triangle'}

def ss_asdr(x): 
	print((x+(x*x)*4))
	return (x+(x*x)*4)

# -------------------- Shapes --------------------
def wave_sine(x): return math.sin((x-0.5)*(math.pi*2))
def wave_saw(x): return x-math.floor(x)
def wave_tri(x): return abs((x*2)%(2)-1)
def wave_squ(x, pw):
    if wave_tri(x) > pw: return 1
    else: return -1

def tripleoct(x, shape, pw, one, two):
    if shape == 'sine': samplepoint = wave_sine(x) + wave_sine(x*2)*one + wave_sine(x*4)*two
    elif shape == 'saw': samplepoint = wave_saw(x) + wave_saw(x*2)*one + wave_saw(x*4)*two
    elif shape == 'triangle': samplepoint = wave_tri(x) + wave_tri(x*2)*one + wave_tri(x*4)*two
    elif shape == 'square': samplepoint = wave_squ(x, pw) + wave_squ(x*2, pw)*one + wave_squ(x*4, pw)*two
    else: samplepoint = x
    return samplepoint

# -------------------- VST --------------------
def vst_add_param(paramlist, num, name, value):
	paramlist[str(num)] = {}
	paramlist[str(num)]['name'] = name
	paramlist[str(num)]['value'] = str(value)

# -------------------- Instruments --------------------
def convplug_inst(instdata, dawname, extra_json, nameid):
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# ---------------------------------------- 1 ----------------------------------------
			if pluginname == 'native-fl':
				fl_plugdata = base64.b64decode(plugindata['data'])
				fl_plugstr = data_bytes.bytearray2BytesIO(base64.b64decode(plugindata['data']))
				if plugindata['name'].lower() == 'fruity soundfont player':
					flsf_unk = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_patch = int.from_bytes(fl_plugstr.read(4), "little")-1
					flsf_bank = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_reverb_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_chorus_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_mod = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_asdf_A = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_asdf_D = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_asdf_S = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_asdf_R = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_lfo_predelay = int.from_bytes(fl_plugstr.read(4), "little") # max 5900
					flsf_lfo_amount = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_lfo_speed = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_cutoff = int.from_bytes(fl_plugstr.read(4), "little") # max 127

					flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')

					flsf_reverb_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
					flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_chorus_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
					flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

					instdata['plugin'] = "soundfont2"
					instdata['plugindata'] = {}
					instdata['plugindata']['file'] = flsf_filename
					if flsf_patch > 127:
						instdata['plugindata']['bank'] = 128
						instdata['plugindata']['patch'] = flsf_patch-128
					else:
						instdata['plugindata']['bank'] = flsf_bank
						instdata['plugindata']['patch'] = flsf_patch
				elif plugindata['name'].lower() == 'fruity dx10':
					int.from_bytes(fl_plugstr.read(4), "little")
					fldx_amp_att = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_amp_dec = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_amp_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_course = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_fine = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_init = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_time = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_sus = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_vibrato = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_waveform = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_thru = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_lforate = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_course = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_fine = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_init = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_time = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_sus = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_octave = (int.from_bytes(fl_plugstr.read(4), "little", signed="True")/6)+0.5

					vstdxparams = {}
					vstdxparams[0] = {"name": "Attack  ","value": fldx_amp_att}
					vstdxparams[1] = {"name": "Decay   ","value": fldx_amp_dec}
					vstdxparams[2] = {"name": "Release ","value": fldx_amp_rel}
					vstdxparams[3] = {"name": "Coarse  ","value": fldx_mod_course}
					vstdxparams[4] = {"name": "Fine    ","value": fldx_mod_fine}
					vstdxparams[5] = {"name": "Mod Init","value": fldx_mod_init}
					vstdxparams[6] = {"name": "Mod Dec ","value": fldx_mod_time}
					vstdxparams[7] = {"name": "Mod Sus ","value": fldx_mod_sus}
					vstdxparams[8] = {"name": "Mod Rel ","value": fldx_mod_rel}
					vstdxparams[9] = { "name": "Mod Vel ","value": fldx_mod_velsen}
					vstdxparams[10] = {"name": "Vibrato ","value": fldx_vibrato}
					vstdxparams[11] = {"name": "Octave  ","value": fldx_octave}
					vstdxparams[12] = {"name": "FineTune","value": 0.5}
					vstdxparams[13] = {"name": "Waveform","value": fldx_waveform}
					vstdxparams[14] = {"name": "Mod Thru","value": fldx_mod_thru}
					vstdxparams[15] = {"name": "LFO Rate","value": fldx_lforate}
					list_vst.replace_params(instdata, 'DX10', 16, vstdxparams)
				elif plugindata['name'].lower() == 'simsynth':
					#osc1_pw, osc1_crs, osc1_fine, osc1_lvl, osc1_lfo, osc1_env, osc1_shape
					osc1_pw, osc1_crs, osc1_fine, osc1_lvl, osc1_lfo, osc1_env, osc1_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
					osc2_pw, osc2_crs, osc2_fine, osc2_lvl, osc2_lfo, osc2_env, osc2_shape = struct.unpack('ddddddd', fl_plugstr.read(56))
					osc3_pw, osc3_crs, osc3_fine, osc3_lvl, osc3_lfo, osc3_env, osc3_shape = struct.unpack('ddddddd', fl_plugstr.read(56))

					lfo_del, lfo_rate, unused, lfo_shape = struct.unpack('dddd', fl_plugstr.read(32))
					UNK, svf_cut, svf_emph, svf_env = struct.unpack('dddd', fl_plugstr.read(32))
					svf_lfo, svf_kb, UNK, svf_high = struct.unpack('dddd', fl_plugstr.read(32))
					svf_band, UNK, amp_att, amp_dec = struct.unpack('dddd', fl_plugstr.read(32))
					amp_sus, amp_rel, amp_lvl, UNK = struct.unpack('dddd', fl_plugstr.read(32))
					svf_att, svf_dec, svf_sus, svf_rel = struct.unpack('dddd', fl_plugstr.read(32))

					fl_plugstr.read(64)
					fl_plugstr.read(12)

					osc1_on, osc1_o1, osc1_o2, osc1_warm = struct.unpack('IIII', fl_plugstr.read(16))
					osc2_on, osc2_o1, osc2_o2, osc2_warm = struct.unpack('IIII', fl_plugstr.read(16))
					osc3_on, osc3_o1, osc3_o2, osc3_warm = struct.unpack('IIII', fl_plugstr.read(16))
					lfo_on, lfo_retrugger, svf_on, UNK = struct.unpack('IIII', fl_plugstr.read(16))
					lfo_trackamp, UNK, chorus_on, UNK = struct.unpack('IIII', fl_plugstr.read(16))

					#vst_inst_vital.create()

					#vital_osc1_shape = []
					#for num in range(2048): vital_osc1_shape.append(tripleoct(num/2048, simsynth_shapes[osc1_shape], osc1_pw, osc1_o1, osc1_o2))
					#vst_inst_vital.replacewave(0, vital_osc1_shape)
					#vst_inst_vital.setvalue('osc_1_on', osc1_on)
					#vst_inst_vital.setvalue('osc_1_transpose', (osc1_crs-0.5)*48)
					#vst_inst_vital.setvalue('osc_1_tune', (osc1_fine-0.5)*2)
					#vst_inst_vital.setvalue('osc_1_level', osc1_lvl/2)
					#if osc1_warm == 1:
						#vst_inst_vital.setvalue('osc_1_unison_detune', 2.2)
						#vst_inst_vital.setvalue('osc_1_unison_voices', 6)

					#vital_osc2_shape = []
					#for num in range(2048): vital_osc2_shape.append(tripleoct(num/2048, simsynth_shapes[osc2_shape], osc2_pw, osc2_o1, osc2_o2))
					#vst_inst_vital.replacewave(1, vital_osc2_shape)
					#vst_inst_vital.setvalue('osc_2_on', osc2_on)
					#vst_inst_vital.setvalue('osc_2_transpose', (osc2_crs-0.5)*48)
					#vst_inst_vital.setvalue('osc_2_tune', (osc2_fine-0.5)*2)
					#vst_inst_vital.setvalue('osc_2_level', osc2_lvl/2)
					#if osc2_warm == 1:
						#vst_inst_vital.setvalue('osc_2_unison_detune', 2.2)
						#vst_inst_vital.setvalue('osc_2_unison_voices', 6)

					#vital_osc3_shape = []
					#for num in range(2048): vital_osc3_shape.append(tripleoct(num/2048, simsynth_shapes[osc3_shape], osc3_pw, osc3_o1, osc3_o2))
					#vst_inst_vital.replacewave(2, vital_osc3_shape)
					#vst_inst_vital.setvalue('osc_3_on', osc3_on)
					#vst_inst_vital.setvalue('osc_3_transpose', (osc3_crs-0.5)*48)
					#vst_inst_vital.setvalue('osc_3_tune', (osc3_fine-0.5)*2)
					#vst_inst_vital.setvalue('osc_3_level', osc3_lvl/2)
					#if osc3_warm == 1:
						#vst_inst_vital.setvalue('osc_3_unison_detune', 2.2)
						#vst_inst_vital.setvalue('osc_3_unison_voices', 6)

					#vst_inst_vital.setvalue('env_1_attack', ss_asdr(amp_att)*4)
					#vst_inst_vital.setvalue('env_1_decay', ss_asdr(amp_dec)*4)
					#vst_inst_vital.setvalue('env_1_sustain', amp_sus)
					#vst_inst_vital.setvalue('env_1_release', ss_asdr(amp_rel)*4)

					#vitaldata = vst_inst_vital.getdata()
					#list_vst.replace_data(instdata, 'Vital', vitaldata.encode('utf-8'))

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
				list_vst.replace_data(instdata, 'juicysfplugin', vst_params.make_vc2_xml(jsfp_xml))

			# -------------------- vst2 (magical8bitplug) --------------------

			elif pluginname == 'retro':
				fsd_data = instdata['plugindata']
				m8p_root = ET.Element("root")
				m8p_params = ET.SubElement(m8p_root, "Params")
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioDirection", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioTime", 0.02999999932944775)
				vst_inst.m8bp_addvalue(m8p_params, "attack", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "bendRange", 12.0)
				vst_inst.m8bp_addvalue(m8p_params, "colorScheme", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "decay", 0.0)
				
				duty = 2
				if fsd_data['wave'] == 'square': duty = 2
				if 'duty' in fsd_data: duty = fsd_data['duty']
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
				vst_inst.m8bp_addvalue(m8p_params, "pitchSequenceMode_raw", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "release", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "restrictsToNESFrequency_raw", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "suslevel", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepInitialPitch", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepTime", 0.1000000014901161)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDelay", 0.2999999821186066)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDepth", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoIgnoresWheel_raw", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoRate", 0.1500000059604645)
				list_vst.replace_data(instdata, 'Magical 8bit Plug 2', vst_params.make_vc2_xml(m8p_root))

			# -------------------- zynaddsubfx > vst2 (Zyn-Fusion) - from lmms --------------------
			elif pluginname == 'zynaddsubfx-lmms' and dawname != 'lmms':
				zasfxdata = instdata['plugindata']['data']
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
				list_vst.replace_data(instdata, 'ZynAddSubFX', zasfxdatafixed)
			else:
				print('[plug-conv] Unchanged')

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
					list_vst.replace_data(fxdata, 'Wolf Shaper', vst_params.make_nullbytegroup(vst_fx.wolfshaper_get()))
			else:
				print('[plug-conv] Unchanged')

# -------------------- convproj --------------------
def do_fxchain(fxchain, dawname, extra_json, nameid):
	for fxslot in fxchain:
		convplug_fx(fxslot, dawname, extra_json, nameid)

def convproj(cvpjdata, in_type, out_type, dawname, extra_json):
	global supportedplugins
	list_vst.listinit('windows')
	supportedplugins = {}
	supportedplugins['sf2'] = ['cvpj', 'cvpj_f', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler'] = ['cvpj', 'cvpj_f', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler-multi'] = ['cvpj', 'cvpj_f', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'ableton']
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if in_type == 'r':
			if 'trackdata' in cvpj_l:
				for track in cvpj_l['trackdata']:
					trackdata = cvpj_l['trackdata'][track]
					if 'type' in trackdata:
						if trackdata['type'] == 'instrument':
							if 'instdata' in trackdata:
								instdata = trackdata['instdata']
								print('[plug-conv] --- Inst: '+track)
								convplug_inst(instdata, dawname, extra_json, track)
		if in_type == 'm' or in_type == 'mi':
			if 'instruments' in cvpj_l:
				for track in cvpj_l['instruments']:
					trackdata = cvpj_l['instruments'][track]
					if 'instdata' in trackdata:
						instdata = trackdata['instdata']
						print('[plug-conv] --- Inst: '+track)
						convplug_inst(instdata, dawname, extra_json, track)
		if 'fxrack' in cvpj_l:
			for fxid in cvpj_l['fxrack']:
				fxiddata = cvpj_l['fxrack'][fxid]
				if 'fxchain' in fxiddata:
					fxchain = fxiddata['fxchain']
					print('[plug-conv] --- FX: '+fxid)
					do_fxchain(fxchain, dawname, extra_json, fxid)
		return json.dumps(cvpj_l, indent=2)
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import io
import struct
import math
import lxml.etree as ET
from functions import list_vst
from functions import params_vst
from functions import params_vital
from functions import params_vital_wavetable

def clamp(n, minn, maxn):
	return max(min(maxn, n), minn)

def socalabs_addparam(x_sid, name, value):
    x_temp = ET.SubElement(x_sid, 'param')
    x_temp.set('uid', name)
    x_temp.set('val', str(value))

def sid_shape(lmms_sid_shape):
	if lmms_sid_shape == 0: return 3 #squ
	if lmms_sid_shape == 1: return 1 #tri
	if lmms_sid_shape == 2: return 2 #saw
	if lmms_sid_shape == 3: return 4 #noise

def kickmess_add(bio_data, i_cat, i_name, i_value):
	kickmess_text = i_cat+' : '+i_name+'='+str(i_value)+';\n'
	bio_data.write(str.encode(kickmess_text))

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'native-lmms':
		
		lmmsnat_data = plugindata['data']
		lmmsnat_name = plugindata['name']

		if lmmsnat_name == 'bitinvader':
			params_vital.create()
			bitinvader_shape_data = base64.b64decode(lmmsnat_data['sampleShape'])
			bitinvader_shape_vals = struct.unpack('f'*(len(bitinvader_shape_data)//4), bitinvader_shape_data)
			params_vital.setvalue('osc_1_on', 1)
			params_vital.setvalue('osc_1_transpose', 12)
			params_vital.replacewave(0, params_vital_wavetable.resizewave(bitinvader_shape_vals))
			params_vital.cvpj_asdrlfo2vitalparams(plugindata)
			vitaldata = params_vital.getdata()
			list_vst.replace_data(instdata, 2, 'any', 'Vital', 'raw', vitaldata.encode('utf-8'), None)

		if lmmsnat_name == 'sid':
			x_sid = ET.Element("state")
			x_sid.set('valueTree', '<?xml version="1.0" encoding="UTF-8"?>\n<state/>')
			x_sid.set('program', '0')
			socalabs_addparam(x_sid, "a1", lmmsnat_data['attack0'])
			socalabs_addparam(x_sid, "a2", lmmsnat_data['attack1'])
			socalabs_addparam(x_sid, "a3", lmmsnat_data['attack2'])
			socalabs_addparam(x_sid, "cutoff", lmmsnat_data['filterFC'])
			socalabs_addparam(x_sid, "d1", lmmsnat_data['decay0'])
			socalabs_addparam(x_sid, "d2", lmmsnat_data['decay1'])
			socalabs_addparam(x_sid, "d3", lmmsnat_data['decay2'])
			socalabs_addparam(x_sid, "f1", lmmsnat_data['filtered0'])
			socalabs_addparam(x_sid, "f2", lmmsnat_data['filtered1'])
			socalabs_addparam(x_sid, "f3", lmmsnat_data['filtered2'])
			socalabs_addparam(x_sid, "fine1", 0.0)
			socalabs_addparam(x_sid, "fine2", 0.0)
			socalabs_addparam(x_sid, "fine3", 0.0)
			if lmmsnat_data['filterMode'] == 0.0: socalabs_addparam(x_sid, "highpass", 1.0)
			else: socalabs_addparam(x_sid, "highpass", 0.0)
			if lmmsnat_data['filterMode'] == 1.0: socalabs_addparam(x_sid, "bandpass", 1.0)
			else: socalabs_addparam(x_sid, "bandpass", 0.0)
			if lmmsnat_data['filterMode'] == 2.0: socalabs_addparam(x_sid, "lowpass", 1.0)
			else: socalabs_addparam(x_sid, "lowpass", 0.0)
			socalabs_addparam(x_sid, "output3", lmmsnat_data['voice3Off'])
			socalabs_addparam(x_sid, "pw1", lmmsnat_data['pulsewidth0'])
			socalabs_addparam(x_sid, "pw2", lmmsnat_data['pulsewidth1'])
			socalabs_addparam(x_sid, "pw3", lmmsnat_data['pulsewidth2'])
			socalabs_addparam(x_sid, "r1", lmmsnat_data['release0'])
			socalabs_addparam(x_sid, "r2", lmmsnat_data['release1'])
			socalabs_addparam(x_sid, "r3", lmmsnat_data['release2'])
			socalabs_addparam(x_sid, "reso", lmmsnat_data['filterResonance'])
			socalabs_addparam(x_sid, "ring1", lmmsnat_data['ringmod0'])
			socalabs_addparam(x_sid, "ring2", lmmsnat_data['ringmod1'])
			socalabs_addparam(x_sid, "ring3", lmmsnat_data['ringmod2'])
			socalabs_addparam(x_sid, "s1", lmmsnat_data['sustain0'])
			socalabs_addparam(x_sid, "s2", lmmsnat_data['sustain1'])
			socalabs_addparam(x_sid, "s3", lmmsnat_data['sustain2'])
			socalabs_addparam(x_sid, "sync1", lmmsnat_data['sync0'])
			socalabs_addparam(x_sid, "sync2", lmmsnat_data['sync1'])
			socalabs_addparam(x_sid, "sync3", lmmsnat_data['sync2'])
			socalabs_addparam(x_sid, "tune1", lmmsnat_data['coarse0'])
			socalabs_addparam(x_sid, "tune2", lmmsnat_data['coarse1'])
			socalabs_addparam(x_sid, "tune3", lmmsnat_data['coarse2'])
			socalabs_addparam(x_sid, "voices", 8.0)
			socalabs_addparam(x_sid, "vol", lmmsnat_data['volume'])
			socalabs_addparam(x_sid, "w1", sid_shape(lmmsnat_data['waveform0']))
			socalabs_addparam(x_sid, "w2", sid_shape(lmmsnat_data['waveform1']))
			socalabs_addparam(x_sid, "w3", sid_shape(lmmsnat_data['waveform2']))
			list_vst.replace_data(instdata, 2, 'any', 'SID', 'raw', ET.tostring(x_sid, encoding='utf-8'), None)
			if 'middlenote' in instdata: instdata['middlenote'] -= 12
			else: instdata['middlenote'] = -12

		if lmmsnat_name == 'kicker':
			kickmess_out = io.BytesIO()
			kickmess_out.write(b'!PARAMS;\n')
			kickmess_add(kickmess_out, 'pub', 'freq_start', math.sqrt((lmmsnat_data['startfreq']-2.51)/3000))
			kickmess_add(kickmess_out, 'pub', 'freq_end', math.sqrt((lmmsnat_data['endfreq']-2.51)/2000))
			kickmess_add(kickmess_out, 'pub', 'f_env_release', math.sqrt((lmmsnat_data['decay']-2.51)/5000))
			kickmess_add(kickmess_out, 'pub', 'dist_start', lmmsnat_data['dist']/100)
			kickmess_add(kickmess_out, 'pub', 'dist_end', lmmsnat_data['distend']/100)
			kickmess_add(kickmess_out, 'pub', 'gain', clamp(lmmsnat_data['gain'], 0, 2)/2)
			kickmess_add(kickmess_out, 'pub', 'env_slope', lmmsnat_data['env'])
			kickmess_add(kickmess_out, 'pub', 'freq_slope', lmmsnat_data['slope'])
			kickmess_add(kickmess_out, 'pub', 'noise', lmmsnat_data['noise'])
			if lmmsnat_data['startnote'] == 1: kickmess_add(kickmess_out, 'pub', 'freq_note_start', 0.5)
			else: kickmess_add(kickmess_out, 'pub', 'freq_note_start', 0.25)
			if lmmsnat_data['endnote'] == 1: kickmess_add(kickmess_out, 'pub', 'freq_note_end', 0.5)
			else: kickmess_add(kickmess_out, 'pub', 'freq_note_end', 0.25)
			kickmess_add(kickmess_out, 'pub', 'env_release', 0)
			kickmess_add(kickmess_out, 'pub', 'phase_offs', lmmsnat_data['click'])
			kickmess_add(kickmess_out, 'pub', 'dist_on', 1)
			kickmess_add(kickmess_out, 'pub', 'f1_cutoff', 1)
			kickmess_add(kickmess_out, 'pub', 'f1_res', 0)
			kickmess_add(kickmess_out, 'pub', 'f1_drive', 0.2)
			kickmess_add(kickmess_out, 'pub', 'main_gain', 0.70710677)
			kickmess_add(kickmess_out, 'pub', 'e1_attack', 0.1)
			kickmess_add(kickmess_out, 'pub', 'e1_decay', 0.14142135)
			kickmess_add(kickmess_out, 'pub', 'e1_sustain', 0.75)
			kickmess_add(kickmess_out, 'pub', 'e1_release', 0.1)
			kickmess_add(kickmess_out, 'priv', 'f1_type', 0.5)
			kickmess_add(kickmess_out, 'priv', 'f1_on', 0.25)
			kickmess_add(kickmess_out, 'priv', 'midi_chan', 0)
			kickmess_out.seek(0)
			list_vst.replace_data(instdata, 2, 'any', 'Kickmess (VST)', 'raw', kickmess_out.read(), None)
			if 'middlenote' in instdata: instdata['middlenote'] -= 12
			else: instdata['middlenote'] = -12

		if lmmsnat_name == 'lb302':
			params_vital.create()
			lb302_shape = lmmsnat_data['shape']
			if lb302_shape == 0: vital_shape = params_vital_wavetable.create_wave('saw', 0, None)
			if lb302_shape == 1: vital_shape = params_vital_wavetable.create_wave('triangle', 0, None)
			if lb302_shape == 2: vital_shape = params_vital_wavetable.create_wave('square', 0, 0.5)
			if lb302_shape == 3: vital_shape = params_vital_wavetable.create_wave('square_roundend', 0, None)
			if lb302_shape == 4: vital_shape = params_vital_wavetable.create_wave('mooglike', 0, None)
			if lb302_shape == 5: vital_shape = params_vital_wavetable.create_wave('sine', 0, None)
			if lb302_shape == 6: vital_shape = params_vital_wavetable.create_wave('exp', 0, None)
			if lb302_shape == 8: vital_shape = params_vital_wavetable.create_wave('saw', 0, None)
			if lb302_shape == 9: vital_shape = params_vital_wavetable.create_wave('square', 0, 0.5)
			if lb302_shape == 10: vital_shape = params_vital_wavetable.create_wave('triangle', 0, None)
			if lb302_shape == 11: vital_shape = params_vital_wavetable.create_wave('mooglike', 0, None)
			if lb302_shape != 7: 
				params_vital.setvalue('osc_1_on', 1)
				params_vital.replacewave(0, vital_shape)
			else: params_vital.setvalue('sample_on', 1)
			params_vital.setvalue('osc_1_level', 1)
			params_vital.setvalue('sample_level', 1)
			if lmmsnat_data['db24'] == 0:
				vitalcutoff_first = (lmmsnat_data['vcf_cut']*40)+50
				vitalcutoff_minus = (lmmsnat_data['vcf_mod']*16)
				params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (lmmsnat_data['vcf_mod']+0.5)*0.25, 0, 0, 0, 0)
			else:
				vitalcutoff_first = (lmmsnat_data['vcf_cut']*60)+20
				vitalcutoff_minus = (lmmsnat_data['vcf_mod']*20)
				params_vital.set_modulation(1, 'env_2', 'filter_fx_cutoff', (lmmsnat_data['vcf_mod']+0.2)*0.5, 0, 0, 0, 0)
			params_vital.setvalue('polyphony', 1)
			if lmmsnat_data['slide'] == 1:
				params_vital.setvalue('portamento_force', 1)
				params_vital.setvalue('portamento_slope', 5)
				params_vital.setvalue('portamento_time', (-5)+(pow(lmmsnat_data['slide_dec']*2, 2.5)))
			params_vital.setvalue('filter_fx_on', 1)
			params_vital.setvalue('filter_fx_cutoff', vitalcutoff_first-vitalcutoff_minus)
			params_vital.setvalue('filter_fx_resonance', lmmsnat_data['vcf_res']/1.7)
			if lmmsnat_data['dead'] == 0: params_vital.setvalue_timed('env_2_decay', 0.4+(lmmsnat_data['vcf_dec']*3))
			else: params_vital.setvalue_timed('env_2_decay', 0)
			params_vital.setvalue('env_2_sustain', 0)
			vitaldata = params_vital.getdata()
			list_vst.replace_data(instdata, 2, 'any', 'Vital', 'raw', vitaldata.encode('utf-8'), None)
			if 'middlenote' in instdata: instdata['middlenote'] -= 12
			else: instdata['middlenote'] = -12

	if pluginname == 'zynaddsubfx-lmms':				
		zasfxdata = instdata['plugindata']['data']
		zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
		zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
		list_vst.replace_data(instdata, 2, 'any', 'ZynAddSubFX', 'raw', zasfxdatafixed, None)
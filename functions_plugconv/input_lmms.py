# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import struct
import lxml.etree as ET
from functions import list_vst
from functions import params_vst
from functions import params_vital
from functions import params_vital_wavetable

def sid_addparam(x_sid, name, value):
    x_temp = ET.SubElement(x_sid, 'param')
    x_temp.set('uid', name)
    x_temp.set('val', str(value))

def sid_shape(lmms_sid_shape):
	if lmms_sid_shape == 0: return 3 #squ
	if lmms_sid_shape == 1: return 1 #tri
	if lmms_sid_shape == 2: return 2 #saw
	if lmms_sid_shape == 3: return 4 #noise

def convert_inst(instdata):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']
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
		sid_addparam(x_sid, "a1", lmmsnat_data['attack0'])
		sid_addparam(x_sid, "a2", lmmsnat_data['attack1'])
		sid_addparam(x_sid, "a3", lmmsnat_data['attack2'])
		sid_addparam(x_sid, "cutoff", lmmsnat_data['filterFC'])
		sid_addparam(x_sid, "d1", lmmsnat_data['decay0'])
		sid_addparam(x_sid, "d2", lmmsnat_data['decay1'])
		sid_addparam(x_sid, "d3", lmmsnat_data['decay2'])
		sid_addparam(x_sid, "f1", lmmsnat_data['filtered0'])
		sid_addparam(x_sid, "f2", lmmsnat_data['filtered1'])
		sid_addparam(x_sid, "f3", lmmsnat_data['filtered2'])
		sid_addparam(x_sid, "fine1", 0.0)
		sid_addparam(x_sid, "fine2", 0.0)
		sid_addparam(x_sid, "fine3", 0.0)
		if lmmsnat_data['filterMode'] == 0.0: sid_addparam(x_sid, "highpass", 1.0)
		else: sid_addparam(x_sid, "highpass", 0.0)
		if lmmsnat_data['filterMode'] == 1.0: sid_addparam(x_sid, "bandpass", 1.0)
		else: sid_addparam(x_sid, "bandpass", 0.0)
		if lmmsnat_data['filterMode'] == 2.0: sid_addparam(x_sid, "lowpass", 1.0)
		else: sid_addparam(x_sid, "lowpass", 0.0)
		sid_addparam(x_sid, "output3", lmmsnat_data['voice3Off'])
		sid_addparam(x_sid, "pw1", lmmsnat_data['pulsewidth0'])
		sid_addparam(x_sid, "pw2", lmmsnat_data['pulsewidth1'])
		sid_addparam(x_sid, "pw3", lmmsnat_data['pulsewidth2'])
		sid_addparam(x_sid, "r1", lmmsnat_data['release0'])
		sid_addparam(x_sid, "r2", lmmsnat_data['release1'])
		sid_addparam(x_sid, "r3", lmmsnat_data['release2'])
		sid_addparam(x_sid, "reso", lmmsnat_data['filterResonance'])
		sid_addparam(x_sid, "ring1", lmmsnat_data['ringmod0'])
		sid_addparam(x_sid, "ring2", lmmsnat_data['ringmod1'])
		sid_addparam(x_sid, "ring3", lmmsnat_data['ringmod2'])
		sid_addparam(x_sid, "s1", lmmsnat_data['sustain0'])
		sid_addparam(x_sid, "s2", lmmsnat_data['sustain1'])
		sid_addparam(x_sid, "s3", lmmsnat_data['sustain2'])
		sid_addparam(x_sid, "sync1", lmmsnat_data['sync0'])
		sid_addparam(x_sid, "sync2", lmmsnat_data['sync1'])
		sid_addparam(x_sid, "sync3", lmmsnat_data['sync2'])
		sid_addparam(x_sid, "tune1", lmmsnat_data['coarse0'])
		sid_addparam(x_sid, "tune2", lmmsnat_data['coarse1'])
		sid_addparam(x_sid, "tune3", lmmsnat_data['coarse2'])
		sid_addparam(x_sid, "voices", 8.0)
		sid_addparam(x_sid, "vol", lmmsnat_data['volume'])
		sid_addparam(x_sid, "w1", sid_shape(lmmsnat_data['waveform0']))
		sid_addparam(x_sid, "w2", sid_shape(lmmsnat_data['waveform1']))
		sid_addparam(x_sid, "w3", sid_shape(lmmsnat_data['waveform2']))
		list_vst.replace_data(instdata, 2, 'any', 'SID', 'raw', ET.tostring(x_sid, encoding='utf-8'), None)
		if 'middlenote' in instdata: instdata['middlenote'] -= 12
		else: instdata['middlenote'] = -12
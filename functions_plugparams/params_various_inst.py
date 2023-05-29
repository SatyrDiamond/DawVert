# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import io
import math

# -------------------- drops --------------------

def drops_init():
	global drops_samplefile
	global drops_params
	drops_samplefile = {'filepath': '','ui_sample_loaded': 'ui_sample_loaded yes/no'}
	drops_params = {'sample_in': 0.000000,'sample_out': 1.000000,'sample_loop_start': 0.000000,'sample_loop_end': 1.000000,'pitch_center': '60.000000','pitch': '100.000000','no_pitch': 0.000000,'playmode': 0.000000,'play_direction': 0.000000,'oversampling': 1.000000,'amp_attack': 0.000000,'amp_decay': 0.000000,'amp_sustain': 1.000000,'amp_release': 0.000000,'amp_lfo_type': 0.000000,'amp_lfo_sync': 0.000000,'amp_lfo_freq': 0.000000,'amp_lfo_sync_freq': 0.000000,'amp_lfo_depth': 0.000000,'amp_lfo_fade': 0.000000,'filter_type': 0.000000,'cutoff': 1.000000,'resonance': 1.000000,'filter_eg_depth': 0.000000,'filter_attack': 0.000000,'filter_decay': 0.000000,'filter_sustain': 0.000000,'filter_release': 0.000000,'filter_lfo_type': 0.000000,'filter_lfo_sync': 0.000000,'filter_lfo_freq': 0.000000,'filter_lfo_sync_freq': 0.000000,'filter_lfo_depth': 0.000000,'filter_lfo_fade': 0.000000,'pitch_eg_depth': 0.000000,'pitch_attack': 0.000000,'pitch_decay': 0.000000,'pitch_sustain': 0.000000,'pitch_release': 0.000000,'pitch_lfo_type': 0.000000}
def drops_setfile(value):
	global drops_samplefile
	drops_samplefile['filepath'] = value
def drops_setvalue(name, value):
	global drops_params
	drops_params[name] = value
def drops_get():
	global drops_samplefile
	global drops_params
	return [drops_samplefile, drops_params]
def drops_shape(input_val):
	output_val = 0
	if input_val == "triangle": output_val = 0.0
	if input_val == "sine": output_val = 1.0
	if input_val == "square": output_val = 2.0
	if input_val == "saw": output_val = 3.0
	if input_val == "saw up": output_val = 3.0
	if input_val == "saw down": output_val = 4.0
	if input_val == "random": output_val = 5.0
	return output_val

# -------------------- magical8bitplug --------------------
def shape_m8bp(pluginname, plugindata):
	m8p_root = ET.Element("root")
	m8p_params = ET.SubElement(m8p_root, "Params")
	m8bp_addvalue(m8p_params, "arpeggioDirection", 0.0)
	m8bp_addvalue(m8p_params, "arpeggioTime", 0.02999999932944775)
	m8bp_addvalue(m8p_params, "attack", 0.0)
	m8bp_addvalue(m8p_params, "bendRange", 12.0)
	m8bp_addvalue(m8p_params, "colorScheme", 1.0)
	m8bp_addvalue(m8p_params, "decay", 0.0)
	m8bp_addvalue(m8p_params, "duty", 0.0)
	m8bp_addvalue(m8p_params, "gain", 0.5)
	m8bp_addvalue(m8p_params, "isAdvancedPanelOpen_raw", 1.0)
	m8bp_addvalue(m8p_params, "isArpeggioEnabled_raw", 0.0)
	m8bp_addvalue(m8p_params, "isDutySequenceEnabled_raw", 0.0)
	m8bp_addvalue(m8p_params, "isVolumeSequenceEnabled_raw", 0.0)
	m8bp_addvalue(m8p_params, "maxPoly", 8.0)
	m8bp_addvalue(m8p_params, "noiseAlgorithm_raw", 0.0)
	if pluginname == 'shape-square':
		m8bp_addvalue(m8p_params, "osc", 0.0)
		m8bp_addvalue(m8p_params, "duty", 2.0)
	elif pluginname == 'shape-pulse':
		m8bp_addvalue(m8p_params, "osc", 0.0)
		if 'duty' in plugindata:
			if plugindata['duty'] == 0.25: m8bp_addvalue(m8p_params, "duty", 1.0)
			elif plugindata['duty'] == 0.125: m8bp_addvalue(m8p_params, "duty", 0.0)
			else: m8bp_addvalue(m8p_params, "duty", 0.0)
		else: m8bp_addvalue(m8p_params, "duty", 1.0)
	elif pluginname == 'shape-triangle':
		m8bp_addvalue(m8p_params, "osc", 1.0)
		m8bp_addvalue(m8p_params, "duty", 0.0)
	elif pluginname == 'retro-noise':
		m8bp_addvalue(m8p_params, "osc", 2.0)
		if 'type' in plugindata:
			if plugindata['type'] == '4bit': m8bp_addvalue(m8p_params, "duty", 0.0)
			elif plugindata['type'] == '1bit_long': m8bp_addvalue(m8p_params, "duty", 1.0)
			elif plugindata['type'] == '1bit_short': m8bp_addvalue(m8p_params, "duty", 2.0)
			else: m8bp_addvalue(m8p_params, "duty", 0.0)
		else: m8bp_addvalue(m8p_params, "duty", 0.0)
	else: m8bp_addvalue(m8p_params, "osc", 0.0)
	m8bp_addvalue(m8p_params, "pitchSequenceMode_raw", 0.0)
	m8bp_addvalue(m8p_params, "release", 0.0)
	m8bp_addvalue(m8p_params, "restrictsToNESFrequency_raw", 0.0)
	m8bp_addvalue(m8p_params, "suslevel", 1.0)
	m8bp_addvalue(m8p_params, "sweepInitialPitch", 0.0)
	m8bp_addvalue(m8p_params, "sweepTime", 0.1000000014901161)
	m8bp_addvalue(m8p_params, "vibratoDelay", 0.2999999821186066)
	m8bp_addvalue(m8p_params, "vibratoDepth", 0.0)
	m8bp_addvalue(m8p_params, "vibratoIgnoresWheel_raw", 1.0)
	m8bp_addvalue(m8p_params, "vibratoRate", 0.1500000059604645)
	return m8p_root

def m8bp_init():
	global m8bp_params
	global m8bp_params_env

	m8bp_params_env = {}
	m8bp_params_env["duty"] = None
	m8bp_params_env["pitch"] = None
	m8bp_params_env["volume"] = None

	m8bp_params = {}
	m8bp_params["arpeggioDirection"] = 0.0
	m8bp_params["arpeggioTime"] = 0.02999999932944775
	m8bp_params["attack"] = 0.0
	m8bp_params["bendRange"] = 12.0
	m8bp_params["colorScheme"] = 1.0
	m8bp_params["decay"] = 0.0
	m8bp_params["duty"] = 0.0
	m8bp_params["gain"] = 0.5
	m8bp_params["isAdvancedPanelOpen_raw"] = 1.0
	m8bp_params["isArpeggioEnabled_raw"] = 0.0
	m8bp_params["isPitchSequenceEnabled_raw"] = 0.0
	m8bp_params["isDutySequenceEnabled_raw"] = 0.0
	m8bp_params["isVolumeSequenceEnabled_raw"] = 0.0
	m8bp_params["maxPoly"] = 8.0
	m8bp_params["noiseAlgorithm_raw"] = 0.0
	m8bp_params["osc"] = 0.0
	m8bp_params["duty"] = 2.0
	m8bp_params["pitchSequenceMode_raw"] = 0.0
	m8bp_params["release"] = 0.0
	m8bp_params["restrictsToNESFrequency_raw"] = 0.0
	m8bp_params["suslevel"] = 1.0
	m8bp_params["sweepInitialPitch"] = 0.0
	m8bp_params["sweepTime"] = 0.1000000014901161
	m8bp_params["vibratoDelay"] = 0.2999999821186066
	m8bp_params["vibratoDepth"] = 0.0
	m8bp_params["vibratoIgnoresWheel_raw"] = 1.0
	m8bp_params["vibratoRate"] = 0.1500000059604645

def m8bp_setvalue(name, value):
	global m8bp_params
	m8bp_params[name] = value

def m8bp_setenv(name, value):
	global m8bp_params_env
	m8bp_params_env[name] = value

def m8bp_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, 'PARAM')
	temp_xml.set('id', str(name))
	temp_xml.set('value', str(value))

def m8bp_out():
	global m8bp_params
	global m8bp_params_env
	xml_m8p_root = ET.Element("root")
	xml_m8p_params = ET.SubElement(xml_m8p_root, "Params")
	for m8bp_param in m8bp_params:
		m8bp_addvalue(xml_m8p_params, m8bp_param, str(m8bp_params[m8bp_param]))

	m8p_dutyEnv = ET.SubElement(xml_m8p_root, "dutyEnv")
	m8p_pitchEnv = ET.SubElement(xml_m8p_root, "pitchEnv")
	m8p_volumeEnv = ET.SubElement(xml_m8p_root, "volumeEnv")

	if m8bp_params_env["duty"] != None: m8p_dutyEnv.text = ','.join(str(item) for item in m8bp_params_env["duty"])
	if m8bp_params_env["pitch"] != None: m8p_pitchEnv.text = ','.join(str(item) for item in m8bp_params_env["pitch"])
	if m8bp_params_env["volume"] != None: m8p_volumeEnv.text = ','.join(str(item) for item in m8bp_params_env["volume"])

	return xml_m8p_root

# -------------------- juicysfplugin --------------------
def juicysfplugin_create(bank, patch, filename):
	jsfp_xml = ET.Element("MYPLUGINSETTINGS")
	jsfp_params = ET.SubElement(jsfp_xml, "params")
	jsfp_uiState = ET.SubElement(jsfp_xml, "uiState")
	jsfp_soundFont = ET.SubElement(jsfp_xml, "soundFont")
	if 'bank' != None: jsfp_params.set('bank', str(bank/128))
	else: jsfp_params.set('bank', "0")
	if 'patch' != None: jsfp_params.set('preset', str(patch/128))
	else: jsfp_params.set('preset', "0")
	jsfp_params.set('attack', "0.0")
	jsfp_params.set('decay', "0.0")
	jsfp_params.set('sustain', "0.0")
	jsfp_params.set('release', "0.0")
	jsfp_params.set('filterCutOff', "0.0")
	jsfp_params.set('filterResonance', "0.0")
	jsfp_uiState.set('width', "500.0")
	jsfp_uiState.set('height', "300.0")
	if 'file' != None: jsfp_soundFont.set('path', filename)
	else: jsfp_soundFont.set('path', '')
	return jsfp_xml


# -------------------- grace --------------------
def grace_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, name)
	if value != None:
		temp_xml.text = value
def grace_create_main():
	gx_root = ET.Element("root")

	gx_GlobalParameters = ET.SubElement(gx_root, "GlobalParameters")
	grace_addvalue(gx_GlobalParameters, 'VoiceMode', 'Poly')
	grace_addvalue(gx_GlobalParameters, 'VoiceGlide', '0')

	gx_SampleGroup = ET.SubElement(gx_root, "SampleGroup")
	grace_addvalue(gx_SampleGroup, 'Name', 'Group 1')
	gx_VoiceParameters = ET.SubElement(gx_SampleGroup, "VoiceParameters")
	grace_addvalue(gx_VoiceParameters, 'AmpAttack', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpDecay', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpEnvSnap', 'SnapOff')
	grace_addvalue(gx_VoiceParameters, 'AmpHold', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpRelease', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpSustain', '1')
	grace_addvalue(gx_VoiceParameters, 'AmpVelocityDepth', 'Vel80')
	grace_addvalue(gx_VoiceParameters, 'Filter1KeyFollow', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par4', '1')
	grace_addvalue(gx_VoiceParameters, 'Filter1Type', 'ftNone')
	grace_addvalue(gx_VoiceParameters, 'Filter2KeyFollow', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par4', '1')
	grace_addvalue(gx_VoiceParameters, 'Filter2Type', 'ftNone')
	grace_addvalue(gx_VoiceParameters, 'FilterOutputBlend', '1')
	grace_addvalue(gx_VoiceParameters, 'FilterRouting', 'Serial')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'LfoFreqMode1', 'Fixed100Millisecond')
	grace_addvalue(gx_VoiceParameters, 'LfoFreqMode2', 'Fixed100Millisecond')
	grace_addvalue(gx_VoiceParameters, 'LfoShape1', 'Triangle')
	grace_addvalue(gx_VoiceParameters, 'LfoShape2', 'Triangle')
	grace_addvalue(gx_VoiceParameters, 'LoopEnd', '1')
	grace_addvalue(gx_VoiceParameters, 'LoopStart', '0')
	grace_addvalue(gx_VoiceParameters, 'ModAttack', '0')
	grace_addvalue(gx_VoiceParameters, 'ModDecay', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModEnvSnap', 'SnapOff')
	grace_addvalue(gx_VoiceParameters, 'ModHold', '0')
	grace_addvalue(gx_VoiceParameters, 'ModRelease', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModSustain', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModVelocityDepth', 'Vel80')
	grace_addvalue(gx_VoiceParameters, 'OutputGain', '0.5')
	grace_addvalue(gx_VoiceParameters, 'OutputPan', '0.504999995231628')
	grace_addvalue(gx_VoiceParameters, 'PitchTracking', 'Note')
	grace_addvalue(gx_VoiceParameters, 'SampleEnd', '1')
	grace_addvalue(gx_VoiceParameters, 'SampleReset', 'None')
	grace_addvalue(gx_VoiceParameters, 'SamplerLoopBounds', 'LoopPoints')
	grace_addvalue(gx_VoiceParameters, 'SamplerTriggerMode', 'LoopOff')
	grace_addvalue(gx_VoiceParameters, 'SampleStart', '0')
	grace_addvalue(gx_VoiceParameters, 'Seq1Clock', 'Div_4')
	grace_addvalue(gx_VoiceParameters, 'Seq1Direction', 'Forwards')
	grace_addvalue(gx_VoiceParameters, 'Seq2Clock', 'Div_4')
	grace_addvalue(gx_VoiceParameters, 'Seq2Direction', 'Forwards')
	grace_addvalue(gx_VoiceParameters, 'StepSeq1Length', 'Eight')
	grace_addvalue(gx_VoiceParameters, 'StepSeq2Length', 'Eight')
	grace_addvalue(gx_VoiceParameters, 'VoicePitchOne', '0.5')
	grace_addvalue(gx_VoiceParameters, 'VoicePitchTwo', '0.5')

	grace_addvalue(gx_root, 'PatchFileFormatVersion', '4')
	grace_addvalue(gx_root, 'PatchFileType', 'LucidityPatchFile')

	gx_PresetInfo = ET.SubElement(gx_root, "PresetInfo")
	grace_addvalue(gx_PresetInfo, 'PresetName', 'Defualt')
	grace_addvalue(gx_PresetInfo, 'PresetFileName', None)

	gx_MidiMap = ET.SubElement(gx_root, "MidiMap")

	return gx_root
def grace_create_region(gx_root, regionparams):
	gx_SampleGroup = gx_root.findall('SampleGroup')[0]
	gx_Region = ET.SubElement(gx_SampleGroup, "Region")
	gx_RegionProp = ET.SubElement(gx_Region, "RegionProperties")
	gx_SampleProp = ET.SubElement(gx_Region, "SampleProperties")

	FileName = ''

	if 'file' in regionparams: FileName = regionparams['file']
	grace_addvalue(gx_SampleProp, 'SampleFileName', str(FileName))

	LowNote = 0
	HighNote = 127
	LowVelocity = 0
	HighVelocity = 127
	RootNote = 60
	SampleStart = 0
	SampleEnd = 0
	LoopStart = -1
	LoopEnd = -1
	
	if 'r_key' in regionparams:
		LowNote = regionparams['r_key'][0] + 60
		HighNote = regionparams['r_key'][1] + 60

	if 'r_vol' in regionparams:
		LowVelocity = int(regionparams['vol'][0]*127)
		HighVelocity = int(regionparams['vol'][1]*127)

	if 'loop' in regionparams:
		if regionparams['loop']['enabled'] == 1:
			LoopStart = regionparams['loop']['points'][0]
			LoopEnd = regionparams['loop']['points'][1]

	if 'middlenote' in regionparams: RootNote = regionparams['middlenote'] + 60
	if 'start' in regionparams: SampleStart = regionparams['start']
	if 'end' in regionparams: SampleEnd = regionparams['end'] - 1

	grace_addvalue(gx_RegionProp, 'LowNote', str(LowNote))
	grace_addvalue(gx_RegionProp, 'HighNote', str(HighNote))
	grace_addvalue(gx_RegionProp, 'LowVelocity', str(LowVelocity))
	grace_addvalue(gx_RegionProp, 'HighVelocity', str(HighVelocity))
	grace_addvalue(gx_RegionProp, 'RootNote', str(RootNote))
	grace_addvalue(gx_RegionProp, 'SampleStart', str(SampleStart))
	grace_addvalue(gx_RegionProp, 'SampleEnd', str(SampleEnd))
	grace_addvalue(gx_SampleProp, 'SampleFrames', str(SampleEnd))
	grace_addvalue(gx_RegionProp, 'LoopStart', str(LoopStart))
	grace_addvalue(gx_RegionProp, 'LoopEnd', str(LoopEnd))

	SampleVolume = 0
	SamplePan = 0
	SampleTune = 0
	SampleFine = 0

	grace_addvalue(gx_RegionProp, 'SampleVolume', str(SampleVolume))
	grace_addvalue(gx_RegionProp, 'SamplePan', str(SamplePan))
	grace_addvalue(gx_RegionProp, 'SampleTune', str(SampleTune))
	grace_addvalue(gx_RegionProp, 'SampleFine', str(SampleFine))

	SampleBeats = 4

	grace_addvalue(gx_RegionProp, 'SampleBeats', str(SampleBeats))

	return gx_root

# -------------------- opn2 > opnplug --------------------

def opnplug_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, 'VALUE')
	temp_xml.set('name', str(name))
	temp_xml.set('val', str(value))

def opnplug_addbank(xmltag, num, name):
	bank_xml = ET.SubElement(xmltag, 'bank')
	opnplug_addvalue(bank_xml, 'bank', num)
	opnplug_addvalue(bank_xml, 'name', name)

def opnplug_op_params(xmltag, opnum, plugindata):
	opdata = plugindata["op"+str(opnum)]
	opnplug_addvalue(xmltag, "op"+str(opnum)+"detune" ,opdata["detune"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"fmul" ,opdata["freqmul"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"level" ,opdata["level"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ratescale" ,opdata["ratescale"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"attack" ,opdata["env_attack"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"am" ,opdata["am"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"decay1" ,opdata["env_decay"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"decay2" ,opdata["env_decay2"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"sustain" ,opdata["env_sustain"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"release" ,opdata["env_release"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ssgenable" ,opdata["ssg_enable"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ssgwave" ,opdata["ssg_mode"])

def opnplug_convert(plugindata):
	opnplug_root = ET.Element("ADLMIDI-state")
	opnplug_addbank(opnplug_root, 1, 'DawVert')
	opnplug_params = ET.SubElement(opnplug_root, 'instrument')
	opnplug_addvalue(opnplug_params, "blank" ,0)
	opnplug_addvalue(opnplug_params, "note_offset" ,0)
	opnplug_addvalue(opnplug_params, "feedback" ,plugindata["feedback"])
	opnplug_addvalue(opnplug_params, "algorithm" ,plugindata["algorithm"])
	opnplug_addvalue(opnplug_params, "ams" ,0)
	opnplug_addvalue(opnplug_params, "fms" ,0)
	opnplug_addvalue(opnplug_params, "midi_velocity_offset" ,0)
	opnplug_addvalue(opnplug_params, "percussion_key_number" ,0)
	for opnum in range(4):
		opnplug_op_params(opnplug_params, opnum+1, plugindata)

	opnplug_addvalue(opnplug_params, "delay_off_ms" ,120)
	opnplug_addvalue(opnplug_params, "delay_on_ms" ,486)
	opnplug_addvalue(opnplug_params, "bank" ,0)
	opnplug_addvalue(opnplug_params, "program" ,0)
	opnplug_addvalue(opnplug_params, "name" ,'DawVert')
	#print(ET.tostring(opnplug_params, encoding='utf-8'))
	#exit()

	opnplug_selection = ET.SubElement(opnplug_root, 'selection')
	opnplug_addvalue(opnplug_selection, "part" ,0)
	opnplug_addvalue(opnplug_selection, "bank" ,0)
	opnplug_addvalue(opnplug_selection, "program" ,0)

	opnplug_chip = ET.SubElement(opnplug_root, 'chip')
	opnplug_addvalue(opnplug_chip, "emulator" ,0)
	opnplug_addvalue(opnplug_chip, "chip_count" ,1)
	opnplug_addvalue(opnplug_chip, "chip_type" ,0)

	opnplug_global = ET.SubElement(opnplug_root, 'global')
	opnplug_addvalue(opnplug_global, "volume_model" ,0)
	opnplug_addvalue(opnplug_global, "lfo_enable" ,1)
	opnplug_addvalue(opnplug_global, "lfo_frequency" ,1)

	opnplug_common = ET.SubElement(opnplug_root, 'common')
	opnplug_addvalue(opnplug_common, "bank_title" ,'DawVert')
	opnplug_addvalue(opnplug_common, "part" ,0)
	opnplug_addvalue(opnplug_common, "master_volume" ,2.0)

	return opnplug_root

# -------------------- ninjas2 --------------------

def ninjas2_create_blank_prog():
	progout = ''
	progtext = '0 0 0 0.001000 0.001000 1.000000 0.001000 '
	progout += '1 '
	for _ in range(128): progout += progtext
	return progout

def ninjas2_init():
	global ninjas2_data_progs
	global ninjas2_data_main
	ninjas2_data_main = {}
	ninjas2_data_progs = {}

	ninjas2_data_main['number_of_slices'] = '0.000000'
	ninjas2_data_main['sliceSensitivity'] = '0.500000'
	ninjas2_data_main['attack'] = '0.001000'
	ninjas2_data_main['decay'] = '0.001000'
	ninjas2_data_main['sustain'] = '1.000000'
	ninjas2_data_main['release'] = '0.001000'
	ninjas2_data_main['load'] = '0.000000'
	ninjas2_data_main['slicemode'] = '1.000000'
	ninjas2_data_main['programGrid'] = '1.000000'
	ninjas2_data_main['playmode'] = '0.000000'
	ninjas2_data_main['pitchbendDepth'] = '12.000000'
	ninjas2_data_main['OneShotForward'] = '1.000000'
	ninjas2_data_main['OneShotReverse'] = '0.000000'
	ninjas2_data_main['LoopForward'] = '0.000000'
	ninjas2_data_main['LoopReverse'] = '0.000000'

	ninjas2_data_progs['slices'] = 'empty'
	ninjas2_data_progs['filepathFromUI'] = ''
	ninjas2_data_progs['program00'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program01'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program02'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program03'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program04'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program05'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program06'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program07'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program08'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program09'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program10'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program11'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program12'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program13'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program14'] = ninjas2_create_blank_prog()
	ninjas2_data_progs['program15'] = ninjas2_create_blank_prog()

def ninjas2_slicerdata(slicerdata):
	global ninjas2_data_progs
	global ninjas2_data_main
	ninjas2_data_progs['filepathFromUI'] = slicerdata['file']
	if 'slices' in slicerdata:
		slices = slicerdata['slices']
		progtable = []
		
		releasevalue = '0.001000'
		if 'trigger' in slicerdata:
			print(slicerdata['trigger'])
			if slicerdata['trigger'] == 'normal': releasevalue = '0.001000'
			if slicerdata['trigger'] == 'oneshot': releasevalue = '1.000000'

		for _ in range(127): progtable.append('0 0 0 0.001000 0.001000 1.000000 '+releasevalue+' ')

		ninjas2_data_main['release'] = releasevalue

		progout = ''
		progout += str(len(slices))+' 128 '
		ninjas2_data_main['number_of_slices'] = str(len(slices))

		for slicenum in range(len(slices)):
			slicedata = slices[slicenum]
			s_reverse = False
			s_looped = False
			if 'reverse' in slicedata: 
				if slicedata['reverse'] == 1: s_reverse = True
			if 'looped' in slicedata: 
				if slicedata['looped'] == 1: s_looped = True
			ninjas2_loopout = 0
			if s_reverse == True: ninjas2_loopout += 1
			if s_looped == True: ninjas2_loopout += 2
			progtable[slicenum] = str(slicedata['pos']*2)+' '+str(slicedata['end']*2)+' '+str(ninjas2_loopout)+' 0.001000 0.001000 1.000000 '+releasevalue

		for prognums in progtable: progout += prognums+' '
		ninjas2_data_progs['program00'] = progout


def ninjas2_get():
	global ninjas2_data_progs
	global ninjas2_data_main
	return [ninjas2_data_progs, ninjas2_data_main]

# -------------------- kickmess --------------------

def kickmess_init():
	global kickmess_params
	kickmess_params = {}
	kickmess_params['pub'] = {}
	kickmess_params['pub']['freq_start'] = 440
	kickmess_params['pub']['freq_end'] = 440
	kickmess_params['pub']['f_env_release'] = 1000
	kickmess_params['pub']['dist_start'] = 0
	kickmess_params['pub']['dist_end'] = 0
	kickmess_params['pub']['gain'] = 0.5
	kickmess_params['pub']['env_slope'] = 0.5
	kickmess_params['pub']['freq_slope'] = 0.5
	kickmess_params['pub']['noise'] = 0
	kickmess_params['pub']['freq_note_start'] = 0.25
	kickmess_params['pub']['freq_note_end'] = 0.25
	kickmess_params['pub']['env_release'] = 0
	kickmess_params['pub']['phase_offs'] = 0
	kickmess_params['pub']['dist_on'] = 0
	kickmess_params['pub']['f1_cutoff'] = 1
	kickmess_params['pub']['f1_res'] = 0
	kickmess_params['pub']['f1_drive'] = 0.2
	kickmess_params['pub']['main_gain'] = 0.70710677
	kickmess_params['pub']['e1_attack'] = 0.1
	kickmess_params['pub']['e1_decay'] = 0.14142135
	kickmess_params['pub']['e1_sustain'] = 0.75
	kickmess_params['pub']['e1_release'] = 0.1
	kickmess_params['priv'] = {}
	kickmess_params['priv']['f1_type'] = 0.5
	kickmess_params['priv']['f1_on'] = 0.25
	kickmess_params['priv']['midi_chan'] = 0

def kickmess_setvalue(i_cat, i_name, i_value):
	global kickmess_params
	kickmess_params[i_cat][i_name] = i_value

def kickmess_add(bio_data, i_cat, i_name, i_value):
	kickmess_text = i_cat+' : '+i_name+'='+str(i_value)+';\n'
	bio_data.write(str.encode(kickmess_text))

def kickmess_get():
	global kickmess_params

	kickmess_out = io.BytesIO()
	kickmess_out.write(b'!PARAMS;\n')

	for paramcat in kickmess_params:
		for paramval in kickmess_params[paramcat]:
			o_value = kickmess_params[paramcat][paramval]
			if paramval in ['freq_start']: o_value = math.sqrt((o_value-2.51)/3000)
			if paramval in ['freq_end']: o_value = math.sqrt((o_value-2.51)/2000)
			if paramval in ['f_env_release']: 
				if o_value > 2.4: o_value = math.sqrt((o_value-2.51)/5000)
			kickmess_add(kickmess_out, paramcat, paramval, o_value)

	kickmess_out.seek(0)
	return kickmess_out.read()
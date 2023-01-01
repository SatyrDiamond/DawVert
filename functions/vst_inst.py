
import xml.etree.ElementTree as ET

# -------------------- magical8bitplug --------------------
def m8bp_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, 'PARAM')
	temp_xml.set('id', str(name))
	temp_xml.set('value', str(value))
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
	ninjas2_data_main['OneShotForward'] = '0.000000'
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
		for _ in range(127): progtable.append('0 0 0 0.001000 0.001000 1.000000 0.001000')
		
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
			progtable[slicenum] = str(slicedata['pos']*2)+' '+str(slicedata['end']*2)+' '+str(ninjas2_loopout)+' 0.001000 0.001000 1.000000 0.001000'

		for prognums in progtable: progout += prognums+' '
		ninjas2_data_progs['program00'] = progout


def ninjas2_get():
	global ninjas2_data_progs
	global ninjas2_data_main
	return [ninjas2_data_progs, ninjas2_data_main]

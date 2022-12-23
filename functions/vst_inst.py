
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
	else:jsfp_params.set('bank', "0")
	if 'patch' != None: jsfp_params.set('preset', str(patch/128))
	else:jsfp_params.set('preset', "0")
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

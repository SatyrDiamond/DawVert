# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import configparser
import base64
import xml.etree.ElementTree as ET
import pathlib
from os.path import exists
from functions import audio_wav

def xml_addvalue(xmltag, name, value):
    temp_xml = ET.SubElement(xmltag, name)
    if value != None:
        temp_xml.text = value

def complete_wav_info(sampler_file_data):
	if exists(sampler_file_data['file']) == True and pathlib.Path(sampler_file_data['file']).suffix == '.wav':
		wavinfo = audio_wav.decode(sampler_file_data['file'])
		sampler_file_data['length'] = wavinfo[0]['length']
		wavformat = wavinfo[0]['format']
		returnvalue = None
		if wavinfo[2] != {}:
			if 'loops' in wavinfo[2]:
				if wavinfo[2]['loops'] != {}:
					if 'loops' not in sampler_file_data:
						sampler_file_data['loops'] = {}
					wavloopdata = wavinfo[2]['loops'][next(iter(wavinfo[2]['loops']))]
					sampler_file_data['loops']['points'] = [wavloopdata['start'], wavloopdata['end']]
		return wavformat
	return None

def grace_create_main():
    gx_root = ET.Element("root")

    gx_GlobalParameters = ET.SubElement(gx_root, "GlobalParameters")
    xml_addvalue(gx_GlobalParameters, 'VoiceMode', 'Poly')
    xml_addvalue(gx_GlobalParameters, 'VoiceGlide', '0')

    gx_SampleGroup = ET.SubElement(gx_root, "SampleGroup")
    xml_addvalue(gx_SampleGroup, 'Name', 'Group 1')
    gx_VoiceParameters = ET.SubElement(gx_SampleGroup, "VoiceParameters")
    xml_addvalue(gx_VoiceParameters, 'AmpAttack', '0')
    xml_addvalue(gx_VoiceParameters, 'AmpDecay', '0')
    xml_addvalue(gx_VoiceParameters, 'AmpEnvSnap', 'SnapOff')
    xml_addvalue(gx_VoiceParameters, 'AmpHold', '0')
    xml_addvalue(gx_VoiceParameters, 'AmpRelease', '0')
    xml_addvalue(gx_VoiceParameters, 'AmpSustain', '1')
    xml_addvalue(gx_VoiceParameters, 'AmpVelocityDepth', 'Vel80')
    xml_addvalue(gx_VoiceParameters, 'Filter1KeyFollow', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter1Par1', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter1Par2', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter1Par3', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter1Par4', '1')
    xml_addvalue(gx_VoiceParameters, 'Filter1Type', 'ftNone')
    xml_addvalue(gx_VoiceParameters, 'Filter2KeyFollow', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter2Par1', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter2Par2', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter2Par3', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Filter2Par4', '1')
    xml_addvalue(gx_VoiceParameters, 'Filter2Type', 'ftNone')
    xml_addvalue(gx_VoiceParameters, 'FilterOutputBlend', '1')
    xml_addvalue(gx_VoiceParameters, 'FilterRouting', 'Serial')
    xml_addvalue(gx_VoiceParameters, 'Lfo1Par1', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Lfo1Par2', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Lfo1Par3', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Lfo2Par1', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Lfo2Par2', '0.5')
    xml_addvalue(gx_VoiceParameters, 'Lfo2Par3', '0.5')
    xml_addvalue(gx_VoiceParameters, 'LfoFreqMode1', 'Fixed100Millisecond')
    xml_addvalue(gx_VoiceParameters, 'LfoFreqMode2', 'Fixed100Millisecond')
    xml_addvalue(gx_VoiceParameters, 'LfoShape1', 'Triangle')
    xml_addvalue(gx_VoiceParameters, 'LfoShape2', 'Triangle')
    xml_addvalue(gx_VoiceParameters, 'LoopEnd', '1')
    xml_addvalue(gx_VoiceParameters, 'LoopStart', '0')
    xml_addvalue(gx_VoiceParameters, 'ModAttack', '0')
    xml_addvalue(gx_VoiceParameters, 'ModDecay', '0.300000011920929')
    xml_addvalue(gx_VoiceParameters, 'ModEnvSnap', 'SnapOff')
    xml_addvalue(gx_VoiceParameters, 'ModHold', '0')
    xml_addvalue(gx_VoiceParameters, 'ModRelease', '0.300000011920929')
    xml_addvalue(gx_VoiceParameters, 'ModSustain', '0.300000011920929')
    xml_addvalue(gx_VoiceParameters, 'ModVelocityDepth', 'Vel80')
    xml_addvalue(gx_VoiceParameters, 'OutputGain', '0.5')
    xml_addvalue(gx_VoiceParameters, 'OutputPan', '0.504999995231628')
    xml_addvalue(gx_VoiceParameters, 'PitchTracking', 'Note')
    xml_addvalue(gx_VoiceParameters, 'SampleEnd', '1')
    xml_addvalue(gx_VoiceParameters, 'SampleReset', 'None')
    xml_addvalue(gx_VoiceParameters, 'SamplerLoopBounds', 'LoopPoints')
    xml_addvalue(gx_VoiceParameters, 'SamplerTriggerMode', 'LoopOff')
    xml_addvalue(gx_VoiceParameters, 'SampleStart', '0')
    xml_addvalue(gx_VoiceParameters, 'Seq1Clock', 'Div_4')
    xml_addvalue(gx_VoiceParameters, 'Seq1Direction', 'Forwards')
    xml_addvalue(gx_VoiceParameters, 'Seq2Clock', 'Div_4')
    xml_addvalue(gx_VoiceParameters, 'Seq2Direction', 'Forwards')
    xml_addvalue(gx_VoiceParameters, 'StepSeq1Length', 'Eight')
    xml_addvalue(gx_VoiceParameters, 'StepSeq2Length', 'Eight')
    xml_addvalue(gx_VoiceParameters, 'VoicePitchOne', '0.5')
    xml_addvalue(gx_VoiceParameters, 'VoicePitchTwo', '0.5')

    xml_addvalue(gx_root, 'PatchFileFormatVersion', '4')
    xml_addvalue(gx_root, 'PatchFileType', 'LucidityPatchFile')

    gx_PresetInfo = ET.SubElement(gx_root, "PresetInfo")
    xml_addvalue(gx_PresetInfo, 'PresetName', 'Defualt')
    xml_addvalue(gx_PresetInfo, 'PresetFileName', None)

    gx_MidiMap = ET.SubElement(gx_root, "MidiMap")

    return gx_root

def grace_create_region(gx_root, regionparams):
    gx_SampleGroup = gx_root.findall('SampleGroup')[0]
    gx_Region = ET.SubElement(gx_SampleGroup, "Region")
    gx_RegionProp = ET.SubElement(gx_Region, "RegionProperties")
    gx_SampleProp = ET.SubElement(gx_Region, "SampleProperties")

    FileName = ''

    if 'filename' in regionparams: FileName = regionparams['filename']
    xml_addvalue(gx_SampleProp, 'SampleFileName', str(FileName))

    LowNote = 0
    HighNote = 127
    LowVelocity = 0
    HighVelocity = 127
    RootNote = 60
    SampleStart = 0
    SampleEnd = 173181
    LoopStart = -1
    LoopEnd = -1
    
    if 'note' in regionparams:
        LowNote = regionparams['note'][0] + 60
        HighNote = regionparams['note'][1] + 60

    if 'velocity' in regionparams:
        LowVelocity = int(regionparams['velocity'][0]*127)
        HighVelocity = int(regionparams['velocity'][1]*127)

    if 'loop' in regionparams:
        LoopStart = regionparams['loop'][0]
        LoopEnd = regionparams['loop'][1]

    if 'middlenote' in regionparams: RootNote = regionparams['middlenote'] + 60
    if 'start' in regionparams: SampleStart = regionparams['start']
    if 'length' in regionparams: SampleEnd = regionparams['length'] - 1

    xml_addvalue(gx_RegionProp, 'LowNote', str(LowNote))
    xml_addvalue(gx_RegionProp, 'HighNote', str(HighNote))
    xml_addvalue(gx_RegionProp, 'LowVelocity', str(LowVelocity))
    xml_addvalue(gx_RegionProp, 'HighVelocity', str(HighVelocity))
    xml_addvalue(gx_RegionProp, 'RootNote', str(RootNote))
    xml_addvalue(gx_RegionProp, 'SampleStart', str(SampleStart))
    xml_addvalue(gx_RegionProp, 'SampleEnd', str(SampleEnd))
    xml_addvalue(gx_SampleProp, 'SampleFrames', str(SampleEnd))
    xml_addvalue(gx_RegionProp, 'LoopStart', str(LoopStart))
    xml_addvalue(gx_RegionProp, 'LoopEnd', str(LoopEnd))

    SampleVolume = 0
    SamplePan = 0
    SampleTune = 0
    SampleFine = 0

    xml_addvalue(gx_RegionProp, 'SampleVolume', str(SampleVolume))
    xml_addvalue(gx_RegionProp, 'SamplePan', str(SamplePan))
    xml_addvalue(gx_RegionProp, 'SampleTune', str(SampleTune))
    xml_addvalue(gx_RegionProp, 'SampleFine', str(SampleFine))

    SampleBeats = 4

    xml_addvalue(gx_RegionProp, 'SampleBeats', str(SampleBeats))

    return gx_root

vstpaths = configparser.ConfigParser()
vstpaths.read('vst.ini')

def convplug_inst(instdata, dawname):
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

# -------------------- sampler > vst (Grace) --------------------
			if pluginname == 'sampler' and dawname not in supportedplugins['sampler']:
				sampler_data = instdata
				sampler_file_data = instdata['plugindata']
				wireturn = complete_wav_info(sampler_file_data)
				if 'file' in sampler_file_data and wireturn != None and wireturn == 1:
					file_extension = pathlib.Path(sampler_file_data['file']).suffix
					if file_extension == '.wav':
						gx_root = grace_create_main()
						regionparams = {}
						regionparams['filename'] = sampler_file_data['file']
						regionparams['length'] = sampler_file_data['length']
						regionparams['start'] = 0
						if 'loops' in sampler_file_data:
							if 'points' in sampler_file_data['loops']:
								regionparams['loop'] = sampler_file_data['loops']['points']
						grace_create_region(gx_root, regionparams)
						xmlout = ET.tostring(gx_root, encoding='utf-8')
						print('[plugin-convert] plugin: sampler > Grace (VST)')
						instdata['plugin'] = 'vst'
						instdata['plugindata'] = {}
						instdata['plugindata']['plugin'] = {}
						instdata['plugindata']['plugin']['name'] = 'Grace'
						if 'Grace' in vstpaths:
							instdata['plugindata']['plugin']['path'] = vstpaths['Grace']['path']
						instdata['plugindata']['data'] = base64.b64encode(xmlout).decode('ascii')
				else:
					print("[plugin-convert] plugin: unchanged - Grace (VST) only supports '.wav' and format 1")

# -------------------- sf2 > vst (juicysfplugin) --------------------
			elif pluginname == 'soundfont2' and dawname not in supportedplugins['sf2']:
				print('[plugin-convert] plugin: soundfont2 > juicysfplugin (VST)')
				instdata['plugin'] = 'vst'
				sf2data = instdata['plugindata']
				instdata['plugindata'] = {}
				instdata['plugindata']['plugin'] = {}
				instdata['plugindata']['plugin']['name'] = 'juicysfplugin'
				if 'juicysfplugin' in vstpaths:
					instdata['plugindata']['plugin']['path'] = vstpaths['juicysfplugin']['path']
				jsfp_xml = ET.Element("MYPLUGINSETTINGS")
				jsfp_params = ET.SubElement(jsfp_xml, "params")
				jsfp_uiState = ET.SubElement(jsfp_xml, "uiState")
				jsfp_soundFont = ET.SubElement(jsfp_xml, "soundFont")
				if 'bank' in sf2data: jsfp_params.set('bank', str(sf2data['bank']/128))
				else:jsfp_params.set('bank', "0")
				if 'patch' in sf2data: jsfp_params.set('preset', str(sf2data['patch']/128))
				else:jsfp_params.set('preset', "0")
				jsfp_params.set('attack', "0.0")
				jsfp_params.set('decay', "0.0")
				jsfp_params.set('sustain', "0.0")
				jsfp_params.set('release', "0.0")
				jsfp_params.set('filterCutOff', "0.0")
				jsfp_params.set('filterResonance', "0.0")
				jsfp_uiState.set('width', "500.0")
				jsfp_uiState.set('height', "300.0")
				if 'file' in sf2data: jsfp_soundFont.set('path', sf2data['file'])
				else: jsfp_soundFont.set('path', '')
				xmlout = ET.tostring(jsfp_xml, encoding='utf-8')
				vstdata = b'VC2!' + len(xmlout).to_bytes(4, "little") + xmlout
				instdata['plugindata']['data'] = base64.b64encode(vstdata).decode('ascii')

# -------------------- zynaddsubfx - from lmms --------------------
			elif pluginname == 'zynaddsubfx' and dawname != 'lmms':
				print('[plugin-convert] plugin: zynaddsubfx > ZynAddSubFX (VST)')
				instdata['plugin'] = 'vst'
				zasfxdata = instdata['plugindata']['data']
				instdata['plugindata'] = {}
				instdata['plugindata']['plugin'] = {}
				instdata['plugindata']['plugin']['name'] = 'ZynAddSubFX-2'
				if 'ZynAddSubFX' in vstpaths:
					instdata['plugindata']['plugin']['path'] = vstpaths['ZynAddSubFX-2']['path']
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
				instdata['plugindata']['data'] = base64.b64encode(zasfxdatafixed).decode('ascii')

			else:
				print('[plugin-convert] plugin: unchanged')

def convproj(cvpjdata, cvpjtype, dawname):
	global supportedplugins
	supportedplugins = {}
	supportedplugins['sf2'] = ['lmms', 'fl']
	supportedplugins['sampler'] = ['lmms', 'fl']
	cvpj_l = json.loads(cvpjdata)
	if cvpjtype == 'r':
		if 'trackdata' in cvpj_l:
			for track in cvpj_l['trackdata']:
				trackdata = cvpj_l['trackdata'][track]
				if 'type' in trackdata:
					if trackdata['type'] == 'instrument':
						if 'instdata' in trackdata:
							instdata = trackdata['instdata']
							convplug_inst(instdata, dawname)
	if cvpjtype == 'm' or cvpjtype == 'mi':
		if 'instruments' in cvpj_l:
			for track in cvpj_l['instruments']:
				trackdata = cvpj_l['instruments'][track]
				if 'instdata' in trackdata:
					instdata = trackdata['instdata']
					convplug_inst(instdata, dawname)
	return json.dumps(cvpj_l, indent=2)
# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import configparser
import base64
import xml.etree.ElementTree as ET
import pathlib
from os.path import exists
from functions import audio_wav

global vst2paths
global vst3paths

global vst2path_loaded
global vst3path_loaded

vst2path_loaded = False
vst3path_loaded = False

# -------------------- Sampler --------------------

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

    if 'filename' in regionparams: FileName = regionparams['filename']
    grace_addvalue(gx_SampleProp, 'SampleFileName', str(FileName))

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

# -------------------- VST List --------------------
def replace_vst(instdata, name, data):
	change_ok = 0
	vst_path = ''
	if vst2path_loaded == True:
		if name in vst2paths:
			if 'path64' in vst2paths[name]: 
				vst_path = vst2paths[name]['path64']
				print('[plugin-convert] Plugin: ' + instdata['plugin'] +' > ' + name + ' (VST2 64-bit)')
				change_ok = 1
			elif 'path32' in vst2paths[name]: 
				vst_path = vst2paths[name]['path32']
				print('[plugin-convert] Plugin: ' + instdata['plugin'] +' > ' + name + ' (VST2 32-bit)')
				change_ok = 1
			else:
				print('[plugin-convert] Unchanged,', 'Plugin path of ' + name + ' not Found')
		else: 
			instdata['plugindata']['plugin']['path'] = ''
			print('[plugin-convert] Unchanged,', 'Plugin ' + name + ' not Found')
	else: 
		instdata['plugindata']['plugin']['path'] = ''
		print('[plugin-convert] Unchanged,', "VST2 list not found")
	if change_ok == 1:
		instdata['plugin'] = 'vst2'
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['data'] = base64.b64encode(data).decode('ascii')
def vstlist_init(osplatform):
	global vst2paths
	global vst3paths
	global vst2path_loaded
	global vst3path_loaded
	if osplatform == 'windows':
		if exists('vst2_win.ini'):
			vst2paths = configparser.ConfigParser()
			vst2paths.read('vst2_win.ini')
			vst2path_loaded = True
			print('[plugin-convert] # of VST2 Plugins:', len(vst2paths))
		if exists('vst3_win.ini'):
			vst3paths = configparser.ConfigParser()
			vst3paths.read('vst3_win.ini')
			vst2path_loaded = True
			print('[plugin-convert] # of VST3 Plugins:', len(vst3paths))

def convplug_inst(instdata, dawname):
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

# -------------------- sampler > vst2 (Grace) --------------------
			if pluginname == 'sampler' and dawname not in supportedplugins['sampler']:
				sampler_data = instdata
				sampler_file_data = instdata['plugindata']
				wireturn = audio_wav.complete_wav_info(sampler_file_data)
				if vst2path_loaded == True:
					if 'Grace' in vst2paths:
						if 'file' in sampler_file_data and wireturn != None and wireturn == 1:
							file_extension = pathlib.Path(sampler_file_data['file']).suffix
							if file_extension == '.wav':
								gx_root = grace_create_main()
								regionparams = {}
								regionparams['filename'] = sampler_file_data['file']
								regionparams['length'] = sampler_file_data['length']
								regionparams['start'] = 0
								if 'loop' in sampler_file_data:
									if 'points' in sampler_file_data['loop']:
										regionparams['loop'] = sampler_file_data['loop']['points']
								grace_create_region(gx_root, regionparams)
								xmlout = ET.tostring(gx_root, encoding='utf-8')
								replace_vst(instdata, 'Grace', xmlout)
						else:
							print("[plugin-convert] Unchanged, Grace (VST2) only supports Format 1 .WAV")
					else:
						print('[plugin-convert] Unchanged, Plugin Grace not Found')
				else:
					print('[plugin-convert] Unchanged, VST2 list not found')
# -------------------- sf2 > vst2 (juicysfplugin) --------------------
			elif pluginname == 'soundfont2' and dawname not in supportedplugins['sf2']:
				sf2data = instdata['plugindata']
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
				vst2data = b'VC2!' + len(xmlout).to_bytes(4, "little") + xmlout
				replace_vst(instdata, 'juicysfplugin', vst2data)

# -------------------- zynaddsubfx - from lmms --------------------
			elif pluginname == 'zynaddsubfx' and dawname != 'lmms':
				zasfxdata = instdata['plugindata']['data']
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
				replace_vst(instdata, 'ZynAddSubFX', zasfxdatafixed)

			else:
				print('[plugin-convert] Unchanged')

def convproj(cvpjdata, cvpjtype, dawname):
	global supportedplugins
	vstlist_init('windows')
	supportedplugins = {}
	supportedplugins['sf2'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
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
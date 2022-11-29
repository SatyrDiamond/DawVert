# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import configparser
import base64
import xml.etree.ElementTree as ET

vstpaths = configparser.ConfigParser()
vstpaths.read('vst.ini')

def convplug_inst(instdata, dawname):
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

# -------------------- zynaddsubfx - from lmms --------------------
			if pluginname == 'zynaddsubfx' and dawname != 'lmms':
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

# -------------------- sf2 - from lmms --------------------
			if pluginname == 'soundfont2' and dawname not in supportedplugins['sf2']:
				print('[plugin-convert] plugin: soundfont2 > juicysfplugin (VST)')
				instdata['plugin'] = 'vst'
				sf2data = instdata['plugindata']
				print(sf2data)
				instdata['plugindata'] = {}
				instdata['plugindata']['plugin'] = {}
				instdata['plugindata']['plugin']['name'] = 'juicysfplugin'
				if 'juicysfplugin' in vstpaths:
					instdata['plugindata']['plugin']['path'] = vstpaths['juicysfplugin']['path']
				jsfp_xml = ET.Element("MYPLUGINSETTINGS")
				jsfp_params = ET.SubElement(jsfp_xml, "params")
				jsfp_uiState = ET.SubElement(jsfp_xml, "uiState")
				jsfp_soundFont = ET.SubElement(jsfp_xml, "soundFont")
				print(ET.tostring(jsfp_xml, encoding='utf-8'))
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
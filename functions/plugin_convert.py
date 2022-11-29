# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import configparser
import base64

vstpaths = configparser.ConfigParser()
vstpaths.read('vst.ini')

def convplug_inst(instdata, dawname):
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

# -------------------- zynaddsubfx - from lmms --------------------
			if pluginname == 'zynaddsubfx' and dawname != 'lmms':
				print('[plugin-convert] plugin: zynaddsubfx > zynaddsubfx (VST)')
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
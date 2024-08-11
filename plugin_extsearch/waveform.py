# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_extsearch
import os
from os.path import exists
import xml.etree.ElementTree as ET
from objects import globalstore

class plugsearch(plugin_extsearch.base):
	def __init__(self): pass
	def getname(self): return 'Waveform'
	def is_dawvert_plugin(self): return 'externalsearch'
	def issupported(self, platformtxt): return True
	def import_plugins(self, platformtxt, homepath):
		if platformtxt == 'win': searchpath = os.path.join(homepath, "AppData", "Roaming", "Tracktion", "Waveform")
		if platformtxt == 'lin': searchpath = os.path.join(homepath, ".config", "Tracktion", "Waveform")

		plugfilename = os.path.join(searchpath, 'knownPluginList64.settings')

		if exists(plugfilename):
			vst2count = 0
			vstxmldata = ET.parse(plugfilename)
			vstxmlroot = vstxmldata.getroot()
			x_pluginfos = vstxmlroot.findall('PLUGIN')
			for x_pluginfo in x_pluginfos:
				vst_file = x_pluginfo.get('file')
				vst_format = x_pluginfo.get('format')
				if os.path.exists(vst_file):
					if vst_format == 'VST':
						vst_name = x_pluginfo.get('descriptiveName')
						vst_inst = x_pluginfo.get('isInstrument')
						if vst_inst == '1': plugdata_type = 'synth'
						if vst_inst == '0': plugdata_type = 'effect'
						plugdata_fourid = int(x_pluginfo.get('uniqueId'), 16)

						with globalstore.extplug.add('vst2', platformtxt) as pluginfo_obj:
							pluginfo_obj.type = plugdata_type
							pluginfo_obj.id = plugdata_fourid
							pluginfo_obj.basename = x_pluginfo.get('name')
							pluginfo_obj.name = x_pluginfo.get('descriptiveName')
							pluginfo_obj.path_64bit = x_pluginfo.get('file')
							pluginfo_obj.creator = x_pluginfo.get('manufacturer')
							pluginfo_obj.version = x_pluginfo.get('version')
							pluginfo_obj.audio_num_inputs = x_pluginfo.get('numInputs')
							pluginfo_obj.audio_num_outputs = x_pluginfo.get('numOutputs')
						vst2count += 1

					#if vst_format == 'LADSPA':
					#   ladspa_name = x_pluginfo.get('name')
					#   db_plugins.execute("INSERT OR IGNORE INTO ladspa (name) VALUES (?)", (ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET path_unix = ? WHERE name = ?", (x_pluginfo.get('file'), ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET filename = ? WHERE name = ?", (os.path.basename(x_pluginfo.get('file')).split('.')[0], ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET creator = ? WHERE name = ?", (x_pluginfo.get('manufacturer'), ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET version = ? WHERE name = ?", (x_pluginfo.get('version'), ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET audio_num_inputs = ? WHERE name = ?", (x_pluginfo.get('numInputs'), ladspa_name,))
					#   db_plugins.execute("UPDATE ladspa SET audio_num_outputs = ? WHERE name = ?", (x_pluginfo.get('numOutputs'), ladspa_name,))

			print('[waveform] VST2: '+str(vst2count))
			return True

		else:
			return False

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
from functions_plugin_ext import data_vc2xml
from functions_plugin import juce_memoryblock
from functions import data_xml

class juce_plugin:
	def __init__(self):
		self.plugtype = None
		self.memoryblock = ''
		self.name = None
		self.filename = None
		self.manufacturer = None
		self.fourid = None

	def from_cvpj(self, convproj_obj, plugin_obj):
		plugin_obj.type.type
		if plugin_obj.type.type == 'vst2':
			chunkdata = plugin_vst2.export_presetdata(plugin_obj)
			self.plugtype = 'vst2'
			self.name = plugin_obj.datavals_global.get('basename', None)
			self.manufacturer = plugin_obj.datavals_global.get('creator', None)
			self.filename = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
			self.fourid = plugin_obj.datavals_global.get('fourid', None)
			self.memoryblock = juce_memoryblock.toJuceBase64Encoding(chunkdata)

	def to_cvpj(self, convproj_obj, pluginid):
		if self.filename.endswith('.vst3'): self.plugtype = 'vst3'
		else: self.plugtype = 'vst2'

		chunkdata = juce_memoryblock.fromJuceBase64Encoding(self.memoryblock)

		if not pluginid:
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', self.plugtype, None)
			plugin_obj.role = 'effect'

		if self.plugtype == 'vst2':
			if chunkdata[0:4] != b'CcnK':
				pluginfo_obj = plugin_vst2.replace_data(convproj_obj, plugin_obj, 'basename', None, self.name, 'chunk', chunkdata, None)
				if not pluginfo_obj.out_exists: pluginfo_obj = plugin_vst2.replace_data(convproj_obj, plugin_obj, 'path', None, self.filename, 'chunk', chunkdata, None)
				if not pluginfo_obj.out_exists: 
					if self.name: plugin_obj.datavals_global.add('basename', self.name)
					if self.manufacturer: plugin_obj.datavals_global.add('creator', self.manufacturer)
					if self.filename:
						if os.path.exists(self.filename):
							vst2_pathid = pluginid+'_vstpath'
							convproj_obj.fileref__add(vst2_pathid, self.filename)
							plugin_obj.filerefs_global['plugin'] = vst2_pathid
			else: plugin_vst2.import_presetdata_raw(convproj_obj, plugin_obj, chunkdata, None)
			name = plugin_obj.datavals_global.get('name', None)

		if self.plugtype == 'vst3':
			pluginstate_x = data_vc2xml.get(chunkdata)
			IComponent = data_xml.find_first(pluginstate_x, 'IComponent')
			if IComponent != None and self.name:
				chunkdata = juce_memoryblock.fromJuceBase64Encoding(IComponent.text)
				pluginfo_obj = plugin_vst3.replace_data(convproj_obj, plugin_obj, 'name', None, self.name, chunkdata)
				if not pluginfo_obj.out_exists: 
					if self.filename:
						if os.path.exists(self.filename):
							vst3_pathid = pluginid+'_vstpath'
							convproj_obj.fileref__add(vst3_pathid, self.filename)
							plugin_obj.filerefs_global['plugin'] = vst3_pathid

		return plugin_obj, pluginid
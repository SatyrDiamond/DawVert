# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
#from functions_plugin_ext import data_vc2xml
from functions.juce import juce_memoryblock
from functions import data_xml

class juce_plugin:
	def __init__(self):
		self.plugtype = None
		self.memoryblock = ''
		self.rawdata = b''
		self.name = None
		self.filename = None
		self.manufacturer = None
		self.fourid = None
		self.program_num = None

	def from_cvpj(self, convproj_obj, plugin_obj):

		if plugin_obj.type.type == 'vst2':
			extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
			chunkdata = extmanu_obj.vst2__export_presetdata(None)

			self.plugtype = 'vst2'
			self.name = plugin_obj.external_info.basename
			self.manufacturer = plugin_obj.external_info.creator
			self.filename = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
			self.fourid = plugin_obj.external_info.fourid
			self.memoryblock = juce_memoryblock.toJuceBase64Encoding(chunkdata)

	def to_cvpj(self, convproj_obj, pluginid):
		if not self.plugtype:
			if self.filename.endswith('.vst3'): self.plugtype = 'vst3'
			else: self.plugtype = 'vst2'

		chunkdata = juce_memoryblock.fromJuceBase64Encoding(self.memoryblock) if self.memoryblock else self.rawdata

		if not pluginid:
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', self.plugtype, None)
			plugin_obj.role = 'effect'
		else:
			plugin_obj = convproj_obj.plugin__add(pluginid, 'external', self.plugtype, None)
			plugin_obj.role = 'effect'

		extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)

		if chunkdata:

			if self.plugtype == 'vst2':
				extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
				if chunkdata[0:4] != b'CcnK':
					extmanu_obj.vst2__replace_data('basename', self.name, chunkdata, None, True)
					if self.manufacturer: plugin_obj.external_info.creator = self.manufacturer

					if not out_exists: 
						if self.name: plugin_obj.external_info.basename = self.name
						if self.filename:
							if os.path.exists(self.filename):
								vst2_pathid = pluginid+'_vstpath'
								convproj_obj.fileref__add(vst2_pathid, self.filename)
								plugin_obj.filerefs_global['plugin'] = vst2_pathid
				else: 
					extmanu_obj.vst2__import_presetdata('raw', chunkdata, None)

				if self.program_num is not None:
					plugin_obj.current_program = self.program_num

			#if self.plugtype == 'vst3':
			#	pluginstate_x = data_vc2xml.get(chunkdata)
			#	IComponent = data_xml.find_first(pluginstate_x, 'IComponent')
			#	if IComponent != None and self.name:
			#		chunkdata = juce_memoryblock.fromJuceBase64Encoding(IComponent.text)
			#		out_exists = extmanu_obj.vst3__replace_data('name', self.name, chunkdata, None)
	#
			#		if not out_exists: 
			#			if self.filename:
			#				if os.path.exists(self.filename):
			#					vst3_pathid = pluginid+'_vstpath'
			#					convproj_obj.fileref__add(vst3_pathid, self.filename)
			#					plugin_obj.filerefs_global['plugin'] = vst3_pathid

		return plugin_obj, pluginid
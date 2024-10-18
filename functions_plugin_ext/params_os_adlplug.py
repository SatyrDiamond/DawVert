# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

def addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, 'VALUE')
	temp_xml.set('name', str(name))
	temp_xml.set('val', str(value))

class adlplug_data:
	def __init__(self):
		self.adlplug_root = ET.Element("ADLMIDI-state")  
		self.addbank(self.adlplug_root, 1, 'DawVert')
		self.adlplug_params = ET.SubElement(self.adlplug_root, 'instrument')

	def addbank(self, xmltag, num, name):
		bank_xml = ET.SubElement(xmltag, 'bank')
		addvalue(bank_xml, 'bank', num)
		addvalue(bank_xml, 'name', name)

	def set_param(self, name, value):
		addvalue(self.adlplug_params, name, value)

	def add_selection(self, part, bank, program):
		opnplug_selection = ET.SubElement(self.adlplug_root, 'selection')	
		addvalue(opnplug_selection, "part" ,part)  
		addvalue(opnplug_selection, "bank" ,bank)  
		addvalue(opnplug_selection, "program" ,program)

	def add_common(self, bank_title, part, master_volume):
		adlplug_common = ET.SubElement(self.adlplug_root, 'common')  
		addvalue(adlplug_common, "bank_title" ,bank_title)   
		addvalue(adlplug_common, "part" ,part) 
		addvalue(adlplug_common, "master_volume" ,master_volume)

	def opnplug_chip(self, emulator, chip_count, chip_type):
		adlplug_common = ET.SubElement(self.adlplug_root, 'chip')  
		addvalue(adlplug_common, "emulator" ,emulator)   
		addvalue(adlplug_common, "chip_count" ,chip_count) 
		addvalue(adlplug_common, "chip_type" ,chip_type)

	def adlplug_chip(self, emulator, chip_count, fop_count):
		adlplug_common = ET.SubElement(self.adlplug_root, 'chip')  
		addvalue(adlplug_common, "emulator" ,emulator)   
		addvalue(adlplug_common, "chip_count" ,chip_count) 
		addvalue(adlplug_common, "4op_count" ,fop_count)

	def opnplug_global(self, volume_model, lfo_enable, lfo_frequency):
		adlplug_global = ET.SubElement(self.adlplug_root, 'global')  
		addvalue(adlplug_global, "volume_model" ,volume_model) 
		addvalue(adlplug_global, "lfo_enable" ,lfo_enable)  
		addvalue(adlplug_global, "lfo_frequency" ,lfo_frequency)

	def adlplug_global(self, volume_model, deep_tremolo, deep_vibrato):
		adlplug_global = ET.SubElement(self.adlplug_root, 'global')  
		addvalue(adlplug_global, "volume_model" ,volume_model) 
		addvalue(adlplug_global, "deep_tremolo" ,deep_tremolo)  
		addvalue(adlplug_global, "deep_vibrato" ,deep_vibrato)

	def adlplug_to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'ADLplug', 'chunk', data_vc2xml.make(self.adlplug_root), None)

	def opnplug_to_cvpj_vst2(self, convproj_obj, plugin_obj):
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'name', 'any', 'OPNplug', 'chunk', data_vc2xml.make(self.adlplug_root), None) 
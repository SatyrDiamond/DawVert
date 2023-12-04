# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugin_input import base as base_input
from plugin_output import base as base_output
from experiments_plugin_input import base as experiments_plugin_input
from functions import song_compat
from functions import plug_conv

from functions_song import convert_r2m
from functions_song import convert_ri2mi
from functions_song import convert_ri2r
from functions_song import convert_rm2r
from functions_song import convert_m2r
from functions_song import convert_m2mi
from functions_song import convert_mi2m

import platform
import os

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['debug'] = 'debug'

class core:
	def __init__(self):
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': self.platform_id = 'win'
		else: self.platform_id = 'lin'

		self.pluglist_input = {}
		self.pluglist_input_auto = {}
		self.currentplug_input = [None, None]

		self.pluglist_output = {}
		self.currentplug_output = [None, None]

		self.convproj_j = {}

	def input_load_plugins(self, pluginset):
		self.pluglist_input = {}
		print('[core] Plugins (Input): ',end='')
		dv_pluginclasses = base_input
		if pluginset == 'experiments': dv_pluginclasses = experiments_plugin_input

		for inputplugin in dv_pluginclasses.plugins:
			in_class_list = inputplugin()
			in_validplugin = False
			try:
				plugtype = in_class_list.is_dawvert_plugin()
				if plugtype == 'input': in_validplugin = True
			except: pass
			if in_validplugin == True:
				shortname = in_class_list.getshortname()
				self.pluglist_input[shortname] = in_class_list
				if in_class_list.supported_autodetect() == True:
					self.pluglist_input_auto[shortname] = in_class_list
					print(shortname,end='[a] ')
				else:
					print(shortname,end=' ')
		print('')

	def input_get_plugins(self): return self.pluglist_input

	def input_get_plugins_auto(self): return self.pluglist_input_auto

	def input_get_current(self): return self.currentplug_input[1]

	def input_set(self, pluginname): 
		if pluginname in self.pluglist_input:
			self.currentplug_input = [
				self.pluglist_input[pluginname], 
				pluginname, 
				self.pluglist_input[pluginname].getname(),
				self.pluglist_input[pluginname].gettype(),
				self.pluglist_input[pluginname].getdawcapabilities()
				]
			print('[core] Set input format:',self.currentplug_input[2],'('+ self.currentplug_input[1]+')')
			print('[core] Input Format:',self.currentplug_input[1])
			print('[core] Input DataType:',typelist[self.currentplug_input[3]])
			return pluginname
		else: return None

	def input_autoset(self, in_file):
		outputname = None
		for autoplugin in self.pluglist_input_auto:
			temp_in_class = self.pluglist_input_auto[autoplugin]
			detected_format = temp_in_class.detect(in_file)
			if detected_format == True:
				outputname = temp_in_class.getshortname()
				full_name = temp_in_class.getname()
				self.input_set(outputname)
				break
		return outputname

	def output_load_plugins(self):
		print('[core] Plugins (Output): ',end='')
		for outputplugin in base_output.plugins:
			out_class_list = outputplugin()
			out_validplugin = False
			try:
				plugtype = out_class_list.is_dawvert_plugin()
				if plugtype == 'output':
					out_validplugin = True
			except: pass
			if out_validplugin == True:
				shortname = out_class_list.getshortname()
				self.pluglist_output[shortname] = out_class_list
				print(shortname,end=' ')
		print('')

	def output_get_plugins(self): return self.pluglist_output

	def output_get_current(self): return self.currentplug_output[1]

	def output_get_extension(self): return self.currentplug_output[7]

	def output_set(self, pluginname): 
		if pluginname in self.pluglist_output:
			self.currentplug_output = [
				self.pluglist_output[pluginname], 
				pluginname, 
				self.pluglist_output[pluginname].getname(),
				self.pluglist_output[pluginname].gettype(),
				self.pluglist_output[pluginname].getdawcapabilities(),
				self.pluglist_output[pluginname].getsupportedplugins(),
				self.pluglist_output[pluginname].getsupportedplugformats(),
				self.pluglist_output[pluginname].getfileextension()
				]
			print('[core] Output Format:',self.currentplug_output[1])
			print('[core] Output DataType:',typelist[self.currentplug_output[3]])
			return pluginname
		else: return None

	def get_cvpj(self, extra_json): return self.convproj_j

	def parse_input(self, in_file, extra_json): 
		if 'samples_inside' in self.currentplug_input[4]: os.makedirs(extra_json['samplefolder'], exist_ok=True)

		self.convproj_j = [self.currentplug_input[0].parse(in_file, extra_json), self.currentplug_input[3], self.currentplug_input[4]]
		if self.convproj_j == '{}' or self.convproj_j == None:
			print('[error] Input Plugin outputted no json')
			exit()

	def convert_plugins(self, extra_json): 
		CVPJ_C = plug_conv.convproj(self.convproj_j[0], self.platform_id, self.convproj_j[1], self.currentplug_output[3], self.currentplug_input[1], self.currentplug_output[1], self.currentplug_output[5], self.currentplug_output[6], extra_json)
		if CVPJ_C != None: self.convproj_j[0] = CVPJ_C

	def convert_type_output(self, extra_json): 
		in_type = self.currentplug_input[3]
		out_type = self.currentplug_output[3]
		in_dawcapabilities = self.currentplug_input[4]
		out_dawcapabilities = self.currentplug_output[4]

		compactclass = song_compat.song_compat()

		compactclass.set_dawcapabilities(in_dawcapabilities, out_dawcapabilities)

		print('[core] ' + typelist[in_type] + ' > ' + typelist[out_type])

		#if in_type in ['r', 'm']: self.convproj_j[0] = compactclass.makecompat_audiostretch(self.convproj_j[0], in_type, in_dawcapabilities, out_dawcapabilities)
	
		if out_type != 'debug':
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], in_type)

		if in_type == 'ri' and out_type == 'mi': 
			self.convproj_j[0] = convert_ri2mi.convert(self.convproj_j[0])
		elif in_type == 'ri' and out_type == 'r': 
			self.convproj_j[0] = convert_ri2r.convert(self.convproj_j[0])

		elif in_type == 'm' and out_type == 'mi': 
			self.convproj_j[0] = convert_m2mi.convert(self.convproj_j[0])
		elif in_type == 'm' and out_type == 'r': 
			self.convproj_j[0] = convert_m2r.convert(self.convproj_j[0])

		elif in_type == 'r' and out_type == 'm': 
			self.convproj_j[0] = convert_r2m.convert(self.convproj_j[0])
		elif in_type == 'r' and out_type == 'mi': 
			self.convproj_j[0] = convert_r2m.convert(self.convproj_j[0])
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], 'm')
			self.convproj_j[0] = convert_m2mi.convert(self.convproj_j[0])

		elif in_type == 'mi' and out_type == 'm': 
			self.convproj_j[0] = convert_mi2m.convert(self.convproj_j[0], extra_json)
		elif in_type == 'mi' and out_type == 'r': 
			self.convproj_j[0] = convert_mi2m.convert(self.convproj_j[0], extra_json)
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], 'm')
			self.convproj_j[0] = convert_m2r.convert(self.convproj_j[0])
	
		elif in_type == 'rm' and out_type == 'r': 
			self.convproj_j[0] = convert_rm2r.convert(self.convproj_j[0])
		elif in_type == 'rm' and out_type == 'm': 
			self.convproj_j[0] = convert_rm2r.convert(self.convproj_j[0])
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], 'r')
			self.convproj_j[0] = convert_r2m.convert(self.convproj_j[0])
		elif in_type == 'rm' and out_type == 'mi': 
			self.convproj_j[0] = convert_rm2r.convert(self.convproj_j[0])
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], 'r')
			self.convproj_j[0] = convert_r2m.convert(self.convproj_j[0])
			self.convproj_j[0] = convert_m2mi.convert(self.convproj_j[0])

		elif in_type == out_type: 
			pass
		
		elif out_type == 'debug': 
			pass

		else:
			print(typelist[in_type],'to',typelist[out_type],'is not supported')
			exit()

		if out_type != 'debug':
			self.convproj_j[0] = compactclass.makecompat(self.convproj_j[0], out_type)

		self.convproj_j[1] = self.currentplug_output[3]
		self.convproj_j[2] = self.currentplug_output[4]

	def parse_output(self, out_file): 
		self.currentplug_output[0].parse(self.convproj_j[0], out_file)
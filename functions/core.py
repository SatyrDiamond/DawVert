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

from objects import convproj

import platform
import os

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['debug'] = 'debug'

class config_data:
	path_samples_extracted = os.getcwd() + '/__samples_extracted/'
	path_samples_downloaded = os.getcwd() + '/__samples_downloaded/'
	path_samples_generated = os.getcwd() + '/__samples_generated/'
	path_samples_converted = os.getcwd() + '/__samples_converted/'
	path_soundfont_gm = None
	path_soundfont_xg = None
	path_soundfont_sc55 = None
	path_soundfont_mt32 = None
	path_extrafile = None
	allow_download = True
	songnum = 1
	flags_plugins = []
	flags_convproj = []
	flags_core = []

class dawinfo:
	def __init__(self):
		self.name = ""
		self.file_ext = ''
		self.plugin_arch = [32, 64]
		self.plugin_ext = []
		self.plugin_included = []

		self.audio_filetypes = []

		self.track_lanes = False
		self.track_nopl = False
		self.track_hybrid = False
		self.placement_cut = False
		self.placement_loop = []
		self.audio_nested = False
		self.audio_stretch = []
		self.fxrack = False
		self.fxrack_params = ['vol','enabled']
		self.auto_types = []
		self.fxchain_mixer = False
		self.fxtype = 'groupreturn'

		self.time_seconds = False

class core:
	def __init__(self):
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': self.platform_id = 'win'
		else: self.platform_id = 'lin'

		self.config = config_data()

		self.pluglist_input = {}
		self.pluglist_input_auto = {}
		self.currentplug_input = [None, None]

		self.pluglist_output = {}
		self.currentplug_output = [None, None]

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
			inputclass = self.pluglist_input[pluginname]
			dawinfo_obj = dawinfo()
			inputclass.getdawinfo(dawinfo_obj)
			self.currentplug_input = [
				inputclass, 
				pluginname, 
				dawinfo_obj
				]
			print('[core] Set input format:',self.currentplug_input[2].name,'('+ self.currentplug_input[1]+')')
			print('[core] Input Format:',self.currentplug_input[1])
			return pluginname
		else: return None

	def input_autoset(self, in_file):
		outputname = None
		for pluginname, inputclass in self.pluglist_input_auto.items():
			detected_format = inputclass.detect(in_file)
			if detected_format == True:
				outputname = inputclass.getshortname()
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

	def output_get_extension(self): return self.currentplug_output[2].file_ext

	def output_set(self, pluginname): 
		if pluginname in self.pluglist_output:

			dawinfo_obj = dawinfo()
			self.pluglist_output[pluginname].getdawinfo(dawinfo_obj)
			self.currentplug_output = [
				self.pluglist_output[pluginname], 
				pluginname, 
				dawinfo_obj,
				self.pluglist_output[pluginname].gettype()
				]

			print('[core] Output Format:',self.currentplug_output[1])
			print('[core] Output DataType:',typelist[self.currentplug_output[3]])
			return pluginname
		else: return None

	def parse_input(self, in_file, dv_config): 
		self.convproj_obj = convproj.cvpj_project()
		self.currentplug_input[0].parse(self.convproj_obj, in_file, dv_config)

		self.convproj_obj.sample_folders.append(os.path.dirname(in_file))

		for sample_folder in self.convproj_obj.sample_folders:
			self.convproj_obj.fill_samplerefs(sample_folder)

	def convert_plugins(self, dv_config): 
		plug_conv.convproj(self.convproj_obj, self.platform_id, self.currentplug_input[1], self.currentplug_output[1], self.currentplug_output[2], dv_config)
		#exit()

	def convert_type_output(self, dv_config): 
		in_type = self.convproj_obj.type
		out_type = self.currentplug_output[3]
		in_dawinfo = self.currentplug_input[2]
		out_dawinfo = self.currentplug_output[2]

		compactclass = song_compat.song_compat()

		print('[core] ' + typelist[in_type] + ' > ' + typelist[out_type])

		#if in_type in ['r', 'm']: compactclass.makecompat_audiostretch(self.convproj_obj, in_type, in_dawinfo, out_dawinfo)
	
		if out_type != 'debug':
			compactclass.makecompat(self.convproj_obj, in_type, in_dawinfo, out_dawinfo)

		if in_type == 'ri' and out_type == 'mi': 
			convert_ri2mi.convert(self.convproj_obj)
		elif in_type == 'ri' and out_type == 'r': 
			convert_ri2r.convert(self.convproj_obj)

		elif in_type == 'm' and out_type == 'mi': 
			convert_m2mi.convert(self.convproj_obj)
		elif in_type == 'm' and out_type == 'r': 
			convert_m2r.convert(self.convproj_obj)

		elif in_type == 'r' and out_type == 'm': 
			convert_r2m.convert(self.convproj_obj)
		elif in_type == 'r' and out_type == 'mi': 
			convert_r2m.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == 'mi' and out_type == 'm': 
			convert_mi2m.convert(self.convproj_obj, dv_config)
		elif in_type == 'mi' and out_type == 'r': 
			convert_mi2m.convert(self.convproj_obj, dv_config)
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo)
			convert_m2r.convert(self.convproj_obj)
	
		elif in_type == 'rm' and out_type == 'r': 
			convert_rm2r.convert(self.convproj_obj)
		elif in_type == 'rm' and out_type == 'm': 
			convert_rm2r.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'r', in_dawinfo, out_dawinfo)
			convert_r2m.convert(self.convproj_obj)
		elif in_type == 'rm' and out_type == 'mi': 
			convert_rm2r.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'r', in_dawinfo, out_dawinfo)
			convert_r2m.convert(self.convproj_obj)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == out_type: 
			pass
		
		elif out_type == 'debug': 
			pass

		else:
			print(typelist[in_type],'to',typelist[out_type],'is not supported')
			exit()

		if 'do_sorttracks' in self.convproj_obj.do_actions:
			self.convproj_obj.sort_tracks()

		if out_type != 'debug':
			compactclass.makecompat(self.convproj_obj, out_type, in_dawinfo, out_dawinfo)

	def parse_output(self, out_file): 
		self.currentplug_output[0].parse(self.convproj_obj, out_file)
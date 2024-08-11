# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugins import base as dv_plugins

#from experiments_plugin_input import base as experiments_plugin_input
from functions import song_compat
from functions import plug_conv

from functions_song import convert_r2m
from functions_song import convert_ri2mi
from functions_song import convert_ri2r
from functions_song import convert_rm2r
from functions_song import convert_m2r
from functions_song import convert_m2mi
from functions_song import convert_mi2m
from functions_song import convert_rm2m

from functions_song import convert_ms2rm
from functions_song import convert_rs2r

from objects.convproj import project as convproj

import os
import configparser
import platform
import logging

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['rs'] = 'RegularScened'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['ms'] = 'MultipleScened'
typelist['debug'] = 'debug'

logFormatter = logging.Formatter(fmt='%(levelname)8s | %(name)12s | %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logFormatter)

logging.root.setLevel(logging.DEBUG)

logger_core = logging.getLogger('core')
logger_compat = logging.getLogger('compat')
logger_fxchange = logging.getLogger('fxchange')
logger_project = logging.getLogger('project')
logger_automation = logging.getLogger('automation')
logger_globalstore = logging.getLogger('globalstore')

logger_input = logging.getLogger('input')
logger_output = logging.getLogger('output')
logger_plugconv = logging.getLogger('plugconv')
logger_plugconv_ext = logging.getLogger('plugconv_ext')

logger_audiofile = logging.getLogger('audiofile')
logger_projparse = logging.getLogger('projparse')
logger_plugins = logging.getLogger('plugins')

logger_core.addHandler(consoleHandler)
logger_compat.addHandler(consoleHandler)
logger_fxchange.addHandler(consoleHandler)
logger_project.addHandler(consoleHandler)
logger_automation.addHandler(consoleHandler)
logger_globalstore.addHandler(consoleHandler)

logger_input.addHandler(consoleHandler)
logger_output.addHandler(consoleHandler)
logger_plugconv.addHandler(consoleHandler)
logger_plugconv_ext.addHandler(consoleHandler)

logger_audiofile.addHandler(consoleHandler)
logger_projparse.addHandler(consoleHandler)
logger_plugins.addHandler(consoleHandler)

class config_data:
	path_samples_extracted = os.getcwd() + '/__samples_extracted/'
	path_samples_downloaded = os.getcwd() + '/__samples_downloaded/'
	path_samples_generated = os.getcwd() + '/__samples_generated/'
	path_samples_converted = os.getcwd() + '/__samples_converted/'
	path_extrafile = None
	path_soundfont = None
	paths_soundfonts = {}
	allow_download = True
	songnum = 1
	extplug_cat = []
	flags_convproj = []
	flags_core = []
	splitter_mode = 0
	splitter_detect_start = False
	searchpaths = []

	def load(self, filepath):
		global paths_soundfonts
		config = configparser.ConfigParser()
		if os.path.exists(filepath):
			config.read_file(open(filepath))
			for devtype in ['gm', 'xg', 'gs', 'mt32', 'mariopaint']:
				try: self.paths_soundfonts[devtype] = config.get('soundfont2', devtype)
				except: pass
			for plugcat in ['foss', 'nonfree', 'shareware', 'old']:
				try:
					ifyes = bool(int(config.get('extplug_cat', plugcat)))
					if ifyes: self.extplug_cat.append(plugcat)
				except: pass

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

		self.currentplug_input = None
		self.currentplug_output = None
		dv_plugins.load_plugindir('audiofile')
		dv_plugins.load_plugindir('audiocodecs')

	def input_load_plugins(self, pluginset):
		if pluginset == 'experiments': 
			dv_plugins.load_plugindir('input_experiments')
		else:
			dv_plugins.load_plugindir('input')

	def input_get_plugins(self): return dv_plugins.plugins_input

	def input_get_plugins_auto(self): return dv_plugins.plugins_input_auto

	def input_get_current(self): return self.currentplug_input[1]

	def input_set(self, pluginname): 
		if pluginname in dv_plugins.plugins_input:
			inputdawobj = dv_plugins.plugins_input[pluginname]
			self.currentplug_input = [
				inputdawobj.object, 
				pluginname, 
				inputdawobj
				]
			logger_core.info('Set input format: '+self.currentplug_input[2].name+' ('+ self.currentplug_input[1]+')')
			logger_core.info('Input Format: '+self.currentplug_input[1])
			return pluginname
		else: return None

	def input_autoset(self, in_file):
		outputname = None
		for pluginname, inputclass in dv_plugins.plugins_input_auto.items():
			detected_format = inputclass.object.detect(in_file)
			if detected_format == True:
				outputname = pluginname
				self.input_set(outputname)
				break
		return outputname

	def output_load_plugins(self):
		dv_plugins.load_plugindir('output')

	def output_get_plugins(self): return dv_plugins.plugins_output

	def output_get_current(self): return self.currentplug_output[1]

	def output_get_extension(self): return self.currentplug_output[2].file_ext

	def output_set(self, pluginname): 
		if pluginname in dv_plugins.plugins_output:
			dawinfo_obj = dv_plugins.plugins_output[pluginname]
			self.currentplug_output = [
				dawinfo_obj.object, 
				pluginname, 
				dawinfo_obj,
				dawinfo_obj.object.gettype()
				]

			logger_core.info('Output Format: '+self.currentplug_output[1])
			logger_core.info('Output DataType: '+typelist[self.currentplug_output[3]])
			return pluginname
		else: return None

	def parse_input(self, in_file, dv_config): 
		self.convproj_obj = convproj.cvpj_project()
		dv_config.searchpaths.append(os.path.dirname(in_file))
		self.currentplug_input[0].parse(self.convproj_obj, in_file, dv_config)
		#for samplerefid, sampleref_obj in self.convproj_obj.samplerefs.items():
		#	if not sampleref_obj.found:
		#		print(samplerefid, sampleref_obj.found, sampleref_obj.fileref.get_path('win', True))

	def convert_plugins(self, dv_config): 
		plug_conv.convproj(self.convproj_obj, in_dawinfo, out_dawinfo, dv_config)

	def convert_type_output(self, dv_config): 
		global in_dawinfo
		global out_dawinfo
		in_type = self.convproj_obj.type
		out_type = self.currentplug_output[3]
		in_dawinfo = self.currentplug_input[2]
		out_dawinfo = self.currentplug_output[2]

		compactclass = song_compat.song_compat()

		logger_core.info('' + typelist[in_type] + ' > ' + typelist[out_type])

		#if in_type in ['r', 'm']: compactclass.makecompat_audiostretch(self.convproj_obj, in_type, in_dawinfo, out_dawinfo, out_type)
	
		if out_type != 'debug':
			compactclass.makecompat(self.convproj_obj, in_type, in_dawinfo, out_dawinfo, out_type)

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
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == 'mi' and out_type == 'm': 
			convert_mi2m.convert(self.convproj_obj, dv_config)
		elif in_type == 'mi' and out_type == 'r': 
			convert_mi2m.convert(self.convproj_obj, dv_config)
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2r.convert(self.convproj_obj)
	
		elif in_type == 'rm' and out_type == 'r': 
			convert_rm2r.convert(self.convproj_obj)
		elif in_type == 'rm' and out_type == 'm': 
			convert_rm2m.convert(self.convproj_obj, True)
		elif in_type == 'rm' and out_type == 'mi': 
			convert_rm2m.convert(self.convproj_obj, True)
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == 'rs' and out_type == 'mi': 
			convert_rs2r.convert(self.convproj_obj)
			convert_r2m.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == 'rs' and out_type == 'r': 
			convert_rs2r.convert(self.convproj_obj)

		elif in_type == 'ms' and out_type == 'mi': 
			convert_ms2rm.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'rm', in_dawinfo, out_dawinfo, out_type)
			convert_rm2m.convert(self.convproj_obj, True)
			convert_m2mi.convert(self.convproj_obj)

		elif in_type == 'ms' and out_type == 'r': 
			convert_ms2rm.convert(self.convproj_obj)
			compactclass.makecompat(self.convproj_obj, 'r', in_dawinfo, out_dawinfo, out_type)
			convert_rm2r.convert(self.convproj_obj)

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
			compactclass.makecompat(self.convproj_obj, out_type, in_dawinfo, out_dawinfo, out_type)

	def parse_output(self, out_file): 
		self.currentplug_output[0].parse(self.convproj_obj, out_file)
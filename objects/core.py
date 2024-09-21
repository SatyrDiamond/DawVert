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

logFormatter = logging.Formatter(fmt='%(levelname)8s | %(name)12s | %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
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
	path_external_data = os.getcwd() + '/_external_data/'
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

		self.currentplug_input = dv_plugins.create_selector('input')
		self.currentplug_output = dv_plugins.create_selector('output')
		dv_plugins.load_plugindir('audiofile')
		dv_plugins.load_plugindir('audiocodecs')
		dv_plugins.load_plugindir('audioconv')

	def input_load_plugins(self, pluginset):
		if pluginset == 'experiments': 
			dv_plugins.load_plugindir('input_experiments')
		else:
			dv_plugins.load_plugindir('input')

	def input_get_plugins(self): return dv_plugins.get_list('input')

	def input_get_plugins_auto(self): return dv_plugins.get_list_detect('input')

	def input_get_current(self): return self.currentplug_input.selected_shortname

	def input_set(self, pluginname): return self.currentplug_input.set(pluginname)

	def input_autoset(self, in_file): return self.currentplug_input.set_auto(in_file)

	def output_load_plugins(self):
		dv_plugins.load_plugindir('output')

	def output_get_plugins(self): return dv_plugins.get_list('output')

	def output_get_current(self): return self.currentplug_output.selected_shortname

	def output_get_extension(self): 
		prop_obj = self.currentplug_output.get_prop_obj()
		return prop_obj.file_ext if prop_obj else None

	def output_set(self, pluginname): return self.currentplug_output.set(pluginname)

	def parse_input(self, in_file, dv_config): 
		self.convproj_obj = convproj.cvpj_project()
		dv_config.searchpaths.append(os.path.dirname(in_file))
		plug_obj = self.currentplug_input.selected_plugin.plug_obj
		plug_obj.parse(self.convproj_obj, in_file, dv_config)

	def convert_type_output(self, dv_config): 
		global in_dawinfo
		global out_dawinfo
		in_type = self.convproj_obj.type
		out_type = self.currentplug_output.selected_plugin.plug_obj.gettype()
		in_dawinfo = self.currentplug_input.selected_plugin.prop_obj
		out_dawinfo = self.currentplug_output.selected_plugin.prop_obj

		logger_core.info('' + convproj.typelist[in_type] + ' > ' + convproj.typelist[out_type])

		self.convproj_obj.change_projtype(in_dawinfo, out_dawinfo, out_type, dv_config)
		if 'do_sorttracks' in self.convproj_obj.do_actions: self.convproj_obj.sort_tracks()

		isconverted = False
		for sampleref_id, sampleref_obj in self.convproj_obj.samplerefs.items():
			if sampleref_obj.found:
				if sampleref_obj.fileformat not in out_dawinfo.audio_filetypes:
					isconverted = sampleref_obj.convert(out_dawinfo.audio_filetypes, dv_config.path_samples_converted)

	def convert_plugins(self, dv_config): 
		plug_conv.convproj(self.convproj_obj, in_dawinfo, out_dawinfo, self.currentplug_output.selected_shortname, dv_config)

	def parse_output(self, out_file): 
		plug_obj = self.currentplug_output.selected_plugin.plug_obj
		plug_obj.parse(self.convproj_obj, out_file)
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugins import base as dv_plugins
from functions_plugin_ext import plugin_vst2

from functions import song_compat
from functions import plug_conv
import pathlib

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
from objects.convproj import fileref

import os
import configparser
import platform
import logging

logFormatter = logging.Formatter(fmt='%(levelname)8s | %(name)12s | %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)

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
logger_filesearch = logging.getLogger('filesearch')

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
logger_filesearch.addHandler(consoleHandler)

logger_core.setLevel(logging.INFO)
logger_compat.setLevel(logging.INFO)
logger_fxchange.setLevel(logging.INFO)
logger_project.setLevel(logging.INFO)
logger_automation.setLevel(logging.INFO)
logger_globalstore.setLevel(logging.INFO)
logger_input.setLevel(logging.INFO)
logger_output.setLevel(logging.INFO)
logger_plugconv.setLevel(logging.INFO)
logger_plugconv_ext.setLevel(logging.INFO)
logger_audiofile.setLevel(logging.INFO)
logger_projparse.setLevel(logging.INFO)
logger_plugins.setLevel(logging.INFO)

log_pathsearchonly = False

if log_pathsearchonly:
	logger_core.setLevel(logging.ERROR)
	logger_compat.setLevel(logging.ERROR)
	logger_fxchange.setLevel(logging.ERROR)
	logger_project.setLevel(logging.ERROR)
	logger_filesearch.setLevel(logging.DEBUG)
	logger_automation.setLevel(logging.ERROR)
	logger_globalstore.setLevel(logging.ERROR)
	logger_input.setLevel(logging.ERROR)
	logger_output.setLevel(logging.ERROR)
	logger_plugconv.setLevel(logging.ERROR)
	logger_plugconv_ext.setLevel(logging.ERROR)
	logger_audiofile.setLevel(logging.ERROR)
	logger_projparse.setLevel(logging.ERROR)
	logger_plugins.setLevel(logging.ERROR)

class dawvert_intent:
	def __init__(self):
		self.input_file = ''
		self.input_data = b''
		self.input_mode = 'file'
		self.input_visname = ''
		self.input_params = {}
		
		self.output_file = ''
		self.output_mode = 'file'
		self.output_params = {}
		self.output_samples = ''

		self.plugin_set = True
		self.plugin_input = None
		self.plugin_output = None
		self.plugset_input = None
		self.plugset_output = None

		self.path_samples = {}
		self.path_soundfonts = {}
		self.path_external_data = ''

		self.splitter_mode = 0
		self.splitter_detect_start = False

		self.flags_compat = []
		self.flag_overwrite = False

		self.extplug_cat = []
		self.songnum = 0

		self.custom_config = {}

		self.set_defualt_path()

	def set_defualt_path(self):
		self.path_samples['extracted'] = os.getcwd() + '/__samples_extracted/'
		self.path_samples['downloaded'] = os.getcwd() + '/__samples_downloaded/'
		self.path_samples['generated'] = os.getcwd() + '/__samples_generated/'
		self.path_samples['converted'] = os.getcwd() + '/__samples_converted/'

	def set_projname_path(self):
		file_name = self.input_visname
		self.set_defualt_path()
		self.path_samples['extracted'] += file_name + '/'
		self.path_samples['downloaded'] += file_name + '/'
		self.path_samples['generated'] += file_name + '/'
		self.path_samples['converted'] += file_name + '/'

	def create_folder_paths(self):
		os.makedirs(self.path_samples['extracted'], exist_ok=True)
		os.makedirs(self.path_samples['downloaded'], exist_ok=True)
		os.makedirs(self.path_samples['generated'], exist_ok=True)
		os.makedirs(self.path_samples['converted'], exist_ok=True)

	def config_load(self, filepath):
		config = configparser.ConfigParser()
		if os.path.exists(filepath):
			config.read_file(open(filepath))
			for devtype in ['gm', 'xg', 'gs', 'mt32', 'mariopaint']:
				try: self.path_soundfonts[devtype] = config.get('soundfont2', devtype)
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
		self.plugin_ext_arch = [32, 64]
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

pluginsets_input = {
'main': ['', 'Main'],
'exper': ['exper', 'Experiments'],
'ai': ['ai', 'AI'],
'vgm': ['vgm', 'VGM'],
'gameres': ['gameres', 'Game Mod'],
'gamespec': ['gamespec', 'Game Specific'],
'old': ['old', 'Old/Broken']
}

pluginsets_output = {
'main': ['', 'Main'],
'wip': ['wip', 'WIP'],
'old': ['old', 'Old/Broken']
}

class core:
	def __init__(self):
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': self.platform_id = 'win'
		else: self.platform_id = 'lin'

		self.currentplug_input = dv_plugins.create_selector('input')
		self.currentplug_output = dv_plugins.create_selector('output')
		dv_plugins.load_plugindir('audiofile', '')
		dv_plugins.load_plugindir('audiocodecs', '')
		dv_plugins.load_plugindir('audioconv', '')

	def intent_setplugins(self, dawvert_intent):
		if dawvert_intent.plugin_set:
			self.input_load_plugins(dawvert_intent.plugset_input if dawvert_intent.plugset_input else 'main')
			self.output_load_plugins(dawvert_intent.plugset_output if dawvert_intent.plugset_output else 'main')

			if dawvert_intent.plugin_input == None:
				detect_plugin_found = self.input_autoset(dawvert_intent.input_file)
				if detect_plugin_found == None:
					detect_plugin_found = self.input_autoset_fileext(dawvert_intent.input_file)
					if detect_plugin_found == None:
						logger_core.error('Could not identify the input format')
						return False
			else:
				if dawvert_intent.plugin_input in self.input_get_plugins():
					in_class = self.input_set(dawvert_intent.plugin_input)
				else:
					logger_core.error('Input format plugin not found')
					return False

			if dawvert_intent.plugin_output in self.output_get_plugins():
				out_class = self.output_set(dawvert_intent.plugin_output)
			else:
				logger_core.error('Output format plugin not found')
				return False

		return True


	def logger_only_plugconv(self):
		logger_core.setLevel(logging.WARNING)
		logger_compat.setLevel(logging.WARNING)
		logger_fxchange.setLevel(logging.WARNING)
		logger_project.setLevel(logging.WARNING)
		logger_automation.setLevel(logging.WARNING)
		logger_globalstore.setLevel(logging.WARNING)
		logger_input.setLevel(logging.WARNING)
		logger_output.setLevel(logging.WARNING)
		logger_audiofile.setLevel(logging.WARNING)
		logger_projparse.setLevel(logging.WARNING)
		logger_plugins.setLevel(logging.WARNING)

	def input_load_plugins(self, pluginset):
		if pluginset in pluginsets_input: 
			plugsetfolder, fullname = pluginsets_input[pluginset]
			dv_plugins.load_plugindir('input', plugsetfolder)
		else: dv_plugins.load_plugindir('input', '')

	def input_get_pluginsets(self): return list(pluginsets_input)

	def input_get_pluginsets_names(self): return [n[1] for _, n in pluginsets_input.items()]

	def input_get_pluginsets_index(self, num): return list(pluginsets_input)[num]

	def input_get_plugins(self): return dv_plugins.get_list('input')

	def input_get_plugins_names(self): return dv_plugins.get_list_names('input')

	def input_get_plugins_props(self): return dv_plugins.get_list_prop_obj('input')

	def input_get_plugins_index(self, num): 
		pluglist = dv_plugins.get_list('input')
		if num != -1:
			if (len(pluglist)-1)>=num: return pluglist[min(num, len(pluglist)-1)]
			else: return None
		else:
			return None

	def input_get_plugins_auto(self): return dv_plugins.get_list_detect('input')

	def input_get_current(self): return self.currentplug_input.selected_shortname

	def input_get_current_name(self): return self.currentplug_input.selected_plugin.name if self.currentplug_input.selected_plugin else 'None'

	def input_get_usable(self): 
		selected_plugin = self.currentplug_input.selected_plugin
		if selected_plugin:
			return selected_plugin.usable, selected_plugin.usable_meg
		else:
			return False, ''

	def input_set(self, pluginname): 
		return self.currentplug_input.set(pluginname)

	def input_unset(self, pluginname): 
		return self.currentplug_input.unset()

	def input_autoset(self, in_file): return self.currentplug_input.set_auto(in_file)

	def input_autoset_keepset(self, in_file): return self.currentplug_input.set_auto_keepset(in_file)

	def input_autoset_fileext(self, in_file):
		fileext = pathlib.Path(in_file).suffix
		shortname = None
		for shortname, plug_obj, prop_obj in self.currentplug_input.iter():
			if prop_obj.file_ext_detect:
				if fileext.lower() in ['.'+x.lower() for x in prop_obj.file_ext]:
					self.input_set(shortname)
					return shortname
		if shortname: self.input_unset(shortname)

	def output_load_plugins(self, pluginset):
		if pluginset in pluginsets_output: 
			plugsetfolder, fullname = pluginsets_output[pluginset]
			dv_plugins.load_plugindir('output', plugsetfolder)
		else: dv_plugins.load_plugindir('output', '')

	def output_get_plugins(self): return dv_plugins.get_list('output')

	def output_get_plugins_names(self): return dv_plugins.get_list_names('output')

	def output_get_plugins_props(self): return dv_plugins.get_list_prop_obj('output')

	def output_get_plugins_index(self, num):
		pluglist = dv_plugins.get_list('output')
		if num != -1:
			if (len(pluglist)-1)>=num: return pluglist[min(num, len(pluglist)-1)]
			else: return None
		else:
			return None

	def output_get_pluginsets(self): return list(pluginsets_output)

	def output_get_pluginsets_index(self, num): return list(pluginsets_output)[num]

	def output_get_pluginsets_names(self): return [n[1] for _, n in pluginsets_output.items()]

	def output_get_current(self): return self.currentplug_output.selected_shortname

	def output_get_current_name(self): return self.currentplug_output.selected_plugin.name if self.currentplug_output.selected_plugin else 'None'

	def output_get_usable(self): 
		selected_plugin = self.currentplug_output.selected_plugin
		if selected_plugin:
			return selected_plugin.usable, selected_plugin.usable_meg
		else:
			return False, ''

	def output_get_extension(self): 
		prop_obj = self.currentplug_output.get_prop_obj()
		return prop_obj.file_ext if prop_obj else None

	def output_set(self, pluginname): return self.currentplug_output.set(pluginname)

	def parse_input(self, dawvert_intent): 
		self.convproj_obj = convproj.cvpj_project()
		selected_plugin = self.currentplug_input.selected_plugin
		plug_obj = selected_plugin.plug_obj
		if selected_plugin.usable:
			plug_obj.parse(self.convproj_obj, dawvert_intent)
		else:
			logger_core.error(self.currentplug_input.selected_shortname+' is not usable: '+selected_plugin.usable_meg)
			exit()

	def convert_type_output(self, dawvert_intent): 
		global in_dawinfo
		global out_dawinfo
		in_type = self.convproj_obj.type
		out_type = self.currentplug_output.selected_plugin.plug_obj.gettype()
		in_dawinfo = self.currentplug_input.selected_plugin.prop_obj
		out_dawinfo = self.currentplug_output.selected_plugin.prop_obj
		plugin_vst2.cpu_arch_list = out_dawinfo.plugin_ext_arch

		logger_core.info('' + convproj.typelist[in_type] + ' > ' + convproj.typelist[out_type])

		self.convproj_obj.main__change_type(in_dawinfo, out_dawinfo, out_type, dawvert_intent)
		if 'do_sorttracks' in self.convproj_obj.do_actions: self.convproj_obj.main__sort_tracks()

		isconverted = False
		for sampleref_id, sampleref_obj in self.convproj_obj.samplerefs.items():
			if sampleref_obj.found:
				if sampleref_obj.fileformat not in out_dawinfo.audio_filetypes:
					isconverted = sampleref_obj.convert(out_dawinfo.audio_filetypes, dawvert_intent.path_samples['extracted'])

	def convert_plugins(self, dawvert_intent): 
		plug_conv.convproj(self.convproj_obj, in_dawinfo, out_dawinfo, self.currentplug_output.selected_shortname, dawvert_intent)

	def parse_output(self, dawvert_intent): 
		plug_obj = self.currentplug_output.selected_plugin.plug_obj
		plug_obj.parse(self.convproj_obj, dawvert_intent)
		#logger_core.info('File outputted: '+out_file)
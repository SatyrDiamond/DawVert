# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from functions import data_values
from objects.file import preset_clap
from objects import globalstore
import struct
import platform
import os

import logging
logger_plugins = logging.getLogger('plugins')

cpu_arch_list = [64, 32]

def set_cpu_arch_list(cpu_arch_list_in):
	global cpu_arch_list
	cpu_arch_list = cpu_arch_list_in

def getplatformtxt(in_platform):
	if in_platform == 'win': platform_txt = 'win'
	if in_platform == 'lin': platform_txt = 'lin'
	else: 
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': platform_txt = 'win'
		else: platform_txt = 'lin'
	return platform_txt

# -------------------- VST List --------------------

def check_exists(bycat, in_val):
	return globalstore.extplug.check('clap', bycat, in_val)

def replace_data(convproj_obj, plugin_obj, bycat, platform, in_val, data):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)

	pluginfo_obj = globalstore.extplug.get('clap', bycat, in_val, platformtxt, cpu_arch_list)

	if pluginfo_obj.out_exists:
		if plugin_obj.type.type != 'clap': plugin_obj.replace('external', 'clap', None)
		else: plugin_obj.type.subtype = platformtxt
		vst_cpuarch, vst_path = pluginfo_obj.find_locpath(cpu_arch_list)
		if vst_cpuarch and vst_path:
			convproj_obj.add_fileref(vst_path, vst_path, None)
			plugin_obj.filerefs_global['plugin'] = vst_path
			plugin_obj.datavals_global.add('cpu_arch', vst_cpuarch)

		plugin_obj.datavals_global.add('name', pluginfo_obj.name)
		plugin_obj.datavals_global.add('id', pluginfo_obj.id)
		plugin_obj.datavals_global.add('creator', pluginfo_obj.creator)
		plugin_obj.datavals_global.add('numparams', pluginfo_obj.num_params)
		plugin_obj.role = pluginfo_obj.type
		plugin_obj.audioports.setnums_auto(pluginfo_obj.audio_num_inputs, pluginfo_obj.audio_num_outputs)

		plugin_obj.datavals_global.add('datatype', 'chunk')
		plugin_obj.rawdata_add('chunk', data)
	elif bycat == 'id':
		plugin_obj.replace('external', 'clap', platformtxt)
		plugin_obj.datavals_global.add('id', in_val)
		plugin_obj.datavals_global.add('datatype', 'chunk')
		plugin_obj.rawdata_add('chunk', data)

	return pluginfo_obj

def import_presetdata_raw(convproj_obj, plugin_obj, databytes, platform):
	clap_obj = preset_clap.clap_preset()
	clap_obj.read_raw(databytes)
	replace_data(convproj_obj, plugin_obj, 'id', platform, clap_obj.id, clap_obj.data)

def import_presetdata_file(convproj_obj, plugin_obj, fxfile, platform):
	clap_obj = preset_clap.clap_preset()
	clap_obj.read_file(fxfile)
	replace_data(convproj_obj, plugin_obj, 'id', platform, clap_obj.id, clap_obj.data)

def export_presetdata(plugin_obj):
	clap_obj = preset_clap.clap_preset()
	clap_obj.id = plugin_obj.datavals_global.get('id', None)
	clap_obj.data = plugin_obj.rawdata_get('chunk')
	if clap_obj.id != None: 
		return clap_obj.write_to_raw()
	else:
		logger_plugins.warning('clap: id is missing')
		return b''

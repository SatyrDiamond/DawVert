# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from functions import data_values
from objects.file import preset_vst3
from objects import globalstore
import struct
import platform
import os
import pathlib
import base64

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
	return globalstore.extplug.check('vst3', bycat, in_val)

def replace_data(convproj_obj, plugin_obj, bycat, platform, in_val, data):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)

	pluginfo_obj = globalstore.extplug.get('vst3', bycat, in_val, platformtxt, cpu_arch_list)

	if pluginfo_obj.out_exists:
		if plugin_obj.type.type != 'vst3': plugin_obj.replace('external', 'vst3', platformtxt)
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
	else:
		pluginname = plugin_obj.datavals_global.get('name', None)
		outtxt = '"'+str(in_val)+'" from '+str(bycat)
		if pluginname: outtxt = pluginname
		logger_plugins.warning('vst3: plugin not found in database: '+outtxt)

	return pluginfo_obj

def import_presetdata_raw(convproj_obj, plugin_obj, databytes, platform):
	byr_stream = bytereader.bytereader()
	byr_stream.load_raw(databytes)
	preset_obj = preset_vst3.vst3_main()
	preset_obj.parse(byr_stream)
	replace_data(convproj_obj, plugin_obj, 'id', platform, preset_obj.uuid, preset_obj.data)

def import_presetdata(convproj_obj, plugin_obj, byr_stream, platform):
	preset_obj = preset_vst3.vst3_main()
	preset_obj.parse(byr_stream)
	replace_data(convproj_obj, plugin_obj, 'id', platform, preset_obj.uuid, preset_obj.data)

def import_presetdata_file(convproj_obj, plugin_obj, fxfile, platform):
	preset_obj = preset_vst3.vst3_main()
	preset_obj.read_file(fxfile)
	replace_data(convproj_obj, plugin_obj, 'id', platform, preset_obj.uuid, preset_obj.data)

def export_presetdata(plugin_obj):
	byw_stream = bytewriter.bytewriter()
	preset_obj = preset_vst3.vst3_main()
	datatype = plugin_obj.datavals_global.get('datatype', 'chunk')
	vstid = plugin_obj.datavals_global.get('id', None)
	if vstid != None:
		preset_obj.uuid = vstid
		preset_obj.data = plugin_obj.rawdata_get('chunk')
		preset_obj.write(byw_stream)
		return byw_stream.getvalue()
	else:
		logger_plugins.warning('vst3: id is missing')
		return b''

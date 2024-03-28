# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from objects import manager_extplug
import struct
import platform
import os
import pathlib
import base64

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
	return manager_extplug.vst3_check(bycat, in_val)

def replace_data(convproj_obj, plugin_obj, bycat, platform, in_val, data):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)

	pluginfo_obj = manager_extplug.vst3_get(bycat, in_val, platformtxt, cpu_arch_list)

	if pluginfo_obj.out_exists:
		if plugin_obj.plugin_type != 'vst3': plugin_obj.replace('vst3', platformtxt)
		else: plugin_obj.plugin_subtype = platformtxt

		vst_cpuarch, vst_path = pluginfo_obj.find_locpath(cpu_arch_list)
		if vst_cpuarch and vst_path:
			convproj_obj.add_fileref(vst_path, vst_path)
			plugin_obj.filerefs['plugin'] = vst_path
			plugin_obj.datavals.add('cpu_arch', vst_cpuarch)

		plugin_obj.datavals.add('name', pluginfo_obj.name)
		plugin_obj.datavals.add('id', pluginfo_obj.id)
		plugin_obj.datavals.add('creator', pluginfo_obj.creator)
		plugin_obj.role = pluginfo_obj.type
		plugin_obj.audioports.setnums_auto(pluginfo_obj.audio_num_inputs, pluginfo_obj.audio_num_outputs)

		plugin_obj.datavals.add('datatype', 'chunk')
		plugin_obj.rawdata_add('chunk', data)

	return pluginfo_obj

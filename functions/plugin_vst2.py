# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import exists
import configparser
import base64
import struct
import platform
import os

glo_vstpaths = {}

cpu_arch_list = ['amd64', 'i386']

def set_cpu_arch_list(cpu_arch_list_in):
	global cpu_arch_list
	cpu_arch_list = cpu_arch_list_in

def getplatformtxt(in_platform):
	if in_platform == 'win': platform_txt = 'dll'
	if in_platform == 'lin': platform_txt = 'so'
	if in_platform == 'any': 
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': platform_txt = 'dll'
		else: platform_txt = 'so'
	return platform_txt

# -------------------- VST List --------------------

def get_path(platformtype, vstname, pefer_cpu_arch):
	global cpu_arch_list
	output = [None, None]
	if pefer_cpu_arch != None:
		if 'path_'+pefer_cpu_arch in glo_vstpaths[platformtype][vstname]:
			output = [pefer_cpu_arch, glo_vstpaths[platformtype][vstname]['path_'+pefer_cpu_arch]]
	for cpu_arch_part in cpu_arch_list:
		if 'path_'+cpu_arch_part in glo_vstpaths[platformtype][vstname]:
			output = [cpu_arch_part, glo_vstpaths[platformtype][vstname]['path_'+cpu_arch_part]]
	return output

def find_path_by_name(in_name, platformtype, pefer_cpu_arch):
	output = [None, None]
	platformtxt = getplatformtxt(platformtype)
	for vstname in glo_vstpaths[platformtxt]:
		if in_name == vstname: output = get_path(platformtxt, vstname, pefer_cpu_arch)
	return output

def replace_data(instdata, platform, in_name, datatype, data, numparams):
	global cpu_arch_list
	vst_cpuarch, vst_path = find_path_by_name(in_name, platform, cpu_arch_list[0])
	platformtxt = getplatformtxt(platform)
	if vst_path != None:
		vstinfo = glo_vstpaths[platformtxt][in_name]
		if 'plugin' not in instdata: instdata['plugin'] = 'none'
		print('[list-vst2] ' + instdata['plugin'] +' > ' + in_name + ' (VST2 '+vst_cpuarch+')')
		instdata['plugin'] = 'vst2-'+platformtxt
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = in_name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['plugin']['cpu_arch'] = vst_cpuarch
		instdata['plugindata']['plugin']['fourid'] = int(vstinfo['fourid'])
		if 'version' in vstinfo: 
			versionsplit = [int(i) for i in vstinfo['version'].split('.')]
			versionbytes =  struct.pack('B'*len(versionsplit), *versionsplit)
			instdata['plugindata']['plugin']['version'] = int.from_bytes(versionbytes, "little")

		if datatype == 'chunk':
			instdata['plugindata']['datatype'] = 'chunk'
			instdata['plugindata']['data'] = base64.b64encode(data).decode('ascii')
		if datatype == 'param':
			instdata['plugindata']['datatype'] = 'param'
			instdata['plugindata']['numparams'] = numparams
			instdata['plugindata']['params'] = data

def vstpaths(): return glo_vstpaths

def loadlist(filepath, platform):
	vstpaths = {}
	if exists(filepath):
		vstpaths = configparser.ConfigParser()
		vstpaths.read(filepath)
		list_loaded = True
		print('[list-vst2] # of VST2 Plugins:', len(vstpaths))
	else: list_loaded = False
	glo_vstpaths[getplatformtxt(platform)] = vstpaths

def listinit():
	currentdir = os.getcwd() + '/__config/'
	os.makedirs(currentdir, exist_ok=True)
	loadlist(currentdir+'plugins_vst2_win.ini', 'win')
	loadlist(currentdir+'plugins_vst3_win.ini', 'lin')
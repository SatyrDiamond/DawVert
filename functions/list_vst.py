# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import exists
import configparser
import base64
import platform

glo_vstpaths = {}
glo_vstpaths_loaded = {}

cpu_arch_list = ['amd64', 'i386']
vst_version_list = [2, 3]

def set_cpu_arch_list(cpu_arch_list_in):
	global cpu_arch_list
	cpu_arch_list = cpu_arch_list_in

def set_vst_version_list(vst_version_list_in):
	global vst_version_list
	vst_version_list = vst_version_list_in

def getplatformtxt(in_platform):
	if in_platform == 'win': platform_txt = 'dll'
	if in_platform == 'lin': platform_txt = 'so'
	if in_platform == 'any': 
		platform_architecture = platform.architecture()
		print(platform_architecture)
		if platform_architecture[1] == 'WindowsPE': platform_txt = 'dll'
		else: platform_txt = 'so'
	return platform_txt

def getverplat(vstvers, platform):
	platform_txt = getplatformtxt(platform)
	if platform_txt != '': platform_txt = '-'+platform_txt
	return str(vstvers)+platform_txt

# -------------------- VST List --------------------
def vstpaths(): return glo_vstpaths
def vstpaths_loaded(): return glo_vstpaths_loaded

def find_path_by_name(in_name, vstvers, platform, pefer_cpu_arch):
	output = [None, None]
	verplat = getverplat(vstvers, platform)
	if verplat in glo_vstpaths:
		for vstname in glo_vstpaths[verplat]:
			if pefer_cpu_arch != None:
				if 'path_'+pefer_cpu_arch in glo_vstpaths[verplat][vstname] and vstname == in_name:
					output = [pefer_cpu_arch, glo_vstpaths[verplat][vstname]['path_'+pefer_cpu_arch]]
					if output != [None, None]: break
			for cpu_arch_part in cpu_arch_list:
				if 'path_'+cpu_arch_part in glo_vstpaths[verplat][vstname] and vstname == in_name:
					output = [cpu_arch_part, glo_vstpaths[verplat][vstname]['path_'+cpu_arch_part]]
					if output != [None, None]: break
	return output

def replace_data(instdata, vstvers, platform, in_name, datatype, data, numparams):
	vst_cpuarch, vst_path = find_path_by_name(in_name, vstvers, platform, cpu_arch_list[0])
	verplat = getverplat(vstvers, platform)
	if vst_path != None:
		if 'plugin' not in instdata: instdata['plugin'] = 'none'
		print('[list-vst'+verplat+'] ' + instdata['plugin'] +' > ' + in_name + ' (VST'+str(vstvers)+' '+vst_cpuarch+')')
		instdata['plugin'] = 'vst'+verplat
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = in_name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['plugin']['cpu_arch'] = vst_cpuarch
		if datatype == 'raw':
			instdata['plugindata']['datatype'] = 'raw'
			instdata['plugindata']['data'] = base64.b64encode(data).decode('ascii')
		if datatype == 'param':
			instdata['plugindata']['datatype'] = 'param'
			instdata['plugindata']['numparams'] = numparams
			instdata['plugindata']['params'] = data

def loadlist(filepath, vstvers, platform):
	vstpaths = None
	verplat = getverplat(vstvers, platform)
	if exists(filepath):
		vstpaths = configparser.ConfigParser()
		vstpaths.read(filepath)
		list_loaded = True
		print('[list-vst'+verplat+'] # of VST2 Plugins:', len(vstpaths))
	else: list_loaded = False
	glo_vstpaths[verplat] = vstpaths

def listinit():
	loadlist('vst2_win.ini', '2', 'win')
	loadlist('vst3_win.ini', '3', 'win')
	loadlist('vst2_lin.ini', '2', 'lin')
	loadlist('vst3_lin.ini', '3', 'lin')
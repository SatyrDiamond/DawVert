# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import exists
import configparser
import base64
import struct
import platform
import os
import sqlite3

glo_vstpaths = {}

cpu_arch_list = [64, 32]

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
else: platformtxt = 'lin'

os.makedirs(os.getcwd() + '/__config/', exist_ok=True)

db_exists = False

if os.path.exists('./__config/plugins_external.db'):
	db_plugins = sqlite3.connect('./__config/plugins_external.db')
	db_exists = True

def set_cpu_arch_list(cpu_arch_list_in):
	global cpu_arch_list
	cpu_arch_list = cpu_arch_list_in

def getplatformtxt(in_platform):
	if in_platform == 'win': platform_txt = 'win'
	if in_platform == 'lin': platform_txt = 'lin'
	if in_platform == 'any': 
		platform_architecture = platform.architecture()
		if platform_architecture[1] == 'WindowsPE': platform_txt = 'win'
		else: platform_txt = 'lin'
	return platform_txt

# -------------------- VST List --------------------

def find_path_by_name(in_name, platformtype):
	vst_cpuarch = None
	vst_path = None

	if db_exists:
		if platformtype == 'win': out_paths = db_plugins.execute("SELECT path_32bit_win, path_64bit_win FROM vst2 WHERE name = ?", (in_name,)).fetchone()
		if platformtype == 'lin': out_paths = db_plugins.execute("SELECT path_32bit_unix, path_64bit_unix FROM vst2 WHERE name = ?", (in_name,)).fetchone()
	else:
		out_paths = [None, None]

	if out_paths[0] != None and out_paths[1] == None and 32 in cpu_arch_list: 
		vst_cpuarch = 32
		vst_path = out_paths[0]
	if out_paths[0] == None and out_paths[1] != None and 64 in cpu_arch_list: 
		vst_cpuarch = 64
		vst_path = out_paths[1]

	return vst_cpuarch, vst_path

def check_exists(in_name):
	if db_exists:
		outval = db_plugins.execute("SELECT count(*) FROM vst2 WHERE name = ?", (in_name,)).fetchone()
		return bool(outval[0])
	else:
		return False

def replace_data(instdata, platform, in_name, datatype, data, numparams):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)
	vst_cpuarch, vst_path = find_path_by_name(in_name, platformtxt)

	if vst_path != None:

		if 'plugin' not in instdata: instdata['plugin'] = 'none'
		print('[list-vst2] ' + instdata['plugin'] +' > ' + in_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')

		if platformtxt == 'win': instdata['plugin'] = 'vst2-dll'
		if platformtxt == 'lin': instdata['plugin'] = 'vst2-so'
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = in_name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['plugin']['cpu_arch'] = vst_cpuarch

		if db_exists:
			fouridval = db_plugins.execute("SELECT id FROM vst2 WHERE name = ?", (in_name,)).fetchone()
			versionval = db_plugins.execute("SELECT version FROM vst2 WHERE name = ?", (in_name,)).fetchone()

		if fouridval != None: instdata['plugindata']['plugin']['fourid'] = int(fouridval[0])

		if versionval != None: 
			versionsplit = [int(i) for i in versionval[0].split('.')]
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

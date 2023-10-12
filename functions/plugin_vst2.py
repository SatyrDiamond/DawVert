# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from os.path import exists
from functions import data_values
from functions import plugins
import configparser
import base64
import struct
import platform
import os
import sqlite3

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

def find_locpath(out_paths):
	vst_cpuarch = None
	vst_path = None

	if out_paths[0] != None and out_paths[1] == None and 32 in cpu_arch_list: 
		vst_cpuarch = 32
		vst_path = out_paths[0]
	if out_paths[0] == None and out_paths[1] != None and 64 in cpu_arch_list: 
		vst_cpuarch = 64
		vst_path = out_paths[1]
	if out_paths[0] != None and out_paths[1] != None and 64 in cpu_arch_list: 
		vst_cpuarch = 64
		vst_path = out_paths[1]

	return vst_cpuarch, vst_path

def find_path(in_data, platformtype, bycat):
	vst_cpuarch = None
	vst_path = None
	vst_name = None

	if db_exists:
		if bycat == 'name':
			vst_name = in_data
			if platformtype == 'win': out_paths = db_plugins.execute("SELECT path_32bit_win, path_64bit_win FROM vst2 WHERE name = ?", (in_data,)).fetchone()
			else: out_paths = db_plugins.execute("SELECT path_32bit_unix, path_64bit_unix FROM vst2 WHERE name = ?", (in_data,)).fetchone()
		if bycat == 'id':
			if platformtype == 'win':  out_paths = db_plugins.execute("SELECT path_32bit_win, path_64bit_win FROM vst2 WHERE id = ?", (in_data,)).fetchone()
			else: out_paths = db_plugins.execute("SELECT path_32bit_unix, path_64bit_unix FROM vst2 WHERE id = ?", (in_data,)).fetchone()
			vst_name = db_plugins.execute("SELECT name FROM vst2 WHERE id = ?", (in_data,)).fetchone()[0]
	else:
		out_paths = [None, None]

	#print(bycat, vst_cpuarch, out_paths, vst_name)
	if out_paths == None: out_paths = [None, None]
	vst_cpuarch, vst_path = find_locpath(out_paths)

	return vst_cpuarch, vst_path, vst_name

def check_exists(in_name):
	if db_exists:
		outval = db_plugins.execute("SELECT count(*) FROM vst2 WHERE name = ?", (in_name,)).fetchone()
		return bool(outval[0])
	else:
		return False

def replace_data(cvpj_l, pluginid, bycat, platform, in_name, datatype, data, numparams):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)
	vst_cpuarch, vst_path, vst_name = find_path(in_name, platformtxt, bycat)

	if vst_path != None:
		plugintype = plugins.get_plug_type(cvpj_l, pluginid)

		if plugintype[0] != 'vst2':
			plugins.replace_plug(cvpj_l, pluginid, 'vst2', platformtxt)

		if bycat == 'name': 
			if plugintype[0] == None and plugintype[1] == None: print('[plugin-vst2] ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')
			if plugintype[0] != None and plugintype[1] == None: print('[plugin-vst2] ' + plugintype[0] +' > ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')
			if plugintype[0] != None and plugintype[1] != None: print('[plugin-vst2] ' + ':'.join(plugintype) +' > ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')

		plugins.add_plug_data(cvpj_l, pluginid, 'name', vst_name)
		plugins.add_plug_data(cvpj_l, pluginid, 'path', vst_path)
		plugins.add_plug_data(cvpj_l, pluginid, 'cpu_arch', vst_cpuarch)

		if db_exists:
			if bycat == 'name':
				fouridval = db_plugins.execute("SELECT id FROM vst2 WHERE name = ?", (in_name,)).fetchone()
				versionval = db_plugins.execute("SELECT version FROM vst2 WHERE name = ?", (in_name,)).fetchone()
			if bycat == 'id':
				fouridval = in_name
				versionval = db_plugins.execute("SELECT version FROM vst2 WHERE name = ?", (in_name,)).fetchone()

		if fouridval != None and fouridval != (None,): 
			if bycat == 'name':
				plugins.add_plug_data(cvpj_l, pluginid, 'fourid', int(fouridval[0]))
			if bycat == 'id':
				plugins.add_plug_data(cvpj_l, pluginid, 'fourid', in_name)

		if versionval != None and versionval != (None,) and versionval != ('',): 
			versionsplit = [int(i) for i in versionval[0].split('.')]
			versionbytes =  struct.pack('B'*len(versionsplit), *versionsplit)
			plugins.add_plug_data(cvpj_l, pluginid, 'version', int.from_bytes(versionbytes, "little"))

		if datatype == 'chunk':
			plugins.add_plug_data(cvpj_l, pluginid, 'datatype', 'chunk')
			plugins.add_plug_data(cvpj_l, pluginid, 'chunk', base64.b64encode(data).decode('ascii'))
		if datatype == 'param':
			plugins.add_plug_data(cvpj_l, pluginid, 'datatype', 'param')
			plugins.add_plug_data(cvpj_l, pluginid, 'numparams', numparams) 
		if datatype == 'bank':
			plugins.add_plug_data(cvpj_l, pluginid, 'datatype', 'bank')
			plugins.add_plug_data(cvpj_l, pluginid, 'programs', data) 
	else:
		print('[plugin-vst2] Plugin, '+str(in_name)+' not found.')

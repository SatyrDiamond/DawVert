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
	if out_paths[0] != None and out_paths[1] == None and 32 in cpu_arch_list: vst_cpuarch, vst_path = 32, out_paths[0]
	if out_paths[0] == None and out_paths[1] != None and 64 in cpu_arch_list: vst_cpuarch, vst_path = 64, out_paths[1]
	if out_paths[0] != None and out_paths[1] != None and 64 in cpu_arch_list: vst_cpuarch, vst_path = 64, out_paths[1]
	return vst_cpuarch, vst_path

def db_search(in_data, platformtype, bycat):
	vst_cpuarch = None
	vst_path = None
	vst_name = None
	vst_id = None
	vst_version = None
	out_paths = [None, None]

	if db_exists:
		if bycat == 'name':
			if platformtype == 'win': out_paths = db_plugins.execute("SELECT path_32bit_win, path_64bit_win FROM vst2 WHERE name = ?", (in_data,)).fetchone()
			else: out_paths = db_plugins.execute("SELECT path_32bit_unix, path_64bit_unix FROM vst2 WHERE name = ?", (in_data,)).fetchone()
			vst_name = in_data
			vst_id = db_plugins.execute("SELECT id FROM vst2 WHERE name = ?", (in_data,)).fetchone()[0]

		if bycat == 'id':
			if platformtype == 'win': out_paths = db_plugins.execute("SELECT path_32bit_win, path_64bit_win FROM vst2 WHERE id = ?", (in_data,)).fetchone()
			else: out_paths = db_plugins.execute("SELECT path_32bit_unix, path_64bit_unix FROM vst2 WHERE id = ?", (in_data,)).fetchone()
			vst_name = db_plugins.execute("SELECT name FROM vst2 WHERE id = ?", (in_data,)).fetchone()[0]
			vst_id = in_data

		if bycat == 'path':
			if platformtype == 'win': 
				vst_path = in_data.replace('/', '\\')
				vstname_32 = db_plugins.execute("SELECT name FROM vst2 WHERE path_32bit_win = ?", (vst_path,)).fetchone()
				vstname_64 = db_plugins.execute("SELECT name FROM vst2 WHERE path_64bit_win = ?", (vst_path,)).fetchone()
				vstpath_32 = db_plugins.execute("SELECT name, id, path_32bit_win, path_64bit_win FROM vst2 WHERE path_32bit_win = ?", (vst_path,)).fetchone()
				vstpath_64 = db_plugins.execute("SELECT name, id, path_32bit_win, path_64bit_win FROM vst2 WHERE path_64bit_win = ?", (vst_path,)).fetchone()
			else: 
				vstname_32 = db_plugins.execute("SELECT name FROM vst2 WHERE path_32bit_unix = ?", (vst_path,)).fetchone()
				vstname_64 = db_plugins.execute("SELECT name FROM vst2 WHERE path_64bit_unix = ?", (vst_path,)).fetchone()
				vstpath_32 = db_plugins.execute("SELECT name, id, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_32bit_unix = ?", (vst_path,)).fetchone()
				vstpath_64 = db_plugins.execute("SELECT name, id, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_64bit_unix = ?", (vst_path,)).fetchone()

			if vstname_32 != None: vst_cpuarch = 32
			if vstname_64 != None: vst_cpuarch = 64

			vst_paths = data_values.list_usefirst([vstpath_32, vstpath_64])
			if vst_paths != None: 
				vst_name = vst_paths[0]
				vst_id = vst_paths[1]
				out_paths = [vst_paths[2], vst_paths[3]]

		if vst_id:
			vst_version_db = db_plugins.execute("SELECT version FROM vst2 WHERE id = ?", (str(vst_id),)).fetchone()
			if vst_version_db: vst_version = vst_version_db[0]

	if out_paths == None: out_paths = [None, None]
	vst_cpuarch, vst_path = find_locpath(out_paths)

	return vst_cpuarch, vst_path, vst_name, vst_id, vst_version

def check_exists(in_name):
	if db_exists:
		outval = db_plugins.execute("SELECT count(*) FROM vst2 WHERE name = ?", (in_name,)).fetchone()
		return bool(outval[0])
	else:
		return False

def replace_data(cvpj_plugindata, bycat, platform, in_name, datatype, data, numparams):
	global cpu_arch_list
	platformtxt = getplatformtxt(platform)
	vst_cpuarch, vst_path, vst_name, vst_id, vst_version = db_search(in_name, platformtxt, bycat)

	if vst_path != None:
		plugintype = cvpj_plugindata.type_get()

		if plugintype[0] != 'vst2': cvpj_plugindata.replace('vst2', platformtxt)

		if bycat == 'name': 
			if plugintype[0] == None and plugintype[1] == None: print('[plugin-vst2] ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')
			if plugintype[0] != None and plugintype[1] == None: print('[plugin-vst2] ' + plugintype[0] +' > ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')
			if plugintype[0] != None and plugintype[1] != None: print('[plugin-vst2] ' + ':'.join(plugintype) +' > ' + vst_name + ' (VST2 '+str(vst_cpuarch)+'-bit)')

		cvpj_plugindata.dataval_add('name', vst_name)
		cvpj_plugindata.dataval_add('path', vst_path)
		cvpj_plugindata.dataval_add('cpu_arch', vst_cpuarch)
		cvpj_plugindata.dataval_add('fourid', int(vst_id))
		cvpj_plugindata.dataval_add('version', vst_version)

		if vst_version != None: 
			versionsplit = [int(i) for i in vst_version.split('.')]
			versionbytes =  struct.pack('B'*len(versionsplit), *versionsplit)
			cvpj_plugindata.dataval_add('version_bytes', int.from_bytes(versionbytes, "little"))
			cvpj_plugindata.dataval_add('version', vst_version)

		if datatype == 'chunk':
			cvpj_plugindata.dataval_add('datatype', 'chunk')
			cvpj_plugindata.rawdata_add(data)
		if datatype == 'param':
			cvpj_plugindata.dataval_add('datatype', 'param')
			cvpj_plugindata.dataval_add('numparams', numparams) 
		if datatype == 'bank':
			cvpj_plugindata.dataval_add('datatype', 'bank')
			cvpj_plugindata.dataval_add('programs', data) 
	else:
		print('[plugin-vst2] Plugin, '+str(in_name)+' not found.')

	return cvpj_plugindata
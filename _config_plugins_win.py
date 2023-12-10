import winreg
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import exists
import sqlite3
import uuid

os.makedirs(os.getcwd() + '/__config/', exist_ok=True)
db_plugins = sqlite3.connect('./__config/plugins_external.db')

db_plugins.execute('''
	CREATE TABLE IF NOT EXISTS vst2(
		 name text,
		 id text,
		 type text,
		 creator text,
		 version text,
		 audio_num_inputs integer,
		 audio_num_outputs integer,
		 midi_num_inputs integer,
		 midi_num_outputs integer,
		 num_params integer,
		 path_32bit_win text,
		 path_64bit_win text,
		 path_32bit_unix text,
		 path_64bit_unix text,
		 UNIQUE(id)
	)''')

db_plugins.execute('''
	CREATE TABLE IF NOT EXISTS vst3(
		name text,
		id text,
		creator text,
		category text,
		version text,
		sdk_version text,
		url text,
		email text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		midi_num_inputs integer,
		midi_num_outputs integer,
		num_params integer,
		path_32bit_win text,
		path_64bit_win text,
		path_32bit_unix text,
		path_64bit_unix text,
		UNIQUE(id)
	)''')

db_plugins.execute('''
	CREATE TABLE IF NOT EXISTS clap(
		name text,
		id text,
		creator text,
		category text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		midi_num_inputs integer,
		midi_num_outputs integer,
		path_64bit_win text,
		path_64bit_unix text,
		UNIQUE(id)
	)''')

def reg_get(name, regpath):
	try:
		registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regpath, 0, winreg.KEY_READ)
		value, regtype = winreg.QueryValueEx(registry_key, name)
		winreg.CloseKey(registry_key)
		return value
	except WindowsError:
		return None

def reg_list(winregpath):
	winregobj = winreg.OpenKey(winreg.HKEY_CURRENT_USER, winregpath)
	pathlist = []
	i = 0
	while True:
		try:
			keypath = winreg.EnumKey(winregobj, i)
			pathlist.append(w_regkey_cakewalk + '\\' + keypath)
			i += 1
		except WindowsError: break
	return pathlist

def reg_checkexist(winregpath):
	try:
		winregobj_cakewalk = winreg.OpenKey(winreg.HKEY_CURRENT_USER, winregpath)
		return True
	except: return False

dawlist = []

homepath = os.path.expanduser("~")

w_regkey_cakewalk = 'SOFTWARE\\Cakewalk Music Software\\Cakewalk\\Cakewalk VST X64\\Inventory'

path_flstudio = os.path.join(homepath, "Documents", "Image-Line", "FL Studio", "Presets", "Plugin database", "Installed")
path_flstudio_vst2_inst = os.path.join(homepath, "Documents", "Image-Line", "FL Studio", "Presets", "Plugin database", "Installed", "Generators", "VST")
path_flstudio_vst2_fx = os.path.join(homepath, "Documents", "Image-Line", "FL Studio", "Presets", "Plugin database", "Installed", "Effects", "VST")
path_flstudio_vst3_inst = os.path.join(homepath, "Documents", "Image-Line", "FL Studio", "Presets", "Plugin database", "Installed", "Generators", "VST3")
path_flstudio_vst3_fx = os.path.join(homepath, "Documents", "Image-Line", "FL Studio", "Presets", "Plugin database", "Installed", "Effects", "VST3")

path_ploguebidule = os.path.join(homepath, "AppData", "Roaming", "Plogue", "Bidule")
path_ploguebidule_vst3_64 = os.path.join(homepath, "AppData", "Roaming", "Plogue", "Bidule", "vst3_x64.cache")
path_ploguebidule_vst2_64 = os.path.join(homepath, "AppData", "Roaming", "Plogue", "Bidule", "vst_x64.cache")
path_ploguebidule_clap_64 = os.path.join(homepath, "AppData", "Roaming", "Plogue", "Bidule", "clap_x64.cache")


if reg_checkexist(w_regkey_cakewalk) == True: dawlist.append('cakewalk')
if os.path.exists(path_flstudio) == True: dawlist.append('flstudio')
if os.path.exists(path_ploguebidule) == True: dawlist.append('bidule')

if len(dawlist) == 0:
	print('[dawvert-vst] No DAWs Found. exit', end=' ')
	exit()

#  ------------------------------------- CakeWalk -------------------------------------
if 'cakewalk' in dawlist:
	print('[dawvert-vst] Importing Plugin List from: Cakewalk')
	vstlist = reg_list(w_regkey_cakewalk)
	for vstplugin in vstlist:
		registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, vstplugin, 0, winreg.KEY_READ)
		try: vst_is_v2 = winreg.QueryValueEx(registry_key, 'isVst')[0]
		except WindowsError: vst_is_v2 = 0
		try: vst_is_v3 = winreg.QueryValueEx(registry_key, 'isVst3')[0]
		except WindowsError: vst_is_v3 = 0
		vst_path = winreg.QueryValueEx(registry_key, 'FullPath')[0]
		if (vst_is_v2 == 1 or vst_is_v3 == 1) and os.path.exists(vst_path):
			vst_name = winreg.QueryValueEx(registry_key, 'FullName')[0]
			vst_uniqueId = winreg.QueryValueEx(registry_key, 'uniqueId')[0]
			vst_Vendor = winreg.QueryValueEx(registry_key, 'Vendor')[0]
			vst_is64 = winreg.QueryValueEx(registry_key, 'isX64')[0]
			vst_isSynth = winreg.QueryValueEx(registry_key, 'isSynth')[0]
			vst_numInputs = winreg.QueryValueEx(registry_key, 'numInputs')[0]
			vst_numOutputs = winreg.QueryValueEx(registry_key, 'numOutputs')[0]
			vst_numParams = winreg.QueryValueEx(registry_key, 'numParams')[0]

			if vst_is_v2 == 1:
				db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (vst_uniqueId,))
				db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (vst_name, vst_uniqueId,))
				if vst_is64 == 1: db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (vst_path, vst_uniqueId,))
				else: db_plugins.execute("UPDATE vst2 SET path_32bit_win = ? WHERE id = ?", (vst_path, vst_uniqueId,))
				if vst_isSynth == 1: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", ('synth', vst_uniqueId,))
				else: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", ('effect', vst_uniqueId,))
				if vst_Vendor != None: db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (vst_Vendor, vst_uniqueId,))
				db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (vst_numInputs, vst_uniqueId,))
				db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (vst_numOutputs, vst_uniqueId,))
				db_plugins.execute("UPDATE vst2 SET num_params = ? WHERE id = ?", (vst_numParams, vst_uniqueId,))

			if vst_is_v3 == 1:
				vst_clsidPlug = uuid.UUID(winreg.QueryValueEx(registry_key, 'clsidPlug')[0]).hex.upper()
				vst_Subcategories = winreg.QueryValueEx(registry_key, 'Subcategories')[0]
				db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (vst_clsidPlug,))
				db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (vst_name, vst_clsidPlug,))
				if vst_is64 == 1: db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (vst_path, vst_clsidPlug,))
				else: db_plugins.execute("UPDATE vst3 SET path_32bit_win = ? WHERE id = ?", (vst_path, vst_clsidPlug,))
				if vst_Subcategories != None: db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (vst_Subcategories, vst_clsidPlug,))
				if vst_Vendor != None: db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (vst_Vendor, vst_clsidPlug,))
				db_plugins.execute("UPDATE vst3 SET audio_num_inputs = ? WHERE id = ?", (vst_numInputs, vst_clsidPlug,))
				db_plugins.execute("UPDATE vst3 SET audio_num_outputs = ? WHERE id = ?", (vst_numOutputs, vst_clsidPlug,))
				db_plugins.execute("UPDATE vst3 SET num_params = ? WHERE id = ?", (vst_numParams, vst_clsidPlug,))

#  ------------------------------------- CakeWalk -------------------------------------
if 'flstudio' in dawlist:
	print('[dawvert-vst] Importing Plugin List from: FL Studio')
	for pathtype in [ ['vst2',path_flstudio_vst2_inst],['vst2',path_flstudio_vst2_fx],['vst3',path_flstudio_vst3_inst],['vst3',path_flstudio_vst3_fx] ]:
		for filename in os.listdir(pathtype[1]):
			if '.nfo' in filename:
				bio_data = open(pathtype[1]+'\\'+filename, "r")
				flp_nfo_plugdata = bio_data.readlines()

				dict_vstinfo = {}
				for s_flp_nfo_plugdata in flp_nfo_plugdata:
					splittedtxt = s_flp_nfo_plugdata.strip().split('=')
					dict_vstinfo[splittedtxt[0]] = splittedtxt[1]

				for filenum in range(int(dict_vstinfo['ps_files'])):
					if pathtype[0] == 'vst2':
						if 'ps_file_magic_'+str(filenum) in dict_vstinfo:
							if os.path.exists(dict_vstinfo['ps_file_filename_'+str(filenum)]):
								vst_uniqueId = dict_vstinfo['ps_file_magic_'+str(filenum)]
								db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (vst_uniqueId,))
								db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (dict_vstinfo['ps_file_name_'+str(filenum)], vst_uniqueId,))
								if 'ps_file_vendorname_'+str(filenum) in dict_vstinfo: db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (dict_vstinfo['ps_file_vendorname_'+str(filenum)], vst_uniqueId,))
								if 'ps_file_category_'+str(filenum) in dict_vstinfo: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", (dict_vstinfo['ps_file_category_'+str(filenum)].lower(), vst_uniqueId,))
								if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '32': db_plugins.execute("UPDATE vst2 SET path_32bit_win = ? WHERE id = ?", (dict_vstinfo['ps_file_filename_'+str(filenum)], vst_uniqueId,))
								if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '64': db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (dict_vstinfo['ps_file_filename_'+str(filenum)], vst_uniqueId,))

					if pathtype[0] == 'vst3':
						if 'ps_file_guid_'+str(filenum) in dict_vstinfo:
							if os.path.exists(dict_vstinfo['ps_file_filename_'+str(filenum)]):
								vst_uniqueId = uuid.UUID(dict_vstinfo['ps_file_guid_'+str(filenum)]).hex.upper()
								db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (vst_uniqueId,))
								db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (dict_vstinfo['ps_file_name_'+str(filenum)], vst_uniqueId,))
								if 'ps_file_vendorname_'+str(filenum) in dict_vstinfo: db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (dict_vstinfo['ps_file_vendorname_'+str(filenum)], vst_uniqueId,))
								if 'ps_file_category_'+str(filenum) in dict_vstinfo: db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (dict_vstinfo['ps_file_category_'+str(filenum)], vst_uniqueId,))
								if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '32': db_plugins.execute("UPDATE vst3 SET path_32bit_win = ? WHERE id = ?", (dict_vstinfo['ps_file_filename_'+str(filenum)], vst_uniqueId,))
								if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '64': db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (dict_vstinfo['ps_file_filename_'+str(filenum)], vst_uniqueId,))

#  ------------------------------------- CakeWalk -------------------------------------
if 'bidule' in dawlist:
	print('[dawvert-vst] Importing Plugin List from: Plogue Bidule')

	if os.path.exists(path_ploguebidule_vst2_64) == True:
		bio_data = open(path_ploguebidule_vst2_64, "r")
		for vstline in bio_data.readlines():
			vstsplit = vstline.strip().split(';')
			if '_' not in vstsplit[5]:
				if os.path.exists(vstsplit[0]) == True:
					vst_uniqueId = vstsplit[5]
					db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (vst_uniqueId,))
					db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (vstsplit[0], vst_uniqueId,))
					db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (vstsplit[2], vst_uniqueId,))
					db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (vstsplit[3], vst_uniqueId,))

	if os.path.exists(path_ploguebidule_vst3_64) == True:
		bio_data = open(path_ploguebidule_vst3_64, "r")
		for vstline in bio_data.readlines():
			vstsplit = vstline.strip().split(';')
			if '_' not in vstsplit[3]:
				if os.path.exists(vstsplit[0]) == True:
					vst_uniqueId = uuid.UUID(vstsplit[3]).hex.upper()
					db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (vst_uniqueId,))
					db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (vstsplit[0], vst_uniqueId,))
					db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (vstsplit[1], vst_uniqueId,))
					db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (vstsplit[2], vst_uniqueId,))

	if os.path.exists(path_ploguebidule_clap_64) == True:
		bio_data = open(path_ploguebidule_clap_64, "r")
		for vstline in bio_data.readlines():
			clapsplit = vstline.strip().split(';')
			if os.path.exists(vstsplit[0]) == True:
				vst_uniqueId = clapsplit[3]
				db_plugins.execute("INSERT OR IGNORE INTO clap (id) VALUES (?)", (vst_uniqueId,))
				db_plugins.execute("UPDATE clap SET path_64bit_win = ? WHERE id = ?", (clapsplit[0], vst_uniqueId,))
				db_plugins.execute("UPDATE clap SET name = ? WHERE id = ?", (clapsplit[1], vst_uniqueId,))
				db_plugins.execute("UPDATE clap SET creator = ? WHERE id = ?", (clapsplit[2], vst_uniqueId,))



#  ------------------------------------- Output -------------------------------------

db_plugins.commit()
db_plugins.close()

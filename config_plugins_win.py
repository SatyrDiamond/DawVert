import winreg
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import exists
import sqlite3
import uuid

os.makedirs(os.getcwd() + '/__config/', exist_ok=True)
db_plugins = sqlite3.connect('./__config/plugins_plugins_win.db')

db_plugins.execute('''
   CREATE TABLE IF NOT EXISTS vst2(
       name text,
       internal_name text,
       id text,
       type text,
       creator text,
       version text,
       audio_num_inputs integer,
       audio_num_outputs integer,
       midi_num_inputs integer,
       midi_num_outputs integer,
       path_32bit text,
       path_64bit text,
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
      path_32bit text,
      path_64bit text,
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

if reg_checkexist(w_regkey_cakewalk) == True: dawlist.append('cakewalk')

#if len(dawlist) >= 1:
#	print('[dawvert-vst] Plugin List from DAWs Found:', end=' ')
#	for daw in dawlist: print(daw, end=' ')
#	print()
#	selecteddaw=input("[dawvert-vst] Select one to import: ")
#	if selecteddaw not in dawlist:
#		print('[dawvert-vst] exit', end=' ')
#		exit()
elif len(dawlist) == 0:
	print('[dawvert-vst] No DAWs Found. exit', end=' ')
	exit()

#  ------------------------------------- CakeWalk -------------------------------------
if 'cakewalk' in dawlist:
	print('[dawvert-vst] Importing VST List from: Cakewalk')
	vstlist = reg_list(w_regkey_cakewalk)
	for vstplugin in vstlist:
		registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, vstplugin, 0, winreg.KEY_READ)
		try: vst_is_v2 = winreg.QueryValueEx(registry_key, 'isVst')[0]
		except WindowsError: vst_is_v2 = 0
		try: vst_is_v3 = winreg.QueryValueEx(registry_key, 'isVst3')[0]
		except WindowsError: vst_is_v3 = 0
		if vst_is_v2 == 1 or vst_is_v3 == 1:
			vst_name = winreg.QueryValueEx(registry_key, 'FullName')[0]
			vst_path = winreg.QueryValueEx(registry_key, 'FullPath')[0]
			vst_uniqueId = winreg.QueryValueEx(registry_key, 'uniqueId')[0]
			vst_Vendor = winreg.QueryValueEx(registry_key, 'Vendor')[0]
			vst_is64 = winreg.QueryValueEx(registry_key, 'isX64')[0]
			vst_isSynth = winreg.QueryValueEx(registry_key, 'isSynth')[0]
			if vst_is_v2 == 1:
				db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (vst_uniqueId,))
				db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (vst_name, vst_uniqueId,))
				if vst_is64 == 1: db_plugins.execute("UPDATE vst2 SET path_64bit = ? WHERE id = ?", (vst_path, vst_uniqueId,))
				else: db_plugins.execute("UPDATE vst2 SET path_32bit = ? WHERE id = ?", (vst_path, vst_uniqueId,))
				if vst_isSynth == 1: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", ('synth', vst_uniqueId,))
				else: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", ('effect', vst_uniqueId,))
				if vst_Vendor != None: db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (vst_Vendor, vst_uniqueId,))

			if vst_is_v3 == 1:
				vst_clsidPlug = uuid.UUID(winreg.QueryValueEx(registry_key, 'clsidPlug')[0]).hex.upper()
				vst_Subcategories = winreg.QueryValueEx(registry_key, 'Subcategories')[0]
				db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (vst_clsidPlug,))
				db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (vst_name, vst_clsidPlug,))
				if vst_is64 == 1: db_plugins.execute("UPDATE vst3 SET path_64bit = ? WHERE id = ?", (vst_path, vst_clsidPlug,))
				else: db_plugins.execute("UPDATE vst3 SET path_32bit = ? WHERE id = ?", (vst_path, vst_clsidPlug,))
				if vst_Subcategories != None: db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (vst_Subcategories, vst_clsidPlug,))
				if vst_Vendor != None: db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (vst_Vendor, vst_uniqueId,))


#  ------------------------------------- Output -------------------------------------

db_plugins.commit()
db_plugins.close()

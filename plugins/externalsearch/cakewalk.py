# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import winreg

import plugins
import os
from os.path import exists
import xml.etree.ElementTree as ET
from objects import globalstore
import uuid

w_regkey_cakewalk = 'SOFTWARE\\Cakewalk Music Software\\Cakewalk\\Cakewalk VST X64\\Inventory'

def reg_get(name, regpath):
	try:
		registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regpath, 0, winreg.KEY_READ)
		value, regtype = winreg.QueryValueEx(registry_key, name)
		winreg.CloseKey(registry_key)
		return value
	except WindowsError:
		return None

def reg_list(winregpath):
	pathlist = []
	try: 
		winregobj = winreg.OpenKey(winreg.HKEY_CURRENT_USER, winregpath)
		i = 0
		while True:
			try:
				keypath = winreg.EnumKey(winregobj, i)
				pathlist.append(w_regkey_cakewalk + '\\' + keypath)
				i += 1
			except WindowsError: break
	except: 
		pass
	return pathlist

def reg_checkexist(winregpath):
	try:
		winregobj_cakewalk = winreg.OpenKey(winreg.HKEY_CURRENT_USER, winregpath)
		return True
	except: return False

class plugsearch(plugins.base):
	def __init__(self): pass
	def get_shortname(self): return 'cakewalk'
	def get_name(self): return 'Cakewalk'
	def is_dawvert_plugin(self): return 'externalsearch'
	def get_prop(self, in_dict): in_dict['supported_os'] = ['win']
	def import_plugins(self):

		vst2count = 0
		vst3count = 0

		vstlist = reg_list(w_regkey_cakewalk)
		if reg_checkexist(w_regkey_cakewalk):
			for vstplugin in vstlist:
				registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, vstplugin, 0, winreg.KEY_READ)
				try: vst_is_v2 = winreg.QueryValueEx(registry_key, 'isVst')[0]
				except WindowsError: vst_is_v2 = 0
				try: vst_is_v3 = winreg.QueryValueEx(registry_key, 'isVst3')[0]
				except WindowsError: vst_is_v3 = 0
				try: vst_path = winreg.QueryValueEx(registry_key, 'FullPath')[0]
				except WindowsError: vst_path = ''
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
						with globalstore.extplug.add('vst2', 'win') as pluginfo_obj:
							pluginfo_obj.id = vst_uniqueId
							pluginfo_obj.name = vst_name
							if vst_is64 == 1: pluginfo_obj.path_64bit = vst_path
							else: pluginfo_obj.path_32bit = vst_path
							pluginfo_obj.type = 'synth' if vst_isSynth else 'fx'
							if vst_Vendor != None: pluginfo_obj.creator = vst_Vendor
							pluginfo_obj.audio_num_inputs = vst_numInputs
							pluginfo_obj.audio_num_outputs = vst_numOutputs
							pluginfo_obj.num_params = vst_numParams
						vst2count += 1

					if vst_is_v3 == 1:
						vst_clsidPlug = uuid.UUID(winreg.QueryValueEx(registry_key, 'clsidPlug')[0]).hex.upper()
						vst_Subcategories = winreg.QueryValueEx(registry_key, 'Subcategories')[0]
						with globalstore.extplug.add('vst3', 'win') as pluginfo_obj:
							pluginfo_obj.name = vst_name
							pluginfo_obj.id = vst_clsidPlug
							if vst_is64 == 1: pluginfo_obj.path_64bit = vst_path
							else: pluginfo_obj.path_32bit = vst_path
							if vst_Subcategories != None: pluginfo_obj.category = vst_Subcategories
							if vst_Vendor != None: pluginfo_obj.creator = vst_Vendor
							pluginfo_obj.audio_num_inputs = vst_numInputs
							pluginfo_obj.audio_num_outputs = vst_numOutputs
							pluginfo_obj.num_params = vst_numParams
						vst3count += 1
			print('[cakewalk] VST2: '+str(vst2count)+', VST3: '+str(vst3count))
			return True
		else: return False

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import winreg

import plugins
import os
from os.path import exists
import xml.etree.ElementTree as ET
from objects import globalstore
import base64
import struct
import uuid

w_regkey_soundbridge64 = 'SOFTWARE\\SoundBridge\\SoundBridge\\PluginCache.x64'

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
				pathlist.append(w_regkey_soundbridge64 + '\\' + keypath)
				i += 1
			except WindowsError: 
				break
	except: 
		pass
	return pathlist

def reg_checkexist(winregpath):
	try:
		winreg.OpenKey(winreg.HKEY_CURRENT_USER, winregpath)
		return True
	except: return False

def decode_chunk(statedata):
	if statedata:
		statedata = statedata.replace('.', '/')
		return base64.b64decode(statedata)
	return b''

def parse_entry(PluginData):
	outdata = {}
	outtxt = PluginData.decode(encoding='utf-16')
	if outtxt.startswith('@String('):
		xroot = ET.fromstring(outtxt[8:-2])
		for x in xroot:
			if x.tag == 'factory':
				uid = decode_chunk(x.get('uid'))
				fid = x.get('id')
				if uid: outdata['uid'] = uid
				if fid: outdata['id'] = fid
				outdata['shellId'] = x.get('shellId')
				outdata['name'] = x.get('name')
				outdata['vendor'] = x.get('vendor')
				outdata['category'] = x.get('category')
	return outdata

class plugsearch(plugins.base):
	def __init__(self): pass
	def get_shortname(self): return 'soundbridge'
	def get_name(self): return 'Soundbridge'
	def is_dawvert_plugin(self): return 'externalsearch'
	def get_prop(self, in_dict): in_dict['supported_os'] = ['win']
	def import_plugins(self):

		vst2count = 0
		vst3count = 0

		vstlist = reg_list(w_regkey_soundbridge64)

		if reg_checkexist(w_regkey_soundbridge64):
			for vstplugin in vstlist:
				registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, vstplugin, 0, winreg.KEY_READ)
				try: PluginData = winreg.QueryValueEx(registry_key, 'PluginData')[0]
				except WindowsError: PluginData = b''
				try: PluginType = winreg.QueryValueEx(registry_key, 'PluginType')[0]
				except WindowsError: PluginType = ''
				try: vst_path = winreg.QueryValueEx(registry_key, 'PluginFilePath')[0]
				except WindowsError: vst_path = ''

				if PluginData:
					if True:
						outdata = parse_entry(PluginData)
						shellid = outdata['shellid'] if 'shellid' in outdata else 0

						if PluginType == 'VST' and shellid == 0:
							with globalstore.extplug.add('vst2', globalstore.os_platform) as pluginfo_obj:
								if 'category' in outdata: pluginfo_obj.type = 'synth' if outdata['category'] == 'Instrument' else 'fx'
								if 'id' in outdata: pluginfo_obj.id = int(outdata['id'])
								if 'vendor' in outdata: pluginfo_obj.creator = outdata['vendor']
								if 'name' in outdata: pluginfo_obj.name = outdata['name']
								pluginfo_obj.path_64bit = vst_path
							vst2count += 1

						if PluginType == 'VST3':
							vuuid = outdata['uid']
							dev_uuid = uuid.UUID(int=int.from_bytes(vuuid[::-1], 'little')).bytes_le
							with globalstore.extplug.add('vst3', globalstore.os_platform) as pluginfo_obj:
								if 'category' in outdata: pluginfo_obj.type = outdata['category']
								if 'id' in outdata: pluginfo_obj.id = dev_uuid.hex().upper
								if 'vendor' in outdata: pluginfo_obj.creator = outdata['vendor']
								if 'name' in outdata: pluginfo_obj.name = outdata['name']
								pluginfo_obj.path_64bit = vst_path
							vst3count += 1




			print('[soundbridge] VST2: '+str(vst2count)+', VST3: '+str(vst3count))

			return True
		else: return False


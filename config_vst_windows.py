import winreg
import configparser
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import exists

config = configparser.ConfigParser()

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

l_path_aurdor = homepath+'\\AppData\\Local\\Ardour6\\cache\\vst'
l_path_waveform = homepath+'\\AppData\\Roaming\\Tracktion\\Waveform'
w_regkey_cakewalk = 'SOFTWARE\\Cakewalk Music Software\\Cakewalk\\Cakewalk VST X64\\Inventory'

vst2ini = configparser.ConfigParser()
vst3ini = configparser.ConfigParser()

if reg_checkexist(w_regkey_cakewalk) == True: dawlist.append('cakewalk')
if os.path.exists(l_path_aurdor) == True: dawlist.append('ardour')
if os.path.exists(l_path_waveform) == True: dawlist.append('waveform')


if len(dawlist) >= 1:
	print('[dawvert-vst] Plugin List from DAWs Found:', end=' ')
	for daw in dawlist: print(daw, end=' ')
	print()
	selecteddaw=input("[dawvert-vst] Select one to import: ")
	if selecteddaw not in dawlist:
		print('[dawvert-vst] exit', end=' ')
		exit()
elif len(dawlist) == 0:
	print('[dawvert-vst] No DAWs Found. exit', end=' ')
	exit()

#  ------------------------------------- CakeWalk -------------------------------------
if selecteddaw == 'cakewalk':
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
				if vst2ini.has_section(vst_name) == False:
					vst2ini.add_section(vst_name)
				if vst_is64 == 1: vst2ini.set(vst_name, 'path_amd64', vst_path)
				else: vst2ini.set(vst_name, 'path_i386', vst_path)
				if vst_isSynth == 1: vst2ini.set(vst_name, 'type', 'synth')
				else: vst2ini.set(vst_name, 'type', 'effect')
				if vst_uniqueId != None: vst2ini.set(vst_name, 'fourid', str(vst_uniqueId))
				if vst_Vendor != None: vst2ini.set(vst_name, 'creator', str(vst_Vendor))
			if vst_is_v3 == 1:
				if vst3ini.has_section(vst_name) == False:
					vst3ini.add_section(vst_name)
				if vst_is64 == 1: vst3ini.set(vst_name, 'path_amd64', vst_path)
				else: vst3ini.set(vst_name, 'path_i386', vst_path)
				if vst_isSynth == 1: vst3ini.set(vst_name, 'type', 'synth')
				else: vst3ini.set(vst_name, 'type', 'effect')

#  ------------------------------------- Ardour -------------------------------------
if selecteddaw == 'ardour':
	vstcachelist = os.listdir(l_path_aurdor)
	for vstcache in vstcachelist:
		vstxmlfile = vstcache
		vstxmlpath = l_path_aurdor+'\\'+vstxmlfile
		vstxmlext = Path(vstxmlfile).suffix
		vstxmldata = ET.parse(vstxmlpath)
		vstxmlroot = vstxmldata.getroot()

		if vstxmlext == '.v2i':
			vst_path = vstxmlroot.get('binary')
			VST2Info = vstxmlroot.findall('VST2Info')[0]
			vst_name = VST2Info.get('name')
			vst_fourid = VST2Info.get('id')
			vst_creator = VST2Info.get('creator')
			vst_arch = vstxmlroot.get('arch')
			vst_category = VST2Info.get('category')
			if vst_arch == 'x86_64':
				if vst2ini.has_section(vst_name) == False: vst2ini.add_section(vst_name)
				vst2ini.set(vst_name, 'path_amd64', vst_path)
				vst2ini.set(vst_name, 'fourid', vst_fourid)
				vst2ini.set(vst_name, 'creator', vst_creator)
				if vst_category == 'Instrument': vst2ini.set(vst_name, 'type', 'synth')
				if vst_category == 'Effect': vst2ini.set(vst_name, 'type', 'effect')
		if vstxmlext == '.v3i':
			vst_path = vstxmlroot.get('bundle')
			VST3Info = vstxmlroot.findall('VST3Info')[0]
			vst_name = VST3Info.get('name')
			if vst3ini.has_section(vst_name) == False: vst3ini.add_section(vst_name)
			vst3ini.set(vst_name, 'path', vst_path)

#  ------------------------------------- Waveform -------------------------------------
if selecteddaw == 'waveform':
	if exists(l_path_waveform+'\\knownPluginList64.settings'):
		vstxmldata = ET.parse(l_path_waveform+'\\knownPluginList64.settings')
		vstxmlroot = vstxmldata.getroot()
		vst2infos = vstxmlroot.findall('PLUGIN')
		for vst2info in vst2infos:
			vst_name = vst2info.get('descriptiveName')
			vst_inst = vst2info.get('isInstrument')
			
			if vst_name == None: vst_name = vst2info.get('name')

			if vst2ini.has_section(vst_name) == False: vst2ini.add_section(vst_name)
			vst2ini.set(vst_name, 'path_amd64', vst2info.get('file'))
			vst2ini.set(vst_name, 'internal_name', vst2info.get('name'))
			vst2ini.set(vst_name, 'version', vst2info.get('version'))
			vst2ini.set(vst_name, 'creator', vst2info.get('manufacturer'))
			vst2ini.set(vst_name, 'fourid', str(int(vst2info.get('uniqueId'), 16)))
			vst2ini.set(vst_name, 'num_inputs', vst2info.get('numInputs'))
			vst2ini.set(vst_name, 'num_outputs', vst2info.get('numOutputs'))
			if vst_inst == '1': vst2ini.set(vst_name, 'type', 'synth')
			if vst_inst == '0': vst2ini.set(vst_name, 'type', 'effect')
			
#  ------------------------------------- Output -------------------------------------

currentdir = os.getcwd() + '/__config/'
os.makedirs(currentdir, exist_ok=True)

with open(currentdir+'plugins_vst2_win.ini', 'w') as configfile: vst2ini.write(configfile)
with open(currentdir+'plugins_vst3_win.ini', 'w') as configfile: vst3ini.write(configfile)

print('[dawvert-vst] # of VST2 Plugins:', len(vst2ini))
print('[dawvert-vst] # of VST3 Plugins:', len(vst3ini))

import winreg
import configparser
import os
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

w_regkey_cakewalk = 'SOFTWARE\\Cakewalk Music Software\\Cakewalk\\Cakewalk VST X64\\Inventory'

vst2ini = configparser.ConfigParser()
vst3ini = configparser.ConfigParser()
if reg_checkexist(w_regkey_cakewalk) == True: dawlist.append('cakewalk')
#if os.path.exists(os.path.expanduser('~\Documents\Image-Line\FL Studio\Presets\Plugin database\Installed')) == True: dawlist.append('flstudio')

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
			vst_is64 = winreg.QueryValueEx(registry_key, 'isX64')[0]
			vst_isSynth = winreg.QueryValueEx(registry_key, 'isSynth')[0]
			if vst_is_v2 == 1:
				if vst2ini.has_section(vst_name) == False:
					vst2ini.add_section(vst_name)
				if vst_is64 == 1: vst2ini.set(vst_name, 'path_amd64', vst_path)
				else: vst2ini.set(vst_name, 'path_i386', vst_path)
				if vst_isSynth == 1: vst2ini.set(vst_name, 'type', 'synth')
				else: vst2ini.set(vst_name, 'type', 'effect')
			if vst_is_v3 == 1:
				if vst3ini.has_section(vst_name) == False:
					vst3ini.add_section(vst_name)
				if vst_is64 == 1: vst3ini.set(vst_name, 'path_amd64', vst_path)
				else: vst3ini.set(vst_name, 'path_i386', vst_path)
				if vst_isSynth == 1: vst3ini.set(vst_name, 'type', 'synth')
				else: vst3ini.set(vst_name, 'type', 'effect')
	print('[dawvert-vst] # of VST2 Plugins:', len(vst2ini))
	print('[dawvert-vst] # of VST3 Plugins:', len(vst3ini))

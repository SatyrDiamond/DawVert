
from os.path import exists
import configparser
import base64

global vst2paths
global vst3paths

global vst2path_loaded
global vst3path_loaded

vst2path_loaded = False
vst3path_loaded = False

# -------------------- VST List --------------------
def vst2path_loaded(): return vst2path_loaded
def vst3path_loaded(): return vst3path_loaded

def ifexists_vst2(name):
	if name in vst2paths: return True
	else: False

def find_vst2path(name, instdata):
	path_found = 0
	vst_path = None
	if 'plugindata' in instdata and 'plugin' in instdata:
		if vst2path_loaded == True:
			if name in vst2paths:
				if 'path64' in vst2paths[name]: 
					vst_path = vst2paths[name]['path64']
					print('[plug-vst2] ' + instdata['plugin'] +' > ' + name + ' (VST2 64-bit)')
					path_found = 1
				elif 'path32' in vst2paths[name]: 
					vst_path = vst2paths[name]['path32']
					print('[plug-vst2] ' + instdata['plugin'] +' > ' + name + ' (VST2 32-bit)')
					path_found = 1
				else:
					print('[plug-vst2] Unchanged,', 'Plugin path of ' + name + ' not Found')
			else: 
				instdata['plugindata']['plugin']['path'] = ''
				print('[plug-vst2] Unchanged,', 'Plugin ' + name + ' not Found')
		else: 
			print('[plug-vst2] Unchanged,', "VST2 list not found")
	else: 
		print('[plug-vst2] Unchanged,', "No Plugin and PluginData defined")
	return vst_path
def replace_data(instdata, name, data):
	vst_path = find_vst2path(name, instdata)
	if vst_path != None:
		instdata['plugin'] = 'vst2'
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['datatype'] = 'raw'
		instdata['plugindata']['data'] = base64.b64encode(data).decode('ascii')
def replace_params(instdata, name, numparams, params):
	vst_path = find_vst2path(name, instdata)
	if vst_path != None:
		instdata['plugin'] = 'vst2'
		instdata['plugindata'] = {}
		instdata['plugindata']['plugin'] = {}
		instdata['plugindata']['plugin']['name'] = name
		instdata['plugindata']['plugin']['path'] = vst_path
		instdata['plugindata']['datatype'] = 'param'
		instdata['plugindata']['numparams'] = numparams
		instdata['plugindata']['params'] = params
def listinit(osplatform):
	global vst2paths
	global vst3paths
	global vst2path_loaded
	global vst3path_loaded
	if osplatform == 'windows':
		if exists('vst2_win.ini'):
			vst2paths = configparser.ConfigParser()
			vst2paths.read('vst2_win.ini')
			vst2path_loaded = True
			print('[plug-vst2] # of VST2 Plugins:', len(vst2paths))
		if exists('vst3_win.ini'):
			vst3paths = configparser.ConfigParser()
			vst3paths.read('vst3_win.ini')
			vst2path_loaded = True
			print('[plug-vst ] # of VST3 Plugins:', len(vst3paths))

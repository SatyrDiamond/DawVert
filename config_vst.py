import configparser
import os
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import exists

dawlist = []

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
else: platformtxt = 'lin'

vst2ini_path = 'plugins_vst2_'+platformtxt+'.ini'
vst3ini_path = 'plugins_vst3_'+platformtxt+'.ini'

homepath = os.path.expanduser("~")

if platformtxt == 'win':
	l_path_aurdor = os.path.join(homepath, "AppData", "Local", "Ardour6", "cache", "vst")
	l_path_waveform = os.path.join(homepath, "AppData", "Roaming", "Tracktion", "Waveform")
if platformtxt == 'lin':
	l_path_aurdor = os.path.join(homepath, ".cache", "ardour6", "vst")

vst2ini = configparser.ConfigParser()
vst3ini = configparser.ConfigParser()

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

def xml_add_part(xmlfile, inifile, vst_name, ini_var_name, xml_var_name):
	var_data = xmlfile.get(xml_var_name)
	if var_data != None: inifile.set(vst_name, ini_var_name, var_data)

#  ------------------------------------- Ardour -------------------------------------
if selecteddaw == 'ardour':
	vstcachelist = os.listdir(l_path_aurdor)
	for vstcache in vstcachelist:
		vstxmlfile = vstcache
		vstxmlpath = os.path.join(l_path_aurdor, vstxmlfile)
		vstxmlext = Path(vstxmlfile).suffix
		vstxmldata = ET.parse(vstxmlpath)
		vstxmlroot = vstxmldata.getroot()

		if vstxmlext == '.v2i':
			VST2Info = vstxmlroot.findall('VST2Info')[0]
			vst_name = VST2Info.get('name')
			vst_arch = vstxmlroot.get('arch')
			vst_category = VST2Info.get('category')
			if vst_arch == 'x86_64':
				if vst2ini.has_section(vst_name) == False: vst2ini.add_section(vst_name)
				xml_add_part(VST2Info, vst2ini, vst_name, 'fourid', 'id')
				xml_add_part(VST2Info, vst2ini, vst_name, 'creator', 'creator')
				xml_add_part(vstxmlroot, vst2ini, vst_name, 'path_amd64', 'binary')
				xml_add_part(VST2Info, vst2ini, vst_name, 'version', 'version')
				xml_add_part(VST2Info, vst2ini, vst_name, 'audio_num_inputs', 'n_inputs')
				xml_add_part(VST2Info, vst2ini, vst_name, 'audio_num_outputs', 'n_outputs')
				xml_add_part(VST2Info, vst2ini, vst_name, 'midi_num_inputs', 'n_midi_inputs')
				xml_add_part(VST2Info, vst2ini, vst_name, 'midi_num_outputs', 'n_midi_outputs')
				if vst_category == 'Instrument': vst2ini.set(vst_name, 'type', 'synth')
				if vst_category == 'Effect': vst2ini.set(vst_name, 'type', 'effect')

		if vstxmlext == '.v3i':
			VST3Info = vstxmlroot.findall('VST3Info')[0]
			vst_name = VST3Info.get('name')
			if vst3ini.has_section(vst_name) == False: vst3ini.add_section(vst_name)
			xml_add_part(vstxmlroot, vst3ini, vst_name, 'path', 'bundle')
			xml_add_part(VST3Info, vst3ini, vst_name, 'id', 'uid')
			xml_add_part(VST3Info, vst3ini, vst_name, 'creator', 'vendor')
			xml_add_part(VST3Info, vst3ini, vst_name, 'category', 'category')
			xml_add_part(VST3Info, vst3ini, vst_name, 'version', 'version')
			xml_add_part(VST3Info, vst3ini, vst_name, 'sdk-version', 'sdk-version')
			xml_add_part(VST3Info, vst3ini, vst_name, 'url', 'url')
			xml_add_part(VST3Info, vst3ini, vst_name, 'email', 'email')
			xml_add_part(VST3Info, vst3ini, vst_name, 'audio_num_inputs', 'n_inputs')
			xml_add_part(VST3Info, vst3ini, vst_name, 'audio_num_outputs', 'n_outputs')
			xml_add_part(VST3Info, vst3ini, vst_name, 'midi_num_inputs', 'n_midi_inputs')
			xml_add_part(VST3Info, vst3ini, vst_name, 'midi_num_outputs', 'n_midi_outputs')

#  ------------------------------------- Waveform -------------------------------------
if selecteddaw == 'waveform':
	vst2filename = os.path.join(l_path_waveform, 'knownPluginList64.settings')
	if exists(vst2filename):
		vstxmldata = ET.parse(vst2filename)
		vstxmlroot = vstxmldata.getroot()
		vst2infos = vstxmlroot.findall('PLUGIN')
		for vst2info in vst2infos:
			vst_name = vst2info.get('descriptiveName')
			vst_inst = vst2info.get('isInstrument')
			if vst_name == None: vst_name = vst2info.get('name')
			if vst2ini.has_section(vst_name) == False: vst2ini.add_section(vst_name)
			xml_add_part(vst2info, vst2ini, vst_name, 'path_amd64', 'file')
			xml_add_part(vst2info, vst2ini, vst_name, 'internal_name', 'name')
			xml_add_part(vst2info, vst2ini, vst_name, 'version', 'version')
			xml_add_part(vst2info, vst2ini, vst_name, 'creator', 'manufacturer')
			vst2ini.set(vst_name, 'fourid', str(int(vst2info.get('uniqueId'), 16)))
			xml_add_part(vst2info, vst2ini, vst_name, 'audio_num_inputs', 'numInputs')
			xml_add_part(vst2info, vst2ini, vst_name, 'audio_num_outputs', 'numOutputs')
			if vst_inst == '1': vst2ini.set(vst_name, 'type', 'synth')
			if vst_inst == '0': vst2ini.set(vst_name, 'type', 'effect')
			
#  ------------------------------------- Output -------------------------------------

currentdir = os.getcwd() + '/__config/'
os.makedirs(currentdir, exist_ok=True)

with open(currentdir+vst2ini_path, 'w') as configfile: vst2ini.write(configfile)
with open(currentdir+vst3ini_path, 'w') as configfile: vst3ini.write(configfile)

print('[dawvert-vst] # of VST2 Plugins:', len(vst2ini))
print('[dawvert-vst] # of VST3 Plugins:', len(vst3ini))

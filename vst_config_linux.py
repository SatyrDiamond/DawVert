import configparser
import os
import xml.etree.ElementTree as ET
from os.path import expanduser
from pathlib import Path

config = configparser.ConfigParser()
homepath = expanduser("~")

dawlist = []

l_path_aurdor = homepath+'/.cache/ardour6/vst'

vst2ini = configparser.ConfigParser()
vst3ini = configparser.ConfigParser()
# CakeWalk
if os.path.exists(l_path_aurdor) == True: dawlist.append('ardour')

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

#if vst3ini.has_section(vst_name) == False:
#vst2ini.add_section(vst_name)

if selecteddaw == 'ardour':
	vstcachelist = os.listdir(l_path_aurdor)
	for vstcache in vstcachelist:
		vstxmlfile = vstcache
		vstxmlpath = l_path_aurdor+'/'+vstxmlfile
		vstxmlext = Path(vstxmlfile).suffix
		#print(vstxmlfile, vstxmlext)
		vstxmldata = ET.parse(vstxmlpath)
		vstxmlroot = vstxmldata.getroot()

		if vstxmlext == '.v2i':
			vst_path = vstxmlroot.get('binary')
			VST2Info = vstxmlroot.findall('VST2Info')[0]
			vst_name = VST2Info.get('name')
			vst_arch = vstxmlroot.get('arch')
			vst_category = VST2Info.get('category')
			if vst_arch == 'x86_64':
				if vst2ini.has_section(vst_name) == False: vst2ini.add_section(vst_name)
				vst2ini.set(vst_name, 'path64', vst_path)
				if vst_category == 'Instrument': vst2ini.set(vst_name, 'type', 'synth')
				if vst_category == 'Effect': vst2ini.set(vst_name, 'type', 'effect')
		if vstxmlext == '.v3i':
			vst_path = vstxmlroot.get('bundle')
			VST3Info = vstxmlroot.findall('VST3Info')[0]
			vst_name = VST3Info.get('name')
			if vst3ini.has_section(vst_name) == False: vst3ini.add_section(vst_name)
			vst3ini.set(vst_name, 'path', vst_path)

	print('[dawvert-vst] # of VST2 Plugins:', len(vst2ini))
	print('[dawvert-vst] # of VST3 Plugins:', len(vst3ini))

with open('vst2_lin.ini', 'w') as configfile: vst2ini.write(configfile)
with open('vst3_lin.ini', 'w') as configfile: vst3ini.write(configfile)

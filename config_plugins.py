import os
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import exists
import sqlite3

dawlist = []

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
else: platformtxt = 'lin'

os.makedirs(os.getcwd() + '/__config/', exist_ok=True)
db_plugins = sqlite3.connect('./__config/plugins_external.db')

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
      path_32bit_win text,
      path_64bit_win text,
      path_32bit_unix text,
      path_64bit_unix text,
		UNIQUE(id)
   )''')

db_plugins.execute('''
   CREATE TABLE IF NOT EXISTS ladspa(
		name text,
		creator text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
      path_win text,
      path_unix text,
      UNIQUE(name)
   )''')

homepath = os.path.expanduser("~")

if platformtxt == 'win':
	l_path_aurdor = os.path.join(homepath, "AppData", "Local", "Ardour6", "cache", "vst")
	l_path_waveform = os.path.join(homepath, "AppData", "Roaming", "Tracktion", "Waveform")
if platformtxt == 'lin':
	l_path_aurdor = os.path.join(homepath, ".cache", "ardour6", "vst")
	l_path_waveform = os.path.join(homepath, ".config", "Tracktion", "Waveform")

if os.path.exists(l_path_aurdor) == True: dawlist.append('ardour')
if os.path.exists(l_path_waveform) == True: dawlist.append('waveform')

elif len(dawlist) == 0:
	print('[dawvert-vst] No DAWs Found. exit', end=' ')
	exit()

#  ------------------------------------- Ardour -------------------------------------
if 'ardour' in dawlist:
	print('[dawvert-vst] Importing VST List from: Ardour')
	vstcachelist = os.listdir(l_path_aurdor)
	for vstcache in vstcachelist:
		vstxmlfile = vstcache
		vstxmlpath = os.path.join(l_path_aurdor, vstxmlfile)
		vstxmlext = Path(vstxmlfile).suffix
		vstxmldata = ET.parse(vstxmlpath)
		vstxmlroot = vstxmldata.getroot()

		if vstxmlext == '.v2i':
			pluginfo = vstxmlroot.findall('VST2Info')[0]
			vst_arch = vstxmlroot.get('arch')
			vst_category = pluginfo.get('category')
			if vst_arch == 'x86_64' and os.path.exists(vstxmlroot.get('binary')):
				vst2data_fourid = int(pluginfo.get('id'))
				if vst_category == 'Instrument': vst2data_type = 'synth'
				if vst_category == 'Effect': vst2data_type = 'effect'
				db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (pluginfo.get('name'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (pluginfo.get('creator'), vst2data_fourid,))
				if platformtxt == 'win':
					db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (vstxmlroot.get('binary'), vst2data_fourid,))
				if platformtxt == 'lin':
					db_plugins.execute("UPDATE vst2 SET path_64bit_unix = ? WHERE id = ?", (vstxmlroot.get('binary'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET version = ? WHERE id = ?", (pluginfo.get('version'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (pluginfo.get('n_inputs'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (pluginfo.get('n_outputs'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET midi_num_inputs = ? WHERE id = ?", (pluginfo.get('n_midi_inputs'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET midi_num_outputs = ? WHERE id = ?", (pluginfo.get('n_midi_outputs'), vst2data_fourid,))
				db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", (vst2data_type, vst2data_fourid,))

		if vstxmlext == '.v3i':
			VST3Info = vstxmlroot.findall('VST3Info')[0]
			vst3data_id = VST3Info.get('uid')
			if os.path.exists(vstxmlroot.get('bundle')):
				db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (VST3Info.get('name'), vst3data_id,))
				if platformtxt == 'win':
					db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (vstxmlroot.get('bundle'), vst3data_id,))
				if platformtxt == 'lin':
					db_plugins.execute("UPDATE vst3 SET path_64bit_unix = ? WHERE id = ?", (vstxmlroot.get('bundle'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (VST3Info.get('vendor'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (VST3Info.get('category'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET version = ? WHERE id = ?", (VST3Info.get('version'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET sdk_version = ? WHERE id = ?", (VST3Info.get('sdk-version'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET url = ? WHERE id = ?", (VST3Info.get('url'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET email = ? WHERE id = ?", (VST3Info.get('email'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET audio_num_inputs = ? WHERE id = ?", (VST3Info.get('n_inputs'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET audio_num_outputs = ? WHERE id = ?", (VST3Info.get('n_outputs'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET midi_num_inputs = ? WHERE id = ?", (VST3Info.get('n_midi_inputs'), vst3data_id,))
				db_plugins.execute("UPDATE vst3 SET midi_num_outputs = ? WHERE id = ?", (VST3Info.get('n_midi_outputs'), vst3data_id,))

#  ------------------------------------- Waveform -------------------------------------
if 'waveform' in dawlist:
	print('[dawvert-vst] Importing VST List from: Waveform')
	plugfilename = os.path.join(l_path_waveform, 'knownPluginList64.settings')
	if exists(plugfilename):
		vstxmldata = ET.parse(plugfilename)
		vstxmlroot = vstxmldata.getroot()
		pluginfos = vstxmlroot.findall('PLUGIN')
		for pluginfo in pluginfos:
			vst_file = pluginfo.get('file')
			vst_format = pluginfo.get('format')
			#print(vst_format)
			if os.path.exists(vst_file):
				if vst_format == 'VST':
					vst_name = pluginfo.get('descriptiveName')
					vst_inst = pluginfo.get('isInstrument')
					if vst_inst == '1': plugdata_type = 'synth'
					if vst_inst == '0': plugdata_type = 'effect'
					plugdata_fourid = int(pluginfo.get('uniqueId'), 16)
					db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (plugdata_fourid,))
					if vst_name != None: db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (vst_name, plugdata_fourid,))
					else: db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (pluginfo.get('name'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET internal_name = ? WHERE id = ?", (pluginfo.get('name'), plugdata_fourid,))
					if platformtxt == 'win':
						db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (pluginfo.get('file'), plugdata_fourid,))
					if platformtxt == 'lin':
						db_plugins.execute("UPDATE vst3 SET path_64bit_unix = ? WHERE id = ?", (pluginfo.get('file'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (pluginfo.get('manufacturer'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET version = ? WHERE id = ?", (pluginfo.get('version'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (pluginfo.get('numInputs'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (pluginfo.get('numOutputs'), plugdata_fourid,))
					db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", (plugdata_type, plugdata_fourid,))
				if vst_format == 'LADSPA':
					ladspa_name = pluginfo.get('name')
					db_plugins.execute("INSERT OR IGNORE INTO ladspa (name) VALUES (?)", (ladspa_name,))
					db_plugins.execute("UPDATE ladspa SET path_unix = ? WHERE name = ?", (pluginfo.get('file'), ladspa_name,))
					db_plugins.execute("UPDATE ladspa SET creator = ? WHERE name = ?", (pluginfo.get('manufacturer'), ladspa_name,))
					db_plugins.execute("UPDATE ladspa SET version = ? WHERE name = ?", (pluginfo.get('version'), ladspa_name,))
					db_plugins.execute("UPDATE ladspa SET audio_num_inputs = ? WHERE name = ?", (pluginfo.get('numInputs'), ladspa_name,))
					db_plugins.execute("UPDATE ladspa SET audio_num_outputs = ? WHERE name = ?", (pluginfo.get('numOutputs'), ladspa_name,))

#  ------------------------------------- Output -------------------------------------

db_plugins.commit()
db_plugins.close()

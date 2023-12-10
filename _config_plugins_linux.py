from os.path import exists
from pathlib import Path
import os
import platform
import sqlite3
import base64
import xml.etree.ElementTree as ET

def muse_getvalue(fallback, xmldata, name):
	outval = xmldata.findall(name)
	if outval == []: return fallback
	else: return outval[0].text

dawlist = []

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
else: platformtxt = 'lin'

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
	CREATE TABLE IF NOT EXISTS ladspa(
		name text,
		creator text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		num_params integer,
		path_win text,
		path_unix text,
		filename text,
		UNIQUE(name)
	)''')

db_plugins.execute('''
	CREATE TABLE IF NOT EXISTS dssi(
		name text,
		id text,
		creator text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		num_params integer,
		path_unix text,
		UNIQUE(id)
	)''')

homepath = os.path.expanduser("~")
 
l_path_muse = os.path.join(homepath,".cache", "MusE", "MusE", "scanner")

if os.path.exists(l_path_muse) == True: dawlist.append('muse')

elif len(dawlist) == 0:
	print('[dawvert-vst] No DAWs Found. exit', end=' ')
	exit()

#  ------------------------------------- Ardour -------------------------------------
if 'muse' in dawlist:
	print('[dawvert-vst] Importing Plugin List from: MusE')

	muse_g_path_vst = l_path_muse+'/linux_vst_plugins.scan'
	muse_g_path_ladspa = l_path_muse+'/ladspa_plugins.scan'
	muse_g_path_dssi = l_path_muse+'/dssi_plugins.scan'

	if os.path.exists(muse_g_path_vst):
		path_vst_linux = muse_g_path_vst
		vstxmldata = ET.parse(path_vst_linux)
		vstxmlroot = vstxmldata.getroot()
		for x_vst_plug_cache in vstxmlroot:
			muse_file = x_vst_plug_cache.get('file')
			if os.path.exists(muse_file):
				muse_uniqueID = muse_getvalue(None, x_vst_plug_cache, 'uniqueID')
				muse_name = muse_getvalue(None, x_vst_plug_cache, 'name')
				muse_maker = muse_getvalue(None, x_vst_plug_cache, 'maker')
				muse_inports = muse_getvalue(0, x_vst_plug_cache, 'inports')
				muse_outports = muse_getvalue(0, x_vst_plug_cache, 'outports')
				muse_ctlInports = muse_getvalue(0, x_vst_plug_cache, 'ctlInports')
				
				db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (muse_uniqueID,))
				if muse_name != None: db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (muse_name, muse_uniqueID,))
				if muse_maker != None: db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (muse_maker, muse_uniqueID,))
				if muse_inports != None: db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (muse_inports, muse_uniqueID,))
				if muse_outports != None: db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (muse_outports, muse_uniqueID,))
				if muse_ctlInports != None: db_plugins.execute("UPDATE vst2 SET num_params = ? WHERE id = ?", (muse_ctlInports, muse_uniqueID,))
				db_plugins.execute("UPDATE vst2 SET path_64bit_unix = ? WHERE id = ?", (muse_file, muse_uniqueID,))

	if os.path.exists(muse_g_path_ladspa):
		path_ladspa_linux = muse_g_path_ladspa
		ladspaxmldata = ET.parse(path_ladspa_linux)
		ladspaxmlroot = ladspaxmldata.getroot()
		for x_ladspa_plug_cache in ladspaxmlroot:
			muse_file = x_ladspa_plug_cache.get('file')
			if os.path.exists(muse_file):
				muse_name = muse_getvalue(None, x_ladspa_plug_cache, 'name')
				muse_maker = muse_getvalue(None, x_ladspa_plug_cache, 'maker')
				muse_inports = muse_getvalue(0, x_ladspa_plug_cache, 'inports')
				muse_outports = muse_getvalue(0, x_ladspa_plug_cache, 'outports')
				muse_ctlInports = muse_getvalue(0, x_ladspa_plug_cache, 'ctlInports')
				
				db_plugins.execute("INSERT OR IGNORE INTO ladspa (name) VALUES (?)", (muse_name,))
				if muse_maker != None: db_plugins.execute("UPDATE ladspa SET creator = ? WHERE name = ?", (muse_maker, muse_name,))
				if muse_inports != None: db_plugins.execute("UPDATE ladspa SET audio_num_inputs = ? WHERE name = ?", (muse_inports, muse_name,))
				if muse_outports != None: db_plugins.execute("UPDATE ladspa SET audio_num_outputs = ? WHERE name = ?", (muse_outports, muse_name,))
				if muse_ctlInports != None: db_plugins.execute("UPDATE ladspa SET num_params = ? WHERE name = ?", (muse_ctlInports, muse_name,))
				db_plugins.execute("UPDATE ladspa SET path_unix = ? WHERE name = ?", (muse_file, muse_name,))
				db_plugins.execute("UPDATE ladspa SET filename = ? WHERE name = ?", (os.path.basename(muse_file).split('.')[0], muse_name,))

	if os.path.exists(muse_g_path_dssi):
		path_dssi_linux = muse_g_path_dssi
		dssixmldata = ET.parse(path_dssi_linux)
		dssixmlroot = dssixmldata.getroot()
		for x_dssi_plug_cache in dssixmlroot:
			muse_file = x_dssi_plug_cache.get('file')
			if os.path.exists(muse_file):
				muse_uniqueID = muse_getvalue(None, x_dssi_plug_cache, 'uniqueID')
				muse_name = muse_getvalue(None, x_dssi_plug_cache, 'name')
				muse_maker = muse_getvalue(None, x_dssi_plug_cache, 'maker')
				muse_inports = muse_getvalue(0, x_dssi_plug_cache, 'inports')
				muse_outports = muse_getvalue(0, x_dssi_plug_cache, 'outports')
				muse_ctlInports = muse_getvalue(0, x_dssi_plug_cache, 'ctlInports')
				
				db_plugins.execute("INSERT OR IGNORE INTO dssi (id) VALUES (?)", (muse_uniqueID,))
				if muse_name != None: db_plugins.execute("UPDATE dssi SET name = ? WHERE id = ?", (muse_name, muse_uniqueID,))
				if muse_maker != None: db_plugins.execute("UPDATE dssi SET creator = ? WHERE id = ?", (muse_maker, muse_uniqueID,))
				if muse_inports != None: db_plugins.execute("UPDATE dssi SET audio_num_inputs = ? WHERE id = ?", (muse_inports, muse_uniqueID,))
				if muse_outports != None: db_plugins.execute("UPDATE dssi SET audio_num_outputs = ? WHERE id = ?", (muse_outports, muse_uniqueID,))
				if muse_ctlInports != None: db_plugins.execute("UPDATE dssi SET num_params = ? WHERE id = ?", (muse_ctlInports, muse_uniqueID,))
				db_plugins.execute("UPDATE dssi SET path_unix = ? WHERE id = ?", (muse_file, muse_uniqueID,))

db_plugins.commit()
db_plugins.close()

# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sqlite3
import platform
from objects import dv_dataset
import json


os.makedirs(os.getcwd() + '/__config/', exist_ok=True)
db_plugins = sqlite3.connect('./__config/plugins_external.db', check_same_thread=False)

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
else: platformtxt = 'lin'

extplug_dset_path = './__config/extplug.dset'
extplug_dataset = dv_dataset.dataset(extplug_dset_path)

extplug_dataset.category_add('vst2')
extplug_dataset.category_add('vst3')
extplug_dataset.category_add('clap')
extplug_dataset.category_add('ladspa')

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
		type text,
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
	CREATE TABLE IF NOT EXISTS clap(
		name text,
		id text,
		creator text,
		category text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		midi_num_inputs integer,
		midi_num_outputs integer,
		path_win text,
		path_unix text,
		UNIQUE(id)
	)''')

db_plugins.execute('''
	CREATE TABLE IF NOT EXISTS ladspa(
		name text,
		id text,
		inside_id text,
		creator text,
		version text,
		audio_num_inputs integer,
		audio_num_outputs integer,
		midi_num_inputs integer,
		midi_num_outputs integer,
		num_params text,
		num_params_out text,
		path_win text,
		path_unix text,
		UNIQUE(id)
	)''')

def write_db():
	db_plugins.commit()
	with open(extplug_dset_path, "w") as fileout: 
		json.dump(extplug_dataset.dataset, fileout, indent=4, sort_keys=True)

class pluginfo:
	def __init__(self):
		self.out_exists = False
		self.name = None
		self.id = None
		self.type = None
		self.category = None
		self.creator = None
		self.version = None
		self.sdk_version = None
		self.url = None
		self.email = None
		self.audio_num_inputs = None
		self.audio_num_outputs = None
		self.midi_num_inputs = None
		self.midi_num_outputs = None
		self.num_params = None
		self.path_32bit = None
		self.path_64bit = None
		self.path = None

	def find_locpath(self, cpu_arch_list):
		vst_cpuarch = None
		vst_path = None
		if self.path_32bit != None and self.path_64bit == None and 32 in cpu_arch_list: 
			vst_cpuarch, vst_path = 32, self.path_32bit
		if self.path_32bit == None and self.path_64bit != None and 64 in cpu_arch_list: 
			vst_cpuarch, vst_path = 64, self.path_64bit
		if self.path_32bit != None and self.path_64bit != None and 64 in cpu_arch_list: 
			vst_cpuarch, vst_path = 64, self.path_64bit
		return vst_cpuarch, vst_path

def vst2_add(pluginfo_obj, platformtxt):

	if pluginfo_obj.id:
		db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (pluginfo_obj.id,))
		if pluginfo_obj.name: db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
		if pluginfo_obj.creator: db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))

		if pluginfo_obj.path_32bit:
			if os.path.exists(pluginfo_obj.path_32bit):
				if platformtxt == 'win': db_plugins.execute("UPDATE vst2 SET path_32bit_win = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
				if platformtxt == 'lin': db_plugins.execute("UPDATE vst2 SET path_32bit_unix = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))

		if pluginfo_obj.path_64bit:
			if os.path.exists(pluginfo_obj.path_64bit):
				if platformtxt == 'win': db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
				if platformtxt == 'lin': db_plugins.execute("UPDATE vst2 SET path_64bit_unix = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))

		if pluginfo_obj.version: db_plugins.execute("UPDATE vst2 SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_inputs: db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_outputs: db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_inputs: db_plugins.execute("UPDATE vst2 SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_outputs: db_plugins.execute("UPDATE vst2 SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.num_params: db_plugins.execute("UPDATE vst2 SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
		if pluginfo_obj.type: db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", (pluginfo_obj.type, pluginfo_obj.id,))

		id_str = str(pluginfo_obj.id)
		extplug_dataset.object_add('vst2', id_str)
		extplug_dataset.object_visual_set('vst2', id_str, {'name': pluginfo_obj.name})


def vst2_check(bycat, in_val):
	if bycat == 'name':
		return bool(db_plugins.execute("SELECT count(*) FROM vst2 WHERE name = ?", (in_val,)).fetchone())
	elif bycat == 'id':
		return bool(db_plugins.execute("SELECT count(*) FROM vst2 WHERE id = ?", (in_val,)).fetchone()[0])

def vst2_get(bycat, in_val, in_platformtxt, cpu_arch_list):
	founddata = None

	if in_platformtxt == None: in_platformtxt = platformtxt

	if bycat == 'id':
		founddata = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE id = ?", (in_val,)).fetchone()

	if bycat == 'name':
		founddata = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE name = ?", (in_val,)).fetchone()

	if bycat == 'path':
		if in_platformtxt == 'win':
			in_val = in_val.replace('/', '\\')
			founddata_path32 = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_32bit_win = ?", (in_val,)).fetchone()
			founddata_path64 = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_64bit_win = ?", (in_val,)).fetchone()
			if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
			if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64
		else:
			in_val = in_val.replace('/', '\\')
			founddata_path32 = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_64bit_unix = ?", (in_val,)).fetchone()
			founddata_path64 = db_plugins.execute("SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2 WHERE path_32bit_unix = ?", (in_val,)).fetchone()
			if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
			if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64

	pluginfo_obj = pluginfo()
	if founddata: vst2_split_pluginfo(founddata, in_platformtxt, pluginfo_obj)
	return pluginfo_obj

def vst2_split_pluginfo(founddata, platformtxt, pluginfo_obj):
	p_name, p_id, p_type, p_creator, p_version, p_audio_num_inputs, p_audio_num_outputs, p_midi_num_inputs, p_midi_num_outputs, p_num_params, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix = founddata
	pluginfo_obj.out_exists = True
	pluginfo_obj.name = p_name
	pluginfo_obj.id = p_id
	pluginfo_obj.type = p_type
	pluginfo_obj.creator = p_creator
	pluginfo_obj.version = p_version
	pluginfo_obj.audio_num_inputs = p_audio_num_inputs
	pluginfo_obj.audio_num_outputs = p_audio_num_outputs
	pluginfo_obj.midi_num_inputs = p_midi_num_inputs
	pluginfo_obj.midi_num_outputs = p_midi_num_outputs
	pluginfo_obj.num_params = p_num_params
	if platformtxt == 'win': 
		pluginfo_obj.path_32bit = p_path_32bit_win
		pluginfo_obj.path_64bit = p_path_64bit_win
	if platformtxt == 'lin': 
		pluginfo_obj.path_32bit = p_path_32bit_unix
		pluginfo_obj.path_64bit = p_path_64bit_unix

def vst2_getall():
	vst2all = db_plugins.execute("SELECT * FROM vst2").fetchall()
	o = []
	for x in vst2all:
		pluginfo_obj = pluginfo()
		vst2_split_pluginfo(x, platformtxt, pluginfo_obj)
		o.append(pluginfo_obj)
	return o

def vst3_add(pluginfo_obj, platformtxt):

	if pluginfo_obj.id:
		db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (pluginfo_obj.id,))

		if not pluginfo_obj.type and pluginfo_obj.category:
			splitcat = pluginfo_obj.category.split('|')
			if splitcat[0] == 'Fx': pluginfo_obj.type = 'effect'
			if splitcat[0] == 'Instrument': pluginfo_obj.type = 'synth'

		if pluginfo_obj.name: db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
		if pluginfo_obj.creator: db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))

		if pluginfo_obj.path_32bit:
			if os.path.exists(pluginfo_obj.path_32bit):
				if platformtxt == 'win': db_plugins.execute("UPDATE vst3 SET path_32bit_win = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
				if platformtxt == 'lin': db_plugins.execute("UPDATE vst3 SET path_32bit_unix = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))

		if pluginfo_obj.path_64bit:
			if os.path.exists(pluginfo_obj.path_64bit):
				if platformtxt == 'win': db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
				if platformtxt == 'lin': db_plugins.execute("UPDATE vst3 SET path_64bit_unix = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))

		if pluginfo_obj.version: db_plugins.execute("UPDATE vst3 SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
		if pluginfo_obj.sdk_version: db_plugins.execute("UPDATE vst3 SET sdk_version = ? WHERE id = ?", (pluginfo_obj.sdk_version, pluginfo_obj.id,))
		if pluginfo_obj.url: db_plugins.execute("UPDATE vst3 SET url = ? WHERE id = ?", (pluginfo_obj.url, pluginfo_obj.id,))
		if pluginfo_obj.email: db_plugins.execute("UPDATE vst3 SET email = ? WHERE id = ?", (pluginfo_obj.email, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_inputs: db_plugins.execute("UPDATE vst3 SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_outputs: db_plugins.execute("UPDATE vst3 SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_inputs: db_plugins.execute("UPDATE vst3 SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_outputs: db_plugins.execute("UPDATE vst3 SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.num_params: db_plugins.execute("UPDATE vst3 SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
		if pluginfo_obj.type: db_plugins.execute("UPDATE vst3 SET type = ? WHERE id = ?", (pluginfo_obj.type, pluginfo_obj.id,))
		if pluginfo_obj.category: db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (pluginfo_obj.category, pluginfo_obj.id,))

def vst3_check(bycat, in_val):
	if bycat == 'name':
		return bool(db_plugins.execute("SELECT count(*) FROM vst3 WHERE name = ?", (in_val,)).fetchone())
	elif bycat == 'id':
		return bool(db_plugins.execute("SELECT count(*) FROM vst3 WHERE id = ?", (in_val,)).fetchone())

def vst3_get(bycat, in_val, in_platformtxt, cpu_arch_list):
	founddata = None

	if in_platformtxt == None: in_platformtxt = platformtxt

	if bycat == 'id':
		founddata = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE id = ?", (in_val,)).fetchone()

	if bycat == 'name':
		founddata = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE name = ?", (in_val,)).fetchone()

	if bycat == 'path':
		if in_platformtxt == 'win':
			in_val = in_val.replace('/', '\\')
			founddata_path32 = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE path_32bit_win = ?", (in_val,)).fetchone()
			founddata_path64 = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE path_64bit_win = ?", (in_val,)).fetchone()
			if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
			if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64
		else:
			in_val = in_val.replace('/', '\\')
			founddata_path32 = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE path_64bit_unix = ?", (in_val,)).fetchone()
			founddata_path64 = db_plugins.execute("SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3 WHERE path_32bit_unix = ?", (in_val,)).fetchone()
			if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
			if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64

	pluginfo_obj = pluginfo()
	if founddata: vst3_split_pluginfo(founddata, in_platformtxt, pluginfo_obj)
	return pluginfo_obj

def vst3_split_pluginfo(founddata, platformtxt, pluginfo_obj):
	p_name, p_id, p_type, p_creator, p_category, p_version, p_sdk_version, p_url, p_email, p_audio_num_inputs, p_audio_num_outputs, p_midi_num_inputs, p_midi_num_outputs, p_num_params, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix = founddata
	pluginfo_obj.out_exists = True
	pluginfo_obj.name = p_name
	pluginfo_obj.id = p_id
	pluginfo_obj.type = p_type
	pluginfo_obj.creator = p_creator
	pluginfo_obj.category = p_category
	pluginfo_obj.version = p_version
	pluginfo_obj.sdk_version = p_sdk_version
	pluginfo_obj.url = p_url
	pluginfo_obj.email = p_email
	pluginfo_obj.audio_num_inputs = p_audio_num_inputs
	pluginfo_obj.audio_num_outputs = p_audio_num_outputs
	pluginfo_obj.midi_num_inputs = p_midi_num_inputs
	pluginfo_obj.midi_num_outputs = p_midi_num_outputs
	pluginfo_obj.num_params = p_num_params
	if platformtxt == 'win': 
		pluginfo_obj.path_32bit = p_path_32bit_win
		pluginfo_obj.path_64bit = p_path_64bit_win
	if platformtxt == 'lin': 
		pluginfo_obj.path_32bit = p_path_32bit_unix
		pluginfo_obj.path_64bit = p_path_64bit_unix

def clap_add(pluginfo_obj, platformtxt):

	if pluginfo_obj.id:
		db_plugins.execute("INSERT OR IGNORE INTO clap (id) VALUES (?)", (pluginfo_obj.id,))
		if pluginfo_obj.name: db_plugins.execute("UPDATE clap SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
		if pluginfo_obj.creator: db_plugins.execute("UPDATE clap SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
		if pluginfo_obj.category: db_plugins.execute("UPDATE clap SET category = ? WHERE id = ?", (pluginfo_obj.category, pluginfo_obj.id,))
		if pluginfo_obj.version: db_plugins.execute("UPDATE clap SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_inputs: db_plugins.execute("UPDATE clap SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_outputs: db_plugins.execute("UPDATE clap SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_inputs: db_plugins.execute("UPDATE clap SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_outputs: db_plugins.execute("UPDATE clap SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))

		if pluginfo_obj.path:
			if os.path.exists(pluginfo_obj.path):
				if platformtxt == 'win': db_plugins.execute("UPDATE clap SET path_win = ? WHERE id = ?", (pluginfo_obj.path, pluginfo_obj.id,))
				if platformtxt == 'lin': db_plugins.execute("UPDATE clap SET path_unix = ? WHERE id = ?", (pluginfo_obj.path, pluginfo_obj.id,))

def ladspa_add(pluginfo_obj, platformtxt):

	if pluginfo_obj.id:
		db_plugins.execute("INSERT OR IGNORE INTO ladspa (id) VALUES (?)", (pluginfo_obj.id,))
		if pluginfo_obj.name: db_plugins.execute("UPDATE ladspa SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
		if pluginfo_obj.inside_id: db_plugins.execute("UPDATE ladspa SET inside_id = ? WHERE id = ?", (pluginfo_obj.inside_id, pluginfo_obj.id,))
		if pluginfo_obj.creator: db_plugins.execute("UPDATE ladspa SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
		if pluginfo_obj.version: db_plugins.execute("UPDATE ladspa SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_inputs: db_plugins.execute("UPDATE ladspa SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.audio_num_outputs: db_plugins.execute("UPDATE ladspa SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_inputs: db_plugins.execute("UPDATE ladspa SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
		if pluginfo_obj.midi_num_outputs: db_plugins.execute("UPDATE ladspa SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
		if pluginfo_obj.num_params: db_plugins.execute("UPDATE ladspa SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
		if pluginfo_obj.num_params_out: db_plugins.execute("UPDATE ladspa SET num_params_out = ? WHERE id = ?", (pluginfo_obj.num_params_out, pluginfo_obj.id,))

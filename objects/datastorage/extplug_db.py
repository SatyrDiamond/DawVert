# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sqlite3
import platform

class pluginfo:
	def __init__(self):
		self.out_exists = False
		self.name = None
		self.basename = None
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

	def from_sql_vst2(self, indata, platformtxt):
		p_name, p_id, p_type, p_creator, p_version, p_audio_num_inputs, p_audio_num_outputs, p_midi_num_inputs, p_midi_num_outputs, p_num_params, p_basename, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix = indata
		self.out_exists = True
		self.name = p_name
		self.id = p_id
		self.type = p_type
		self.creator = p_creator
		self.version = p_version
		self.basename = p_basename
		self.audio_num_inputs = p_audio_num_inputs
		self.audio_num_outputs = p_audio_num_outputs
		self.midi_num_inputs = p_midi_num_inputs
		self.midi_num_outputs = p_midi_num_outputs
		self.num_params = p_num_params
		if platformtxt == 'win': 
			self.path_32bit = p_path_32bit_win
			self.path_64bit = p_path_64bit_win
		if platformtxt == 'lin': 
			self.path_32bit = p_path_32bit_unix
			self.path_64bit = p_path_64bit_unix

	def from_sql_vst3(self, indata, platformtxt):
		p_name, p_id, p_type, p_creator, p_category, p_version, p_sdk_version, p_url, p_email, p_audio_num_inputs, p_audio_num_outputs, p_midi_num_inputs, p_midi_num_outputs, p_num_params, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix = indata
		self.out_exists = True
		self.name = p_name
		self.id = p_id
		self.type = p_type
		self.creator = p_creator
		self.category = p_category
		self.version = p_version
		self.sdk_version = p_sdk_version
		self.url = p_url
		self.email = p_email
		self.audio_num_inputs = p_audio_num_inputs
		self.audio_num_outputs = p_audio_num_outputs
		self.midi_num_inputs = p_midi_num_inputs
		self.midi_num_outputs = p_midi_num_outputs
		self.num_params = p_num_params
		if platformtxt == 'win': 
			self.path_32bit = p_path_32bit_win
			self.path_64bit = p_path_64bit_win
		if platformtxt == 'lin': 
			self.path_32bit = p_path_32bit_unix
			self.path_64bit = p_path_64bit_unix

	def from_sql_clap(self, indata, platformtxt):
		p_name, p_id, p_creator, p_category, p_version, p_audio_num_inputs, p_audio_num_outputs, p_midi_num_inputs, p_midi_num_outputs, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix = indata
		self.out_exists = True
		self.name = p_name
		self.id = p_id
		self.creator = p_creator
		self.category = p_category
		self.version = p_version
		self.audio_num_inputs = p_audio_num_inputs
		self.audio_num_outputs = p_audio_num_outputs
		self.midi_num_inputs = p_midi_num_inputs
		self.midi_num_outputs = p_midi_num_outputs
		self.num_params = p_num_params
		if platformtxt == 'win': 
			self.path_32bit = p_path_win
			self.path_64bit = p_path_win
		if platformtxt == 'lin': 
			self.path_32bit = p_path_unix
			self.path_64bit = p_path_unix

def get_def_platform():
	platform_architecture = platform.architecture()
	if platform_architecture[1] == 'WindowsPE': return 'win'
	else: return 'lin'

class extplug_db:
	os.makedirs(os.getcwd() + '/__config/', exist_ok=True)

	platformtxt = get_def_platform()

	db_plugins = None

	def load_db():
		if extplug_db.db_plugins == None:
			extplug_db.db_plugins = sqlite3.connect('./__config/plugins_external.db', check_same_thread=False)
			extplug_db.init_db()
			return True
		else:
			return False

	def init_db():
		extplug_db.db_plugins.execute('''
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
				basename text,
				path_32bit_win text,
				path_64bit_win text,
				path_32bit_unix text,
				path_64bit_unix text,
				UNIQUE(id)
			)''')
		
		extplug_db.db_plugins.execute('''
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
		
		extplug_db.db_plugins.execute('''
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
				path_32bit_win text,
				path_64bit_win text,
				path_32bit_unix text,
				path_64bit_unix text,
				UNIQUE(id)
			)''')
		
		extplug_db.db_plugins.execute('''
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
		if extplug_db.db_plugins:
			extplug_db.db_plugins.commit()

class vst2:
	exe_txt_start = "SELECT name, id, type, creator, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, basename, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst2"

	def add(pluginfo_obj, platformtxt):
		if pluginfo_obj.id and extplug_db.db_plugins:
			extplug_db.db_plugins.execute("INSERT OR IGNORE INTO vst2 (id) VALUES (?)", (pluginfo_obj.id,))
			if pluginfo_obj.name: extplug_db.db_plugins.execute("UPDATE vst2 SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
			if pluginfo_obj.creator: extplug_db.db_plugins.execute("UPDATE vst2 SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
	
			if pluginfo_obj.path_32bit:
				if os.path.exists(pluginfo_obj.path_32bit):
					if platformtxt == 'win': extplug_db.db_plugins.execute("UPDATE vst2 SET path_32bit_win = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
					if platformtxt == 'lin': extplug_db.db_plugins.execute("UPDATE vst2 SET path_32bit_unix = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
	
			if pluginfo_obj.path_64bit:
				if os.path.exists(pluginfo_obj.path_64bit):
					if platformtxt == 'win': 
						extplug_db.db_plugins.execute("UPDATE vst2 SET path_64bit_win = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
						extplug_db.db_plugins.execute("UPDATE vst2 SET basename = ? WHERE id = ?", (os.path.splitext(os.path.basename(pluginfo_obj.path_64bit))[0], pluginfo_obj.id,))
					if platformtxt == 'lin': 
						extplug_db.db_plugins.execute("UPDATE vst2 SET path_64bit_unix = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
						extplug_db.db_plugins.execute("UPDATE vst2 SET basename = ? WHERE id = ?", (os.path.splitext(os.path.basename(pluginfo_obj.path_64bit))[0], pluginfo_obj.id,))
	
			if pluginfo_obj.version: extplug_db.db_plugins.execute("UPDATE vst2 SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_inputs: extplug_db.db_plugins.execute("UPDATE vst2 SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_outputs: extplug_db.db_plugins.execute("UPDATE vst2 SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_inputs: extplug_db.db_plugins.execute("UPDATE vst2 SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_outputs: extplug_db.db_plugins.execute("UPDATE vst2 SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.num_params: extplug_db.db_plugins.execute("UPDATE vst2 SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
			if pluginfo_obj.type: extplug_db.db_plugins.execute("UPDATE vst2 SET type = ? WHERE id = ?", (pluginfo_obj.type, pluginfo_obj.id,))
	
	def check(bycat, in_val):
		if extplug_db.db_plugins:
			if bycat == 'name':
				return bool(extplug_db.db_plugins.execute("SELECT count(*) FROM vst2 WHERE name = ?", (in_val,)).fetchone())
			elif bycat == 'id':
				return bool(extplug_db.db_plugins.execute("SELECT count(*) FROM vst2 WHERE id = ?", (in_val,)).fetchone()[0])
		else:
			return False

	def get(bycat, in_val, in_platformtxt, cpu_arch_list):
		founddata = None
	
		if in_platformtxt == None: in_platformtxt = get_def_platform()
	
		if extplug_db.db_plugins:
			if bycat == 'id':
				founddata = extplug_db.db_plugins.execute(vst2.exe_txt_start+" WHERE id = ?", (in_val,)).fetchone()
	
			if bycat == 'name':
				founddata = extplug_db.db_plugins.execute(vst2.exe_txt_start+" WHERE name = ?", (in_val,)).fetchone()
	
			if bycat == 'basename':
				founddata = extplug_db.db_plugins.execute(vst2.exe_txt_start+" WHERE basename = ?", (in_val,)).fetchone()
	
			if bycat == 'path':
				patharch = 'win' if in_platformtxt == 'win' else 'unix'
				in_val = in_val.replace('/', '\\')
				founddata_path32 = extplug_db.db_plugins.execute(vst2.exe_txt_start+" WHERE path_32bit_"+patharch+" = ?", (in_val,)).fetchone()
				founddata_path64 = extplug_db.db_plugins.execute(vst2.exe_txt_start+" WHERE path_64bit_"+patharch+" = ?", (in_val,)).fetchone()
				if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
				if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64

		pluginfo_obj = pluginfo()
		if founddata: pluginfo_obj.from_sql_vst2(founddata, in_platformtxt)
		return pluginfo_obj
	
	def getall():
		o = []
		if extplug_db.db_plugins:
			vst2all = extplug_db.db_plugins.execute("SELECT * FROM vst2").fetchall()
			for x in vst2all:
				pluginfo_obj = pluginfo()
				pluginfo_obj.from_sql_vst2(x, platformtxt)
				o.append(pluginfo_obj)
		return o

	def count():
		if extplug_db.db_plugins:
			return extplug_db.db_plugins.execute("SELECT count(*) FROM vst2").fetchone()[0]
		else:
			return 0

class vst3:
	exe_txt_start = "SELECT name, id, type, creator, category, version, sdk_version, url, email, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, num_params, path_32bit_win, path_64bit_win, path_32bit_unix, path_64bit_unix FROM vst3"

	def add(pluginfo_obj, platformtxt):
	
		if pluginfo_obj.id and extplug_db.db_plugins:
			extplug_db.db_plugins.execute("INSERT OR IGNORE INTO vst3 (id) VALUES (?)", (pluginfo_obj.id,))
	
			if not pluginfo_obj.type and pluginfo_obj.category:
				splitcat = pluginfo_obj.category.split('|')
				if splitcat[0] == 'Fx': pluginfo_obj.type = 'effect'
				if splitcat[0] == 'Instrument': pluginfo_obj.type = 'synth'
	
			if pluginfo_obj.name: extplug_db.db_plugins.execute("UPDATE vst3 SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
			if pluginfo_obj.creator: extplug_db.db_plugins.execute("UPDATE vst3 SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
	
			if pluginfo_obj.path_32bit:
				if os.path.exists(pluginfo_obj.path_32bit):
					if platformtxt == 'win': extplug_db.db_plugins.execute("UPDATE vst3 SET path_32bit_win = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
					if platformtxt == 'lin': extplug_db.db_plugins.execute("UPDATE vst3 SET path_32bit_unix = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
	
			if pluginfo_obj.path_64bit:
				if os.path.exists(pluginfo_obj.path_64bit):
					if platformtxt == 'win': extplug_db.db_plugins.execute("UPDATE vst3 SET path_64bit_win = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
					if platformtxt == 'lin': extplug_db.db_plugins.execute("UPDATE vst3 SET path_64bit_unix = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
	
			if pluginfo_obj.version: extplug_db.db_plugins.execute("UPDATE vst3 SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
			if pluginfo_obj.sdk_version: extplug_db.db_plugins.execute("UPDATE vst3 SET sdk_version = ? WHERE id = ?", (pluginfo_obj.sdk_version, pluginfo_obj.id,))
			if pluginfo_obj.url: extplug_db.db_plugins.execute("UPDATE vst3 SET url = ? WHERE id = ?", (pluginfo_obj.url, pluginfo_obj.id,))
			if pluginfo_obj.email: extplug_db.db_plugins.execute("UPDATE vst3 SET email = ? WHERE id = ?", (pluginfo_obj.email, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_inputs: extplug_db.db_plugins.execute("UPDATE vst3 SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_outputs: extplug_db.db_plugins.execute("UPDATE vst3 SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_inputs: extplug_db.db_plugins.execute("UPDATE vst3 SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_outputs: extplug_db.db_plugins.execute("UPDATE vst3 SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.num_params: extplug_db.db_plugins.execute("UPDATE vst3 SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
			if pluginfo_obj.type: extplug_db.db_plugins.execute("UPDATE vst3 SET type = ? WHERE id = ?", (pluginfo_obj.type, pluginfo_obj.id,))
			if pluginfo_obj.category: extplug_db.db_plugins.execute("UPDATE vst3 SET category = ? WHERE id = ?", (pluginfo_obj.category, pluginfo_obj.id,))
	
	def check(bycat, in_val):
		if extplug_db.db_plugins:
			if bycat == 'name':
				return bool(extplug_db.db_plugins.execute("SELECT count(*) FROM vst3 WHERE name = ?", (in_val,)).fetchone())
			elif bycat == 'id':
				return bool(extplug_db.db_plugins.execute("SELECT count(*) FROM vst3 WHERE id = ?", (in_val,)).fetchone())
		else:
			return False

	def get(bycat, in_val, in_platformtxt, cpu_arch_list):
		founddata = None
	
		if in_platformtxt == None: in_platformtxt = platformtxt
	
		if extplug_db.db_plugins:
			if bycat == 'id':
				founddata = extplug_db.db_plugins.execute(vst3.exe_txt_start+" WHERE id = ?", (in_val,)).fetchone()
	
			if bycat == 'name':
				founddata = extplug_db.db_plugins.execute(vst3.exe_txt_start+" WHERE name = ?", (in_val,)).fetchone()
	
			if bycat == 'path':
				patharch = 'win' if in_platformtxt == 'win' else 'unix'
				in_val = in_val.replace('/', '\\')
				founddata_path32 = extplug_db.db_plugins.execute(vst3.exe_txt_start+" WHERE path_32bit_"+patharch+" = ?", (in_val,)).fetchone()
				founddata_path64 = extplug_db.db_plugins.execute(vst3.exe_txt_start+" WHERE path_64bit_"+patharch+" = ?", (in_val,)).fetchone()
				if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
				if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64

		pluginfo_obj = pluginfo()
		if founddata: pluginfo_obj.from_sql_vst3(founddata, in_platformtxt)
		return pluginfo_obj
	
	def count():
		if extplug_db.db_plugins:
			return extplug_db.db_plugins.execute("SELECT count(*) FROM vst3").fetchone()[0]
		else:
			return 0

class clap:
	exe_txt_start = "SELECT name, id, creator, category, version, audio_num_inputs, audio_num_outputs, midi_num_inputs, midi_num_outputs, p_path_32bit_win, p_path_64bit_win, p_path_32bit_unix, p_path_64bit_unix FROM clap"

	def add(pluginfo_obj, platformtxt):
		if pluginfo_obj.id and extplug_db.db_plugins:
			extplug_db.db_plugins.execute("INSERT OR IGNORE INTO clap (id) VALUES (?)", (pluginfo_obj.id,))
			if pluginfo_obj.name: extplug_db.db_plugins.execute("UPDATE clap SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
			if pluginfo_obj.creator: extplug_db.db_plugins.execute("UPDATE clap SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
			if pluginfo_obj.category: extplug_db.db_plugins.execute("UPDATE clap SET category = ? WHERE id = ?", (pluginfo_obj.category, pluginfo_obj.id,))
			if pluginfo_obj.version: extplug_db.db_plugins.execute("UPDATE clap SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_inputs: extplug_db.db_plugins.execute("UPDATE clap SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_outputs: extplug_db.db_plugins.execute("UPDATE clap SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_inputs: extplug_db.db_plugins.execute("UPDATE clap SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_outputs: extplug_db.db_plugins.execute("UPDATE clap SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
	
			if pluginfo_obj.path_32bit:
				if os.path.exists(pluginfo_obj.path_32bit):
					if platformtxt == 'win': extplug_db.db_plugins.execute("UPDATE clap SET path_32bit_win = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
					if platformtxt == 'lin': extplug_db.db_plugins.execute("UPDATE clap SET path_32bit_unix = ? WHERE id = ?", (pluginfo_obj.path_32bit, pluginfo_obj.id,))
	
			if pluginfo_obj.path_64bit:
				if os.path.exists(pluginfo_obj.path_64bit):
					if platformtxt == 'win': extplug_db.db_plugins.execute("UPDATE clap SET path_64bit_win = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
					if platformtxt == 'lin': extplug_db.db_plugins.execute("UPDATE clap SET path_64bit_unix = ? WHERE id = ?", (pluginfo_obj.path_64bit, pluginfo_obj.id,))
	
	def get(bycat, in_val, in_platformtxt, cpu_arch_list):
		founddata = None
	
		if in_platformtxt == None: in_platformtxt = platformtxt
	
		if extplug_db.db_plugins:
			if bycat == 'id':
				founddata = extplug_db.db_plugins.execute(clap.exe_txt_start+" WHERE id = ?", (in_val,)).fetchone()
	
			if bycat == 'name':
				founddata = extplug_db.db_plugins.execute(clap.exe_txt_start+" WHERE name = ?", (in_val,)).fetchone()
	
			if bycat == 'path':
				patharch = 'win' if in_platformtxt == 'win' else 'unix'
				in_val = in_val.replace('/', '\\')
				founddata_path32 = extplug_db.db_plugins.execute(clap.exe_txt_start+" WHERE path_32bit_"+patharch+" = ?", (in_val,)).fetchone()
				founddata_path64 = extplug_db.db_plugins.execute(clap.exe_txt_start+" WHERE path_64bit_"+patharch+" = ?", (in_val,)).fetchone()
				if founddata_path32 and 32 in cpu_arch_list: founddata = founddata_path32
				if founddata_path64 and 64 in cpu_arch_list: founddata = founddata_path64

		pluginfo_obj = pluginfo()
		if founddata: pluginfo_obj.from_sql_clap(founddata, in_platformtxt)
		return pluginfo_obj
	
	def count():
		if extplug_db.db_plugins:
			return extplug_db.db_plugins.execute("SELECT count(*) FROM clap").fetchone()[0]
		else:
			return 0

class ladspa:
	def add(pluginfo_obj, platformtxt):
		if pluginfo_obj.id and extplug_db.db_plugins:
			extplug_db.db_plugins.execute("INSERT OR IGNORE INTO ladspa (id) VALUES (?)", (pluginfo_obj.id,))
			if pluginfo_obj.name: extplug_db.db_plugins.execute("UPDATE ladspa SET name = ? WHERE id = ?", (pluginfo_obj.name, pluginfo_obj.id,))
			if pluginfo_obj.inside_id: extplug_db.db_plugins.execute("UPDATE ladspa SET inside_id = ? WHERE id = ?", (pluginfo_obj.inside_id, pluginfo_obj.id,))
			if pluginfo_obj.creator: extplug_db.db_plugins.execute("UPDATE ladspa SET creator = ? WHERE id = ?", (pluginfo_obj.creator, pluginfo_obj.id,))
			if pluginfo_obj.version: extplug_db.db_plugins.execute("UPDATE ladspa SET version = ? WHERE id = ?", (pluginfo_obj.version, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_inputs: extplug_db.db_plugins.execute("UPDATE ladspa SET audio_num_inputs = ? WHERE id = ?", (pluginfo_obj.audio_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.audio_num_outputs: extplug_db.db_plugins.execute("UPDATE ladspa SET audio_num_outputs = ? WHERE id = ?", (pluginfo_obj.audio_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_inputs: extplug_db.db_plugins.execute("UPDATE ladspa SET midi_num_inputs = ? WHERE id = ?", (pluginfo_obj.midi_num_inputs, pluginfo_obj.id,))
			if pluginfo_obj.midi_num_outputs: extplug_db.db_plugins.execute("UPDATE ladspa SET midi_num_outputs = ? WHERE id = ?", (pluginfo_obj.midi_num_outputs, pluginfo_obj.id,))
			if pluginfo_obj.num_params: extplug_db.db_plugins.execute("UPDATE ladspa SET num_params = ? WHERE id = ?", (pluginfo_obj.num_params, pluginfo_obj.id,))
			if pluginfo_obj.num_params_out: extplug_db.db_plugins.execute("UPDATE ladspa SET num_params_out = ? WHERE id = ?", (pluginfo_obj.num_params_out, pluginfo_obj.id,))

	def count():
		if extplug_db.db_plugins:
			return extplug_db.db_plugins.execute("SELECT count(*) FROM ladspa").fetchone()[0]
		else:
			return 0

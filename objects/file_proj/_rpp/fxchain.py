
from dataclasses import dataclass
from objects.file_proj._rpp import env as rpp_env
from objects.file_proj._rpp import func as reaper_func
import base64
import uuid

rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var
robj = reaper_func.rpp_obj

class rpp_vst:
	def __init__(self):
		self.data_con = b''
		self.data_chunk = b''
		self.vst_name = ''
		self.vst_lib = ''
		self.vst_num = 0
		self.vst_unk = ''
		self.vst_fourid = None
		self.vst_uuid = None
		self.vst3_uuid = None

	def load(self, values, inside_dat):
		for n, v in enumerate(values):
			if n == 0: self.vst_name = v
			if n == 1: self.vst_lib = v
			if n == 2: self.vst_num = v
			if n == 3: self.vst_unk = v
			if n == 4 and v: 
				if '<' in v:
					self.vst_fourid = int(v.split('<')[0])
					self.vst_uuid = v.split('<')[1].split('>')[0]
				elif '{' in v:
					self.vst_fourid = int(v.split('{')[0])
					self.vst3_uuid = v.split('{')[1].split('}')[0]
				else:
					self.vst_fourid = int(v.split('<')[0])

		for n, x in enumerate(reaper_func.getbin_multi(inside_dat)):
			if n == 0: self.data_con = x
			if n == 1: self.data_chunk = x

	def write(self, rpp_data):
		idtxt = ''
		if self.vst_fourid != None:
			idtxt = str(self.vst_fourid)
			if self.vst_uuid: idtxt += '<'+self.vst_uuid+'>'
			elif self.vst3_uuid: idtxt += '{'+self.vst3_uuid+'}'
		rpp_vstdata = robj('VST',[self.vst_name, self.vst_lib, self.vst_num, self.vst_unk, idtxt, ''])

		reaper_func.writebin(rpp_vstdata, self.data_con)
		reaper_func.writebin(rpp_vstdata, self.data_chunk)

		rpp_data.children.append(rpp_vstdata)

class rpp_clap:
	def __init__(self):
		self.data_chunk = b''
		self.clap_name = ''
		self.clap_id = ''
		self.clap_unk = ''
		self.config = rvd([0,0,0,''], ['unk1','unk2','unk3','unk4'], [int, int, int, str], True)

	def load(self, values, rpp_data):
		for n, v in enumerate(values):
			if n == 0: self.clap_name = v
			if n == 1: self.clap_id = v
			if n == 2: self.clap_unk = v
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'CFG': self.config.read(values)
			if name == 'STATE': self.data_chunk = reaper_func.getbin(inside_dat)

	def write(self, rpp_data):
		rpp_clapdata = robj('CLAP',[self.clap_name, self.clap_id, self.clap_unk])
		self.config.write('CFG', rpp_clapdata)
		rpp_clapstate = robj('STATE',[])
		reaper_func.writebin(rpp_clapstate, self.data_chunk)
		rpp_clapdata.children.append(rpp_clapstate)

		rpp_data.children.append(rpp_clapdata)

class rpp_js:
	def __init__(self):
		self.data = []
		self.js_id = ''
		self.js_unk = ''

	def load(self, values, inside_dat):
		if inside_dat: self.data = inside_dat[0]
		for n, v in enumerate(values):
			if n == 0: self.js_id = v
			if n == 1: self.js_unk = v

	def write(self, rpp_data):
		rpp_jsdata = robj('JS',[self.js_id, self.js_unk])
		rpp_jsdata.children.append(self.data)
		rpp_data.children.append(rpp_jsdata)

class rpp_rewire:
	def __init__(self):
		self.data_chunk = b''
		self.rw_id = ''
		self.rw_unk = ''

	def load(self, values, inside_dat):
		for n, v in enumerate(values):
			if n == 0: self.rw_id = v
			if n == 1: self.rw_unk = v
		for n, x in enumerate(reaper_func.getbin_multi(inside_dat)):
			if n == 0: self.data_chunk = x

	def write(self, rpp_data):
		rpp_rwdata = robj('REWIRE',[self.rw_id, self.rw_unk])
		reaper_func.writebin(rpp_rwdata, self.data_chunk)
		rpp_data.children.append(rpp_rwdata)

class rpp_plugin:
	def __init__(self):
		self.plugin = None
		self.type = ''
		self.bypass = rvd([0,0,0], ['bypass','offline','unk'], None, True)
		self.floatpos = rvd([0,0,0,0], ['pos_x','pos_y','size_x','size_y'], None, True)
		self.wak = rvd([0,0], ['keyboard_in','fxui'], None, True)
		self.fxid = rvs('', str, True)
		self.presetname = rvs('', str, False)
		self.wet = rvd([1,0], ['wet','delta_solo'], None, False)
		self.parmenv = []

	def add_env(self):
		parmenv_obj = rpp_env.rpp_env()
		parmenv_obj.is_param = True
		parmenv_obj.used = True
		parmenv_obj.act['bypass'] = 1
		self.parmenv.append(parmenv_obj)
		return parmenv_obj
	
class rpp_fxchain:
	def __init__(self):
		self.wndrect = rvd([0,0,0,0], ['pos_x','pos_y','size_x','size_y'], None, True)
		self.show = rvs(0, float, True)
		self.lastsel = rvs(0, float, True)
		self.docked = rvs(0, float, True)
		self.fxchain = rvs(0, float, True)
		self.plugins = []

	def add_vst(self):
		guid = '{'+str(uuid.uuid4())+'}'
		vst_obj = rpp_vst()
		plug_obj = rpp_plugin()
		plug_obj.type = 'VST'
		plug_obj.plugin = vst_obj
		plug_obj.fxid.set(guid)
		self.plugins.append(plug_obj)
		return plug_obj, vst_obj, guid

	def add_clap(self):
		guid = '{'+str(uuid.uuid4())+'}'
		clap_obj = rpp_clap()
		plug_obj = rpp_plugin()
		plug_obj.type = 'CLAP'
		plug_obj.plugin = clap_obj
		plug_obj.fxid.set(guid)
		self.plugins.append(plug_obj)
		return plug_obj, clap_obj, guid

	def add_js(self):
		guid = '{'+str(uuid.uuid4())+'}'
		js_obj = rpp_js()
		plug_obj = rpp_plugin()
		plug_obj.type = 'JS'
		plug_obj.plugin = js_obj
		plug_obj.fxid.set(guid)
		self.plugins.append(plug_obj)
		return plug_obj, js_obj, guid

	def load(self, rpp_data):
		bypassval = [0,0,0]
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'WNDRECT': self.wndrect.read(values)
			if name == 'SHOW': self.show.set(values[0])
			if name == 'LASTSEL': self.lastsel.set(values[0])
			if name == 'DOCKED': self.docked.set(values[0])
			if name == 'BYPASS': bypassval = [x for x in values]
			if name == 'FXID': self.plugins[-1].fxid.set(values[0])
			if name == 'PRESETNAME': self.plugins[-1].presetname.set(values[0])
			if name == 'FLOATPOS': self.plugins[-1].floatpos.read(values)
			if name == 'WAK': self.plugins[-1].wak.read(values)
			if name == 'WET': self.plugins[-1].wet.read(values)

			if is_dir:
				if name in 'VST': 
					vst_obj = rpp_vst()
					vst_obj.load(values, inside_dat)
					plug_obj = rpp_plugin()
					plug_obj.type = name
					plug_obj.plugin = vst_obj
					plug_obj.bypass.read(bypassval)
					self.plugins.append(plug_obj)
				elif name in 'CLAP': 
					clap_obj = rpp_clap()
					clap_obj.load(values, inside_dat)
					plug_obj = rpp_plugin()
					plug_obj.type = name
					plug_obj.plugin = clap_obj
					plug_obj.bypass.read(bypassval)
					self.plugins.append(plug_obj)
				elif name in 'JS': 
					js_obj = rpp_js()
					js_obj.load(values, inside_dat)
					plug_obj = rpp_plugin()
					plug_obj.type = name
					plug_obj.plugin = js_obj
					plug_obj.bypass.read(bypassval)
					self.plugins.append(plug_obj)
				elif name in 'REWIRE': 
					rewire_obj = rpp_rewire()
					rewire_obj.load(values, inside_dat)
					plug_obj = rpp_plugin()
					plug_obj.type = name
					plug_obj.plugin = rewire_obj
					plug_obj.bypass.read(bypassval)
					self.plugins.append(plug_obj)
				if name == 'PARMENV': 
					parmenv_obj = rpp_env.rpp_env()
					parmenv_obj.read(inside_dat, values)
					self.plugins[-1].parmenv.append(parmenv_obj)
				#else:
				#	plug_obj = rpp_plugin()
				#	plug_obj.type = 'UNKNOWN'
				#	self.plugins.append(plug_obj)


	def write(self, rpp_data):
		self.wndrect.write('WNDRECT', rpp_data)
		self.show.write('SHOW', rpp_data)
		self.lastsel.write('LASTSEL', rpp_data)
		self.docked.write('DOCKED', rpp_data)
		for plugin in self.plugins:
			if plugin.type != 'UNKNOWN':
				plugin.bypass.write('BYPASS', rpp_data)
				plugin.plugin.write(rpp_data)
				plugin.presetname.write('PRESETNAME', rpp_data)
				plugin.wet.write('WET', rpp_data)
				plugin.floatpos.write('FLOATPOS', rpp_data)
				plugin.fxid.write('FXID', rpp_data)
				for e in plugin.parmenv: e.write('PARMENV', rpp_data)
				plugin.wak.write('WAK', rpp_data)
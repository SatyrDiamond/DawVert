# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import numpy as np
import logging
logger_plugins = logging.getLogger('plugins')

extplugdb = globalstore.extplug
os_ext_info = globalstore.os_type_info()

class extplug_vst2_params:
	def __init__(self):
		self.cur_program = 0
		self.set_numprogs(1, 0)
		self.set_program(0)

	def set_numprogs(self, num_programs, num_params):
		self.num_programs = num_programs
		self.num_params = num_params
		self.dtype_program = np.dtype([('name', '<S28'),('params', np.float32, self.num_params)]) 
		self.programs = np.zeros(self.num_programs, dtype=self.dtype_program)
		self.param_names = ['' for _ in range(self.num_params)]

	def set_program(self, cur_program):
		self.cur_program = cur_program
		self.programs_data = self.programs[self.cur_program]

	def set_program_name(self, program_name):
		self.programs_data['name'] = program_name

	def set_param(self, num, val):
		self.programs_data['params'][num] = val

	def set_param_name(self, num, val):
		self.param_names[num] = val

	def output(self, plugin_obj):
		for num, presetdata in enumerate(self.programs):
			plugin_obj.set_program(num)
			plugin_obj.preset.name = presetdata['name'].decode()
			for paramnum, paramval in enumerate(presetdata['params']):
				plugin_obj.params.add_named('ext_param_'+str(paramnum), paramval, 'float', self.param_names[paramnum])
		plugin_obj.set_program(self.cur_program)

class extplug_manu:
	def __init__(self, plugin_obj, convproj_obj, pluginid):
		self.plugin_obj = plugin_obj
		self.convproj_obj = convproj_obj
		self.pluginid = pluginid
		self.extplugtype = None
		self.cur_params = {}
		self.cpu_arch_list = [32, 64] if os_ext_info.bits==64 else [32]
		self.state_vst2_params = extplug_vst2_params()
		if plugin_obj.type.category == 'external': self.extplugtype = plugin_obj.type.type

# --------------------------------------------------- VSTPROGS ---------------------------------------------------

	def vst2__set_numprogs(self, num_programs):
		external_info = self.plugin_obj.external_info
		self.state_vst2_params.set_numprogs(num_programs, external_info.numparams)

	def vst2__set_program(self, cur_program):
		self.state_vst2_params.set_program(cur_program)

	def vst2__set_program_name(self, program_name):
		self.state_vst2_params.set_program_name(program_name)

	def vst2__set_param(self, num, val):
		self.state_vst2_params.set_param(num, val)

	def vst2__set_param_name(self, num, val):
		self.state_vst2_params.set_param_name(num, val)

	def vst2__output(self):
		self.state_vst2_params.output(self.plugin_obj)

# --------------------------------------------------- MAIN ---------------------------------------------------

	def external__from_pluginfo_obj(self, pluginfo_obj):
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info
		external_info.from_pluginfo_obj(pluginfo_obj, plugin_obj.type.type)

		vst_cpuarch, vst_path = pluginfo_obj.find_locpath(self.cpu_arch_list)
		if vst_cpuarch and vst_path:
			self.convproj_obj.fileref__add(vst_path, vst_path, None)
			plugin_obj.filerefs_global['plugin'] = vst_path
			external_info.cpu_arch = vst_cpuarch

		plugin_obj.role = pluginfo_obj.type
		plugin_obj.audioports.setnums_auto(pluginfo_obj.audio_num_inputs, pluginfo_obj.audio_num_outputs)

	def external__set_chunk(self, chunk):
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info

		external_info.datatype = 'chunk'
		plugin_obj.rawdata_add('chunk', chunk)

	def set_type(self, plugtype, platformtxt):
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info
		if plugin_obj.type.subtype != plugtype: plugin_obj.replace('external', plugtype, platformtxt)
		else: plugin_obj.type.subtype = platformtxt

	def db__setinfo(self, plugtype, bycat, in_val, platformtxt):
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info
		platformtxt = os_ext_info.get_ext_ostype(platformtxt)

		extplugdb.load()
		pluginfo_obj = extplugdb.get(plugtype, bycat, in_val, platformtxt, self.cpu_arch_list)

		if pluginfo_obj.out_exists:
			self.set_type(plugtype, platformtxt)
			self.external__from_pluginfo_obj(pluginfo_obj)
			return True
		elif bycat == 'id':
			self.set_type(plugtype, platformtxt)
			plugin_obj.external_info.id = in_val
			outtxt = str(in_val)
			logger_plugins.warning(plugtype+': plugin not found in database: '+outtxt)
			return True
		else:
			pluginname = plugin_obj.external_info.name
			outtxt = '"'+str(in_val)+'" from '+str(bycat)
			if pluginname: outtxt = pluginname
			logger_plugins.warning(plugtype+': plugin not found in database: '+outtxt)
			return False

# --------------------------------------------------- VST3 ---------------------------------------------------

	def vst3__replace_data(self, bycat, in_val, data, platformtxt):
		if self.db__setinfo('vst3', bycat, in_val, platformtxt):
			self.external__set_chunk(data)

	def vst3__import_presetdata(self, datatype, indata, platformtxt):
		from objects.file import preset_vst3
		byr_stream = bytereader.bytereader()
		preset_obj = preset_vst3.vst3_main()
		if datatype == 'raw': 
			byr_stream.load_raw(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'file': 
			byr_stream.load_file(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'byr': 
			preset_obj.parse(indata)
		self.vst3__replace_data('id', preset_obj.uuid, preset_obj.data, platformtxt)

	def vst3__export_presetdata(self, filename):
		from objects.file import preset_vst3
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info

		byw_stream = bytewriter.bytewriter()
		preset_obj = preset_vst3.vst3_main()
		vstid = external_info.id
		outdata = b''
		if vstid != None:
			preset_obj.uuid = vstid
			preset_obj.data = plugin_obj.rawdata_get('chunk')
			preset_obj.write(byw_stream)
			outdata = byw_stream.getvalue()
		else:
			logger_plugins.warning('vst3: id is missing')

		if filename:
			with open(filename, 'wb') as f: f.write(outdata)

		return outdata

# --------------------------------------------------- CLAP ---------------------------------------------------

	def clap__replace_data(self, bycat, in_val, data, platformtxt):
		if self.db__setinfo('clap', bycat, in_val, platformtxt):
			self.external__set_chunk(data)

	def clap__import_presetdata(self, datatype, indata, platformtxt):
		from objects.file import preset_clap
		byr_stream = bytereader.bytereader()
		preset_obj = preset_clap.clap_preset()
		if datatype == 'raw': 
			byr_stream.load_raw(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'file': 
			byr_stream.load_file(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'byr': 
			preset_obj.parse(indata)
		self.clap__replace_data('id', preset_obj.id, preset_obj.data, platformtxt)

	def clap__export_presetdata(self, filename):
		from objects.file import preset_clap
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info

		byw_stream = bytewriter.bytewriter()
		preset_obj = preset_clap.clap_preset()
		vstid = external_info.id
		outdata = b''
		if vstid != None:
			preset_obj.id = vstid
			preset_obj.data = plugin_obj.rawdata_get('chunk')
			preset_obj.write(byw_stream)
			outdata = byw_stream.getvalue()
		else:
			logger_plugins.warning('clap: id is missing')

		if filename:
			with open(filename, 'wb') as f: f.write(outdata)

		return outdata

# --------------------------------------------------- VST2 ---------------------------------------------------

	def vst2__replace_data(self, bycat, in_val, data, platformtxt, isbank):
		external_info = self.plugin_obj.external_info
		if self.db__setinfo('vst2', bycat, in_val, platformtxt):
			self.external__set_chunk(data)
			external_info.is_bank = isbank

	def vst2__setup_params(self, bycat, in_val, nump, platformtxt, isbank):
		external_info = self.plugin_obj.external_info
		if self.db__setinfo('vst2', bycat, in_val, platformtxt):
			external_info.datatype = 'param' if not isbank else 'bank'
			external_info.numparams = nump

	def vst2__import_presetdata(self, datatype, indata, platformtxt):
		from objects.file import preset_vst2

		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info

		byr_stream = bytereader.bytereader()
		fxp_obj = preset_vst2.vst2_main()
		if datatype == 'raw': 
			byr_stream.load_raw(indata)
			fxp_obj.parse(byr_stream)
		if datatype == 'file': 
			byr_stream.load_file(indata)
			fxp_obj.parse(byr_stream)
		if datatype == 'byr': 
			fxp_obj.parse(indata)

		vst_prog = fxp_obj.program
		if vst_prog.type in [1,4]:
			fpch = vst_prog.data
			if fpch.fourid: external_info.fourid = fpch.fourid
			else: fpch.fourid = external_info.fourid
			self.vst2__replace_data('id', fpch.fourid, fpch.chunk, platformtxt, vst_prog.type != 4)
			plugin_obj.preset.name = fpch.prgname
			external_info.version_bytes = fpch.version

		if vst_prog.type == 2:
			fxck = vst_prog.data
			if fxck.fourid: external_info.fourid = fxck.fourid
			else: fxck.fourid = external_info.fourid
			self.vst2__setup_params('id', fxck.fourid, fxck.num_params, platformtxt, False)
			plugin_obj.preset.name = fxck.prgname
			external_info.version_bytes = fxck.version
			for c, p in enumerate(fxck.params): plugin_obj.params.add('ext_param_'+str(c), p, 'float')

		if vst_prog.type == 3:
			fxck = vst_prog.data
			external_info.fourid = fxck.fourid
			if fxck.programs:
				num_params = fxck.programs[0][1].data.num_params
				self.vst2__setup_params('id', fxck.fourid, num_params, platformtxt, True)
				for num, vst_program in enumerate(fxck.programs):
					if vst_program[1].type == 2:
						pprog = vst_program[1].data
						plugin_obj.set_program(num)
						plugin_obj.preset.name = pprog.prgname
						for c, p in enumerate(pprog.params): plugin_obj.params.add('ext_param_'+str(c), p, 'float')
				plugin_obj.set_program(fxck.current_program)

	def vst2__export_presetdata(self, filename):
		from objects.file import preset_vst2
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info
		datatype = external_info.datatype
		fourid = external_info.fourid

		byw_stream = bytewriter.bytewriter()
		fxp_obj = preset_vst2.vst2_main()

		outdata = b''
		if fourid != None:
			program = fxp_obj.program

			if datatype == 'chunk':
				if external_info.is_bank: fpch = program.set_fxChunkSet_bank(None)
				else: fpch = program.set_fxChunkSet(None)
				fpch.fourid = fourid
				fpch.version = external_info.version_bytes
				fpch.num_programs = 1
				fpch.prgname = plugin_obj.preset.name
				fpch.chunk = plugin_obj.rawdata_get('chunk')
				fxp_obj.write(byw_stream)
				outdata = byw_stream.getvalue()
	
			if datatype == 'param':
				fxck = program.set_fxProgram(None)
				fxck.fourid = fourid
				fxck.version = external_info.version_bytes
				fxck.num_params = external_info.numparams
				fxck.prgname = plugin_obj.preset.name
				fxck.params = [plugin_obj.params.get('ext_param_'+str(c), 0).value for c in range(fxck.num_params)]
				fxp_obj.write(byw_stream)
				outdata = byw_stream.getvalue()
	
			if datatype == 'bank':
				fxbk = program.set_fxBank(None)
				fxbk.fourid = fourid
				fxbk.version = external_info.version_bytes
				fxbk.current_program = plugin_obj.current_program
				for num, program in plugin_obj.programs.items():
					inccnk = preset_vst2.vst2_program()
					fxck = inccnk.set_fxProgram(None)
					fxck.fourid = fourid
					fxck.version = fxbk.version
					fxck.num_params = external_info.numparams
					fxck.prgname = program.preset.name
					fxck.params = [program.params.get('ext_param_'+str(c), 0).value for c in range(fxck.num_params)]
					fxbk.programs.append([1130589771, inccnk])
				fxp_obj.write(byw_stream)
				outdata = byw_stream.getvalue()

			if filename:
				with open(filename, 'wb') as f: f.write(outdata)
		else:
			logger_plugins.warning('vst2: fourid is missing')

		return outdata
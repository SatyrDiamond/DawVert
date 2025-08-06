# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
import numpy as np
import logging
logger_plugins = logging.getLogger('extplug')

extplugdb = globalstore.extplug

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
		plugin_obj.program__reset()
		for num, presetdata in enumerate(self.programs):
			plugin_obj.program__set(num)
			plugin_obj.state.preset.name = presetdata['name'].decode()
			for paramnum, paramval in enumerate(presetdata['params']):
				plugin_obj.params.add_named('ext_param_'+str(paramnum), paramval, 'float', self.param_names[paramnum])
		plugin_obj.program__set(self.cur_program)

class extplug_manu:
	def __init__(self, plugin_obj, convproj_obj, pluginid):
		self.plugin_obj = plugin_obj
		self.convproj_obj = convproj_obj
		self.pluginid = pluginid
		self.extplugtype = None
		self.cur_params = {}
		self.state_vst2_params = extplug_vst2_params()
		self.cpu_arch_list = [32, 64] if globalstore.os_info_target.bits==64 else [32]
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

	def vst2__params_output(self):
		self.state_vst2_params.output(self.plugin_obj)

# --------------------------------------------------- MAIN ---------------------------------------------------

	def add_param(self, num, val, name):
		plugin_obj = self.plugin_obj
		param_obj = plugin_obj.params.add('ext_param_'+str(num), val, 'float')
		if name: param_obj.visual.name = name
		return param_obj

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
		if plugin_obj.type.subtype != plugtype: plugin_obj.replace('external', plugtype, platformtxt)
		else: plugin_obj.type.subtype = platformtxt

	def db__setinfo(self, plugtype, bycat, in_val, platformtxt):
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info
		platformtxt = globalstore.os_info_target.get_ext_ostype(platformtxt)

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

	def get_chunk(self, byr_stream, offset, platformtxt):
		byr_stream.seek(offset)
		if byr_stream.detectheader(offset, b'CcnK'):
			self.vst2__import_presetdata('byr', byr_stream, platformtxt)
			return True

		byr_stream.seek(offset)
		if byr_stream.detectheader(offset, b'VST3'):
			self.vst3__import_presetdata('byr', byr_stream, platformtxt)
			return True

		byr_stream.seek(offset)
		if byr_stream.detectheader(offset, b'clap'):
			self.clap__import_presetdata('byr', byr_stream, platformtxt)
			return True

# --------------------------------------------------- VST3 ---------------------------------------------------

	def vst3__replace_data(self, bycat, in_val, data, platformtxt):
		if self.db__setinfo('vst3', bycat, in_val, platformtxt):
			self.external__set_chunk(data)
			return True
		return False

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

# --------------------------------------------------- DIRECTX ---------------------------------------------------

	def dx__import_presetdata(self, datatype, indata):
		from objects.file import preset_dx
		byr_stream = bytereader.bytereader()
		preset_obj = preset_dx.dx_preset()
		if datatype == 'raw': 
			byr_stream.load_raw(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'file': 
			byr_stream.load_file(indata)
			preset_obj.parse(byr_stream)
		if datatype == 'byr': 
			preset_obj.parse(indata)
		self.dx__replace_data(preset_obj.id, preset_obj.data)

	def dx__replace_data(self, inid, chunk):
		external_info = self.plugin_obj.external_info
		external_info.plugtype = 'directx'
		external_info.id = inid
		self.external__set_chunk(chunk)

	def dx__export_presetdata(self):
		from objects.file import preset_dx
		plugin_obj = self.plugin_obj
		external_info = plugin_obj.external_info

		byw_stream = bytewriter.bytewriter()
		preset_obj = preset_dx.dx_preset()
		vstid = external_info.id
		outdata = b''
		if vstid != None:
			preset_obj.id = vstid
			preset_obj.data = plugin_obj.rawdata_get('chunk')
			preset_obj.write(byw_stream)
			outdata = byw_stream.getvalue()
		else:
			logger_plugins.warning('dx: id is missing')

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
			external_info.chunk_is_bank = isbank
			return True
		return False

	def vst2__setup_params(self, bycat, in_val, nump, platformtxt, isbank):
		external_info = self.plugin_obj.external_info
		if self.db__setinfo('vst2', bycat, in_val, platformtxt):
			external_info.datatype = 'param'
			external_info.is_bank = isbank
			external_info.numparams = nump
			self.state_vst2_params.set_numprogs(1, nump)
			return True
		self.state_vst2_params.set_numprogs(1, nump)
		return False

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

		if vst_prog.type == 1:
			fpch = vst_prog.data
			if fpch.fourid: external_info.fourid = fpch.fourid
			else: fpch.fourid = external_info.fourid
			self.vst2__replace_data('id', fpch.fourid, fpch.chunk, platformtxt, True)
			plugin_obj.preset.name = fpch.prgname
			external_info.version_bytes = fpch.version

		if vst_prog.type == 4:
			fpch = vst_prog.data
			if fpch.fourid: external_info.fourid = fpch.fourid
			else: fpch.fourid = external_info.fourid
			self.vst2__replace_data('id', fpch.fourid, fpch.chunk, platformtxt, False)
			external_info.version_bytes = fpch.version

		if vst_prog.type == 2:
			fxck = vst_prog.data
			if fxck.fourid: external_info.fourid = fxck.fourid
			else: fxck.fourid = external_info.fourid
			self.vst2__setup_params('id', fxck.fourid, fxck.num_params, platformtxt, False)
			plugin_obj.preset.name = fxck.prgname
			external_info.version_bytes = fxck.version
			for c, p in enumerate(fxck.params): 
				plugin_obj.params.add('ext_param_'+str(c), p, 'float')
			self.vst2__params_output()

		if vst_prog.type == 3:
			fxck = vst_prog.data
			external_info.fourid = fxck.fourid
			if fxck.programs:
				num_params = fxck.programs[0][1].data.num_params
				self.vst2__setup_params('id', fxck.fourid, num_params, platformtxt, True)
				self.vst2__set_numprogs(len(fxck.programs))
				for num, vst_program in enumerate(fxck.programs):
					self.vst2__set_program(num)
					if vst_program[1].type == 2:
						pprog = vst_program[1].data
						self.vst2__set_program_name(pprog.prgname)
						try:
							for c, p in enumerate(pprog.params): 
								self.vst2__set_param(c, p)
						except:
							#import traceback
							#print(traceback.format_exc())
							pass
				plugin_obj.program__set(fxck.current_program)
			self.vst2__params_output()

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
				if external_info.is_bank and external_info.chunk_is_bank: 
					fpch = program.set_fxChunkSet_bank(None)
				else: fpch = program.set_fxChunkSet(None)
				fpch.fourid = fourid
				fpch.version = external_info.version_bytes
				fpch.num_programs = 1
				fpch.prgname = plugin_obj.state.preset.name
				fpch.chunk = plugin_obj.rawdata_get('chunk')
				fxp_obj.write(byw_stream)
				outdata = byw_stream.getvalue()
	
			if datatype == 'param':
				if not external_info.is_bank:
					fxck = program.set_fxProgram(None)
					fxck.fourid = fourid
					fxck.version = external_info.version_bytes
					fxck.num_params = external_info.numparams
					fxck.prgname = plugin_obj.state.preset.name
					fxck.params = [plugin_obj.params.get('ext_param_'+str(c), 0).value for c in range(fxck.num_params)]
					fxp_obj.write(byw_stream)
					outdata = byw_stream.getvalue()
				else:
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
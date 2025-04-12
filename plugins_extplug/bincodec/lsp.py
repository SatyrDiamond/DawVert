# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins_extplug
import sys
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter
from objects.file import preset_vst2

class lsp_params():
	def __init__(self):
		self.version = {}
		self.params = {}

class plugin_extplug(plugins_extplug.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'bincodec'
	def get_shortname(self): return 'lsp'
	def get_prop(self, in_dict): pass

	def data_create(self): 
		return lsp_params()

	def data_decode(self, byr_stream, exttype, params): 
		lsp_obj = lsp_params()

		fxp_obj = preset_vst2.vst2_main()
		fxp_obj.parse(byr_stream)
		vst_prog = fxp_obj.program
		if vst_prog.type in [1,4]:
			fpch = vst_prog.data
			byr_stream = bytereader.bytereader(fpch.chunk)
		else: 
			return None
		byr_stream.magic_check(b'LSPU')
		size = byr_stream.uint32_b()
		lsp_obj.version = byr_stream.uint32_b()
		byr_stream.magic_check(b'LSPU')

		while byr_stream.remaining():
			with byr_stream.isolate_size(byr_stream.uint32_b(), True) as bye_stream:
				chunk_id = bye_stream.string_t()
				chunk_data = bye_stream.rest()
				lsp_obj.params[chunk_id] = chunk_data

		return lsp_obj

	def data_encode(self, lsp_obj, exttype, params):
		fourid = 0
		if 'fourid' in params: fourid = params['fourid']

		byw_params = bytewriter.bytewriter()
		for n, v in lsp_obj.params.items():
			byw_param = bytewriter.bytewriter()
			byw_param.string_t(n)
			byw_param.raw(v)
			outparam = byw_param.getvalue()
			byw_params.uint32_b(len(outparam))
			byw_params.write(outparam)

		byw_out = bytewriter.bytewriter()
		byw_out.raw(b'LSPU')
		byw_out.uint32_b(len(byw_params.getvalue()))
		byw_out.uint32_b(lsp_obj.version)
		byw_out.raw(b'LSPU')
		byw_out.raw(byw_params.getvalue())
		
		byw_stream = bytewriter.bytewriter()
		fxp_obj = preset_vst2.vst2_main()
		fxp_obj.program.type = 4
		fpch = fxp_obj.program.data = preset_vst2.vst2_fxChunkSet(None)
		fpch.fourid = fourid
		fpch.version = lsp_obj.version
		fpch.num_programs = 0
		fpch.prgname = ''
		fpch.chunk = byw_out.getvalue()

		byw_stream = bytewriter.bytewriter()
		fxp_obj.write(byw_stream)

		return byw_stream.getvalue()
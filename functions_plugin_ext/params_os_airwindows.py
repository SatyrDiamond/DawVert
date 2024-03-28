# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
import struct

class airwindows_data:
	def __init__(self):
		self.paramvals = []
		self.paramnames = []

	def to_cvpj_vst2(self, convproj_obj, plugin_obj, id, ischunk, useparams):
		if ischunk:
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', id, 'chunk', struct.pack('<'+('f'*len(self.paramvals)), *self.paramvals), None)
		else:
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id','any', id, 'param', None, len(self.paramvals))

		if useparams:
			for n, v in enumerate(self.paramvals):
				plugin_obj.params.add_named('ext_param_'+str(n), v, 'float', self.paramnames[n])

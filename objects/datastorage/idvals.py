# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import chardet

class idvals:
	def __init__(self, filename):
		self.l_params = {}
		if os.path.exists(filename):
			with open(filename, 'rb') as csvfile:
				csvdata = csvfile.read()
				csvcharset = chardet.detect(csvdata)['encoding']
				csvtext = csvdata.decode(csvcharset).splitlines()

				typecount = 0
				tid_id = None
				tid_params = {}
				for count, row_unsep in enumerate(csvtext):
					row = row_unsep.split(';')

					if count == 0:
						for valtype in row:
							if valtype == 'id': tid_id = typecount
							else: tid_params[valtype] = typecount
							typecount += 1
					else:
						self.l_params[row[tid_id]] = {}
						for tid_param in tid_params:
							out_value = row[tid_params[tid_param]]
							if tid_param == 'color_r': self.l_params[row[tid_id]][tid_param] = float(out_value)
							elif tid_param == 'color_g': self.l_params[row[tid_id]][tid_param] = float(out_value)
							elif tid_param == 'color_b': self.l_params[row[tid_id]][tid_param] = float(out_value)
							elif tid_param == 'isdrum': self.l_params[row[tid_id]][tid_param] = bool(int(out_value))
							elif tid_param == 'gm_inst':
								if out_value == 'null': self.l_params[row[tid_id]][tid_param] = None
								else: self.l_params[row[tid_id]][tid_param] = int(out_value)
							else: self.l_params[row[tid_id]][tid_param] = out_value
					count += 1

	def check_exists(self, i_id):
		return i_id in self.l_params

	def get_idval(self, i_id, i_param):
		outval = None

		if i_param == 'name':
			outval = 'noname'
			if i_id in self.l_params:
				if 'name' in self.l_params[i_id]: outval = self.l_params[i_id]['name']

		elif i_param == 'color':
			outval = None
			if i_id in self.l_params:
				self.l_params_f = self.l_params[i_id]
				if 'color_r' in self.l_params_f and 'color_g' in self.l_params_f and 'color_b' in self.l_params_f:
					outval = [self.l_params_f['color_r'], self.l_params_f['color_g'], self.l_params_f['color_b']]
		elif i_param == 'isdrum':
			outval = False
			if i_id in self.l_params:
				if 'isdrum' in self.l_params[i_id]: outval = self.l_params[i_id]['isdrum']
		elif i_param == 'gm_inst':
			outval = None
			if i_id in self.l_params:
				if 'gm_inst' in self.l_params[i_id]: outval = self.l_params[i_id]['gm_inst']
		else:
			if i_id in self.l_params:
				if i_param in self.l_params[i_id]: outval = self.l_params[i_id][i_param]
				else: outval = None

		return outval

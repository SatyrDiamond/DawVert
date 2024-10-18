# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import chardet
import numpy as np
from objects import globalstore

dt_cvpj = np.dtype([
		('paramid', np.str_, 32),
		('extid', np.str_, 32),
		('def_one', np.float64), 
		('def', np.float64), 
		('min', np.float64), 
		('max', np.float64), 
		('mathtype', np.str_, 3),
		('mathval', np.float64), 
		('visname', np.str_, 64)
		])

dt_vst2 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 16)
		])

dt_vst3 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 24)
		])

valid_ext_pnames = ['paramnum', 'visname']
valid_cvpj_pnames = ['paramid','extid','def_one','def','min','max','mathtype','mathval']

class paramremap:
	def __init__(self, filename):
		self.cvpj = np.zeros(0, dtype=dt_cvpj)
		self.vst2 = np.zeros(0, dtype=dt_vst2)
		self.vst3 = np.zeros(0, dtype=dt_vst3)
		if os.path.exists(filename):
			with open(filename, 'rb') as csvfile:
				csvdata = csvfile.read()
				csvcharset = chardet.detect(csvdata)['encoding']
				csvtext = csvdata.decode(csvcharset).splitlines()

				if len(csvtext)>2:
					self.cvpj = np.zeros(len(csvtext)-2, dtype=dt_cvpj)
					self.vst2 = np.zeros(len(csvtext)-2, dtype=dt_vst2)
					self.vst3 = np.zeros(len(csvtext)-2, dtype=dt_vst3)

					self.cvpj['min'] = 0
					self.cvpj['max'] = 1
					self.cvpj['mathtype'] = 'lin'
					self.cvpj['mathval'] = 1
					self.vst2['paramnum'] = -1
					self.vst3['paramnum'] = -1

					usedparamnames = {'cvpj': [],'vst2': [],'vst3': []}

					for count, row_unsep in enumerate(csvtext):
						splitsep = row_unsep.split(',')
						if count == 0: 
							data_exttypes = splitsep

						elif count == 1: 
							data_typenames = splitsep
							data_len = len(data_exttypes)
							for n,v in enumerate(data_typenames):
								usedparamnames[data_exttypes[n]].append(v)
						else:
							numparam = count-2
							for x in range(max(data_len, len(splitsep))):
								extname = data_exttypes[x]
								dataname = data_typenames[x]
								dataval = splitsep[x]

								if dataname in ['def_one','def','min','max']: dataval = float(dataval)
								if dataname == 'paramnum': dataval = float(dataval)
								if extname == 'cvpj': self.cvpj[numparam][dataname] = dataval
								if extname == 'vst2': self.vst2[numparam][dataname] = dataval
								if extname == 'vst3': self.vst3[numparam][dataname] = dataval

					if 'def' not in usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def'] *= mulvals
						self.cvpj['def'] += self.cvpj['min']
					elif 'def_one' not in usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def_one'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def_one'] -= self.cvpj['min']
						self.cvpj['def_one'] /= mulvals

	def cvpj_list(self):
		return list(self.cvpj['paramid'])

	def vst2_list(self):
		return list(self.vst2['paramnum'])

	def vst3_list(self):
		return list(self.vst3['paramnum'])

	def iter_cvpj_ext(self, ext_type):
		if len(self.cvpj):
			if ext_type == 'vst2':
				for n in range(len(self.cvpj)):
					yield self.cvpj[n], self.vst2[n]
			elif ext_type == 'vst3':
				for n in range(len(self.cvpj)):
					yield self.cvpj[n], self.vst3[n]
		return []

	def cvpj_to_ext(self, param_name, param_value, ext_type):
		if len(self.cvpj) and param_name in valid_cvpj_pnames:
			item_index = np.where(self.cvpj[param_name]==param_value)
			if len(item_index[0]):
				if ext_type == 'vst2':
					return 1, self.vst2['paramnum'][item_index[0]][0], self.vst2['visname'][item_index[0]][0]
				if ext_type == 'vst3':
					return 1, self.vst3['paramnum'][item_index[0]][0], self.vst3['visname'][item_index[0]][0]
			return 0, -1, ''
		return -1, -1, ''

	def ext_to_cvpj(self, param_name, param_value, ext_type):
		if len(self.cvpj) and param_name in valid_ext_pnames:
			item_index = None
			if ext_type == 'vst2':
				item_index = np.where(self.vst2[param_name]==param_value)
			if ext_type == 'vst3':
				item_index = np.where(self.vst3[param_name]==param_value)
			if not (item_index is None):
				if len(item_index[0]):
					o = self.cvpj[item_index[0]]
					return 1, o
			return 0, None
		return -1, None
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import numpy.lib.recfunctions as recfc
import math

class cursor:
	__slots__ = ['pos', 'baseobj']
	def __init__(self, baseobj):
		self.pos = -1
		self.baseobj = baseobj

	def add(self):
		self.baseobj.alloc_auto(1)
		self.baseobj.num_parts += 1
		self.pos += 1
		self.baseobj.data[self.pos]['used'] = 1

	def skip(self, num):
		self.baseobj.alloc_auto(num)
		self.baseobj.num_parts += num
		self.pos += num

	def getcur(self):
		return self.baseobj.data[self.pos]

	def __getitem__(self, x):
		return self.baseobj.data[self.pos].__getitem__(x)

	def __setitem__(self, n, x):
		return self.baseobj.data[self.pos].__setitem__(n, x)

class dynbytearr_premake:
	__slots__ = ['dtype', 'out_dtype']
	def __init__(self, dtype):
		self.dtype = dtype
		self.out_dtype = None

	def create(self):
		if self.out_dtype == None:
			self.out_dtype = np.dtype(
				[('used', np.int8)]+
				self.dtype
				)
		return dynbytearr(self.out_dtype)

class dynbytearr:
	__slots__ = ['dtype', 'alloc_size', 'data', 'cursor', 'num_parts']
	def __init__(self, dtype):
		self.dtype = dtype
		self.alloc_size = 16
		self.init_data()

	def __iter__(self):
		for i in self.data:
			if i['used']: yield i

	def __eq__(self, aps):
		return self.data[np.nonzero(self.data['used'])] == aps.data[np.nonzero(self.data['used'])]

	def __len__(self):
		return self.count()

	def clear(self):
		self.data = np.zeros(0, dtype=self.dtype)
		self.cursor = -1
		self.num_parts = 0

	def init_data(self):
		self.data = np.zeros(0, dtype=self.dtype)
		self.cursor = -1
		self.num_parts = 0

	def create_cursor(self):
		return cursor(self)

	def alloc_auto(self, num):
		newsize = self.num_parts+num
		if len(self.data) < newsize:
			self.extend(self.alloc_size)

	def alloc(self, num):
		self.data = np.zeros(num, dtype=self.dtype)
		self.cursor = -1
		self.num_parts = 0

	def extend(self, num):
		zeros = np.zeros(num, dtype=self.dtype)
		self.data = np.hstack((self.data,zeros))

	def sort(self, elements):
		nums = self.data.argsort(order=['used']+elements)
		nonzero = np.count_nonzero(self.data['used'])
		self.data[:] = np.roll(self.data[nums], nonzero)
		self.cursor = nonzero-1

	def clean(self):
		used_nums = self.used_nums()[0]
		used_len = len(used_nums)
		unused_len = len(self.data)-used_len
		self.data[0:used_len] = self.data[used_nums]
		self.data[used_len:used_len+unused_len] = 0

	def unique(self, vals):
		unique_elements, indices = np.unique(self.data[:][vals], return_index = True)
		self.data = self.data[indices]
		self.cursor = indices
		self.num_parts = indices

	def remove_minus(self, name):
		self.data = self.data[self.data[name]>=0]

	def min(self, name):
		return np.min(self.data[name]) if len(self.data) else 2147483647

	def max(self, name):
		return np.max(self.data[name]) if len(self.data) else 0

	def tobytes(self):
		return recfc.drop_fields(self.data, "used", usemask=False).tobytes()

	def count(self):
		return len(np.nonzero(self.data['used'])[0])

	def used_nums(self):
		return np.nonzero(self.data['used'])

	def unused_nums(self):
		return np.nonzero(self.data['used']!=1)

	def get_used(self):
		return self.data[self.used_nums()]

	def filter_all(self, name, val):
		return self.data[self.data[name]==val]

	def filter_all_2(self, name, val, name2, val2):
		o = np.logical_and(self.data[name]==val, self.data[name2]==val2)
		return self.data[o]

	def filter_used(self, name, val):
		uf = self.data[self.used_nums()]
		return uf[uf[name]==val]

	def count_part(self, name, val):
		return np.count_nonzero(self.data[name]==val)

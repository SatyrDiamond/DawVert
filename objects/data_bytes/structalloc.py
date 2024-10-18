import numpy as np
import numpy.lib.recfunctions as recfc
import math

class dynarray_premake:
	def __init__(self, dtype, **kwargs):
		self.dtype = dtype
		self.n_idx = kwargs['idx'] if 'idx' in kwargs else []
		self.n_idx_nodupe = kwargs['idx_nodupe'] if 'idx_nodupe' in kwargs else []
		self.out_dtype = None

	def create(self):
		if self.out_dtype == None:
			self.out_dtype = np.dtype(
				[('used', np.int8)]+
				self.dtype+
				[('is_'+x, np.int8) for x in self.n_idx_nodupe]+
				[('is_'+x, np.int8) for x in self.n_idx]+
				[(x, np.int32) for x in self.n_idx_nodupe]+
				[(x, np.int32) for x in self.n_idx]
				)
		da_obj = dynarray_data(self.out_dtype, self.n_idx, self.n_idx_nodupe)
		return da_obj

class dynarray_data:
	def __init__(self, dtype, n_idx, n_idx_nodupe):
		self.dtype = dtype
		self.alloc_size = 16

		self.n_idx = n_idx
		self.n_idx_nodupe = n_idx_nodupe
		self.init_data()

	def __getitem__(self, x):
		return self.data[self.cursor].__getitem__(x)

	def __setitem__(self, n, x):
		return self.data[self.cursor].__setitem__(n, x)

	def __iter__(self):
		for i in self.data:
			if i['used']: yield i

	def __eq__(self, aps):
		return self.data[np.nonzero(self.data['used'])] == aps.data[np.nonzero(self.data['used'])]

	def init_data(self):
		self.data = np.zeros(0, dtype=self.dtype)
		self.cursor = -1
		self.num_parts = 0

		self.v_idx = [[] for x in self.n_idx]
		self.v_idx_nodupe = [[] for x in self.n_idx_nodupe]

	def alloc_auto(self, num):
		newsize = self.num_parts+num
		if len(self.data) < newsize: self.extend(self.alloc_size)

	def alloc(self, num):
		self.data = np.zeros(num, dtype=self.dtype)
		self.cursor = -1
		self.num_parts = 0

	def unique(self, vals):
		unique_elements, indices = np.unique(self.data[:][vals], return_index = True)
		self.data = self.data[indices]
		self.cursor = indices
		self.num_parts = indices

	def extend(self, num):
		zeros = np.zeros(num, dtype=self.dtype)
		self.data = np.hstack((self.data,zeros))

	def sort(self, elements):
		nums = self.data.argsort(order=['used']+elements)
		nonzero = np.count_nonzero(self.data['used'])
		self.data = np.roll(self.data[nums], nonzero)
		self.num_notes = nonzero
		self.cursor = nonzero-1

	def idx_d_set(self, name, value):
		idx_l = self.v_idx[self.n_idx.index(name)]
		if value in idx_l: 
			return idx_l.index(value)
		else:
			idx_l.append(value)
			return len(idx_l)-1

	def idx_nd_set(self, name, value):
		idx_l = self.v_idx_nodupe[self.n_idx_nodupe.index(name)]
		outval = len(idx_l)
		idx_l.append(value)
		return outval

	def idx_d_get(self, name, value):
		return self.v_idx[self.n_idx.index(name)][value]

	def idx_nd_get(self, name, value):
		return self.v_idx[self.n_idx_nodupe.index(name)][value]

	def clean(self):
		self.data = self.data[np.nonzero(self.data['used'])]

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

	def fill_array_name(self, name, nparray):
		self.data['complete'][0:len(nparray)] = 1
		self.data[name][0:len(nparray)] = nparray

	def add(self):
		self.alloc_auto(1)
		self.cursor += 1
		self.data[self.cursor]['used'] = 1
		self.num_parts += 1

	def assoc_nd_add(self, name, value):
		self.data[self.cursor]['is_'+name] = 1
		self.data[self.cursor][name] = self.idx_nd_set(name, value)

	def assoc_d_add(self, name, value):
		self.data[self.cursor]['is_'+name] = 1
		self.data[self.cursor][name] = self.idx_d_set(name, value)

	def used_nums(self):
		return np.nonzero(self.data['used'])

	def unused_nums(self):
		return np.nonzero(self.data['used']!=1)

	def get_used(self):
		return self.data[self.used_nums()]

	def find_nearest_name(self, value, name):
		temptable = self.data[name]
		idx = np.searchsorted(temptable, value, side="left")
		if idx > 0 and (idx == len(temptable) or math.fabs(value - temptable[idx-1]) < math.fabs(value - temptable[idx])):
			return idx-1
		else:
			return idx

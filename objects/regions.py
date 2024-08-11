# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np

class regions:
	dtype = [
	('used', np.int16),
	('start', np.int16),
	('end', np.int16),
	]

	def __init__(self, size):
		self.data = np.zeros(size, dtype=regions.dtype)
		self.cursor = 0

	def __iter__(self):
		for u,s,e in self.data:
			if u: yield s, e

	def add(self, i_min, i_max):
		self.data[self.cursor][0] = 1
		self.data[self.cursor][1] = i_min
		self.data[self.cursor][2] = i_max
		self.cursor += 1

	def from_boollist(self, boollist):
		poslist = []
		for c, v in enumerate(boollist):
			if v: poslist.append(c)

		self.cursor = 0
		prev_val = -2
		for v in poslist:
			if prev_val != v-1: self.add(v, v)
			else: self.data[self.cursor-1][2] += 1
			prev_val = v


	def chop(self, pos):
		founds = np.where(np.logical_and(pos>=self.data['start'], pos<=self.data['end'], self.data['used']==1))[0]

		if len(founds):
			foundidx = founds[0]
			old_start = self.data['start'][foundidx]
			old_end = self.data['end'][foundidx]

			self.data['start'][foundidx] = old_start
			self.data['end'][foundidx] = pos-1
			self.add(pos, old_end)

	def sort(self):
		nums = self.data.argsort(order=['used', 'start'])
		nonzero = np.count_nonzero(self.data['used'])
		self.data = np.roll(self.data[nums], nonzero)
		self.cursor = nonzero-1


	def out_txt(self, sep):
		size = len(np.nonzero(self.data['used']))

		txttab = [[' ']*sep for x in range(np.max(self.data['end'])+1)]
		for u,s,e in self.data:
			if u:
				for v in range(s,e+1): txttab[v] = ['-']*sep
				txttab[s][0] = '['
				txttab[e][-1] = ']'

		return '|'.join([''.join(x) for x in txttab])

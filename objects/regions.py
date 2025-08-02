# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from functions import xtramath

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

class posdurblocks:
	dtype = [
	('steps', np.int16),
	('tempo', float),
	('notemul', float),
	('start', np.int16),
	('end', np.int16),
	]

	def __init__(self, size, steps, tempo):
		self.processed = False
		self.loop_start = 0
		self.loop_end = 0
		self.data = np.zeros(size, dtype=posdurblocks.dtype)
		self.steps = steps
		self.tempo = tempo
		self.data['steps'][:] = steps
		self.data['notemul'][:] = 1
		self.data['tempo'][0] = tempo

	def __getitem__(self, v):
		return self.data.__getitem__(v)

	def proc(self):
		curpos = 0
		for x in self.data:
			x['start'] = curpos
			curpos += x['steps']
			x['end'] = curpos

	def set_steps(self, pos, steps):
		self.data['steps'][pos] = steps

	def set_tempo(self, pos, tempo):
		self.data['tempo'][pos] = tempo

	def set_notemul(self, pos, notemul):
		self.data['notemul'][pos] = notemul

	def get_posdur(self, p):
		p_start = float(self.data[p]['start'])
		p_steps = float(self.data[p]['steps'])
		return p_start, p_steps

	def to_cvpj(self, cvpj_obj):
		auto_bpm_obj = cvpj_obj.automation.create(['main','bpm'], 'float', True)

		cvpj_obj.params.add('bpm', self.tempo, 'float')
		
		prevtempo = 0
		cur_tempo = self.tempo

		ppq = cvpj_obj.time_ppq

		for n, x in enumerate(self.data):
			new_tempo = float(x['tempo'])
			cur_tempo = new_tempo if new_tempo else self.tempo
			if cur_tempo != prevtempo:
				pos = (float(x['start'])/4) * ppq
				dur = (float(x['steps'])/4) * ppq
				auto_bpm_obj.add_all(pos, cur_tempo, dur)
			prevtempo = cur_tempo

		temptimesig = xtramath.get_timesig(self.steps, cvpj_obj.timesig[1])
		cvpj_obj.add_timesig_lengthbeat(temptimesig[0], temptimesig[1])

		prevtimesig = cvpj_obj.timesig
		for n, x in enumerate(self.data):
			temptimesig = xtramath.get_timesig(int(x['steps']), cvpj_obj.timesig[1])
			curpos = (int(x['start'])/4) * ppq

			if prevtimesig != temptimesig: 
				outtimesig = temptimesig.copy()
				if not outtimesig[0]%outtimesig[1]: outtimesig[0] = outtimesig[1]
				cvpj_obj.timesig_auto.add_point(curpos, outtimesig)
			if self.loop_start == n: cvpj_obj.loop_start = curpos
			prevtimesig = temptimesig
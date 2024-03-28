# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects_convproj import notelist
from objects_convproj import placements_notes
from objects import regions
import bisect
import math
import difflib

class cvpj_splittrack:
	def __init__(self, splitpos, placements_obj):
		self.placements_obj = placements_obj
		self.notelist = self.placements_obj.notelist
		self.splitted_nl = [[] for _ in range(len(splitpos))]

		self.debugprint_size = 4
		self.debugprint_hsize = 10

		self.notelist.sort()
		for n in self.notelist.iter():
			numsplit = bisect.bisect_right(splitpos, n[0])-1
			if self.splitted_nl[numsplit]:
				p = self.splitted_nl[numsplit][-1]
				cn = n[0], n[1], n[3], n[4], n[5], n[6], n[7]
				pn = p[0], p[1], p[3], p[4], p[5], p[6], p[7]
				if cn == pn: p[2] += n[2]
				else: self.splitted_nl[numsplit].append(list(n))
			else: self.splitted_nl[numsplit].append(list(n))

		self.notelist.clear()

	def step_overflow(self, splitranges):
		self.overflow = []
		self.overflow_lo = []
		self.is_merged = []

		for c, x in enumerate(splitranges):
			spl_obj = self.splitted_nl[c]
			if spl_obj:
				note_end = max([x[0]+x[1] for x in spl_obj])
				self.overflow.append(max(0, note_end-x[1]))
			else: self.overflow.append(0)
			self.is_merged.append(False)
			self.overflow_lo.append(0)

		for c, sn in enumerate(self.splitted_nl):
			for x in sn:  x[0] -= splitranges[c][0]

		for c, r in enumerate(splitranges):
			reg_start, reg_end = r
			p_spl = self.splitted_nl[c]
			p_of = self.overflow[c]

			if p_of:
				t_of = p_of
				t_p = c
				while max(0, t_of):
					r_start, r_end = splitranges[t_p]
					t_of -= r_end-r_start
					t_p += 1
					self.overflow_lo[t_p] = max(0, self.overflow_lo[t_p], t_of)
					self.is_merged[t_p] = True

		self.overflow = [max(x, self.overflow_lo[c]) for c, x in enumerate(self.overflow)]

	def print(self):
		print('N'.ljust(self.debugprint_hsize)+'|', end='')
		for x in self.splitted_nl: print((str(len(x)).rjust(self.debugprint_size) if x != -1 else self.debugprint_size*' ')+'|', end='')
		print('')

		print('OF'.ljust(self.debugprint_hsize)+'|', end='')
		for x in self.overflow: print((str(x).rjust(self.debugprint_size) if x != -1 else self.debugprint_size*' ')+'|', end='')
		print('')

		print('MERGE'.ljust(self.debugprint_hsize)+'|', end='')
		for x in self.is_merged: print((str(int(x)).rjust(self.debugprint_size) if x != -1 else self.debugprint_size*' ')+'|', end='')
		print('')

		print('')

	def to_placements(self, splitranges):
		pof = False
		for c, p in enumerate(splitranges):
			nl = self.splitted_nl[c]
			if nl or pof:
				if not pof:
					endpos = p[1]-p[0]
					placement_obj = self.placements_obj.add_notes()
					placement_obj.position = p[0]
					placement_obj.duration = endpos
					placement_obj.notelist.nl = nl
				else:
					for n in nl: n[0] += endpos
					placement_obj.duration += p[1]-p[0]
					placement_obj.notelist.nl += nl
					endpos += p[1]-p[0]

			pof = self.overflow[c]
			#print(x, x[1]-x[0], is_merged, len(spl_obj))
		#exit()

class cvpj_notelist_splitter:
	def __init__(self, splitpoints, splitts, ppq, mode):
		self.data = []
		self.ppq = ppq

		self.splitts = splitts
		self.splittsp = [int(x/self.ppq) for x in self.splitts]
		self.numpoints = len(splitpoints)
		self.splitranges = [[splitpoints[x], splitpoints[x+1]] for x in range(self.numpoints-1)]
		self.splitpos = [x[0] for x in self.splitranges]
		self.durations = [x[1]-x[0] for x in self.splitranges]
		self.durbeat = [x/(ppq/4) for x in self.durations]

	def add_nl(self, placements_obj):
		trkdata = cvpj_splittrack(self.splitpos, placements_obj)

		#trkdata['split_nl'] = s_spl
		#trkdata['pat_data'] = []
		#trkdata['pat_similar'] = []
		#trkdata['pat_num'] = []
		#trkdata['pat_parts'] = []
		#trkdata['pat_startend'] = []
		#trkdata['parts'] = []
		#trkdata['overflow'] = []
		#trkdata['used'] = []

		self.data.append(trkdata)

	def process(self):
		for trk_obj in self.data:
			trk_obj.step_overflow(self.splitranges)
			#trk_obj.print()
			trk_obj.to_placements(self.splitranges)




		#print(self.splitpos)
		#print(self.splitranges)

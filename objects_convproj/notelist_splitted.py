# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects_convproj import notelist
from objects_convproj import placements_notes

class cvpj_notelist_splitted:
	def __init__(self):
		self.splnl = []
		self.time_ppq = 1
		self.time_float = False

	def do_split(self, splitpoints, nl, offset):
		#pos, dur, notelist, is_used, overflow, marked_overflow
		nl_dur = nl.get_dur()
		self.time_ppq = nl.time_ppq
		self.time_float = nl.time_float
		old_splnl = self.splnl.copy()
		self.splnl = []
		for x in range(len(splitpoints)-1): self.splnl.append([splitpoints[x], splitpoints[x+1], [], False, 0, False])

		cur_part = 0
		for n in nl.nl.copy():
			n[0] += offset
			while self.splnl[cur_part][0] <= n[0] and cur_part < len(self.splnl)-1: cur_part += 1
			spl_data = self.splnl[cur_part-1]
			spl_data[2].append(n)
			spl_data[3] = True
			nt = n[0]+n[1]-spl_data[1]
			if nt > spl_data[4]: 
				spl_data[4] = nt
				spl_data[5] = True
			n[0] -= spl_data[0]

		remaining_len = 0
		for c, x in enumerate(self.splnl):
			remaining_len += x[4]
			x[4] = remaining_len
			if remaining_len: x[5] = True
			remaining_len = max(0, remaining_len-(x[1]-x[0]))

	def to_pl(self, placements_obj):
		n_pl = []
		curpos = 0
		extend = False
		for c, x in enumerate(self.splnl):
			if n_pl and extend:
				n_pl[-1][1] = x[1]
				curpos += x[1]-x[0]
				extend = False
			elif x[3]:
				n_pl.append([x[0], x[1], []])
				curpos = 0

			for n in x[2]:
				n[0] += curpos
				n_pl[-1][2].append(n)
			extend = x[5]
		
		placements_obj.pl_notes.data = []
		for x in n_pl:
			placement_obj = placements_notes.cvpj_placement_notes(self.time_ppq, self.time_float)
			placement_obj.position = x[0]
			placement_obj.duration = x[1]-x[0]
			placement_obj.notelist.nl = x[2]
			placements_obj.pl_notes.data.append(placement_obj)


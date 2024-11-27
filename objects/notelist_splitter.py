# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import regions
import numpy as np
from functions import xtramath

class timesigblocks:
	def __init__(self):
		self.splitpoints = []
		self.splitts = []
		self.timesigposs = []

	def create_points_cut(self, convproj_obj, dawvert_intent):
		self.timesigposs = []

		mode = dawvert_intent.splitter_mode if dawvert_intent else 0
		detect_start = dawvert_intent.splitter_detect_start if dawvert_intent else False

		ppq = convproj_obj.time_ppq
		songduration = convproj_obj.get_dur()+ppq

		timesig_num, timesig_dem = convproj_obj.timesig

		if detect_start:
			startpos = convproj_obj.loop_start if convproj_obj.loop_start else 0
			if not startpos: startpos = convproj_obj.start_pos if convproj_obj.start_pos else 0
			outstart = startpos if mode in [1] else 0
		else:
			outstart = 0

		ts_parts = [x for x in convproj_obj.timesig_auto]

		if not ts_parts: 
			if mode == 1: self.endsplit(songduration, timesig_num*timesig_dem*ppq, outstart)
			else: self.endsplit(songduration, timesig_num*ppq, outstart)
		else:
			if len(ts_parts)>1: 
				self.timesig(songduration, ts_parts, ppq, timesig_num, timesig_dem, outstart, mode)
			else: 
				pos, timesig = ts_parts[0]
				self.timesig(songduration, ts_parts, ppq, timesig[0], timesig[1], outstart, mode)

	def timesig(self, endpos, ts, ppq, timesig_num, timesig_dem, startpos, mode):
		if mode == 1: 
			tcalc = timesig_num*timesig_dem
			startd = startpos%(ppq*tcalc)
		else: 
			tcalc = timesig_num
			startd = startpos%ppq

		self.timesigposs = [[0, tcalc*ppq]]
		for p, v in ts: 
			if mode == 1: tscalc = timesig_num*timesig_dem
			else: tscalc = timesig_num
			self.timesigposs.append([startd+p, tscalc*ppq])
		self.timesigposs += [[endpos, tcalc*ppq]]
		self.process()

	def endsplit(self, endpos, splitdur, startpos):
		startd = startpos%(splitdur)
		if startd != 0: self.timesigposs = [[0, splitdur], [startd, splitdur], [endpos, None]]
		else: self.timesigposs = [[startd, splitdur], [endpos, None]]
		self.process()

	def process(self):
		self.splitpoints = []
		self.splitts = []

		timesigblocks = []
		for timesigposnum in range(len(self.timesigposs)-1):
			timesigpos = self.timesigposs[timesigposnum]
			timesigblocks.append([timesigpos[0], self.timesigposs[timesigposnum+1][0], timesigpos[1]])

		p_splitts = {}
		for t in timesigblocks:
			if t[0] not in self.splitpoints: self.splitpoints.append(t[0])
			p_splitts[t[0]] = t[2]
			curpos = t[0]
			for x in xtramath.gen_float_blocks(t[1]-t[0],t[2]):
				curpos += x
				p_splitts[curpos] = t[2]
				if int(curpos) not in p_splitts: p_splitts[int(curpos)] = t[2]
				if curpos not in self.splitpoints: self.splitpoints.append(curpos)

		self.splitpoints = np.array(self.splitpoints, dtype=np.uint32) 
		self.splitts = np.array([p_splitts[x] for x in self.splitpoints], dtype=np.uint32) 
		self.splitts[0:-1] = self.splitpoints[1:]-self.splitpoints[0:-1]

		if False:
			print(self.timesigposs)
			print(self.splitpoints)
			#print(self.splitpoints[1:]-self.splitpoints[0:-1])
			print(self.splitts)

		if False:
			import matplotlib.pyplot as plt
			import matplotlib
			matplotlib.interactive(True)
			plt.scatter(self.splitpoints, [0 for x in self.splitpoints])
			plt.scatter([0,songduration], [0.3,0.3])
			plt.scatter([x[0] for x in self.timesigposs], [0.1 for x in self.timesigposs])
			plt.scatter([1,1], [-1,1])
			plt.show(block=True)


splitterdt = np.dtype([
		('start', np.float64),
		('end', np.float64),
		('dur', np.float64),
		('numer', np.uint8),

		('used', np.uint8),
		('nosplit', np.uint8),
		('overflow', np.float64),
		('remaining', np.float64),
		]) 

class cvpj_splittrack:
	def __init__(self, splitdata, i_pl):
		self.splitdata = splitdata.copy()
		self.i_pl = i_pl
		self.i_notelist = self.i_pl.notelist

	def step_overflow(self):
		for splitd in self.splitdata:
			splitd['used'], splitd['overflow'] = self.i_notelist.usedoverflow(splitd['start'], splitd['end'])

		remainval = 0
		for splitd in self.splitdata:
			splitd['remaining'] = remainval
			if remainval: splitd['used'] = 1
			remainval = max(remainval-splitd['dur'], 0)
			remainval += splitd['overflow']
			splitd['nosplit'] = 1+(remainval!=0) if splitd['used'] else 0

	def to_placements(self):
		slicenums = [[None, None]]

		sregions = regions.regions(len(self.splitdata))
		sregions.from_boollist(self.splitdata['used'])

		chopnums = np.where(self.splitdata['nosplit']==1)[0]
		for chopnum in chopnums: sregions.chop(chopnum+1)
		sregions.sort()

		for start, end, numer in [(self.splitdata['start'][s], self.splitdata['end'][e], self.splitdata['numer'][e]) for s,e in sregions]:
			#print(start, end, numer)
			placement_obj = self.i_pl.add_notes()
			placement_obj.time.set_startend(start, end)
			placement_obj.notelist = self.i_notelist.new_nl_start_end(start, end)
		self.i_notelist.clear()

class cvpj_notelist_splitter:
	def __init__(self, timesigblocks_obj, ppq, mode):
		self.data = []
		self.ppq = ppq

		self.splitdata = np.zeros(len(timesigblocks_obj.splitpoints), dtype=splitterdt)
		self.splitdata['start'] = timesigblocks_obj.splitpoints
		self.splitdata['end'] = self.splitdata['start']+timesigblocks_obj.splitts
		self.splitdata['dur'] = timesigblocks_obj.splitts
		self.splitdata['numer'] = self.splitdata['dur']/self.ppq

	def add_nl(self, i_pl):
		trkdata = cvpj_splittrack(self.splitdata.copy(), i_pl)
		self.data.append(trkdata)

	def process(self):
		for trk_obj in self.data:
			trk_obj.step_overflow()
			trk_obj.to_placements()

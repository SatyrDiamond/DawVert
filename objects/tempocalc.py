# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
from functions import xtramath
import numpy as np

tempotickblocks_premake = dynbytearr.dynbytearr_premake([
	('orgt_pos_start', np.float64), 
	('orgt_pos_end', np.float64), 
	('orgt_dur', np.float64), 

	('beats_pos_start', np.float64), 
	('beats_pos_end', np.float64), 
	('beats_dur', np.float64), 

	('sec_pos_start', np.float64), 
	('sec_pos_end', np.float64), 
	('sec_dur', np.float64), 

	('tempo_start', np.float64),  
	('tempo_end', np.float64),  
	('diff', np.float64),  
	])

global_stores = {}

def add_region(tb_cur, is_seconds, pos_start, pos_end, value_start, value_end):
	tb_cur.add()
	if not is_seconds:
		tb_cur['orgt_pos_start'] = pos_start
		tb_cur['orgt_pos_end'] = pos_end
		tb_cur['orgt_dur'] = pos_end-pos_start
	else:
		tb_cur['sec_pos_start'] = pos_start
		tb_cur['sec_pos_end'] = pos_end
		tb_cur['sec_dur'] = pos_end-pos_start
	tb_cur['tempo_start'] = value_start
	tb_cur['tempo_end'] = value_end
	tb_cur['diff'] = value_end-value_start

class tempocalc_store:
	def __init__(self, convproj_obj):
		self.store = None
		self.auto_found = -1
		self.tempo = 120
		self.use_stored = -2
		self.source_seconds = False
		self.convproj_obj = convproj_obj

	def get_tempo(self, pos, is_seconds):
		if self.use_stored>=0 and len(self.store):
			if is_seconds: 
				source_pos = np.round(self.store['sec_pos_start'], 2)
				pos = np.round(pos, 2)
			else: source_pos = self.store['beats_pos_start']
			tempo_start = self.store['tempo_start']
			tempo_end = self.store['tempo_end']
			lenv = len(source_pos)-1
			bisval = np.searchsorted(source_pos, pos, side='right')-1
			#print(pos, source_pos[bisval], end=' ')
			if -1<bisval<lenv:
				val = xtramath.between_to_one(source_pos[bisval], source_pos[bisval+1], pos)
				return xtramath.between_from_one(tempo_start[bisval], tempo_end[bisval], val)
			elif bisval>=lenv:
				return tempo_end[-1]
			else:
				return self.tempo
		else:
			return self.tempo

	def get_pos(self, pos, is_seconds):
		if self.use_stored>0:
			if is_seconds:
				source_pos = self.store['beats_pos_start']
				target_pos = self.store['sec_pos_start']
			else:
				source_pos = self.store['sec_pos_start']
				target_pos = self.store['beats_pos_start']
			lenv = len(source_pos)-1
			bisval = np.searchsorted(source_pos, pos, side='right')-1
			if -1<bisval<lenv:
				val = xtramath.between_to_one(source_pos[bisval], source_pos[bisval+1], pos)
				val = xtramath.between_from_one(target_pos[bisval], target_pos[bisval+1], val)
				return val
			elif bisval>=lenv:
				lastval = source_pos[-1]
				lasto = target_pos[-1]
				last_tempo = self.store['tempo_start'][-1]
				if is_seconds:
					return lasto + ((pos-lastval)*(120/last_tempo))/2
				else:
					return lasto + ((pos-lastval)*(last_tempo/120))*2

		if is_seconds:
			return xtramath.step2sec(pos*4, self.tempo)
		else:
			return xtramath.sec2step(pos, self.tempo)/4

	def proc_points(self):
		convproj_obj = self.convproj_obj

		if self.store is None:
			self.tempo = convproj_obj.params.get('bpm', 120).value

			tempo_auto = convproj_obj.automation.get_opt(['main', 'bpm'])
			self.store = tempotickblocks_premake.create() 
			tb_cur = self.store.create_cursor()

			if self.auto_found==-1:
				if tempo_auto is not None:
					self.source_seconds = tempo_auto.is_seconds

					if tempo_auto.u_pl_ticks or tempo_auto.u_nopl_ticks:
						if not tempo_auto.u_nopl_ticks: tempo_auto.convert____pl_ticks___nopl_ticks()
	
						ticksdata = [x for x in tempo_auto.nopl_ticks]
						if len(ticksdata):
							self.auto_found = 1
							lent = len(ticksdata)
							for n in range(lent-1):
								d_cur = ticksdata[n]
								d_next = ticksdata[n+1]
								tb_cur.add()
								if not tempo_auto.is_seconds:
									tb_cur['orgt_pos_start'] = d_cur[0]
									tb_cur['orgt_pos_end'] = d_next[0]
									tb_cur['orgt_dur'] = d_next[0]-d_cur[0]
								else:
									tb_cur['sec_pos_start'] = d_cur[0]
									tb_cur['sec_pos_end'] = d_next[0]
									tb_cur['sec_dur'] = d_next[0]-d_cur[0]
								tb_cur['tempo_start'] = d_cur[1]
								tb_cur['tempo_end'] = d_cur[1]
								tb_cur['diff'] = 0
							if lent:
								d_cur = ticksdata[-1]
								tb_cur.add()
								if not tempo_auto.is_seconds:
									tb_cur['orgt_pos_start'] = d_cur[0]
									tb_cur['orgt_pos_end'] = d_cur[0]
									tb_cur['orgt_dur'] = -1
								else:
									tb_cur['sec_pos_start'] = d_cur[0]
									tb_cur['sec_pos_end'] = d_cur[0]
									tb_cur['sec_dur'] = -1
								tb_cur['tempo_start'] = d_cur[1]
								tb_cur['tempo_end'] = d_cur[1]
								tb_cur['diff'] = 0
	
	
					elif tempo_auto.u_pl_points or tempo_auto.u_nopl_points:
						if not tempo_auto.u_nopl_points: tempo_auto.convert____pl_points__nopl_points()
						temporegions = tempo_auto.nopl_points.to_regions()
						if len(temporegions):
							self.auto_found = 1
							for temporegion in temporegions:
								add_region(tb_cur, tempo_auto.is_seconds, 
									temporegion['pos_start'], temporegion['pos_end'], temporegion['value_start'], temporegion['value_end']
									)
		
							if len(tempo_auto.nopl_points):
								lastpoint = tempo_auto.nopl_points.get_last()
								add_region(tb_cur, tempo_auto.is_seconds, 
									lastpoint['pos'], lastpoint['pos'], lastpoint['value'], lastpoint['value']
									)
						else:
							self.auto_found = 0
					else:
						self.auto_found = 0
				else:
					self.auto_found = 0
			else:
				self.auto_found = 0

			if len(self.store):
				useddata = self.store.get_used()

				if not self.source_seconds:
					if 0 not in useddata['orgt_pos_start']:
						tb_cur.add()
						tb_cur['orgt_pos_start'] = 0
						tb_cur['orgt_pos_end'] = useddata[0]['orgt_pos_start']
						tb_cur['orgt_dur'] = tb_cur['sec_pos_start']
						tb_cur['tempo_start'] = useddata[0]['tempo_start']
						tb_cur['tempo_end'] = tb_cur['tempo_start']
					self.store.sort(['orgt_pos_start'])
	
					self.store.data['beats_pos_start'] = self.store.data['orgt_pos_start']/convproj_obj.time_ppq
					self.store.data['beats_pos_end'] = self.store.data['orgt_pos_end']/convproj_obj.time_ppq
					self.store.data['beats_dur'] = self.store.data['orgt_dur']/convproj_obj.time_ppq
				else:
					if 0 not in useddata['sec_pos_start']:
						tb_cur.add()
						tb_cur['sec_pos_start'] = 0
						tb_cur['sec_pos_end'] = useddata[0]['sec_pos_start']
						tb_cur['sec_dur'] = tb_cur['sec_pos_start']
						tb_cur['tempo_start'] = useddata[0]['tempo_start']
						tb_cur['tempo_end'] = tb_cur['tempo_start']
					self.store.sort(['sec_pos_start'])

				if np.all(tb_cur['diff']==0):
					self.use_stored = 1
					if not self.source_seconds:
						curpos = 0
						for x in  self.store:
							dur = x['beats_dur']/(x['tempo_start']/120)/2
							x['sec_pos_start'] = curpos
							curpos += dur
							x['sec_pos_end'] = curpos
							x['sec_dur'] = dur
					else:
						curpos = 0
						for x in  self.store:
							dur = x['sec_dur']*(x['tempo_start']/120)*2
							x['beats_pos_start'] = curpos
							curpos += dur
							x['beats_pos_end'] = curpos
							x['beats_dur'] = dur
				else:
					self.use_stored = 1

			self.store = self.store.get_used()
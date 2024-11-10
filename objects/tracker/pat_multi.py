# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
from functions import xtramath
from objects.tracker import notestream
from objects.tracker import pat_data

class multi_patsong:
	def __init__(self):
		self.num_chans = 0
		self.num_rows = 0
		self.dataset_name = None
		self.dataset_cat = None
		self.channels = []
		self.patdata = {}
		self.orders = []

	def add_channel(self, insttype):
		chan_obj = pat_data.tracker_channel()
		chan_obj.insttype = insttype
		self.channels.append(chan_obj)
		self.orders.append([])
		self.num_chans += 1
		return chan_obj

	def get_channel_insttype(self, channum):
		return self.channels[channum].insttype

	def get_data(self, chan_num, pat_num):
		if chan_num in self.patdata: 
			if pat_num in self.patdata[chan_num]: 
				return self.patdata[chan_num][pat_num]

	def pattern_add(self, chan_num, pat_num):
		pat_obj = pat_data.tracker_column()
		if chan_num not in self.patdata: self.patdata[chan_num] = {}
		self.patdata[chan_num][pat_num] = pat_obj
		return pat_obj

	def to_cvpj(self, convproj_obj, s_bpm, s_speed):
		convproj_obj.type = 'm'

		playstr = pat_data.playstream()
		playstr.init_tempo(s_bpm, s_speed)

		initbpm = playstr.cur_tempo.get_speed()

		e_tempo, e_notelen = xtramath.get_lower_tempo(initbpm, 1, 190)

		convproj_obj.set_timings(4*(1/e_notelen), True)

		maxorder = max([len(x) for x in self.orders])

		orderdata = np.zeros([maxorder, self.num_chans], dtype=np.uint8)
		for n in range(self.num_chans):
			orderdata[:, n] = self.orders[n]

		for n, x in enumerate(self.channels):
			playstr.add_channel(x.insttype+'_'+str(n)+'_')

		for patnum, n in enumerate(orderdata):
			playstr.init_patinfo(self.num_rows, patnum)
			playstr.columns = [self.get_data(c, x) for c, x in enumerate(n)]
			while playstr.next_row(): pass

		convproj_obj.params.add('bpm', e_tempo, 'float')
		playstr.auto_tempo.to_cvpj(convproj_obj, ['main','bpm'])

		for chns in playstr.notestreams: chns.add_pl(-1)

		used_inst = {}

		for ch_num, chan_obj in enumerate(self.channels):
			playlist_obj = convproj_obj.playlist__add(ch_num, True, False)
			if chan_obj.name: playlist_obj.visual.name = chan_obj.name
			if chan_obj.color: playlist_obj.visual.color.set_float(chan_obj.color)

			fxchannel_obj = convproj_obj.fx__chan__add(ch_num+1)
			if self.dataset_name and self.dataset_cat:
				fxchannel_obj.visual.from_dset(self.dataset_name, self.dataset_cat, chan_obj.insttype, True)
				playlist_obj.visual.from_dset(self.dataset_name, self.dataset_cat, chan_obj.insttype, False)

			cur_pl_pos = 0
			for tpl in playstr.notestreams[ch_num].placements:
				if tpl[0]:
					for ui in tpl[3]:
						if chan_obj.insttype not in used_inst: 
							used_inst[chan_obj.insttype] = []
						chinst = [ui, ch_num]
						if chinst not in used_inst[chan_obj.insttype]: 
							used_inst[chan_obj.insttype].append(chinst)

					if tpl[1].notesfound():
						tpl[1].stretch(4/(1/e_notelen), True)
						tpl[1].notemod_conv()
						placement_obj = playlist_obj.placements.add_notes()
						placement_obj.time.set_posdur(cur_pl_pos, tpl[0])
						placement_obj.notelist = tpl[1]
				cur_pl_pos += tpl[0]

		patlentable = [x[0] for x in playstr.notestreams[0].placements]
		convproj_obj.timemarker__from_patlenlist(patlentable[:-1], -1)

		return used_inst
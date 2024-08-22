# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc

dtype_usedfx = [
	('reverb', np.uint8),
	('tremolo', np.uint8),
	('chorus', np.uint8),
	('detune', np.uint8),
	('phaser', np.uint8)
	]

chanauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('control', np.uint8),
	('value', np.uint8),
	('smooth', np.uint8)
	])

class midi_cc_auto_multi:
	def __init__(self, numchannels):
		self.data = chanauto_premake.create()
		self.song_channels = numchannels
		self.auto_seperated = [[] for x in range(numchannels)]
		self.used_cc_chans = [[] for x in range(numchannels)]

		self.fx_used_chans = np.zeros(numchannels, dtype=dtype_usedfx)
		self.fx_used = np.zeros(1, dtype=dtype_usedfx)
		self.start_vals = np.zeros(shape=(numchannels, 128), dtype=np.int8)
		self.start_vals[:] = -1

	def add_point(self, curpos, controller, value, smooth, channel):
		ctrlchan = self.data
		ctrlchan.add()
		ctrlchan['pos'] = curpos
		ctrlchan['channel'] = channel
		ctrlchan['control'] = controller
		ctrlchan['value'] = value
		ctrlchan['smooth'] = smooth

	def filter(self, channel, control):
		sepchan = self.auto_seperated[channel]
		return sepchan[sepchan['control']==control]

	def postprocess(self):
		self.data.sort(['pos'])
		self.data.clean()
		if len(self.data.data):
			a_used = self.data.data['used']
			a_data = self.data.data['channel']
			self.auto_seperated = [self.data.data[np.where(np.logical_and(a_used==1, a_data==x))] for x in range(self.song_channels)]
			self.used_cc_chans = [np.unique(self.auto_seperated[x]['control']) for x in range(self.song_channels)]

			self.fx_used_chans['reverb'] = [(91 in x) for x in self.used_cc_chans]
			self.fx_used_chans['tremolo'] = [(92 in x) for x in self.used_cc_chans]
			self.fx_used_chans['chorus'] = [(93 in x) for x in self.used_cc_chans]
			self.fx_used_chans['detune'] = [(94 in x) for x in self.used_cc_chans]
			self.fx_used_chans['phaser'] = [(95 in x) for x in self.used_cc_chans]

			self.fx_used['reverb'] = self.fx_used_chans['reverb'].sum()
			self.fx_used['tremolo'] = self.fx_used_chans['tremolo'].sum()
			self.fx_used['chorus'] = self.fx_used_chans['chorus'].sum()
			self.fx_used['detune'] = self.fx_used_chans['detune'].sum()
			self.fx_used['phaser'] = self.fx_used_chans['phaser'].sum()

	def calc_startpos(self, startpos_chans):
		for channum, ctrlnum, autodata in self.iter():
			acp = autodata[np.where(autodata['pos']<=startpos_chans[channum])]
			if len(acp)!=0: self.start_vals[channum][ctrlnum] = acp['value'][-1]

	def iter(self):
		for channum, chandata in enumerate(self.used_cc_chans):
			for ctrlnum in chandata:
				yield channum, ctrlnum, self.filter(channum, ctrlnum)

	def iter_initval(self):
		for channum, chandata in enumerate(self.used_cc_chans):
			for ctrlnum in chandata:
				yield channum, ctrlnum, self.start_vals[channum][ctrlnum], self.filter(channum, ctrlnum)


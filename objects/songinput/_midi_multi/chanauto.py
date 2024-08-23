# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc

pitchauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('value', np.int16),
	('mode', np.int16)]
	)

class midi_pitch_auto_multi:
	def __init__(self, numchannels):
		self.auto_pitch = pitchauto_premake.create()
		self.numchannels = numchannels

	def add(self):
		self.auto_pitch.add()
		return self.auto_pitch

	def postprocess(self):
		self.auto_pitch.sort(['pos'])
		self.auto_pitch.unique(['pos', 'channel'])

	def from_sysex(self, auto_sysex):
		if len(self.auto_pitch.data):
			pitchdata = self.auto_pitch.data
			for x in auto_sysex:
				p_pos, p_sysexs = x
				for p_sysex in p_sysexs:
					if p_sysex.model_name == 'aibo' and p_sysex.param == 'on?': 
						pitchdata['mode'][np.where(pitchdata['pos']>=p_pos)] = 1
					if p_sysex.model_name == 'sc88':
						if p_sysex.param in ['gs_reset', 'sys_mode']: 
							pitchdata['mode'][np.where(pitchdata['pos']>=p_pos)] = 0

	def get_chan_pitch(self):
		if len(self.auto_pitch.data):
			p_used = self.auto_pitch.data['used']
			p_data = self.auto_pitch.data['channel']
			chan_pitch = [self.auto_pitch.data[np.where(np.logical_and(p_data==x, p_used==1))] for x in range(self.numchannels)]
		else:
			chan_pitch = None

	def filter_chan(self, ch_num):
		return self.auto_pitch.data[np.where(self.auto_pitch.data['channel']==ch_num)]

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

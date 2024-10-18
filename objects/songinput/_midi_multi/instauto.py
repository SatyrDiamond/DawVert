# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc
from functions import data_values

instauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('type', np.uint8),
	('value', np.uint8)])

class midi_instauto_multi:
	def __init__(self, song_channels):
		self.data = instauto_premake.create()
		self.chan_inst = None
		self.song_channels = song_channels

	def addp_inst(self, curpos, channel, value):
		self.data.add()
		self.data['pos'] = curpos
		self.data['channel'] = channel
		self.data['type'] = 0
		self.data['value'] = value

	def addp_bank(self, curpos, channel, value):
		self.data.add()
		self.data['pos'] = curpos
		self.data['channel'] = channel
		self.data['type'] = 1
		self.data['value'] = value

	def addp_bank_hi(self, curpos, channel, value):
		self.data.add()
		self.data['pos'] = curpos
		self.data['channel'] = channel
		self.data['type'] = 2
		self.data['value'] = value

	def addp_drum(self, curpos, channel, value):
		self.data.add()
		self.data['pos'] = curpos
		self.data['channel'] = channel
		self.data['type'] = 3
		self.data['value'] = value

	def postprocess(self):
		self.data.sort(['pos'])
		if len(self.data.data):
			i_used = self.data.data['used']
			i_data = self.data.data['channel']
			self.chan_inst = [self.data.data[np.where(np.logical_and(i_data==x, i_used==1))] for x in range(self.song_channels)]

	def applyinst(self, midinotes, channel, i_type, posval):
		if len(posval) != 0:
			n_used = midinotes.data['used']
			n_chan = midinotes.data['chan']
			n_start = midinotes.data['start']
			filt_chan = np.logical_and(n_used==1, n_chan==channel)

			for start, end, val in data_values.gen__rangepos(posval, -1):
				if end == -1:
					filt_l_all = np.logical_and(filt_chan, n_start>=start)
					midinotes.data[i_type][np.where(filt_l_all)] = val
				else:
					filt_l_all = np.logical_and(filt_chan, n_start>=start, end>n_start)
					midinotes.data[i_type][np.where(filt_l_all)] = val

	def applyinst_chan(self, midinotes, channel):
		n_used = midinotes.data['used']
		n_data = midinotes.data['chan']
		allfilt = np.where(np.logical_and(n_used==1, n_data==channel))
		if self.chan_inst != None:
			chanfilt = self.chan_inst[channel]

			s_inst = chanfilt[np.where(chanfilt['type']==0)][['pos', 'value']]
			s_bank_lo = chanfilt[np.where(chanfilt['type']==1)][['pos', 'value']]
			s_bank_hi = chanfilt[np.where(chanfilt['type']==2)][['pos', 'value']]
			s_drum = chanfilt[np.where(chanfilt['type']==3)][['pos', 'value']]

			self.applyinst(midinotes, channel, 'i_inst', s_inst)
			self.applyinst(midinotes, channel, 'i_drum', s_drum)
			self.applyinst(midinotes, channel, 'i_bank_hi', s_bank_hi)
			self.applyinst(midinotes, channel, 'i_bank', s_bank_lo)


# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc

midinote_premake = structalloc.dynarray_premake([
	('complete', np.uint8),
	('chan', np.uint8),
	('start', np.int32),
	('end', np.int32),
	('key', np.uint8),
	('vol', np.uint8),
	('i_drum', np.uint8),
	('i_bank_hi', np.uint8),
	('i_bank', np.uint8),
	('i_inst', np.uint8),
	])

class midi_notes_multi:
	def __init__(self, numevents):
		self.active_notes = [[[] for x in range(128)] for x in range(16)]
		self.data = midinote_premake.create()
		self.data.alloc(numevents)

	def clean(self):
		self.data.data['used'] = self.data.data['complete']
		self.data.clean()

	def where_chan(self, channel):
		n_used = self.data.data['used']
		n_data = self.data.data['chan']
		return np.where(np.logical_and(n_used==1, n_data==channel))

	def filter_chan(self, channel):
		return self.data.data[self.where_chan(channel)]

	def startpos_chan(self, channel):
		notedata = self.filter_chan(channel)
		return np.min(notedata['start']) if len(notedata) else 2147483647

	def endpos_chan(self, channel):
		notedata = self.filter_chan(channel)
		return np.max(notedata['end']) if len(notedata) else 0

	def note_on(self, curpos, channel, note, velocity):
		self.data.add()
		self.data['chan'] = channel
		self.data['start'] = curpos
		self.data['key'] = note
		self.data['vol'] = velocity
		self.active_notes[channel][note].append(self.data.cursor)

	def note_off(self, curpos, channel, note):
		nd = self.active_notes[channel][note]
		if nd:
			notenum = nd.pop()
			self.data.data[notenum]['end'] = curpos
			self.data.data[notenum]['complete'] = 1

	def note_dur(self, curpos, channel, note, velocity, duration):
		self.data.add()
		self.data['complete'] = 1
		self.data['chan'] = channel
		self.data['start'] = curpos
		self.data['end'] = curpos+duration
		self.data['key'] = note
		self.data['vol'] = velocity

	def get_used_chans(self):
		return np.unique(self.data.data['chan'])

	def get_used_insts(self):
		return np.unique(self.data.data[['chan','i_drum','i_bank_hi','i_bank','i_inst']])

	def postprocess(self):
		self.data.data['i_inst'] = 255
		self.data.data['i_drum'][np.where(self.data.data['chan']==9)] = 1

	def to_cvpj(self, cvpj_notelist, tracknum, channum):
		if channum > -1: tracknotes = self.filter_chan(channum)
		else: tracknotes = self.data.data

		for n in tracknotes:
			if n['complete']:
				instid = '_'.join([str(tracknum),str(n['chan']),str(n['i_inst']),str(n['i_bank']),str(n['i_bank_hi']),str(n['i_drum'])])
				cvpj_notelist.add_m(instid, int(n['start']), int(n['end']-n['start']), int(n['key'])-60, float(n['vol'])/127, None)

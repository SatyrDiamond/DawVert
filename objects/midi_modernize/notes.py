# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np
import objects.midi_modernize.instruments as instruments
import objects.midi_modernize.gfunc as gfunc

midinote_premake = dynbytearr.dynbytearr_premake([
	('complete', np.uint8),
	('track', np.uint64),
	('chanport', np.int32),
	('start', np.uint64),
	('end', np.uint64),
	('key', np.uint8),
	('vol', np.uint8),
	('inst', instruments.midi_instrument),
	('section', np.uint64),
	])

max64 = 18446744073709551615

def iter_posrange(indata):
	for i in range(len(indata)-1):
		yield indata[i]['pos'], indata[i+1]['pos'], indata[i]

def filt_poschan(notesdata, chanport, start, end):
	filt_cp = notesdata['chanport']==chanport
	filt_pos = np.logical_and(end>notesdata['start'], notesdata['start']>=start)
	return np.logical_and(filt_cp, filt_pos)

class notes_data:
	__slots__ = ['all_notes', 'cur_notes', 'num_channels', 'num_ports', 'notes', 'startpos']
	def __init__(self, num_ports, num_channels):
		self.all_notes = midinote_premake.create()
		self.cur_notes = self.all_notes.create_cursor()
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.notes = [[[[] for x in range(128)] for x in range(self.num_channels)] for x in range(self.num_ports)]
		self.startpos = np.zeros([self.num_ports, self.num_channels], np.int64)
		self.startpos[:] = -1

	def get_note_starts(self):
		notesdata = self.all_notes.data
		for p in range(self.num_ports):
			for c in range(self.num_channels):
				wherevals = np.where(notesdata['chanport']==gfunc.calc_channum(c, p, self.num_channels))
				if len(wherevals[0]):
					self.startpos[p,c] = np.min(notesdata[wherevals]['start'])

	def alloc(self, allocsize):
		self.all_notes.alloc(allocsize)

	def add_note_dur(self, track, pos, chan, port, key, vol, dur):
		cur_notes = self.cur_notes
		cur_notes.add()
		cur_notes['track'] = track
		cur_notes['start'] = pos
		cur_notes['chanport'] = gfunc.calc_channum(chan, port, self.num_channels)
		cur_notes['key'] = key
		cur_notes['vol'] = vol
		cur_notes['complete'] = 1
		cur_notes['end'] = pos+dur
		return cur_notes

	def add_note_on(self, track, pos, chan, port, key, vol):
		cur_notes = self.cur_notes
		cur_notes.add()
		cur_notes['track'] = track
		cur_notes['start'] = pos
		cur_notes['chanport'] = gfunc.calc_channum(chan, port, self.num_channels)
		cur_notes['key'] = key
		cur_notes['vol'] = vol
		self.notes[port][chan][key].append(self.cur_notes.pos)
		return cur_notes

	def add_note_off(self, chan, port, key, pos):
		nd = self.notes[port][chan][key]
		if nd:
			notenum = nd.pop()
			non = self.all_notes.data[notenum]
			non['complete'] = 1
			non['end'] = pos

	def sort(self):
		self.all_notes.sort(['start'])

	def proc_instchan(self):
		notesdata = self.all_notes.data
		instdata = notesdata['inst']
		instdata['track'] = notesdata['track']
		instdata['chanport'] = notesdata['chanport']
		instdata['port'] = notesdata['chanport']//self.num_channels
		instdata['chan'] = notesdata['chanport']%self.num_channels
		instdata['drum'] = instdata['chan']==9

	def get_used_inst(self):
		notesdata = self.all_notes.data
		return np.unique(notesdata['inst'])

	def add_instchange(self, instchange_data):
		icb = instchange_data.data
		used_change = np.unique(icb.get_used())
		notesdata = self.all_notes.data
		note_insts = notesdata['inst']
		note_start = notesdata['start']

		for x in used_change:
			xtype = x['type']

			if xtype == instruments.CHANGE__INST:
				note_chanport = notesdata['chanport']
				posd = np.logical_and(note_start>=x['pos'], note_chanport==x['chanport'])
				note_insts['patch'][posd] = x['val']

			if xtype == instruments.CHANGE__BANK:
				note_chanport = notesdata['chanport']
				posd = np.logical_and(note_start>=x['pos'], note_chanport==x['chanport'])
				note_insts['bank'][posd] = x['val']

			if xtype == instruments.CHANGE__HIBANK:
				note_chanport = notesdata['chanport']
				posd = np.logical_and(note_start>=x['pos'], note_chanport==x['chanport'])
				note_insts['bank_hi'][posd] = x['val']

			if xtype == instruments.CHANGE__DRUM:
				note_chanport = notesdata['chanport']
				posd = np.logical_and(note_start>=x['pos'], note_chanport==x['chanport'])
				note_insts['drum'][posd] = x['val']

			if xtype == instruments.CHANGE__DEVICE:
				note_insts['device'][note_start>=x['pos']] = x['val']

	def get_startpos(self, chanport):
		p, c = gfunc.split_channum(chanport, self.num_channels)
		return self.startpos[p][c]

	def filter_chanport(self, n):
		notesdata = self.all_notes.data
		return notesdata[np.where(notesdata['chanport']==n)]

	def filter_track(self, n):
		notesdata = self.all_notes.data
		return notesdata[np.where(notesdata['track']==n)]

	def filter_track_section(self, n, s):
		notesdata = self.all_notes.get_used()
		return notesdata[np.logical_and(notesdata['track']==n, notesdata['section']==s)]

	def get_global_startpos(self):
		gstartpos = self.startpos[self.startpos!=-1]
		if len(gstartpos): return np.min(gstartpos)
		else: return 0

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np

#class active_notes:
#	def __init__(self, num_ports, num_channels):
#		self.notes = [[[[] for x in range(128)] for x in range(num_channels)] for x in range(num_ports)]
#
#	def on(self, port, channel, key, value):
#		notes[port][channel][key].append(value)
#
#	def off(self, port, channel, key):
#		nd = notes[port][channel][key]
#		if nd: return nd.pop()

def calc_channum(i_chan, i_port, numchans):
	return (i_chan)+(i_port*numchans)

def split_channum(i_val, numchans):
	return i_val//numchans, (i_val%numchans)

cc_defualtvals = np.zeros(130, dtype=np.uint8)
cc_defualtvals[:] = 0
cc_defualtvals[10] = 64
cc_defualtvals[11] = 127
cc_defualtvals[7] = 127

class ctrl_auto_diff:
	__slots__ = ['num_channels', 'num_ports', 'data', 'data_current', 'data_prev']
	def __init__(self, num_ports, num_channels):
		self.num_channels = num_channels
		self.num_ports = num_ports

		self.data = np.zeros((2, self.num_ports, self.num_channels, 130), dtype=np.int16)
		self.data_current = self.data[0]
		self.data_prev = self.data[1]

		self.data_current[:] = cc_defualtvals[:]
		self.data_prev[:] = self.data_current[:]

	def get_diffs(self):
		out = []
		check_port = np.where(self.data_current!=self.data_prev)[0]
		check_port = np.unique(check_port)
		for p in check_port:
			check_chan = np.where(self.data_current[p]!=self.data_prev[p])[0]
			check_chan = np.unique(check_chan)
			for c in check_chan:
				check_ctrl = np.where(self.data_current[p][c]!=self.data_prev[p][c])[0]
				check_ctrl = np.unique(check_ctrl)
				for v in check_ctrl: out.append([p, c, v, int(self.data_current[p][c][v])])
		self.data_prev[:] = self.data_current[:]
		return out

	def set(self, port, chan, ctrl, val):
		self.data_current[port][chan][ctrl] = val

	def set_pitch(self, port, chan, val):
		self.data_current[port][chan][128] = val

	def set_pressure(self, port, chan, val):
		self.data_current[port][chan][129] = val




auto_cc_channel = np.dtype([
	('cc_inital', np.int64, 130),
	('cc_dict_ids', np.uintp, 130),
	('cc_after_notes', np.int8, 130),
	])

class ctrl_auto:
	__slots__ = ['num_channels','num_ports','diff','data','data_startvals','data_dictids','data_after_notes','data_startvals','auto']
	def __init__(self, num_ports, num_channels):
		self.num_channels = num_channels
		self.num_ports = num_ports
		self.diff = ctrl_auto_diff(self.num_ports, self.num_channels)
		self.data = np.zeros((self.num_ports, self.num_channels), dtype=auto_cc_channel)
		self.data_startvals = self.data['cc_inital']
		self.data_dictids = self.data['cc_dict_ids']
		self.data_after_notes = self.data['cc_after_notes']
		self.data_startvals[:] = cc_defualtvals[:]
		self.auto = {}

	def set_ctrl_chanport(self, chanport, ctrl, val, before_note):
		port, chan = split_channum(chanport, self.num_channels)
		self.diff.set(port, chan, ctrl, val)
		if before_note:
			self.data_startvals[port][chan][ctrl] = val
		else:
			self.data_after_notes[port][chan][ctrl] = 1

	def get_dict(self, port, chan, ccnum):
		dictid = self.data_dictids[port][chan][ccnum]
		if not dictid: 
			dictdata = {}
			dictid = self.data_dictids[port][chan][ccnum] = id(dictdata)
			self.auto[dictid] = dictdata
		return self.auto[dictid]

	def add_point(self, pos, port, chan, ccnum, val):
		dictdata = self.get_dict(port, chan, ccnum)
		dictdata[pos] = val

	def do_change(self, pos):
		for port, chan, ccnum, val in self.diff.get_diffs():
			self.add_point(pos, port, chan, ccnum, val)

	def get_cc_used_fx(self, port, chan):
		ccnums = self.data_startvals[port][chan]
		dictid = self.data_dictids[port][chan]
		out = []
		for ccid, name in [
			[91, 'reverb'], 
			[92, 'tremolo'], 
			[93, 'chorus'], 
			[94, 'detune'], 
			[95, 'phaser'],
			[74, 'filter'],
			]:
			if ccnums[ccid] or dictid[ccid]:
				out.append(name)
		return out

	def get_cc_all(self, port, chan):
		return self.data_startvals[port][chan][0:128]

	def get_cc_val(self, port, chan, ccnum):
		return self.data_startvals[port][chan][ccnum]

	def get_cc_auto(self, port, chan, ccnum):
		dictid = self.data_dictids[port][chan][ccnum]
		after_note = self.data_after_notes[port][chan][ccnum]
		if not dictid: outdict = None
		else: outdict = self.auto[dictid]
		return self.data_startvals[port][chan][ccnum], outdict, after_note

	def get_pitch_auto(self, port, chan):
		dictids = self.data_dictids[port][chan]


# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import dynbytearr
import numpy as np

pitch_premake = dynbytearr.dynbytearr_premake([
	('pos', np.uint64),
	('chanport', np.int32),
	('type', np.int8),
	('value', np.int32)
	])

class pitch_data:
	def __init__(self, num_ports, num_channels):
		self.data = pitch_premake.create()
		self.cur = self.data.create_cursor()
		self.num_channels = num_channels
		self.num_ports = num_ports

	def alloc(self, allocsize):
		self.data.alloc(allocsize)

	def add(self, pos, chanport, val):
		cur = self.cur
		cur.add()
		cur['pos'] = pos
		cur['type'] = 0
		cur['chanport'] = chanport
		cur['value'] = val

	def add_range(self, pos, chanport, val):
		cur = self.cur
		cur.add()
		cur['pos'] = pos
		cur['type'] = 1
		cur['chanport'] = chanport
		cur['value'] = val

	def add_range_all(self, pos, val):
		cur = self.cur
		cur.add()
		cur['pos'] = pos
		cur['type'] = 1
		cur['chanport'] = -1
		cur['value'] = val

	def sort(self):
		self.data.sort(['pos'])
 
	def get_auto(self, chanport):
		ctrldata = self.data.get_used()
		ctrldata = ctrldata[np.logical_or(ctrldata['chanport']==chanport, ctrldata['chanport']==-1)]
		pitchrange = 1
		curval = 0
		for x in ctrldata:
			if x['type']==0: curval = (x['value']/8191)
			yield x['pos'], curval*pitchrange
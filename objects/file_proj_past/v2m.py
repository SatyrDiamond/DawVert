# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import numpy as np

notes_dtype = np.dtype([
	('time', np.uint32),
	('key', np.int8),
	('vol', np.uint8)
	])

pc_dtype = np.dtype([
	('time', np.uint32),
	('p', np.uint8)
	])

pb_dtype = np.dtype([
	('time', np.uint32),
	('p', np.uint8),
	('b', np.uint8)
	])

class v2m_track:
	def __init__(self, byr_stream):
		numnotes = byr_stream.uint32()
		self.notes = np.zeros(numnotes, dtype=notes_dtype)
		self.cc = []

		if numnotes:
			with byr_stream.isolate_size(5 * numnotes, True) as bye_stream:
				self.notes[:]['time'] += byr_stream.l_uint8(numnotes).astype(np.uint32)
				self.notes[:]['time'] += byr_stream.l_uint8(numnotes).astype(np.uint32)<<8
				self.notes[:]['time'] += byr_stream.l_uint8(numnotes).astype(np.uint32)<<16
				self.notes[:]['key'] = byr_stream.l_int8(numnotes)
				self.notes[:]['vol'] = byr_stream.l_uint8(numnotes)

			pcnum = byr_stream.uint32()
			self.pc = np.zeros(pcnum, dtype=pc_dtype)
			if pcnum:
				with byr_stream.isolate_size(4 * pcnum, True) as bye_stream:
					self.pc[:]['time'] += byr_stream.l_uint8(pcnum).astype(np.uint32)
					self.pc[:]['time'] += byr_stream.l_uint8(pcnum).astype(np.uint32)<<8
					self.pc[:]['time'] += byr_stream.l_uint8(pcnum).astype(np.uint32)<<16
					self.pc[:]['p'] = byr_stream.l_uint8(pcnum)
	
			pbnum = byr_stream.uint32()
			self.pb = np.zeros(pbnum, dtype=pb_dtype)
			if pbnum:
				with byr_stream.isolate_size(5 * pbnum, True) as bye_stream:
					self.pb[:]['time'] += byr_stream.l_uint8(pbnum).astype(np.uint32)
					self.pb[:]['time'] += byr_stream.l_uint8(pbnum).astype(np.uint32)<<8
					self.pb[:]['time'] += byr_stream.l_uint8(pbnum).astype(np.uint32)<<16
					self.pb[:]['p'] = byr_stream.l_uint8(pbnum)
					self.pb[:]['b'] = byr_stream.l_uint8(pbnum)
	
			for j in range(7):
				ccnum = byr_stream.uint32()
				cc_data = np.zeros(ccnum, dtype=pc_dtype)
				if ccnum:
					with byr_stream.isolate_size(4 * ccnum, True) as bye_stream:
						cc_data[:]['time'] += byr_stream.l_uint8(ccnum).astype(np.uint32)
						cc_data[:]['time'] += byr_stream.l_uint8(ccnum).astype(np.uint32)<<8
						cc_data[:]['time'] += byr_stream.l_uint8(ccnum).astype(np.uint32)<<16
						cc_data[:]['p'] = byr_stream.l_uint8(ccnum)
					self.cc.append([ccnum, cc_data])

class v2m_song:
	def __init__(self):
		self.timediv = 1
		self.maxtime = 0
		self.gdnum = 0
		self.gptr = None
		self.tracks = []

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		self.timediv = byr_stream.uint32()
		self.maxtime = byr_stream.uint32()
		self.gdnum = byr_stream.uint32()
		self.gptr = byr_stream.raw(10*self.gdnum)
		self.tracks = [v2m_track(byr_stream) for x in range(16)]
		self.globals = byr_stream.raw(byr_stream.uint32())
		self.patchmap = byr_stream.raw(byr_stream.uint32())
		return True
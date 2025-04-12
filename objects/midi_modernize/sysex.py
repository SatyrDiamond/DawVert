# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import objects.midi_modernize.sysex_decode as sysex_decode

class sysex_data:
	def __init__(self):
		self.data = {}

	def __iter__(self):
		for p, v in self.data.items():
			for x in v:
				yield p, x

	def add(self, pos, sysexbytes):
		pos = int(pos)
		sysex_obj = sysex_decode.sysex_obj()
		sysex_obj.detect(sysexbytes)
		if pos not in self.data: self.data[pos] = []
		self.data[pos].append(sysex_obj)

class seqspec_data:
	def __init__(self):
		self.data = {}

	def add(self, pos, track, seqspecbytes):
		seqspec_obj = sysex_decode.seqspec_obj()
		seqspec_obj.detect(seqspecbytes)
		if pos not in self.data: self.data[pos] = []
		self.data[pos].append(sysex_obj)

	def get(self, track):
		if track in self.data: return self.data[track]
		else: return []
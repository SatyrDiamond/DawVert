# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json

chorddata = []
basechorddata = []
with open("./data_main/json/chords.json") as f: 
	j = json.load(f)
	for n,v in j.items():
		chorddata.append([n,v])
		if len(v) == 2: basechorddata.append([n,v])

class cvpj_chord:
	def __init__(self):
		self.keys = []
		self.base_key = 0
		self.chord_type = 'octave'

	def find_by_key(self, i_keys):
		global chorddata
		self.keys = i_keys
		self.base_key = min(i_keys)
		rest_keys = [x-self.base_key for x in i_keys[1:]]
		self.chord_type = None
		for m,v in chorddata:
			leftovers = v.copy()
			unused = []
			for x in rest_keys:
				if x in leftovers: leftovers.remove(x)
				else: unused.append(x)
			if not leftovers and not unused: self.chord_type = m
		if self.chord_type == None and len(rest_keys) > 1:
			for m,v in basechorddata:
				if rest_keys[0:2] == v: 
					self.chord_type = m
					break

	def find_by_id(self, base_key, i_id):
		self.chord_type = None
		self.base_key = base_key
		for m,v in chorddata:
			if m == i_id: 
				self.chord_type = m
				self.keys = v

class chromatic:
	def __init__(self): 
		self.keys = [0,2,4,5,7,9,11]
		self.octaves = 1

	def get_key(self, i_num, i_offs, i_c_offs):
		key = i_num+i_c_offs
		octkey = self.octaves*7
		octplus = key//octkey
		return self.keys[key%(7*self.octaves)]+(octplus*12)+i_offs


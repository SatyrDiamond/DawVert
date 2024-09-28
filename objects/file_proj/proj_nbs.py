# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class nbs_key:
	def __init__(self):
		self.pos = 0
		self.inst = 0
		self.key = 0
		self.vel = 100
		self.pan = 100
		self.pitch = 0

def nbs_parsekey(song_file, nbs_newformat, note_tick):
	note_obj = nbs_key()
	note_obj.pos = note_tick
	note_obj.inst = song_file.uint8()
	note_obj.key = song_file.uint8()
	if nbs_newformat == 1:
		note_obj.vel = song_file.uint8()
		note_obj.pan = song_file.uint8()
		note_obj.pitch = song_file.int16()
	return note_obj

class nbs_layer:
	def __init__(self):
		self.notes = []
		self.name = ''
		self.lock = 0
		self.vol = 100
		self.stereo = 100

class nbs_custom_inst:
	def __init__(self):
		self.name = ''
		self.file = ''
		self.key = 0
		self.presskey = 0

class nbs_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		startbyte = song_file.uint16()
		if startbyte == 0: 
			self.newformat = 1
			version = song_file.uint8()
			if version != 5:
				raise ProjectFileParserException('mnbs: only version 5 new-NBS or old format is supported.')
			self.inst_count = song_file.uint8()
			self.song_length = song_file.uint16()
			self.layers_count = song_file.uint16()
		else: 
			self.newformat = 0
			self.layers_count = startbyte

		self.custom = []

		self.layers = [nbs_layer() for _ in range(self.layers_count)]
		self.name = song_file.c_string__int32(False)
		self.author = song_file.c_string__int32(False)
		self.orgauthor = song_file.c_string__int32(False)
		self.description = song_file.c_string__int32(False)

		self.tempo = song_file.uint16()
		self.autosave_on = song_file.uint8()
		self.autosave_duration = song_file.uint8()
		self.numerator = song_file.uint8()

		self.stat_minutes_spent = song_file.uint32()
		self.stat_clicks_left = song_file.uint32()
		self.stat_clicks_right = song_file.uint32()
		self.stat_notes_added = song_file.uint32()
		self.stat_notes_removed = song_file.uint32()

		self.source_filename = song_file.c_string__int32(False)
		if self.newformat == 1:
			nbs_loopon = song_file.uint8()
			nbs_maxloopcount = song_file.uint8()
			nbs_loopstarttick = song_file.uint16()
		else:
			nbs_loopon = 1
			nbs_maxloopcount = 1
			nbs_loopstarttick = 128

		notes_done = 0
		note_tick = -1

		while notes_done == 0:
			jump_tick = song_file.uint16()
			if jump_tick != 0:
				jump_layer = song_file.uint16()
				note_tick += jump_tick
				if jump_layer != 0:
					note_layer = jump_layer
					layer_done = 0
					while layer_done == 0:
						self.layers[note_layer].notes.append(nbs_parsekey(song_file, self.newformat, note_tick))
						jump_layer = song_file.uint16()
						if jump_layer == 0: layer_done = 1
						note_layer += jump_layer
			if jump_tick == 0:
				notes_done = 1

		if song_file.remaining():
			for layernum in range(self.layers_count): 
				layer_obj = self.layers[layernum]
				layer_obj.name = song_file.c_string__int32(False)
				if self.newformat == 1: 
					layer_obj.lock = song_file.uint8()
					layer_obj.vol = song_file.uint8()
					layer_obj.stereo = song_file.uint8()

		if song_file.remaining():
			for _ in range(song_file.uint8()):
				custom_obj = nbs_custom_inst()
				custom_obj.name = song_file.c_string__int32(False)
				custom_obj.file = song_file.c_string__int32(False)
				custom_obj.key = song_file.uint8()
				custom_obj.presskey = song_file.uint8()
				self.custom.append(custom_obj)

		return True
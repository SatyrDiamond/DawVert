# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import plugins
import xml.etree.ElementTree as ET

import logging
logger_input = logging.getLogger('input')

notekeys = ['A','B','C','D','E','F','G','H','a','b','c','d','e','f','g','h','i']

def parsenotes(txt):
	notetable = []
	notestr = [0, '']
	for noteletter in txt:
		if noteletter in ['-','+']: 
			notestr[1] = noteletter
		else:
			note = notekeys.index(noteletter)
			notestr[0] = note-2
			notetable.append(notestr)
			notestr = [0, '']
	return notetable

class mss_chord():
	def __init__(self):
		self.volume = 8
		self.notes = {}
		self.notes_muted = {}
		self.bookmark = False
		self.speedmark = -1

class input_mariopaint_mss(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'mariopaint_mss'
	def get_name(self): return 'Advanced Mario Sequencer'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mss']
		in_dict['track_lanes'] = True
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'rm'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		output = False
		try:
			tree = ET.parse(input_file)
			root = tree.getroot()
			if root.tag == "MarioSequencerSong": output = True
		except ET.ParseError: output = False
		return output
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.songinput import mariopaint

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'rm'
		mariopaint_obj = mariopaint.mariopaint_song()

		try: 
			tree = ET.parse(input_file)
		except ET.ParseError as t:
			raise ProjectFileParserException('mariopaint_mss: XML parsing error: '+str(t))

		root = tree.getroot()

		if 'tempo' in root.attrib: mariopaint_obj.tempo = int(root.attrib['tempo'])/4
		if 'soundfont' in root.attrib: mariopaint_obj.soundfont = root.attrib['soundfont']
		if 'measure' in root.attrib: mariopaint_obj.measure = int(root.attrib['measure'])

		chordpos = 0
		for rpart in root:
			if rpart.tag == 'chord':
				mp_chord = mariopaint_obj.add_chord(chordpos)

				if 'volume' in rpart.attrib: mp_chord.volume = int(rpart.attrib['volume'])/8

				for rnote in rpart:
					if rnote.tag == 'bookmark': mp_chord.bookmark = True
					elif rnote.tag == 'speedmark': mp_chord.speedmark = int(rnote.get('tempo'))
					else:
						instname = rnote.tag if rnote.tag[0] != 'x' else rnote.tag[1:]
						muted = rnote.tag[0] == 'x'

						for keynum, toff in parsenotes(rnote.text):
							mp_note = mp_chord.add_note()
							mp_note.inst = instname
							mp_note.key = keynum%7
							mp_note.oct = keynum//7
							if toff == '-': mp_note.offset = -1
							if toff == '+': mp_note.offset = 1

				chordpos += 1

		mariopaint_obj.to_cvpj(convproj_obj)

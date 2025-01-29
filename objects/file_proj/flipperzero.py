# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import re
from objects.exceptions import ProjectFileParserException

class fmf_note:
	def __init__(self):
		self.duration = 1
		self.key = ''
		self.sharp = False
		self.octave = 0
		self.dots = 0

class fmf_song:
	def __init__(self):
		self.version = 0
		self.bpm = 120
		self.duration = 0
		self.octave = 0
		self.notes = []

	def load_from_file(self, input_file):
		try:
			f_fmf = open(input_file, 'r')
			lines_fmf = f_fmf.readlines()
		except UnicodeDecodeError:
			raise ProjectFileParserException('flipperzero: File is not text')

		for line in lines_fmf:
			if line != "\n":
				fmf_command, fmf_param = line.rstrip().split(': ')
				if fmf_command == 'Version': self.version = int(fmf_param)
				if fmf_command == 'BPM': self.bpm = int(fmf_param)
				if fmf_command == 'Duration': self.duration = int(fmf_param)
				if fmf_command == 'Octave': self.octave = int(fmf_param)
				if fmf_command == 'Notes':
					notes = fmf_param.strip()
					notes = notes.replace(',','').split(' ')

					for note in notes:
						note_obj = fmf_note()
						note_obj.dots = note.count('.')
						note_obj.octave = self.octave
						note = note.replace('.','').strip()
						note = re.split('(\\d+)',note)
						while '' in note: note.remove('')

						if note:
							if note[0].isnumeric(): 
								note_obj.duration = int(note[0])
								note = note[1:]

						if note:
							note_obj.key = note[0][0]
							note_obj.sharp = "#" in note[0]
							note = note[1:]

						if note:
							note_obj.octave = int(note[0])

						self.notes.append(note_obj)
		return True
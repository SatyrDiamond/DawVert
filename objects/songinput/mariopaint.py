# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
from functions import xtramath
import copy

instnames = ['MARIO','MUSHROOM','YOSHI','STAR','FLOWER','GAMEBOY','DOG','CAT','PIG','SWAN','FACE','PLANE','BOAT','CAR','HEART','PIRANHA','COIN','SHYGUY','BOO','LUIGI','PEACH','FEATHER','BULLETBILL','GOOMBA','BOBOMB','SPINY','FRUIT','ONEUP','MOON','EGG','GNOME']

keytable = [0,2,4,5,7,9,11]

class mariopaint_note():
	def __init__(self):
		self.key = 0
		self.oct = 0
		self.mode = 0
		self.offset = 0
		self.inst = ''

	def get(self):
		return keytable[self.key]+self.oct*12+self.offset

class mariopaint_chord():
	def __init__(self):
		self.volume = 1
		self.notes = []
		self.notes_muted = []
		self.bookmark = False
		self.speedmark = -1

	def add_note(self):
		note_obj = mariopaint_note()
		self.notes.append(note_obj)
		return note_obj

class mariopaint_song():
	def __init__(self):
		self.data = {}
		self.chords = {}
		self.tempo = 100
		self.soundfont = ''
		self.measure = 4
		self.measure_o = 4
		self.notelen = 1

	def add_chord(self, pos):
		self.chords[pos] = mariopaint_chord()
		return self.chords[pos]

	def to_cvpj(self, convproj_obj):
		convproj_obj.set_timings(4)
		track_obj = convproj_obj.track__add('main', 'instruments', 0, False)
		globalstore.dataset.load('mariopaint', './data_main/dataset/mariopaint.dset')


		#print(outtempo, notelen, self.tempo)

		cvpj_notelist = track_obj.placements.notelist

		songsize = max(list(self.chords))

		auto_bpm_obj = convproj_obj.automation.create(['main','bpm'], 'float', True)

		notepos = 0
		outtempo, notelen = xtramath.get_lower_tempo(self.tempo, 1, 180)
		tempo_changed = True
		for pos in range(songsize):
			chord_obj = self.chords[pos] if pos in self.chords else None

			if chord_obj:
				if chord_obj.speedmark>0:
					tempo_changed = True
					outtempo, notelen = xtramath.get_lower_tempo(chord_obj.speedmark, 1, 180)

				if chord_obj.bookmark:
					timemarker_obj = convproj_obj.timemarker__add()
					timemarker_obj.visual.name = 'Bookmark'
					timemarker_obj.type = 'text'
					timemarker_obj.position = (pos/notelen)
				for n in chord_obj.notes:
					cvpj_notelist.add_m(n.inst, notepos, notelen*2, n.get(), chord_obj.volume, None)

			if tempo_changed: 
				tempo = outtempo
				auto_bpm_obj.add_all(notepos, (outtempo)/2, notelen)
				tempo_changed = False

			notepos += notelen*2

		used_inst = cvpj_notelist.get_used_inst()

		for instnum, instname in enumerate(used_inst): 
			inst_obj = convproj_obj.instrument__add(instname)
			inst_obj.visual.from_dset('mariopaint', 'inst', instname, True)
			plugin_obj = convproj_obj.plugin__add(instname, 'universal', 'mariopaint', None)
			plugin_obj.midi_fallback__add_from_dset('mariopaint', 'inst', instname)
			fxchan_data = convproj_obj.fx__chan__add(instnum+1)
			fxchan_data.visual = copy.deepcopy(inst_obj.visual)
			inst_obj.fxrack_channel = instnum+1
			
		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.timesig = [self.measure, self.measure_o]
		convproj_obj.params.add('bpm', outtempo, 'float')

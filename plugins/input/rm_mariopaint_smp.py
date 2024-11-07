# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import io
import plugins

from objects.exceptions import ProjectFileParserException

smpnames = {'MARIO': "mario", 'MUSHROOM': "toad", 'YOSHI': "yoshi", 'STAR': "star", 'FLOWER': "flower", 'GAMEBOY': "gameboy", 'DOG': "dog", 'CAT': "cat", 'PIG': "pig", 'SWAN': "swan", 'FACE': "face", 'PLANE': "plane", 'BOAT': "boat", 'CAR': "car", 'HEART': "heart", 'PIRANHA': "plant", 'COIN': "coin", 'SHYGUY': "shyguy", 'BOO': "ghost", 'LUIGI': "luigi", 'PEACH': "peach", 'FEATHER': "feather", 'BULLETBILL': "bulletbill", 'GOOMBA': "goomba", 'BOBOMB': "bobomb", 'SPINY': "spiny", 'FRUIT': "fruit", 'ONEUP': "oneup", 'MOON': "moon", 'EGG': "egg", 'GNOME': "gnome"}
keytable = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def get_namval(tin): 
	n,v = tin.split(':')
	return n.lstrip(), v.lstrip()

class input_mariopaint_smp(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'mariopaint_smp'
	def get_name(self): return 'Super Mario Paint'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['txt']
		in_dict['file_ext_detect'] = False
		in_dict['track_lanes'] = True
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'rm'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.songinput import mariopaint

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'rm'
		mariopaint_obj = mariopaint.mariopaint_song()

		f_smp = open(input_file, 'r')
		try:
			lines_smp = f_smp.readlines()
		except UnicodeDecodeError:
			raise ProjectFileParserException('mariopaint_smp: File is not text')

		for num, line in enumerate(lines_smp):
			t_smp_values = line.rstrip().split(',')
			if num == 0:
				for s in t_smp_values:
					n, v = get_namval(s)
					if n == 'TEMPO': mariopaint_obj.tempo = float(v)
					if n == 'TIME': 
						tnum, tdnum = v.split('/')
						mariopaint_obj.measure = int(tnum)
						mariopaint_obj.measure_o = int(tdnum)
			else:
				p, b = t_smp_values[0].split(':')
				mp_chord = mariopaint_obj.add_chord((int(p)-1)*mariopaint_obj.measure + int(b))

				for s in t_smp_values[1:]:
					if ':' not in s:
						mp_note = mp_chord.add_note()

						notesplit = s.split(' ')
						mp_note.inst = smpnames[notesplit[0]]
						notetxt = notesplit[1]
						smpnote_size = len(notetxt)
						smpnote_str = io.StringIO(notetxt)
			
						mp_note.key = keytable.index(smpnote_str.read(1))
						mp_note.oct = int(smpnote_str.read(1))-4
			
						while smpnote_str.tell() < smpnote_size:
							t_txtp = smpnote_str.read(1)
							if t_txtp == '#': mp_note.offset = 1
							if t_txtp == 'b': mp_note.offset = -1
							if t_txtp == 'm': mp_note.mode = smpnote_str.read(1)
					else:
						n,v = get_namval(s)
						if n == 'VOL': mp_chord.volume = int(v)/127

		mariopaint_obj.to_cvpj(convproj_obj)

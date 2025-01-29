# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import numpy as np

from objects.exceptions import ProjectFileParserException

vl_dtype = np.dtype([('n', np.int16),('t', np.int16),('v', np.int16),('f', np.int16),('id', np.int32),('x', np.int16),('p', np.int16),('e', np.int16)])

class LCSound:
	def __init__(self, pd):
		self.play_notes = 32
		self.play_speed = 30
		if pd:
			self.vl = None
			if '__LCSound__' in pd:
				self.vl = pd['vl']
				if 'play_notes' in pd: self.play_notes = pd['play_notes']
				if 'play_speed' in pd: self.play_speed = pd['play_speed']

		self.voicelist = np.zeros(self.play_notes, dtype=vl_dtype)
		self.voicelist.fill(-1)
		self.voicelist['x'] = 14
		self.voicelist['p'] = 8

		if self.vl:
			for num in range(min(len(self.voicelist), len(self.vl))):
				dat = self.vl[num]
				vlp = self.voicelist[num]
				if 'n' in dat:
					if dat['n'] != None: vlp['n'] = dat['n']
				if 't' in dat:
					if dat['t'] != None: vlp['t'] = dat['t']
				if 'v' in dat:
					if dat['v'] != None: vlp['v'] = dat['v']
				if 'f' in dat:
					if dat['f'] != None: vlp['f'] = dat['f']
				if 'id' in dat:
					if dat['id'] != None: vlp['id'] = dat['id']
				if 'x' in dat:
					if dat['x'] != None: vlp['x'] = dat['x']
				if 'p' in dat:
					if dat['p'] != None: vlp['p'] = dat['p']
				if 'e' in dat:
					if dat['e'] != None: vlp['e'] = dat['e']

class LCSoundList:
	def __init__(self, pd):
		self.sl = []
		if pd:
			if '__LCSoundList__' in pd:
				for ch in pd['sl']:
					self.sl.append(LCSound(ch))

class LCChannelList:
	def __init__(self):
		self.ch = []

	def load(self, pd):
		if '__LCChannelList__' in pd:
			for ch in pd['channels']:
				self.ch.append(LCSoundList(ch))

class LCRhythm:
	def __init__(self, pd):
		self.enable_drum = True
		self.enable_base = True
		self.enable_melody = True
		self.bar_rhythm_rate = 3
		self.bar_arpeggio_rate = 3
		self.arpeggio = 0
		self.arpeggio_octave = 1
		self.arpeggio_length = 3
		self.arpeggio_reverse = False
		self.pattern = 3
		self.sub_pattern = 2
		self.enable_chordpart = True

		if '__LCRhythm__' in pd:
			if 'enable_drum' in pd: self.enable_drum = pd['enable_drum']
			if 'enable_base' in pd: self.enable_base = pd['enable_base']
			if 'enable_melody' in pd: self.enable_melody = pd['enable_melody']
			if 'bar_rhythm_rate' in pd: self.bar_rhythm_rate = pd['bar_rhythm_rate']
			if 'bar_arpeggio_rate' in pd: self.bar_arpeggio_rate = pd['bar_arpeggio_rate']
			if 'arpeggio' in pd: self.arpeggio = pd['arpeggio']
			if 'arpeggio_octave' in pd: self.arpeggio_octave = pd['arpeggio_octave']
			if 'arpeggio_length' in pd: self.arpeggio_length = pd['arpeggio_length']
			if 'arpeggio_reverse' in pd: self.arpeggio_reverse = pd['arpeggio_reverse']
			if 'pattern' in pd: self.pattern = pd['pattern']
			if 'sub_pattern' in pd: self.sub_pattern = pd['sub_pattern']
			if 'enable_chordpart' in pd: self.enable_chordpart = pd['enable_chordpart']

class LCRhythmList:
	def __init__(self):
		self.ry = []

	def load(self, pd):
		if '__LCRhythmList__' in pd:
			for ch in pd['rhythms']:
				self.ry.append(LCRhythm(ch))

class LCMusic:
	def __init__(self):
		self.speed = 15
		self.loop_start_bar = 0
		self.loop_end_bar = 9
		self.enable_loop = True
		self.channels = LCChannelList()
		self.chord_channels = LCChannelList()
		self.code_channels = LCChannelList()
		self.rhythms = LCRhythmList()
		self.bars_number_per_page = 4
		self.pages = 20
		self.notes_by_page = True
		self.tempo_by_page = True
		self.play_notes = 32
		self.abrepeat_a = None
		self.abrepeat_b = None
		self.sel_scale_id = 0
		self.pianoroll_display_mode = 0
		self.pro_mode = 0
		self.mixer_expression_list = [0,0,0,0,0]
		self.mixer_output_channel_list = [0,0,0,0,0]
		self.mixer_channel_switch_list = [0,0,0,0,0]
		self.ui_mixer_expression_list = [0,0,0,0,0]
		self.ui_mixer_output_channel_list = [0,0,0,0,0]
		self.mixer_transpose = 0
		self.pan_law_type = 0
		self.compatibility_mode = 0
		self.sel_scale_key = 0
		self.ex_filename = ''
		self.abrepeat_a = None
		self.abrepeat_b = None
		self.pianoroll_display_mode = 0
		self.wave_memory_table_list = []
		self.wave_memory_type_list = []
		self.wave_memory_effect_list = []

		self.title = None
		self.editor = None

	def get_channel(self, num):
		voi_notes = self.channels.ch[num].sl
		voi_chord = self.chord_channels.ch[num].sl
		return voi_notes, voi_chord

	def load(self, pd):
		if '__LCMusic__' in pd:
			if 'speed' in pd: self.speed = pd['speed']
			if 'loop_start_bar' in pd: self.loop_start_bar = pd['loop_start_bar']
			if 'loop_end_bar' in pd: self.loop_end_bar = pd['loop_end_bar']
			if 'enable_loop' in pd: self.enable_loop = pd['enable_loop']
			if 'bars_number_per_page' in pd: self.bars_number_per_page = pd['bars_number_per_page']
			if 'pages' in pd: self.pages = pd['pages']
			if 'notes_by_page' in pd: self.notes_by_page = pd['notes_by_page']
			if 'tempo_by_page' in pd: self.tempo_by_page = pd['tempo_by_page']
			if 'play_notes' in pd: self.play_notes = pd['play_notes']
			if 'abrepeat_a' in pd: self.abrepeat_a = pd['abrepeat_a']
			if 'abrepeat_b' in pd: self.abrepeat_b = pd['abrepeat_b']
			if 'sel_scale_id' in pd: self.sel_scale_id = pd['sel_scale_id']
			if 'pianoroll_display_mode' in pd: self.pianoroll_display_mode = pd['pianoroll_display_mode']
			if 'channels' in pd: self.channels.load(pd['channels'])
			if 'chord_channels' in pd: self.chord_channels.load(pd['chord_channels'])
			if 'code_channels' in pd: self.code_channels.load(pd['code_channels'])
			if 'rhythms' in pd: self.rhythms.load(pd['rhythms'])
			if 'pro_mode' in pd: self.pro_mode = pd['pro_mode']
			if 'mixer_expression_list' in pd: self.mixer_expression_list = pd['mixer_expression_list']
			if 'mixer_output_channel_list' in pd: self.mixer_output_channel_list = pd['mixer_output_channel_list']
			if 'mixer_channel_switch_list' in pd: self.mixer_channel_switch_list = pd['mixer_channel_switch_list']
			if 'ui_mixer_expression_list' in pd: self.ui_mixer_expression_list = pd['ui_mixer_expression_list']
			if 'ui_mixer_output_channel_list' in pd: self.ui_mixer_output_channel_list = pd['ui_mixer_output_channel_list']
			if 'mixer_transpose' in pd: self.mixer_transpose = pd['mixer_transpose']
			if 'pan_law_type' in pd: self.pan_law_type = pd['pan_law_type']
			if 'compatibility_mode' in pd: self.compatibility_mode = pd['compatibility_mode']
			if 'sel_scale_key' in pd: self.sel_scale_key = pd['sel_scale_key']
			if 'title' in pd: self.title = pd['title']
			if 'editor' in pd: self.editor = pd['editor']
			if 'ex_filename' in pd: self.ex_filename = pd['ex_filename']
			if 'abrepeat_a' in pd: self.abrepeat_a = pd['abrepeat_a']
			if 'abrepeat_b' in pd: self.abrepeat_b = pd['abrepeat_b']
			if 'pianoroll_display_mode' in pd: self.pianoroll_display_mode = pd['pianoroll_display_mode']
			if 'wave_memory_table_list' in pd: self.wave_memory_table_list = pd['wave_memory_table_list']
			if 'wave_memory_type_list' in pd: self.wave_memory_type_list = pd['wave_memory_type_list']
			if 'wave_memory_effect_list' in pd: self.wave_memory_effect_list = pd['wave_memory_effect_list']

	def load_from_file(self, input_file):
		try:
			song_file = open(input_file, 'r')
			for num, lined in enumerate(song_file.readlines()):
				if num == 0: 
					metadata = json.loads(lined)
					if 'title' in metadata: self.title = metadata['title']
					if 'editor' in metadata: self.editor = metadata['editor']
				if num == 1: self.load(json.loads(lined))
		except UnicodeDecodeError:
			raise ProjectFileParserException('famistudio_txt: File is not text')

		return True


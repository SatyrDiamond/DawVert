# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.file_proj._zenbeats import func
from objects.file_proj._zenbeats import automation
from objects.file_proj._zenbeats import misc

class zenbeats_envelope:
	def __init__(self, xml_data):
		self.name = ''
		self.x = 0
		self.y = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'x' in attrib: self.x = float(attrib['x'])
		if 'y' in attrib: self.y = float(attrib['y'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "point")
		tempxml.set('name', str(self.name))
		tempxml.set('x', str(self.x))
		tempxml.set('y', str(self.y))

class zenbeats_key_change:
	def __init__(self, xml_data):
		self.key = 0
		self.mode = 0
		self.beat = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'key' in attrib: self.key = int(attrib['key'])
		if 'mode' in attrib: self.mode = int(attrib['mode'])
		if 'beat' in attrib: self.beat = float(attrib['beat'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "key_change")
		tempxml.set('key', str(self.key))
		tempxml.set('mode', str(self.mode))
		tempxml.set('beat', str(self.beat))

class zenbeats_note:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.start = 0
		self.end = 1
		self.velocity = 100
		self.semitone = 60
		self.active = 1
		self.probability = 1.0
		self.velocity_jitter = None
		self.pan_jitter = None
		self.filter_high_cut = None
		self.reverse = 0
		self.pan_linear = 0.5
		self.pitch_offset = 0

		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		self.visual.read(xml_data)
		self.version.read(xml_data)
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'start' in attrib: self.start = float(attrib['start'])
		if 'end' in attrib: self.end = float(attrib['end'])
		if 'velocity' in attrib: self.velocity = int(attrib['velocity'])
		if 'semitone' in attrib: self.semitone = int(attrib['semitone'])
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'probability' in attrib: self.probability = float(attrib['probability'])
		if 'velocity_jitter' in attrib: self.velocity_jitter = float(attrib['velocity_jitter'])
		if 'pan_jitter' in attrib: self.pan_jitter = float(attrib['pan_jitter'])
		if 'filter_high_cut' in attrib: self.filter_high_cut = float(attrib['filter_high_cut'])
		if 'reverse' in attrib: self.reverse = float(attrib['reverse'])
		if 'pan_linear' in attrib: self.pan_linear = float(attrib['pan_linear'])
		if 'pitch_offset' in attrib: self.pitch_offset = float(attrib['pitch_offset'])*100

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "note")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('start', str(self.start))
		tempxml.set('end', str(self.end))
		tempxml.set('velocity', str(self.velocity))
		tempxml.set('semitone', str(self.semitone))
		tempxml.set('active', str(self.active))
		if self.velocity_jitter is not None: tempxml.set('velocity_jitter', str(self.velocity_jitter))
		tempxml.set('probability', str(self.probability))
		if self.filter_high_cut is not None: tempxml.set('filter_high_cut', str(self.filter_high_cut))

class zenbeats_pattern:
	def __init__(self, xml_data):
		self.type = 'pattern'
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.color_index = 2
		self.low_note = 0
		self.high_note = 127
		self.time_signature_numerator = 4
		self.time_signature_denominator = 4
		self.default_note_size = -1.0
		self.start_beat = 0
		self.end_beat = 4
		self.loop = 1
		self.start_playing_on_transport = 0
		self.loop_start_beat = 0
		self.loop_end_beat = 4
		self.loop_play_start = 0
		self.active = 1
		self.play_mutual_exclusive = 1
		self.pattern_type = 1
		self.play_back_ratio = 1.0
		self.original_file_bpm = 0.0
		self.viewport_start = 0
		self.viewport_end = 4
		self.viewport_lower_bound = 0.0
		self.viewport_upper_bound = 6.99999
		self.grid_size = 0.25
		self.snap_to_grid = 1
		self.show_step_sequencer = 0
		self.loop_xfade_length = 0.0
		self.use_adaptive_grid = 0
		self.use_triplets = 0
		self.locked = 0
		self.scale_lock = misc.zenbeats_scale_lock(None)
		self.pattern_envelope = []
		self.timeline_envelope = []
		self.key_change_list = []
		self.notes = []
		self.automation_set = automation.zenbeats_automation_set(None)

		self.default_file_bpm = None
		self.audio_file = None
		self.audio_file_original_bpm = None
		self.timestretching = None
		self.preserve_pitch = None
		self.audio_pitch = None
		self.fine_audio_pitch_offset = None
		self.audio_gain = None
		self.audio_pan = None
		self.reverse_audio = None
		self.icon_name = None
		self.key_string = None
		self.scene_index = -1
		self.accent = None
		self.last_note_automation_function = None

		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.type = xml_data.tag
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])
		if 'low_note' in attrib: self.low_note = int(attrib['low_note'])
		if 'high_note' in attrib: self.high_note = int(attrib['high_note'])
		if 'time_signature_numerator' in attrib: self.time_signature_numerator = int(attrib['time_signature_numerator'])
		if 'time_signature_denominator' in attrib: self.time_signature_denominator = int(attrib['time_signature_denominator'])
		if 'default_note_size' in attrib: self.default_note_size = float(attrib['default_note_size'])
		if 'start_beat' in attrib: self.start_beat = float(attrib['start_beat'])
		if 'end_beat' in attrib: self.end_beat = float(attrib['end_beat'])
		if 'loop' in attrib: self.loop = int(attrib['loop'])
		if 'start_playing_on_transport' in attrib: self.start_playing_on_transport = int(attrib['start_playing_on_transport'])
		if 'loop_start_beat' in attrib: self.loop_start_beat = float(attrib['loop_start_beat'])
		if 'loop_end_beat' in attrib: self.loop_end_beat = float(attrib['loop_end_beat'])
		if 'loop_play_start' in attrib: self.loop_play_start = float(attrib['loop_play_start'])
		if 'active' in attrib: self.active = int(attrib['active'])
		if 'play_mutual_exclusive' in attrib: self.play_mutual_exclusive = int(attrib['play_mutual_exclusive'])
		if 'pattern_type' in attrib: self.pattern_type = int(attrib['pattern_type'])
		if 'play_back_ratio' in attrib: self.play_back_ratio = float(attrib['play_back_ratio'])
		if 'original_file_bpm' in attrib: self.original_file_bpm = float(attrib['original_file_bpm'])
		if 'viewport_start' in attrib: self.viewport_start = float(attrib['viewport_start'])
		if 'viewport_end' in attrib: self.viewport_end = float(attrib['viewport_end'])
		if 'viewport_lower_bound' in attrib: self.viewport_lower_bound = float(attrib['viewport_lower_bound'])
		if 'viewport_upper_bound' in attrib: self.viewport_upper_bound = float(attrib['viewport_upper_bound'])
		if 'grid_size' in attrib: self.grid_size = float(attrib['grid_size'])
		if 'snap_to_grid' in attrib: self.snap_to_grid = int(attrib['snap_to_grid'])
		if 'show_step_sequencer' in attrib: self.show_step_sequencer = int(attrib['show_step_sequencer'])
		if 'last_note_automation_function' in attrib: self.last_note_automation_function = attrib['last_note_automation_function']
		if 'loop_xfade_length' in attrib: self.loop_xfade_length = float(attrib['loop_xfade_length'])
		if 'use_adaptive_grid' in attrib: self.use_adaptive_grid = int(attrib['use_adaptive_grid'])
		if 'use_triplets' in attrib: self.use_triplets = int(attrib['use_triplets'])
		if 'locked' in attrib: self.locked = int(attrib['locked'])
		if 'accent' in attrib: self.accent = attrib['accent']
		if 'scene_index' in attrib: self.scene_index = int(attrib['scene_index'])
		if 'last_note_automation_function' in attrib: self.last_note_automation_function = attrib['last_note_automation_function']

		if 'default_file_bpm' in attrib: self.default_file_bpm = float(attrib['default_file_bpm'])
		if 'audio_file' in attrib: self.audio_file = attrib['audio_file']
		if 'audio_file_original_bpm' in attrib: self.audio_file_original_bpm = float(attrib['audio_file_original_bpm'])
		if 'timestretching' in attrib: self.timestretching = int(attrib['timestretching'])
		if 'preserve_pitch' in attrib: self.preserve_pitch = int(attrib['preserve_pitch'])
		if 'audio_pitch' in attrib: self.audio_pitch = float(attrib['audio_pitch'])
		if 'fine_audio_pitch_offset' in attrib: self.fine_audio_pitch_offset = float(attrib['fine_audio_pitch_offset'])
		if 'audio_gain' in attrib: self.audio_gain = float(attrib['audio_gain'])
		if 'audio_pan' in attrib: self.audio_pan = float(attrib['audio_pan'])
		if 'reverse_audio' in attrib: self.reverse_audio = int(attrib['reverse_audio'])
		if 'icon_name' in attrib: self.icon_name = attrib['icon_name']
		if 'key_string' in attrib: self.key_string = attrib['key_string']
		if 'accent' in attrib: self.accent = attrib['accent']

		for x_part in xml_data:
			if x_part.tag == 'note': self.notes.append(zenbeats_note(x_part))
			if x_part.tag == 'scale_lock': self.scale_lock.read(x_part)
			if x_part.tag == 'pattern_envelope': 
				for inpart in x_part:
					if inpart.tag == 'point': self.pattern_envelope.append(zenbeats_envelope(inpart))
			if x_part.tag == 'timeline_envelope': 
				for inpart in x_part:
					if inpart.tag == 'point': self.timeline_envelope.append(zenbeats_envelope(inpart))
			if x_part.tag == 'key_change_list': 
				for inpart in x_part:
					if inpart.tag == 'key_change': self.key_change_list.append(zenbeats_key_change(inpart))
			if x_part.tag == 'automation_set': self.automation_set.read(x_part)

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, self.type)
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('color_index', str(self.color_index))
		tempxml.set('low_note', str(self.low_note))
		tempxml.set('high_note', str(self.high_note))
		tempxml.set('time_signature_numerator', str(self.time_signature_numerator))
		tempxml.set('time_signature_denominator', str(self.time_signature_denominator))
		tempxml.set('default_note_size', str(self.default_note_size))
		tempxml.set('start_beat', str(self.start_beat))
		tempxml.set('end_beat', str(self.end_beat))
		tempxml.set('loop', str(self.loop))
		tempxml.set('start_playing_on_transport', str(self.start_playing_on_transport))
		tempxml.set('loop_start_beat', str(self.loop_start_beat))
		tempxml.set('loop_end_beat', str(self.loop_end_beat))
		tempxml.set('loop_play_start', str(self.loop_play_start))
		tempxml.set('active', str(self.active))
		tempxml.set('play_mutual_exclusive', str(self.play_mutual_exclusive))
		tempxml.set('pattern_type', str(self.pattern_type))
		tempxml.set('play_back_ratio', str(self.play_back_ratio))
		tempxml.set('original_file_bpm', str(self.original_file_bpm))
		tempxml.set('viewport_start', str(self.viewport_start))
		tempxml.set('viewport_end', str(self.viewport_end))
		tempxml.set('viewport_lower_bound', str(self.viewport_lower_bound))
		tempxml.set('viewport_upper_bound', str(self.viewport_upper_bound))
		tempxml.set('grid_size', str(self.grid_size))
		tempxml.set('snap_to_grid', str(self.snap_to_grid))
		tempxml.set('show_step_sequencer', str(self.show_step_sequencer))
		if self.last_note_automation_function != None: tempxml.set('last_note_automation_function', str(self.last_note_automation_function))
		tempxml.set('loop_xfade_length', str(self.loop_xfade_length))
		tempxml.set('use_adaptive_grid', str(self.use_adaptive_grid))
		tempxml.set('use_triplets', str(self.use_triplets))
		tempxml.set('locked', str(self.locked))
		if self.accent != None: tempxml.set('accent', str(self.accent))
		if self.scene_index != -1: tempxml.set('scene_index', str(self.scene_index))
		self.scale_lock.write(tempxml)

		if self.default_file_bpm != None: tempxml.set('default_file_bpm', str(self.default_file_bpm))
		if self.audio_file != None: tempxml.set('audio_file', str(self.audio_file))
		if self.audio_file_original_bpm != None: tempxml.set('audio_file_original_bpm', str(self.audio_file_original_bpm))
		if self.timestretching != None: tempxml.set('timestretching', str(self.timestretching))
		if self.preserve_pitch != None: tempxml.set('preserve_pitch', str(self.preserve_pitch))
		if self.audio_pitch != None: tempxml.set('audio_pitch', str(self.audio_pitch))
		if self.fine_audio_pitch_offset != None: tempxml.set('fine_audio_pitch_offset', str(self.fine_audio_pitch_offset))
		if self.audio_gain != None: tempxml.set('audio_gain', str(self.audio_gain))
		if self.audio_pan != None: tempxml.set('audio_pan', str(self.audio_pan))
		if self.reverse_audio != None: tempxml.set('reverse_audio', str(self.reverse_audio))
		if self.icon_name != None: tempxml.set('icon_name', str(self.icon_name))
		if self.key_string != None: tempxml.set('key_string', str(self.key_string))
		if self.accent != None: tempxml.set('accent', str(self.accent))
		
		envtempxml = ET.SubElement(tempxml, "pattern_envelope")
		for env in self.pattern_envelope: env.write(envtempxml)
		envtempxml = ET.SubElement(tempxml, "timeline_envelope")
		for env in self.timeline_envelope: env.write(envtempxml)
		kcxml = ET.SubElement(tempxml, "key_change_list")
		for env in self.key_change_list: env.write(kcxml)
		for note in self.notes: note.write(tempxml)
		self.automation_set.write(tempxml)
	
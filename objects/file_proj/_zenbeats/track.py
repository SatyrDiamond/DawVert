# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.file_proj._zenbeats import func
from objects.file_proj._zenbeats import automation
from objects.file_proj._zenbeats import misc
from objects.file_proj._zenbeats import pattern
	
class zenbeats_track:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = -1
		self.type = 1
		self.color_index = 3
		self.sub_track_master_track_uid = None
		self.show_sub_tracks = 0
		self.track_icon_index = -1
		self.arm_record = 0
		self.mute = 0
		self.solo = 0
		self.mute_by_solo = 0
		self.monitor = 0
		self.monitor_by_arm = 0
		self.transpose = 0
		self.input_channel_flags = 0
		self.output_channel = 0
		self.input_device_slot = -1
		self.output_device_slot = -2
		self.output_rack_uid = ""
		self.audio_input_channel_left = 0
		self.audio_input_channel_right = 1
		self.onscreen_midi_input_type = 200
		self.onscreen_midi_start_semitone = 36.0
		self.onscreen_keys_pitch_bend_on_drag = 0
		self.onscreen_midi_end_semitone = 67.0
		self.onscreen_note_pad_count = 24
		self.onscreen_drum_pad_count = 16
		self.onscreen_note_pad_columns = 12
		self.onscreen_drum_pad_columns = 8
		self.onscreen_midi_scale_lock = 1
		self.onscreen_midi_grid_invert = 0
		self.pattern_pre_midi_effects = 1
		self.track_tuner_active = 1
		self.visualizer_array_file = ""
		self.is_sub_track_master = -1
		self.patterns = []
		self.clip_patterns = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'name_set_by_user' in attrib: self.name_set_by_user = int(attrib['name_set_by_user'])
		if 'description' in attrib: self.description = attrib['description']
		if 'color' in attrib: self.color = attrib['color']
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'type' in attrib: self.type = int(attrib['type'])
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])
		if 'show_sub_tracks' in attrib: self.show_sub_tracks = int(attrib['show_sub_tracks'])
		if 'track_icon_index' in attrib: self.track_icon_index = int(attrib['track_icon_index'])
		if 'arm_record' in attrib: self.arm_record = int(attrib['arm_record'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute_by_solo' in attrib: self.mute_by_solo = int(attrib['mute_by_solo'])
		if 'monitor' in attrib: self.monitor = int(attrib['monitor'])
		if 'monitor_by_arm' in attrib: self.monitor_by_arm = int(attrib['monitor_by_arm'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])
		if 'input_channel_flags' in attrib: self.input_channel_flags = int(attrib['input_channel_flags'])
		if 'output_channel' in attrib: self.output_channel = int(attrib['output_channel'])
		if 'input_device_slot' in attrib: self.input_device_slot = int(attrib['input_device_slot'])
		if 'output_device_slot' in attrib: self.output_device_slot = int(attrib['output_device_slot'])
		if 'output_rack_uid' in attrib: self.output_rack_uid = attrib['output_rack_uid']
		if 'audio_input_channel_left' in attrib: self.audio_input_channel_left = int(attrib['audio_input_channel_left'])
		if 'audio_input_channel_right' in attrib: self.audio_input_channel_right = int(attrib['audio_input_channel_right'])
		if 'onscreen_midi_input_type' in attrib: self.onscreen_midi_input_type = int(attrib['onscreen_midi_input_type'])
		if 'onscreen_midi_start_semitone' in attrib: self.onscreen_midi_start_semitone = float(attrib['onscreen_midi_start_semitone'])
		if 'onscreen_keys_pitch_bend_on_drag' in attrib: self.onscreen_keys_pitch_bend_on_drag = int(attrib['onscreen_keys_pitch_bend_on_drag'])
		if 'onscreen_midi_end_semitone' in attrib: self.onscreen_midi_end_semitone = float(attrib['onscreen_midi_end_semitone'])
		if 'onscreen_note_pad_count' in attrib: self.onscreen_note_pad_count = int(attrib['onscreen_note_pad_count'])
		if 'onscreen_drum_pad_count' in attrib: self.onscreen_drum_pad_count = int(attrib['onscreen_drum_pad_count'])
		if 'onscreen_note_pad_columns' in attrib: self.onscreen_note_pad_columns = int(attrib['onscreen_note_pad_columns'])
		if 'onscreen_drum_pad_columns' in attrib: self.onscreen_drum_pad_columns = int(attrib['onscreen_drum_pad_columns'])
		if 'onscreen_midi_scale_lock' in attrib: self.onscreen_midi_scale_lock = int(attrib['onscreen_midi_scale_lock'])
		if 'onscreen_midi_grid_invert' in attrib: self.onscreen_midi_grid_invert = int(attrib['onscreen_midi_grid_invert'])
		if 'pattern_pre_midi_effects' in attrib: self.pattern_pre_midi_effects = int(attrib['pattern_pre_midi_effects'])
		if 'track_tuner_active' in attrib: self.track_tuner_active = int(attrib['track_tuner_active'])
		if 'visualizer_array_file' in attrib: self.visualizer_array_file = attrib['visualizer_array_file']
		if 'is_sub_track_master' in attrib: self.is_sub_track_master = int(attrib['is_sub_track_master'])
		if 'sub_track_master_track_uid' in attrib: self.sub_track_master_track_uid = attrib['sub_track_master_track_uid']
		for x_part in xml_data:
			if x_part.tag == 'pattern': self.patterns.append(pattern.zenbeats_pattern(x_part))
		for x_part in xml_data:
			if x_part.tag == 'clip_pattern': self.clip_patterns.append(pattern.zenbeats_pattern(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "track")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('type', str(self.type))
		tempxml.set('color_index', str(self.color_index))
		if self.is_sub_track_master != -1: tempxml.set('is_sub_track_master', str(self.is_sub_track_master))
		if self.sub_track_master_track_uid is not None: tempxml.set('sub_track_master_track_uid', str(self.sub_track_master_track_uid))
		tempxml.set('show_sub_tracks', str(self.show_sub_tracks))
		tempxml.set('track_icon_index', str(self.track_icon_index))
		tempxml.set('arm_record', str(self.arm_record))
		tempxml.set('mute', str(self.mute))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute_by_solo', str(self.mute_by_solo))
		tempxml.set('monitor', str(self.monitor))
		tempxml.set('monitor_by_arm', str(self.monitor_by_arm))
		tempxml.set('transpose', str(self.transpose))
		tempxml.set('input_channel_flags', str(self.input_channel_flags))
		tempxml.set('output_channel', str(self.output_channel))
		tempxml.set('input_device_slot', str(self.input_device_slot))
		tempxml.set('output_device_slot', str(self.output_device_slot))
		tempxml.set('output_rack_uid', str(self.output_rack_uid))
		tempxml.set('audio_input_channel_left', str(self.audio_input_channel_left))
		tempxml.set('audio_input_channel_right', str(self.audio_input_channel_right))
		tempxml.set('onscreen_midi_input_type', str(self.onscreen_midi_input_type))
		tempxml.set('onscreen_midi_start_semitone', str(self.onscreen_midi_start_semitone))
		tempxml.set('onscreen_keys_pitch_bend_on_drag', str(self.onscreen_keys_pitch_bend_on_drag))
		tempxml.set('onscreen_midi_end_semitone', str(self.onscreen_midi_end_semitone))
		tempxml.set('onscreen_note_pad_count', str(self.onscreen_note_pad_count))
		tempxml.set('onscreen_drum_pad_count', str(self.onscreen_drum_pad_count))
		tempxml.set('onscreen_note_pad_columns', str(self.onscreen_note_pad_columns))
		tempxml.set('onscreen_drum_pad_columns', str(self.onscreen_drum_pad_columns))
		tempxml.set('onscreen_midi_scale_lock', str(self.onscreen_midi_scale_lock))
		tempxml.set('onscreen_midi_grid_invert', str(self.onscreen_midi_grid_invert))
		tempxml.set('pattern_pre_midi_effects', str(self.pattern_pre_midi_effects))
		tempxml.set('track_tuner_active', str(self.track_tuner_active))
		tempxml.set('visualizer_array_file', str(self.visualizer_array_file))
		for pattern in self.patterns: pattern.write(tempxml)
		for clip_pattern in self.clip_patterns: clip_pattern.write(tempxml)

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

from objects.file_proj._zenbeats import track
from objects.file_proj._zenbeats import func
from objects.file_proj._zenbeats import automation
from objects.file_proj._zenbeats import misc
from objects.file_proj._zenbeats import bankrack

# =================================================== CLIP SCENE ===================================================

class zenbeats_clip_scene:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = -1
		self.follow_active = 0
		self.follow_loop_count = 1
		self.color_index = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'follow_active' in attrib: self.follow_active = int(attrib['follow_active'])
		if 'follow_loop_count' in attrib: self.follow_loop_count = int(attrib['follow_loop_count'])
		if 'color_index' in attrib: self.color_index = int(attrib['color_index'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "clip_scene")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('follow_active', str(self.follow_active))
		tempxml.set('follow_loop_count', str(self.follow_loop_count))
		tempxml.set('color_index', str(self.color_index))

class zenbeats_clip_scene_list:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = 0
		self.clip_scenes = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		for x_part in xml_data:
			if x_part.tag == 'clip_scene': self.clip_scenes.append(zenbeats_clip_scene(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "clip_scene_list")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		for clip_scene in self.clip_scenes: clip_scene.write(tempxml)

# =================================================== MAIN ===================================================

class zenbeats_song:
	def __init__(self):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = 0
		self.read_only = 0
		self.grid_size = 0.0
		self.track_view_state = "TIMELINE_VIEW"
		self.show_mixer_view = 0
		self.show_track_inspector = 1
		self.show_pattern_inspector = 0
		self.show_onscreen_midi_input = 0
		self.show_track_header_wide = 1
		self.show_track_header_wide_track_inpector_open = 0
		self.gain = 1.0
		self.bpm = 120.0
		self.x = 0
		self.y = 0
		self.show_curve_editor = 0
		self.loop = 0
		self.loop_start = 0.0
		self.loop_end = 16.0
		self.viewport_start = 0.0
		self.viewport_end = 24.0
		self.viewport_lower_bound = 0.0
		self.viewport_upper_bound = 600.0
		self.input_program_change = -1
		self.input_program_change_channel = 0
		self.output_program_change = -1
		self.output_program_change_channel = 1
		self.play_start_marker = 5.0
		self.show_beat_time = 1
		self.time_signature_numerator = 4
		self.time_signature_denominator = 4
		self.default_pattern_size = 1
		self.pattern_launch_beat = 1
		self.swing_active = 0
		self.track_height_index = 1
		self.scale_lock = misc.zenbeats_scale_lock(None)
		self.bank = bankrack.zenbeats_bank(None)
		self.clip_scene_list = zenbeats_clip_scene_list(None)
		self.tracks = []

		self.storeid__rack = {}

	def read(self, xml_data):
		self.__init__()
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'read_only' in attrib: self.read_only = int(attrib['read_only'])
		if 'grid_size' in attrib: self.grid_size = float(attrib['grid_size'])
		if 'track_view_state' in attrib: self.track_view_state = attrib['track_view_state']
		if 'show_mixer_view' in attrib: self.show_mixer_view = int(attrib['show_mixer_view'])
		if 'show_track_inspector' in attrib: self.show_track_inspector = int(attrib['show_track_inspector'])
		if 'show_pattern_inspector' in attrib: self.show_pattern_inspector = int(attrib['show_pattern_inspector'])
		if 'show_onscreen_midi_input' in attrib: self.show_onscreen_midi_input = int(attrib['show_onscreen_midi_input'])
		if 'show_track_header_wide' in attrib: self.show_track_header_wide = int(attrib['show_track_header_wide'])
		if 'show_track_header_wide_track_inpector_open' in attrib: self.show_track_header_wide_track_inpector_open = int(attrib['show_track_header_wide_track_inpector_open'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'bpm' in attrib: self.bpm = float(attrib['bpm'])
		if 'x' in attrib: self.x = int(attrib['x'])
		if 'y' in attrib: self.y = int(attrib['y'])
		if 'show_curve_editor' in attrib: self.show_curve_editor = int(attrib['show_curve_editor'])
		if 'loop' in attrib: self.loop = int(attrib['loop'])
		if 'loop_start' in attrib: self.loop_start = float(attrib['loop_start'])
		if 'loop_end' in attrib: self.loop_end = float(attrib['loop_end'])
		if 'viewport_start' in attrib: self.viewport_start = float(attrib['viewport_start'])
		if 'viewport_end' in attrib: self.viewport_end = float(attrib['viewport_end'])
		if 'viewport_lower_bound' in attrib: self.viewport_lower_bound = float(attrib['viewport_lower_bound'])
		if 'viewport_upper_bound' in attrib: self.viewport_upper_bound = float(attrib['viewport_upper_bound'])
		if 'input_program_change' in attrib: self.input_program_change = int(attrib['input_program_change'])
		if 'input_program_change_channel' in attrib: self.input_program_change_channel = int(attrib['input_program_change_channel'])
		if 'output_program_change' in attrib: self.output_program_change = int(attrib['output_program_change'])
		if 'output_program_change_channel' in attrib: self.output_program_change_channel = int(attrib['output_program_change_channel'])
		if 'play_start_marker' in attrib: self.play_start_marker = float(attrib['play_start_marker'])
		if 'show_beat_time' in attrib: self.show_beat_time = int(attrib['show_beat_time'])
		if 'time_signature_numerator' in attrib: self.time_signature_numerator = int(attrib['time_signature_numerator'])
		if 'time_signature_denominator' in attrib: self.time_signature_denominator = int(attrib['time_signature_denominator'])
		if 'default_pattern_size' in attrib: self.default_pattern_size = int(attrib['default_pattern_size'])
		if 'pattern_launch_beat' in attrib: self.pattern_launch_beat = int(attrib['pattern_launch_beat'])
		if 'swing_active' in attrib: self.swing_active = int(attrib['swing_active'])
		if 'track_height_index' in attrib: self.track_height_index = int(attrib['track_height_index'])

		for x_part in xml_data:
			if x_part.tag == 'scale_lock': self.scale_lock.read(x_part)
			if x_part.tag == 'track': self.tracks.append(track.zenbeats_track(x_part))
			if x_part.tag == 'bank': self.bank.read(x_part)
			if x_part.tag == 'clip_scene_list': self.clip_scene_list.read(x_part)

		for rack in self.bank.racks: self.storeid__rack[rack.uid] = rack

	def write(self, tempxml):
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('read_only', str(self.read_only))
		tempxml.set('grid_size', str(self.grid_size))
		tempxml.set('track_view_state', str(self.track_view_state))
		tempxml.set('show_mixer_view', str(self.show_mixer_view))
		tempxml.set('show_track_inspector', str(self.show_track_inspector))
		tempxml.set('show_pattern_inspector', str(self.show_pattern_inspector))
		tempxml.set('show_onscreen_midi_input', str(self.show_onscreen_midi_input))
		tempxml.set('show_track_header_wide', str(self.show_track_header_wide))
		tempxml.set('show_track_header_wide_track_inpector_open', str(self.show_track_header_wide_track_inpector_open))
		tempxml.set('gain', str(self.gain))
		tempxml.set('bpm', str(self.bpm))
		tempxml.set('x', str(self.x))
		tempxml.set('y', str(self.y))
		tempxml.set('show_curve_editor', str(self.show_curve_editor))
		tempxml.set('loop', str(self.loop))
		tempxml.set('loop_start', str(self.loop_start))
		tempxml.set('loop_end', str(self.loop_end))
		tempxml.set('viewport_start', str(self.viewport_start))
		tempxml.set('viewport_end', str(self.viewport_end))
		tempxml.set('viewport_lower_bound', str(self.viewport_lower_bound))
		tempxml.set('viewport_upper_bound', str(self.viewport_upper_bound))
		tempxml.set('input_program_change', str(self.input_program_change))
		tempxml.set('input_program_change_channel', str(self.input_program_change_channel))
		tempxml.set('output_program_change', str(self.output_program_change))
		tempxml.set('output_program_change_channel', str(self.output_program_change_channel))
		tempxml.set('play_start_marker', str(self.play_start_marker))
		tempxml.set('show_beat_time', str(self.show_beat_time))
		tempxml.set('time_signature_numerator', str(self.time_signature_numerator))
		tempxml.set('time_signature_denominator', str(self.time_signature_denominator))
		tempxml.set('default_pattern_size', str(self.default_pattern_size))
		tempxml.set('pattern_launch_beat', str(self.pattern_launch_beat))
		tempxml.set('swing_active', str(self.swing_active))
		tempxml.set('track_height_index', str(self.track_height_index))
		self.scale_lock.write(tempxml)
		for track in self.tracks: track.write(tempxml)
		self.bank.write(tempxml)
		self.clip_scene_list.write(tempxml)

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		self.read(x_root)
		return True

	def save_to_file(self, out_file):
		zenbeats_proj = ET.Element("song")
		self.write(zenbeats_proj)

		outfile = ET.ElementTree(zenbeats_proj)
		ET.indent(outfile)
		outfile.write(out_file, xml_declaration = True)

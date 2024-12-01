# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from objects.exceptions import ProjectFileParserException

class serato_sample:
	def __init__(self, json_data):
		self.file = json_data['file'] if 'file' in json_data else None
		self.reverse = json_data['reverse'] if 'reverse' in json_data else None
		self.start = json_data['start'] if 'start' in json_data else 0
		self.end = json_data['end'] if 'end' in json_data else 1
		self.color = json_data['color'] if 'color' in json_data else None
		self.polyphonic = json_data['polyphonic'] if 'polyphonic' in json_data else None
		self.attack = json_data['attack'] if 'attack' in json_data else None
		self.release = json_data['release'] if 'release' in json_data else None
		self.pitch_shift = json_data['pitch_shift'] if 'pitch_shift' in json_data else 0
		self.playback_speed = json_data['playback_speed'] if 'playback_speed' in json_data else 1

class serato_drum:
	def __init__(self, json_data):
		self.used = json_data != None
		if self.used:
			self.sample = serato_sample(json_data['sample']) if 'sample' in json_data else None
			self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)

class serato_channel_strip:
	def __init__(self, json_data):
		self.used = json_data != None
		if self.used:
			self.post_fader_effects = json_data['post_fader_effects'] if 'post_fader_effects' in json_data else None
			self.volume = json_data['volume'] if 'volume' in json_data else 1
			self.high_eq = json_data['high_eq'] if 'high_eq' in json_data else 0
			self.mid_eq = json_data['mid_eq'] if 'mid_eq' in json_data else 0
			self.low_eq = json_data['low_eq'] if 'low_eq' in json_data else 0
			self.pan = json_data['pan'] if 'pan' in json_data else 0
			self.gain = json_data['gain'] if 'gain' in json_data else 1
			self.filter = json_data['filter'] if 'filter' in json_data else 0
		else:
			self.post_fader_effects = None
			self.volume = 0
			self.high_eq = 0
			self.mid_eq = 0
			self.low_eq = 0
			self.pan = 0
			self.gain = 0
			self.filter = 0

class serato_scene_deck:
	def __init__(self, json_data):
		self.type = json_data['type'] if 'type' in json_data else ''
		self.name = json_data['name'] if 'name' in json_data else ''
		self.content_name = json_data['content_name'] if 'content_name' in json_data else ''
		self.groove_amount = json_data['groove_amount'] if 'groove_amount' in json_data else 0.0
		self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)
		self.drums = [serato_drum(x) for x in json_data['drums']] if 'drums' in json_data else ''
		self.make_sequence_genre = json_data['make_sequence_genre'] if 'make_sequence_genre' in json_data else None
		self.view = json_data['view'] if 'view' in json_data else None
		self.deck_source_properties_changed = json_data['deck_source_properties_changed'] if 'deck_source_properties_changed' in json_data else None
		self.zoom = json_data['zoom'] if 'zoom' in json_data else None
		self.original_key = json_data['original_key'] if 'original_key' in json_data else None
		self.tempo_map = json_data['tempo_map'] if 'tempo_map' in json_data else None
		self.sample_file = json_data['sample_file'] if 'sample_file' in json_data else None
		self.original_bpm = json_data['original_bpm'] if 'original_bpm' in json_data else None
		self.sample_regions = json_data['sample_regions'] if 'sample_regions' in json_data else None
		self.bpm = json_data['bpm'] if 'bpm' in json_data else None
		self.cues = json_data['cues'] if 'cues' in json_data else None
		self.momentary = json_data['momentary'] if 'momentary' in json_data else True
		self.attack = json_data['attack'] if 'attack' in json_data else None
		self.release = json_data['release'] if 'release' in json_data else None
		self.instrument_file = json_data['instrument_file'] if 'instrument_file' in json_data else None
		self.polyphony = json_data['polyphony'] if 'polyphony' in json_data else None
		self.sequence_view = json_data['sequence_view'] if 'sequence_view' in json_data else None
		self.bar_mode_enabled = json_data['bar_mode_enabled'] if 'bar_mode_enabled' in json_data else True
		self.playback_speed = json_data['playback_speed'] if 'playback_speed' in json_data else 1
		self.key_shift = json_data['key_shift'] if 'key_shift' in json_data else 0

class serato_note:
	def __init__(self, json_data):
		self.start = json_data['start']
		self.duration = json_data['duration']
		self.channel = json_data['channel'] if 'channel' in json_data else 0
		self.number = json_data['number']
		self.velocity = json_data['velocity'] if 'velocity' in json_data else 100

class serato_deck_sequence:
	def __init__(self, json_data):
		self.notes = [serato_note(x) for x in json_data['notes']] if 'notes' in json_data else []

class serato_scene:
	def __init__(self, json_data):
		self.name = json_data['name'] if 'name' in json_data else None
		self.length = json_data['length'] if 'length' in json_data else None
		self.deck_sequences = [serato_deck_sequence(x) for x in json_data['deck_sequences']] if 'deck_sequences' in json_data else []

class serato_arrangement_clip:
	def __init__(self, json_data):
		self.start = json_data['start']
		self.length = json_data['length']
		self.scene_slot_number = json_data['scene_slot_number'] if 'scene_slot_number' in json_data else None
		self.audio_deck_index = json_data['audio_deck_index'] if 'audio_deck_index' in json_data else None
		self.track_sample = json_data['track_sample'] if 'track_sample' in json_data else None

class serato_arrangement_track:
	def __init__(self, json_data):
		self.type = json_data['type']
		self.name = json_data['name']
		self.channel_strip = serato_channel_strip(json_data['channel_strip'] if 'channel_strip' in json_data else None)
		self.clips = [serato_arrangement_clip(x) for x in json_data['clips']] if 'clips' in json_data else []

class serato_arrangement:
	def __init__(self, json_data):
		self.tracks = [serato_arrangement_track(x) for x in json_data['tracks']] if 'tracks' in json_data else []
		self.loop_start = json_data['loop_start'] if 'loop_start' in json_data else 0
		self.loop_end = json_data['loop_end'] if 'loop_end' in json_data else 0
		self.loop_active = json_data['loop_active'] if 'loop_active' in json_data else False

class serato_song:
	def __init__(self):
		self.version = 81
		self.metadata = {}
		self.bpm = 120.0
		self.key_root_note = 'C'
		self.key_type = 'major'
		self.play_focus_area = 'arrangement'
		self.audio_deck_color_collection = []
		self.scene_decks = []

	def load_from_file(self, input_file):
		f = open(input_file, 'r')
		try: serato_json = json.load(f)
		except: raise ProjectFileParserException('serato: JSON Decoding Error')

		if 'version' in serato_json: self.version = serato_json['version']
		if 'metadata' in serato_json: self.metadata = serato_json['metadata']
		if 'bpm' in serato_json: self.bpm = serato_json['bpm']
		if 'key_root_note' in serato_json: self.key_root_note = serato_json['key_root_note']
		if 'key_type' in serato_json: self.key_type = serato_json['key_type']
		if 'play_focus_area' in serato_json: self.play_focus_area = serato_json['play_focus_area']
		if 'audio_deck_color_collection' in serato_json: self.audio_deck_color_collection = serato_json['audio_deck_color_collection']
		if 'scene_decks' in serato_json: self.scene_decks = [serato_scene_deck(x) for x in serato_json['scene_decks']]
		if 'scenes' in serato_json: self.scenes = [serato_scene(x) for x in serato_json['scenes']]
		if 'arrangement' in serato_json: self.arrangement = serato_arrangement(serato_json['arrangement'])
		return True
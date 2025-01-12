# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.file_proj._zenbeats import func
from objects.file_proj._zenbeats import automation
from objects.file_proj._zenbeats import misc

class zenbeats_plugin:
	def __init__(self, xml_data):
		self.name = ""
		self.descriptiveName = None
		self.format = ""
		self.category = ""
		self.manufacturer = ""
		self.version = '1.0'
		self.file = ""
		self.uniqueId = 17
		self.isInstrument = 0
		self.isMidiEffect = 0
		self.fileTime = 0
		self.infoUpdateTime = 0
		self.numInputs = 2
		self.numOutputs = 2
		self.isShell = 0
		self.uid = 0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'name' in attrib: self.name = attrib['name']
		if 'descriptiveName' in attrib: self.descriptiveName = attrib['descriptiveName']
		if 'format' in attrib: self.format = attrib['format']
		if 'category' in attrib: self.category = attrib['category']
		if 'manufacturer' in attrib: self.manufacturer = attrib['manufacturer']
		if 'version' in attrib: self.version = attrib['version']
		if 'file' in attrib: self.file = attrib['file']
		if 'uniqueId' in attrib: self.uniqueId = attrib['uniqueId']
		if 'isInstrument' in attrib: self.isInstrument = int(attrib['isInstrument'])
		if 'isMidiEffect' in attrib: self.isMidiEffect = int(attrib['isMidiEffect'])
		if 'fileTime' in attrib: self.fileTime = int(attrib['fileTime'])
		if 'infoUpdateTime' in attrib: self.infoUpdateTime = int(attrib['infoUpdateTime'])
		if 'numInputs' in attrib: self.numInputs = int(attrib['numInputs'])
		if 'numOutputs' in attrib: self.numOutputs = int(attrib['numOutputs'])
		if 'isShell' in attrib: self.isShell = int(attrib['isShell'])
		if 'uid' in attrib: self.uid = int(attrib['uid'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "PLUGIN")
		tempxml.set('name', str(self.name))
		if self.descriptiveName is not None: tempxml.set('descriptiveName', str(self.descriptiveName))
		tempxml.set('format', str(self.format))
		tempxml.set('category', str(self.category))
		tempxml.set('manufacturer', str(self.manufacturer))
		tempxml.set('version', str(self.version))
		tempxml.set('file', str(self.file))
		tempxml.set('uniqueId', str(self.uniqueId))
		tempxml.set('isInstrument', str(self.isInstrument))
		tempxml.set('isMidiEffect', str(self.isMidiEffect))
		tempxml.set('fileTime', str(self.fileTime))
		tempxml.set('infoUpdateTime', str(self.infoUpdateTime))
		tempxml.set('numInputs', str(self.numInputs))
		tempxml.set('numOutputs', str(self.numOutputs))
		tempxml.set('isShell', str(self.isShell))
		tempxml.set('uid', str(self.uid))

class zenbeats_cached_parameter:
	def __init__(self, xml_data):
		self.index = 0
		self.name = ''
		self.type = 0.0
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'name' in attrib: self.name = attrib['name']
		if 'value' in attrib: self.value = float(attrib['value'])

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "parameter")
		tempxml.set('index', str(self.index))
		tempxml.set('name', str(self.name))
		tempxml.set('value', str(self.value))

class zenbeats_stream_processor:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = -1
		self.index = 0
		self.block_ccs = 0
		self.bypass = 0
		self.wet_dry_mix = 1.0
		self.pre_gain = 1.0
		self.post_gain = 1.0
		self.mpe_enabled = 0
		self.stream_processor_type = 4
		self.program_index = -1
		self.show_editor_preference = 0
		self.plugin_window_x = -1
		self.plugin_window_y = -1
		self.preset_name = None
		self.cached_parameters = []
		self.plugin = None
		self.plugin_xml_data = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'block_ccs' in attrib: self.block_ccs = int(attrib['block_ccs'])
		if 'bypass' in attrib: self.bypass = int(attrib['bypass'])
		if 'wet_dry_mix' in attrib: self.wet_dry_mix = float(attrib['wet_dry_mix'])
		if 'pre_gain' in attrib: self.pre_gain = float(attrib['pre_gain'])
		if 'post_gain' in attrib: self.post_gain = float(attrib['post_gain'])
		if 'mpe_enabled' in attrib: self.mpe_enabled = int(attrib['mpe_enabled'])
		if 'stream_processor_type' in attrib: self.stream_processor_type = int(attrib['stream_processor_type'])
		if 'program_index' in attrib: self.program_index = int(attrib['program_index'])
		if 'preset_name' in attrib: self.preset_name = attrib['preset_name']
		if 'show_editor_preference' in attrib: self.show_editor_preference = int(attrib['show_editor_preference'])
		if 'plugin_window_x' in attrib: self.plugin_window_x = int(attrib['plugin_window_x'])
		if 'plugin_window_y' in attrib: self.plugin_window_y = int(attrib['plugin_window_y'])
		for x_part in xml_data:
			if x_part.tag == 'PLUGIN': self.plugin = zenbeats_plugin(x_part)
			if x_part.tag == 'plugin_xml_data': self.plugin_xml_data = x_part
			if x_part.tag == 'cached_parameters': 
				for inpart in x_part:
					if inpart.tag == 'parameter': self.cached_parameters.append(zenbeats_cached_parameter(inpart))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "stream_processor")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('index', str(self.index))
		tempxml.set('block_ccs', str(self.block_ccs))
		tempxml.set('bypass', str(self.bypass))
		tempxml.set('wet_dry_mix', str(self.wet_dry_mix))
		tempxml.set('pre_gain', str(self.pre_gain))
		tempxml.set('post_gain', str(self.post_gain))
		tempxml.set('mpe_enabled', str(self.mpe_enabled))
		tempxml.set('stream_processor_type', str(self.stream_processor_type))
		tempxml.set('program_index', str(self.program_index))
		if self.preset_name is not None: tempxml.set('preset_name', str(self.preset_name))
		tempxml.set('show_editor_preference', str(self.show_editor_preference))
		tempxml.set('plugin_window_x', str(self.plugin_window_x))
		tempxml.set('plugin_window_y', str(self.plugin_window_y))
		paramtempxml = ET.SubElement(tempxml, "cached_parameters")
		for env in self.cached_parameters: env.write(paramtempxml)
		if self.plugin is not None: self.plugin.write(tempxml)
		if self.plugin_xml_data is not None: tempxml.append(self.plugin_xml_data)

class zenbeats_signal_chain:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = 0
		self.index = 0
		self.gain = 1.0
		self.pan = 0.0
		self.tranpose = 0
		self.solo = 0
		self.mute = 0
		self.low_key_range = 0
		self.high_key_range = 127
		self.input_midi_channel = 1088044720
		self.target_midi_channel = 0
		self.signal_chain_type = 2
		self.midi_compression_low = 0
		self.midi_compression_high = 127
		self.midi_compression_ratio = 1.0
		self.midi_compression_full_on = 0
		self.stream_processors = []
		self.sub_track_master_instrument = None
		self.sub_track_audio_ch1 = None
		self.sub_track_audio_ch2 = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'index' in attrib: self.index = int(attrib['index'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'pan' in attrib: self.pan = float(attrib['pan'])
		if 'tranpose' in attrib: self.tranpose = int(attrib['tranpose'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'low_key_range' in attrib: self.low_key_range = int(attrib['low_key_range'])
		if 'high_key_range' in attrib: self.high_key_range = int(attrib['high_key_range'])
		if 'input_midi_channel' in attrib: self.input_midi_channel = int(attrib['input_midi_channel'])
		if 'target_midi_channel' in attrib: self.target_midi_channel = int(attrib['target_midi_channel'])
		if 'signal_chain_type' in attrib: self.signal_chain_type = int(attrib['signal_chain_type'])
		if 'midi_compression_low' in attrib: self.midi_compression_low = int(attrib['midi_compression_low'])
		if 'midi_compression_high' in attrib: self.midi_compression_high = int(attrib['midi_compression_high'])
		if 'midi_compression_ratio' in attrib: self.midi_compression_ratio = float(attrib['midi_compression_ratio'])
		if 'midi_compression_full_on' in attrib: self.midi_compression_full_on = int(attrib['midi_compression_full_on'])
		if 'sub_track_master_instrument' in attrib: self.sub_track_master_instrument = attrib['sub_track_master_instrument']
		if 'sub_track_audio_ch1' in attrib: self.sub_track_audio_ch1 = int(attrib['sub_track_audio_ch1'])
		if 'sub_track_audio_ch2' in attrib: self.sub_track_audio_ch2 = int(attrib['sub_track_audio_ch2'])

		for x_part in xml_data:
			if x_part.tag == 'stream_processor': self.stream_processors.append(zenbeats_stream_processor(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "signal_chain")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('index', str(self.index))
		tempxml.set('gain', str(self.gain))
		tempxml.set('pan', str(self.pan))
		tempxml.set('tranpose', str(self.tranpose))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute', str(self.mute))
		tempxml.set('low_key_range', str(self.low_key_range))
		tempxml.set('high_key_range', str(self.high_key_range))
		tempxml.set('input_midi_channel', str(self.input_midi_channel))
		tempxml.set('target_midi_channel', str(self.target_midi_channel))
		tempxml.set('signal_chain_type', str(self.signal_chain_type))
		tempxml.set('midi_compression_low', str(self.midi_compression_low))
		tempxml.set('midi_compression_high', str(self.midi_compression_high))
		tempxml.set('midi_compression_ratio', str(self.midi_compression_ratio))
		tempxml.set('midi_compression_full_on', str(self.midi_compression_full_on))
		if self.sub_track_master_instrument is not None: tempxml.set('sub_track_master_instrument', str(self.sub_track_master_instrument))
		if self.sub_track_audio_ch1 is not None: tempxml.set('sub_track_audio_ch1', str(self.sub_track_audio_ch1))
		if self.sub_track_audio_ch2 is not None: tempxml.set('sub_track_audio_ch2', str(self.sub_track_audio_ch2))
		for stream_processor in self.stream_processors: stream_processor.write(tempxml)

class zenbeats_send_track:
	def __init__(self, xml_data):
		self.send_track_uid = ''
		self.send_amount = ''
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'send_track_uid' in attrib: self.send_track_uid = attrib['send_track_uid']
		if 'send_amount' in attrib: self.send_amount = attrib['send_amount']

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "send_track")
		tempxml.set('send_track_uid', str(self.send_track_uid))
		tempxml.set('send_amount', str(self.send_amount))

class zenbeats_rack:
	def __init__(self, xml_data):
		self.version = misc.zenbeats_version()
		self.visual = misc.zenbeats_visual_info()
		self.uid = func.make_uuid()
		self.selected_child = -1
		self.gain = 0.5011872336272722
		self.force_mono = 0
		self.filter_low_cut = 0.0
		self.filter_high_cut = 1.0
		self.transpose = 0
		self.solo = 0
		self.mute_by_solo = 0
		self.mute = 0
		self.audio_output_left = 0
		self.audio_output_right = 1
		self.audio_output_aux1_left = -1
		self.audio_output_aux1_right = -1
		self.rack_type = 2
		self.phase_invert_audio_output = 0
		self.post_send = 1
		self.automation_set = automation.zenbeats_automation_set(None)
		self.signal_chain = zenbeats_signal_chain(None)
		self.audio_output_channel_left = None
		self.audio_output_channel_right = None
		self.send_tracks = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		self.visual.read(xml_data)
		self.version.read(xml_data)
		attrib = xml_data.attrib
		if 'uid' in attrib: self.uid = attrib['uid']
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'gain' in attrib: self.gain = float(attrib['gain'])
		if 'force_mono' in attrib: self.force_mono = int(attrib['force_mono'])
		if 'filter_low_cut' in attrib: self.filter_low_cut = float(attrib['filter_low_cut'])
		if 'filter_high_cut' in attrib: self.filter_high_cut = float(attrib['filter_high_cut'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])
		if 'solo' in attrib: self.solo = int(attrib['solo'])
		if 'mute_by_solo' in attrib: self.mute_by_solo = int(attrib['mute_by_solo'])
		if 'mute' in attrib: self.mute = int(attrib['mute'])
		if 'audio_output_left' in attrib: self.audio_output_left = int(attrib['audio_output_left'])
		if 'audio_output_right' in attrib: self.audio_output_right = int(attrib['audio_output_right'])
		if 'audio_output_aux1_left' in attrib: self.audio_output_aux1_left = int(attrib['audio_output_aux1_left'])
		if 'audio_output_aux1_right' in attrib: self.audio_output_aux1_right = int(attrib['audio_output_aux1_right'])
		if 'rack_type' in attrib: self.rack_type = int(attrib['rack_type'])
		if 'phase_invert_audio_output' in attrib: self.phase_invert_audio_output = int(attrib['phase_invert_audio_output'])
		if 'post_send' in attrib: self.post_send = int(attrib['post_send'])
		if 'audio_output_channel_left' in attrib: self.audio_output_channel_left = int(attrib['audio_output_channel_left'])
		if 'audio_output_channel_right' in attrib: self.audio_output_channel_right = int(attrib['audio_output_channel_right'])
		for x_part in xml_data:
			if x_part.tag == 'automation_set': self.automation_set.read(x_part)
			if x_part.tag == 'signal_chain': self.signal_chain.read(x_part)
			if x_part.tag == 'send_track': self.send_tracks.append(zenbeats_send_track(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "rack")
		self.version.write(tempxml)
		self.visual.write(tempxml)
		tempxml.set('uid', str(self.uid))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('gain', str(self.gain))
		tempxml.set('force_mono', str(self.force_mono))
		tempxml.set('filter_low_cut', str(self.filter_low_cut))
		tempxml.set('filter_high_cut', str(self.filter_high_cut))
		tempxml.set('transpose', str(self.transpose))
		tempxml.set('solo', str(self.solo))
		tempxml.set('mute_by_solo', str(self.mute_by_solo))
		tempxml.set('mute', str(self.mute))
		if self.audio_output_channel_left is not None: tempxml.set('audio_output_channel_left', str(self.audio_output_channel_left))
		if self.audio_output_channel_right is not None: tempxml.set('audio_output_channel_right', str(self.audio_output_channel_right))
		tempxml.set('audio_output_left', str(self.audio_output_left))
		tempxml.set('audio_output_right', str(self.audio_output_right))
		tempxml.set('audio_output_aux1_left', str(self.audio_output_aux1_left))
		tempxml.set('audio_output_aux1_right', str(self.audio_output_aux1_right))
		tempxml.set('rack_type', str(self.rack_type))
		tempxml.set('phase_invert_audio_output', str(self.phase_invert_audio_output))
		tempxml.set('post_send', str(self.post_send))
		for send_track in self.send_tracks: send_track.write(tempxml)
		self.signal_chain.write(tempxml)
		self.automation_set.write(tempxml)

class zenbeats_bank:
	def __init__(self, xml_data):
		self.version = 6
		self.selected_child = 0
		self.uid = ''
		self.racks = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		attrib = xml_data.attrib
		if 'version' in attrib: self.version = int(attrib['version'])
		if 'selected_child' in attrib: self.selected_child = int(attrib['selected_child'])
		if 'uid' in attrib: self.uid = attrib['uid']
		for x_part in xml_data:
			if x_part.tag == 'rack': self.racks.append(zenbeats_rack(x_part))

	def write(self, xml_data):
		tempxml = ET.SubElement(xml_data, "bank")
		tempxml.set('version', str(self.version))
		tempxml.set('selected_child', str(self.selected_child))
		tempxml.set('uid', str(self.uid))
		for rack in self.racks: rack.write(tempxml)

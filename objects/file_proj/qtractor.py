
from lxml import etree as ET

def set_value(xml_proj, name, val):
	tempxml = ET.SubElement(xml_proj, name)
	if val is not None: tempxml.text = str(val)
	return tempxml

# --------------------------------------------------------- CLIP ---------------------------------------------------------

class qtractor_clip_properties:
	def __init__(self, xmldata):
		self.name = ''
		self.start = 0
		self.offset = 0
		self.length = 0
		self.gain = 1
		self.panning = 0
		self.fade_in = 0
		self.fade_out = 0
		self.fade_in_type = ''
		self.fade_out_type = ''
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'name': self.name = xmlpart.text
			if xmlpart.tag == 'start': self.start = int(xmlpart.text)
			if xmlpart.tag == 'offset': self.offset = int(xmlpart.text)
			if xmlpart.tag == 'length': self.length = int(xmlpart.text)
			if xmlpart.tag == 'gain': self.gain = float(xmlpart.text)
			if xmlpart.tag == 'panning': self.panning = float(xmlpart.text)
			if xmlpart.tag == 'fade-in': 
				self.fade_in = int(xmlpart.text)
				self.fade_in_type = xmlpart.get('type')
			if xmlpart.tag == 'fade-out': 
				self.fade_out = int(xmlpart.text)
				self.fade_out_type = xmlpart.get('type')

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'name', self.name)
		set_value(tempxml, 'start', self.start)
		set_value(tempxml, 'offset', self.offset)
		set_value(tempxml, 'length', self.length)
		set_value(tempxml, 'gain', self.gain)
		set_value(tempxml, 'panning', self.panning)
		fade_in = set_value(tempxml, 'fade-in', self.fade_in)
		if self.fade_in_type: fade_in.set('type', self.fade_in_type)
		fade_out = set_value(tempxml, 'fade-out', self.fade_out)
		if self.fade_out_type: fade_out.set('type', self.fade_out_type)

class qtractor_clip_audioclip:
	def __init__(self, xmldata):
		self.filename = ''
		self.time_stretch = 1
		self.pitch_shift = 1
		self.wsola_time_stretch = 0
		self.wsola_quick_seek = 1
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'time-stretch': self.time_stretch = float(xmlpart.text)
			if xmlpart.tag == 'pitch-shift': self.pitch_shift = float(xmlpart.text)
			if xmlpart.tag == 'wsola-time-stretch': self.wsola_time_stretch = xmlpart.text
			if xmlpart.tag == 'wsola-quick-seek': self.wsola_quick_seek = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'audio-clip')
		set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'time-stretch', self.time_stretch)
		set_value(tempxml, 'pitch-shift', self.pitch_shift)
		set_value(tempxml, 'wsola-time-stretch', self.wsola_time_stretch)
		set_value(tempxml, 'wsola-quick-seek', self.wsola_quick_seek)

class qtractor_clip_midiclip:
	def __init__(self, xmldata):
		self.filename = ''
		self.track_channel = 1
		self.revision = 2
		self.editor_pos = ''
		self.editor_size = ''
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'track-channel': self.track_channel = xmlpart.text
			if xmlpart.tag == 'revision': self.revision = xmlpart.text
			if xmlpart.tag == 'editor-pos': self.editor_pos = xmlpart.text
			if xmlpart.tag == 'editor-size': self.editor_size = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'midi-clip')
		set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'track-channel', self.track_channel)
		set_value(tempxml, 'revision', self.revision)
		set_value(tempxml, 'editor-pos', self.editor_pos)
		set_value(tempxml, 'editor-size', self.editor_size)

class qtractor_clip:
	def __init__(self, xmldata):
		self.name = ''
		self.properties = qtractor_clip_properties(None)
		self.audioclip = None
		self.midiclip = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'name' in trackattrib: self.name = trackattrib['name']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'audio-clip': self.audioclip = qtractor_clip_audioclip(xmlpart)
			if xmlpart.tag == 'midi-clip': self.midiclip = qtractor_clip_midiclip(xmlpart)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'clip')
		tempxml.set('name', self.name)
		self.properties.write(tempxml)
		if self.audioclip: self.audioclip.write(tempxml)
		if self.midiclip: self.midiclip.write(tempxml)

# --------------------------------------------------------- PLUGINS ---------------------------------------------------------

class qtractor_plugin_param:
	def __init__(self, xmldata):
		self.index = ''
		self.name = ''
		self.value = '0'
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib
		if 'index' in trackattrib: self.index = trackattrib['index']
		if 'name' in trackattrib: self.name = trackattrib['name']
		self.value = xml_proj.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'param')
		tempxml.set('index', self.index)
		tempxml.set('name', self.name)
		tempxml.text = str(self.value)

class qtractor_plugin:
	def __init__(self, xmldata):
		self.type = ''
		self.filename = ''
		self.index = ''
		self.label = ''
		self.preset = ''
		self.direct_access_param = ''
		self.activated = ''
		self.params = []
		self.editor_pos = ''
		self.form_pos = ''
		self.configs = []
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'type' in trackattrib: self.type = trackattrib['type']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'filename': self.filename = xmlpart.text
			if xmlpart.tag == 'index': self.index = xmlpart.text
			if xmlpart.tag == 'label': self.label = xmlpart.text
			if xmlpart.tag == 'preset': self.preset = xmlpart.text
			if xmlpart.tag == 'direct-access-param': self.direct_access_param = xmlpart.text
			if xmlpart.tag == 'activated': self.activated = int(xmlpart.text)
			if xmlpart.tag == 'params':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'param': 
						self.params.append(qtractor_plugin_param(xmlinpart))
			if xmlpart.tag == 'configs':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'config': 
						self.configs.append([xmlinpart.get('key'), xmlinpart.get('type'), xmlinpart.text])
			if xmlpart.tag == 'editor-pos': self.editor_pos = xmlpart.text
			if xmlpart.tag == 'form-pos': self.form_pos = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'plugin')
		tempxml.set('type', self.type)
		set_value(tempxml, 'filename', self.filename)
		set_value(tempxml, 'index', self.index)
		set_value(tempxml, 'label', self.label)
		set_value(tempxml, 'preset', self.preset)
		set_value(tempxml, 'direct-access-param', self.direct_access_param)
		set_value(tempxml, 'activated', self.activated)
		configsxml = ET.SubElement(tempxml, 'configs')
		for c_key, c_type, c_value in self.configs:
			configxml = ET.SubElement(configsxml, 'config')
			configxml.set('key', str(c_key))
			if c_type: configxml.set('type', str(c_type))
			configxml.text = str(c_value)
		paramsxml = ET.SubElement(tempxml, 'params')
		for x in self.params: x.write(paramsxml)
		set_value(tempxml, 'editor-pos', self.editor_pos)
		set_value(tempxml, 'form-pos', self.form_pos)

# --------------------------------------------------------- CLIP ---------------------------------------------------------

class qtractor_track_properties:
	def __init__(self, xmldata):
		self.input_bus = ''
		self.output_bus = ''
		self.midi_omni = None
		self.midi_channel = None
		self.midi_bank_sel_method = None
		self.midi_drums = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'input-bus': self.input_bus = xmlpart.text
			if xmlpart.tag == 'output-bus': self.output_bus = xmlpart.text
			if xmlpart.tag == 'midi-omni': self.midi_omni = xmlpart.text
			if xmlpart.tag == 'midi-channel': self.midi_channel = xmlpart.text
			if xmlpart.tag == 'midi-bank-sel-method': self.midi_bank_sel_method = xmlpart.text
			if xmlpart.tag == 'midi-drums': self.midi_drums = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'input-bus', self.input_bus)
		set_value(tempxml, 'output-bus', self.output_bus)
		if self.midi_omni is not None: 
			set_value(tempxml, 'midi-omni', str(self.midi_omni))
		if self.midi_channel is not None: 
			set_value(tempxml, 'midi-channel', str(self.midi_channel))
		if self.midi_bank_sel_method is not None: 
			set_value(tempxml, 'midi-bank-sel-method', str(self.midi_bank_sel_method))
		if self.midi_drums is not None: 
			set_value(tempxml, 'midi-drums', str(self.midi_drums))

class qtractor_track_state:
	def __init__(self, xmldata):
		self.mute = 0
		self.solo = 0
		self.record = 0
		self.monitor = 0
		self.gain = 1
		self.panning = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'mute': self.mute = int(xmlpart.text)
			if xmlpart.tag == 'solo': self.solo = int(xmlpart.text)
			if xmlpart.tag == 'record': self.record = int(xmlpart.text)
			if xmlpart.tag == 'monitor': self.monitor = int(xmlpart.text)
			if xmlpart.tag == 'gain': self.gain = float(xmlpart.text)
			if xmlpart.tag == 'panning': self.panning = float(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'state')
		set_value(tempxml, 'mute', str(self.mute))
		set_value(tempxml, 'solo', str(self.solo))
		set_value(tempxml, 'record', str(self.record))
		set_value(tempxml, 'monitor', str(self.monitor))
		set_value(tempxml, 'gain', str(self.gain))
		set_value(tempxml, 'panning', str(self.panning))

class qtractor_track_view:
	def __init__(self, xmldata):
		self.height = 96
		self.background_color = None
		self.foreground_color = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'height': self.height = xmlpart.text
			if xmlpart.tag == 'background-color': self.background_color = xmlpart.text
			if xmlpart.tag == 'foreground-color': self.foreground_color = xmlpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'view')
		set_value(tempxml, 'height', str(self.height))
		set_value(tempxml, 'background-color', str(self.background_color))
		set_value(tempxml, 'foreground-color', str(self.foreground_color))

class qtractor_track:
	def __init__(self, xmldata):
		self.name = ''
		self.type = ''
		self.properties = qtractor_track_properties(None)
		self.state = qtractor_track_state(None)
		self.view = qtractor_track_view(None)
		self.clips = []
		self.plugins = []
		self.plug_audio_output_bus = None
		self.audio_output_auto_connect = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		trackattrib = xml_proj.attrib

		if 'name' in trackattrib: self.name = trackattrib['name']
		if 'type' in trackattrib: self.type = trackattrib['type']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'state': self.state.read(xmlpart)
			if xmlpart.tag == 'view': self.view.read(xmlpart)
			if xmlpart.tag == 'clips':
				for xmlinpart in xmlpart:
					self.clips.append(qtractor_clip(xmlinpart))
			if xmlpart.tag == 'plugins':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'plugin': 
						self.plugins.append(qtractor_plugin(xmlinpart))
					if xmlinpart.tag == 'audio-output-bus':
						self.plug_audio_output_bus = xmlinpart.text
					if xmlinpart.tag == 'audio-output-auto-connect':
						self.audio_output_auto_connect = xmlinpart.text

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'track')
		tempxml.set('name', self.name)
		tempxml.set('type', self.type)
		self.properties.write(tempxml)
		self.state.write(tempxml)
		self.view.write(tempxml)
		ET.SubElement(tempxml, 'controllers')
		clipsxml = ET.SubElement(tempxml, 'clips')
		for x in self.clips: x.write(clipsxml)
		pluginsxml = ET.SubElement(tempxml, 'plugins')
		for x in self.plugins: x.write(pluginsxml)
		if self.plug_audio_output_bus is not None: 
			set_value(pluginsxml, 'audio-output-bus', self.plug_audio_output_bus)
		if self.audio_output_auto_connect is not None: 
			set_value(pluginsxml, 'audio-output-auto-connect', self.audio_output_auto_connect)

# --------------------------------------------------------- PROJECT ---------------------------------------------------------

class qtractor_proj_properties:
	def __init__(self, xmldata):
		self.directory = ''
		self.description = ''
		self.sample_rate = 48000
		self.tempo = 110
		self.ticks_per_beat = 960
		self.beats_per_bar = 4
		self.beat_divisor = 2
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'directory': self.directory = xmlpart.text
			if xmlpart.tag == 'description': self.description = xmlpart.text
			if xmlpart.tag == 'sample-rate': self.sample_rate = int(xmlpart.text)
			if xmlpart.tag == 'tempo': self.tempo = int(xmlpart.text)
			if xmlpart.tag == 'ticks-per-beat': self.ticks_per_beat = int(xmlpart.text)
			if xmlpart.tag == 'beats-per-bar': self.beats_per_bar = int(xmlpart.text)
			if xmlpart.tag == 'beat-divisor': self.beat_divisor = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'properties')
		set_value(tempxml, 'directory', self.directory)
		set_value(tempxml, 'description', self.description)
		set_value(tempxml, 'sample-rate', self.sample_rate)
		set_value(tempxml, 'tempo', self.tempo)
		set_value(tempxml, 'ticks-per-beat', self.ticks_per_beat)
		set_value(tempxml, 'beats-per-bar', self.beats_per_bar)
		set_value(tempxml, 'beat-divisor', self.beat_divisor)

class qtractor_proj_state:
	def __init__(self, xmldata):
		self.loop_start = 0
		self.loop_end = 0
		self.punch_in = 0
		self.punch_out = 0
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'loop-start': self.loop_start = int(xmlpart.text)
			if xmlpart.tag == 'loop-end': self.loop_end = int(xmlpart.text)
			if xmlpart.tag == 'punch-in': self.punch_in = int(xmlpart.text)
			if xmlpart.tag == 'punch-out': self.punch_out = int(xmlpart.text)

	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'state')
		set_value(tempxml, 'loop-start', self.loop_start)
		set_value(tempxml, 'loop-end', self.loop_end)
		set_value(tempxml, 'punch-in', self.punch_in)
		set_value(tempxml, 'punch-out', self.punch_out)

class qtractor_proj_files:
	def __init__(self, xmldata):
		self.audio_list = {}
		self.midi_list = {}
		if xmldata is not None: self.read(xmldata)

	def read(self, xml_proj):
		for xmlpart in xml_proj:
			if xmlpart.tag == 'audio-list': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'file': 
						self.audio_list[xmlinpart.get('name')] = xmlinpart.text

			if xmlpart.tag == 'midi-list': 
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'file': 
						self.midi_list[xmlinpart.get('name')] = xmlinpart.text


	def write(self, in_xml):
		tempxml = ET.SubElement(in_xml, 'files')
		audio_list = ET.SubElement(tempxml, 'audio-list')
		for name, filename in self.audio_list.items():
			xmlfile = ET.SubElement(audio_list, 'file')
			xmlfile.set('name', name)
			xmlfile.text = filename

		midi_list = ET.SubElement(tempxml, 'midi-list')
		for name, filename in self.midi_list.items():
			xmlfile = ET.SubElement(midi_list, 'file')
			xmlfile.set('name', name)
			xmlfile.text = filename

class qtractor_project:
	def __init__(self):
		self.properties = qtractor_proj_properties(None)
		self.state = qtractor_proj_state(None)
		self.files = qtractor_proj_files(None)
		self.tracks = []
		self.name = ''
		self.version = ''

	def load_from_file(self, input_file):
		self.metadata = {}
		parser = ET.XMLParser()
		xml_data = ET.parse(input_file, parser)
		xml_proj = xml_data.getroot()
		if xml_proj == None: raise ProjectFileParserException('qtractor: no XML root found')

		trackattrib = xml_proj.attrib
		if 'name' in trackattrib: self.name = trackattrib['name']
		if 'version' in trackattrib: self.version = trackattrib['version']

		for xmlpart in xml_proj:
			if xmlpart.tag == 'properties': self.properties.read(xmlpart)
			if xmlpart.tag == 'state': self.state.read(xmlpart)
			if xmlpart.tag == 'files': self.files.read(xmlpart)
			if xmlpart.tag == 'tracks':
				for xmlinpart in xmlpart:
					if xmlinpart.tag == 'track':
						self.tracks.append(qtractor_track(xmlinpart))

		return True

	def write_to_file(self, output_file):
		xml_proj = ET.Element("session")

		xml_proj.set('name', self.name)
		xml_proj.set('version', self.version)
		self.properties.write(xml_proj)
		self.state.write(xml_proj)
		self.files.write(xml_proj)
		tracksxml = ET.SubElement(xml_proj, 'tracks')
		for x in self.tracks: x.write(tracksxml)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space=" ", level=0)
		outfile.write(output_file, doctype="<!DOCTYPE qtractorSession>")

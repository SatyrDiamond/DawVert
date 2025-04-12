# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import gzip
import base64
import xml.etree.ElementTree as ET

class muse_controller:
	def __init__(self):
		self.cur = 1
		self.color = ''
		self.visible = 0

	def read(self, xmltag):
		if 'cur' in xmltag.attrib: self.cur = float(xmltag.attrib['cur'])
		if 'color' in xmltag.attrib: self.color = xmltag.attrib['color']
		if 'visible' in xmltag.attrib: self.visible = int(xmltag.attrib['visible'])

	def write(self, xmltag, idnum):
		trackx = ET.SubElement(xmltag, "controller")
		trackx.set('id', str(idnum))
		trackx.set('cur', str(self.cur))
		trackx.set('color', self.color)
		trackx.set('visible', str(self.visible))

class muse_midi_event:
	def __init__(self):
		self.tick = 0
		self.len = 0
		self.a = 0
		self.b = 100

	def read(self, xmltag):
		if 'tick' in xmltag.attrib: self.tick = int(xmltag.attrib['tick'])
		if 'len' in xmltag.attrib: self.len = xmltag.attrib['len']
		if 'a' in xmltag.attrib: self.a = xmltag.attrib['a']
		if 'b' in xmltag.attrib: self.b = xmltag.attrib['b']

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "event")
		trackx.set('tick', str(self.tick))
		trackx.set('len', str(self.len))
		trackx.set('a', str(self.a))
		trackx.set('b', str(self.b))

class muse_poslen_audio:
	def __init__(self):
		self.sample = 0
		self.len = 0

	def read(self, xmltag):
		if 'sample' in xmltag.attrib: self.sample = int(xmltag.attrib['sample'])
		if 'len' in xmltag.attrib: self.len = xmltag.attrib['len']

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "poslen")
		trackx.set('sample', str(int(self.sample)))
		trackx.set('len', str(int(self.len)))

class muse_poslen:
	def __init__(self):
		self.tick = 0
		self.len = 0

	def read(self, xmltag):
		if 'tick' in xmltag.attrib: self.tick = int(xmltag.attrib['tick'])
		if 'len' in xmltag.attrib: self.len = xmltag.attrib['len']

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "poslen")
		trackx.set('tick', str(self.tick))
		trackx.set('len', str(self.len))

class muse_audio_event:
	def __init__(self):
		self.file = ''
		self.frame = 0
		self.poslen = muse_poslen_audio()
		self.stretchlist = []

	def read(self, xmltag):
		for xpart in xmltag:
			if xpart.tag == 'poslen': self.poslen.read(xpart)
			if xpart.tag == 'file': self.file = xpart.text
			if xpart.tag == 'frame': self.frame = int(xpart.text)
			if xpart.tag == 'stretchlist': self.stretchlist = [x.split(' ') for x in xpart.text.strip().split(',')]

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "event")
		self.poslen.write(trackx)
		ET.SubElement(trackx, 'frame').text = str(self.frame)
		ET.SubElement(trackx, 'file').text = self.file
		stretchtxt = [' '.join([str(n) for n in x]) for x in self.stretchlist]
		ET.SubElement(trackx, 'stretchlist').text = ','.join(stretchtxt)

class muse_audio_part:
	def __init__(self):
		self.name = ''
		self.selected = 0
		self.color = ''
		self.poslen = muse_poslen_audio()
		self.events = []

	def new_event(self):
		event_obj = muse_audio_event()
		self.events.append(event_obj)
		return event_obj

	def read(self, xmltag):
		for xpart in xmltag:
			if xpart.tag == 'name': self.name = xpart.text
			if xpart.tag == 'selected': self.selected = int(xpart.text)
			if xpart.tag == 'color': self.color = xpart.text
			if xpart.tag == 'poslen': self.poslen.read(xpart)
			if xpart.tag == 'event': 
				event_obj = self.new_event(self)
				event_obj.read(xpart)

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "part")
		ET.SubElement(trackx, 'name').text = str(self.name)
		self.poslen.write(trackx)
		ET.SubElement(trackx, 'selected').text = str(self.selected)
		ET.SubElement(trackx, 'color').text = str(self.color)
		for event_obj in self.events:
			event_obj.write(trackx)

class muse_midi_part:
	def __init__(self):
		self.name = ''
		self.selected = 0
		self.color = ''
		self.poslen = muse_poslen()
		self.events = []

	def read(self, xmltag):
		for xpart in xmltag:

			if xpart.tag == 'name': self.name = xpart.text
			if xpart.tag == 'selected': self.selected = int(xpart.text)
			if xpart.tag == 'color': self.color = xpart.text
			if xpart.tag == 'poslen': self.poslen.read(xpart)
			if xpart.tag == 'event': 
				event_obj = muse_midi_event()
				event_obj.read(xpart)
				self.events.append(event_obj)

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, "part")
		ET.SubElement(trackx, 'name').text = str(self.name)
		self.poslen.write(trackx)
		ET.SubElement(trackx, 'selected').text = str(self.selected)
		ET.SubElement(trackx, 'color').text = str(self.color)
		for event_obj in self.events:
			event_obj.write(trackx)

class muse_geometry:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.w = 0
		self.h = 0

	def read(self, xmltag):
		if 'x' in xmltag.attrib: self.x = int(xmltag.attrib['x'])
		if 'y' in xmltag.attrib: self.y = int(xmltag.attrib['y'])
		if 'w' in xmltag.attrib: self.w = int(xmltag.attrib['w'])
		if 'h' in xmltag.attrib: self.h = int(xmltag.attrib['h'])

	def write(self, xmltag, name):
		trackx = ET.SubElement(xmltag, name)
		trackx.set('x', str(self.x))
		trackx.set('y', str(self.y))
		trackx.set('w', str(self.w))
		trackx.set('h', str(self.h))

class muse_control:
	def __init__(self):
		self.name = ''
		self.val = 0

	def read(self, xmltag):
		if 'name' in xmltag.attrib: self.name = xmltag.attrib['name']
		if 'val' in xmltag.attrib: self.val = float(xmltag.attrib['val'])

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, 'control')
		trackx.set('name', str(self.name))
		trackx.set('val', str(self.val))

class muse_plugin:
	def __init__(self):
		self.file = None
		self.label = ''
		self.channel = 1
		self.uri = None
		self.controls = []
		self.geometry = muse_geometry()
		self.nativeGeometry = muse_geometry()
		self.custom_data = None

	def read(self, xmltag):
		if 'file' in xmltag.attrib: self.file = xmltag.attrib['file']
		if 'label' in xmltag.attrib: self.label = xmltag.attrib['label']
		if 'channel' in xmltag.attrib: self.channel = xmltag.attrib['channel']
		if 'uri' in xmltag.attrib: self.uri = xmltag.attrib['uri']

		for xpart in xmltag:
			if xpart.tag == 'geometry': self.geometry.read(xpart)
			if xpart.tag == 'nativeGeometry': self.nativeGeometry.read(xpart)
			if xpart.tag == 'customData': self.custom_data = base64.b64decode(xpart.text)
			if xpart.tag == 'control': 
				control_obj = muse_control() 
				control_obj.read(xpart)
				self.controls.append(control_obj)



	def write(self, xmltag):
		pluginx = ET.SubElement(xmltag, "plugin")
		if self.file: pluginx.set('file', str(self.file))
		if self.uri: pluginx.set('uri', str(self.uri))
		pluginx.set('label', str(self.label))
		pluginx.set('channel', str(self.channel))
		if self.custom_data:
			ET.SubElement(pluginx, 'customData').text = base64.b64encode(self.custom_data).decode()
		for control_obj in self.controls:
			control_obj.write(pluginx)
		self.geometry.write(pluginx, 'geometry')
		self.nativeGeometry.write(pluginx, 'nativeGeometry')

class muse_track:
	def __init__(self, itype):
		self.type = itype
		self.name = ''
		self.record = 0
		self.mute = 0
		self.solo = 0
		self.off = 0
		self.channels = 0
		self.height = 24
		self.locked = 0
		self.recMonitor = 0
		self.color = ''
		self.device = 0
		self.channel = 0
		self.locked = 0
		self.transposition = 0
		self.velocity = 0
		self.delay = 0
		self.len = 100
		self.compression = 100
		self.automation = 1
		self.clef = 0
		self.recMonitor = 0
		self.selected = 1
		self.selectionOrder = 0
		self.prefader = 0
		self.sendMetronome = 1
		self.gain = 1

		self.controllers = {}
		self.note_parts = []
		self.audio_parts = []
		self.plugins = []

		self.synth_synthType = 'MESS'
		self.synth_class = 'vam'
		self.synth_label = 'vam'
		self.synth_openFlags = 3
		self.synth_port = 0
		self.synth_guiVisible = 0
		self.synth_nativeGuiVisible = 0
		self.synth_customData = None
		self.synth_params = []

	def add_controller(self, in_id):
		controller_obj = muse_controller()
		self.controllers[in_id] = controller_obj
		return controller_obj

	def read(self, xmltag):
		for xpart in xmltag:

			if xpart.tag == 'name': self.name = xpart.text
			if xpart.tag == 'record': self.record = int(xpart.text)
			if xpart.tag == 'mute': self.mute = int(xpart.text)
			if xpart.tag == 'solo': self.solo = int(xpart.text)
			if xpart.tag == 'off': self.off = int(xpart.text)
			if xpart.tag == 'channels': self.channels = int(xpart.text)
			if xpart.tag == 'height': self.height = int(xpart.text)
			if xpart.tag == 'locked': self.locked = int(xpart.text)
			if xpart.tag == 'recMonitor': self.recMonitor = int(xpart.text)
			if xpart.tag == 'color': self.color = xpart.text
			if xpart.tag == 'device': self.device = int(xpart.text)
			if xpart.tag == 'channel': self.channel = int(xpart.text)
			if xpart.tag == 'locked': self.locked = int(xpart.text)
			if xpart.tag == 'transposition': self.transposition = int(xpart.text)
			if xpart.tag == 'velocity': self.velocity = int(xpart.text)
			if xpart.tag == 'delay': self.delay = int(xpart.text)
			if xpart.tag == 'len': self.len = int(xpart.text)
			if xpart.tag == 'compression': self.compression = int(xpart.text)
			if xpart.tag == 'automation': self.automation = int(xpart.text)
			if xpart.tag == 'clef': self.clef = int(xpart.text)
			if xpart.tag == 'selected': self.selected = int(xpart.text)
			if xpart.tag == 'selectionOrder': self.selectionOrder = int(xpart.text)
			if xpart.tag == 'prefader': self.prefader = int(xpart.text)
			if xpart.tag == 'sendMetronome': self.sendMetronome = int(xpart.text)
			if xpart.tag == 'gain': self.gain = float(xpart.text)

			if self.type == "SynthI": 
				if xpart.tag == 'synthType': self.synth_synthType = xpart.text
				if xpart.tag == 'class': self.synth_class = xpart.text
				if xpart.tag == 'label': self.synth_label = xpart.text
				if xpart.tag == 'openFlags': self.synth_openFlags = int(xpart.text)
				if xpart.tag == 'port': self.synth_port = int(xpart.text)
				if xpart.tag == 'guiVisible': self.synth_guiVisible = int(xpart.text)
				if xpart.tag == 'nativeGuiVisible': self.synth_nativeGuiVisible = int(xpart.text)
				if xpart.tag == 'customData': self.synth_customData = base64.b64decode(xpart.text)
				if xpart.tag == 'param': self.synth_params.append(xpart.text)

			if xpart.tag == 'controller': 
				controller_obj = muse_controller()
				controller_obj.read(xpart)
				self.controllers[int(xpart.get('id'))] = controller_obj

			if xpart.tag == 'part':
				if self.type in ["miditrack", "newdrumtrack"]: 
					part_obj = muse_midi_part()
					part_obj.read(xpart)
					self.note_parts.append(part_obj)
				if self.type in ["wavetrack"]: 
					part_obj = muse_audio_part()
					part_obj.read(xpart)
					self.audio_parts.append(part_obj)

			if xpart.tag == 'plugin':
				plugin_obj = muse_plugin()
				plugin_obj.read(xpart)
				self.plugins.append(plugin_obj)

	def write(self, xmltag):
		trackx = ET.SubElement(xmltag, self.type)
		ET.SubElement(trackx, 'name').text = str(self.name)
		ET.SubElement(trackx, 'record').text = str(self.record)
		ET.SubElement(trackx, 'mute').text = str(self.mute)
		ET.SubElement(trackx, 'solo').text = str(self.solo)
		ET.SubElement(trackx, 'off').text = str(self.off)
		ET.SubElement(trackx, 'channels').text = str(self.channels)
		ET.SubElement(trackx, 'height').text = str(self.height)
		ET.SubElement(trackx, 'locked').text = str(self.locked)

		if self.type == 'AudioOutput':
			ET.SubElement(trackx, 'selectionOrder').text = str(self.selectionOrder)
			ET.SubElement(trackx, 'prefader').text = str(self.prefader)
			ET.SubElement(trackx, 'sendMetronome').text = str(self.sendMetronome)
			ET.SubElement(trackx, 'automation').text = str(self.automation)
			ET.SubElement(trackx, 'gain').text = str(self.gain)
			ET.SubElement(trackx, 'recMonitor').text = str(self.recMonitor)
			ET.SubElement(trackx, 'selected').text = str(self.selected)


		if self.type == 'wavetrack':
			ET.SubElement(trackx, 'recMonitor').text = str(self.recMonitor)
			ET.SubElement(trackx, 'prefader').text = str(self.prefader)
			ET.SubElement(trackx, 'sendMetronome').text = str(self.sendMetronome)
			ET.SubElement(trackx, 'automation').text = str(self.automation)
			ET.SubElement(trackx, 'gain').text = str(self.gain)


		if self.type == 'SynthI':
			ET.SubElement(trackx, 'recMonitor').text = str(self.recMonitor)
			ET.SubElement(trackx, 'prefader').text = str(self.prefader)
			ET.SubElement(trackx, 'sendMetronome').text = str(self.sendMetronome)
			ET.SubElement(trackx, 'automation').text = str(self.automation)
			ET.SubElement(trackx, 'gain').text = str(self.gain)


		if self.type in ["miditrack", "newdrumtrack"]:
			ET.SubElement(trackx, 'color').text = str(self.color)
			ET.SubElement(trackx, 'device').text = str(self.device)
			ET.SubElement(trackx, 'channel').text = str(self.channel)
			ET.SubElement(trackx, 'locked').text = str(self.locked)
			ET.SubElement(trackx, 'transposition').text = str(self.transposition)
			ET.SubElement(trackx, 'velocity').text = str(self.velocity)
			ET.SubElement(trackx, 'delay').text = str(self.delay)
			ET.SubElement(trackx, 'len').text = str(self.len)
			ET.SubElement(trackx, 'compression').text = str(self.compression)
			ET.SubElement(trackx, 'automation').text = str(self.automation)
			ET.SubElement(trackx, 'clef').text = str(self.clef)

		for plugin_obj in self.plugins:
			plugin_obj.write(trackx)

		for cnum, controller_obj in self.controllers.items():
			controller_obj.write(trackx, cnum)

		if self.type in ["miditrack", "newdrumtrack"]:
			for part_obj in self.note_parts:
				part_obj.write(trackx)

		if self.type in ["wavetrack"]:
			for part_obj in self.audio_parts:
				part_obj.write(trackx)

		if self.type == 'SynthI':
			ET.SubElement(trackx, 'synthType').text = str(self.synth_synthType)
			ET.SubElement(trackx, 'class').text = str(self.synth_class)
			ET.SubElement(trackx, 'label').text = str(self.synth_label)
			ET.SubElement(trackx, 'openFlags').text = str(self.synth_openFlags)
			ET.SubElement(trackx, 'port').text = str(self.synth_port)
			ET.SubElement(trackx, 'guiVisible').text = str(self.synth_guiVisible)
			ET.SubElement(trackx, 'nativeGuiVisible').text = str(self.synth_nativeGuiVisible)
			if self.synth_customData:
				ET.SubElement(trackx, 'customData').text = base64.b64encode(self.synth_customData).decode()
			for param in self.synth_params:
				ET.SubElement(trackx, 'param').text = param

class muse_route:
	def __init__(self):
		self.channel = -1
		self.output_track = -1
		self.output_mport = -1
		self.output_name = ''
		self.output_type = 0
		self.output_devtype = 0
		self.input_mport = -1
		self.input_track = -1
		self.input_name = ''
		self.input_type = 0
		self.input_devtype = 0

	def read(self, xmltag):
		if 'channel' in xmltag.attrib: self.channel = int(xmltag.attrib['channel'])

		source_attr = {}
		dest_attr = {}
		for x_part in xmltag:
			if x_part.tag == 'source': source_attr = x_part.attrib
			if x_part.tag == 'dest': dest_attr = x_part.attrib

		if 'track' in source_attr: self.input_track = int(source_attr['track'])
		if 'type' in source_attr: self.input_type = int(source_attr['type'])
		if 'name' in source_attr: self.input_name = source_attr['name']
		if 'devtype' in source_attr: self.input_devtype = int(source_attr['devtype'])
		if 'mport' in source_attr: self.input_mport = int(source_attr['mport'])

		if 'track' in dest_attr: self.output_track = int(dest_attr['track'])
		if 'type' in dest_attr: self.output_type = int(dest_attr['type'])
		if 'name' in dest_attr: self.output_name = dest_attr['name']
		if 'devtype' in dest_attr: self.output_devtype = int(dest_attr['devtype'])
		if 'mport' in dest_attr: self.output_mport = int(dest_attr['mport'])

	def write(self, xmltag):
		routex = ET.SubElement(xmltag, 'Route')

		if self.channel != -1: routex.set('channel', str(self.channel))

		sourcex = ET.SubElement(routex, 'source')
		if self.input_mport != -1: sourcex.set('mport', str(self.input_mport))
		if self.input_track != -1: sourcex.set('track', str(self.input_track))
		if self.input_type: sourcex.set('type', str(self.input_type))
		if self.input_devtype: sourcex.set('devtype', str(self.input_devtype))
		if self.input_name: sourcex.set('name', str(self.input_name))

		destx = ET.SubElement(routex, 'dest')
		if self.output_mport != -1: destx.set('mport', str(self.output_mport))
		if self.output_track != -1: destx.set('track', str(self.output_track))
		if self.output_type: destx.set('type', str(self.output_type))
		if self.output_devtype: destx.set('devtype', str(self.output_devtype))
		if self.output_name: destx.set('name', str(self.output_name))

class muse_tempo:
	def __init__(self):
		self.at = 0
		self.tick = 0
		self.val = 0

	def read(self, xmltag):
		if 'at' in xmltag.attrib: self.at = int(xmltag.attrib['at'])
		for x_part in xmltag:
			if x_part.tag == 'tick': self.tick = int(x_part.text)
			if x_part.tag == 'val': self.val = int(x_part.text)

	def write(self, xmltag):
		tempox = ET.SubElement(xmltag, "tempo")
		tempox.set('at', str(self.at))
		ET.SubElement(tempox, 'tick').text = str(self.tick)
		ET.SubElement(tempox, 'val').text = str(self.val)

class muse_tempolist:
	def __init__(self):
		self.fix = 0
		self.events = []

	def read(self, xmltag):
		if 'fix' in xmltag.attrib: self.fix = int(xmltag.attrib['fix'])
		for x_part in xmltag:
			if x_part.tag == 'tempo':
				tempo_obj = muse_tempo()
				tempo_obj.read(x_part)
				self.events.append(tempo_obj)

	def write(self, xmltag):
		tlx = ET.SubElement(xmltag, "tempolist")
		tlx.set('fix', str(self.fix))
		for tempo_obj in self.events:
			tempo_obj.write(tlx)

class muse_sig:
	def __init__(self):
		self.at = 0
		self.tick = 0
		self.nom = 4
		self.denom = 4

	def read(self, xmltag):
		if 'at' in xmltag.attrib: self.at = int(xmltag.attrib['at'])
		for x_part in xmltag:
			if x_part.tag == 'tick': self.tick = int(x_part.text)
			if x_part.tag == 'nom': self.nom = int(x_part.text)
			if x_part.tag == 'denom': self.denom = int(x_part.text)

	def write(self, xmltag):
		tempox = ET.SubElement(xmltag, "sig")
		tempox.set('at', str(self.at))
		ET.SubElement(tempox, 'tick').text = str(self.tick)
		ET.SubElement(tempox, 'nom').text = str(self.nom)
		ET.SubElement(tempox, 'denom').text = str(self.denom)

class muse_key:
	def __init__(self):
		self.at = 0
		self.tick = 0
		self.val = 0
		self.minor = 0

	def read(self, xmltag):
		if 'at' in xmltag.attrib: self.at = int(xmltag.attrib['at'])
		for x_part in xmltag:
			if x_part.tag == 'tick': self.tick = int(x_part.text)
			if x_part.tag == 'val': self.val = int(x_part.text)
			if x_part.tag == 'minor': self.minor = int(x_part.text)

	def write(self, xmltag):
		tempox = ET.SubElement(xmltag, "key")
		tempox.set('at', str(self.at))
		ET.SubElement(tempox, 'tick').text = str(self.tick)
		ET.SubElement(tempox, 'val').text = str(self.val)
		ET.SubElement(tempox, 'minor').text = str(self.minor)

class muse_song:
	def __init__(self):
		self.tracks = []
		self.info = ''
		self.showinfo = 1
		self.cpos = 0
		self.rpos = -1
		self.lpos = 0
		self.master = 1
		self.loop = 0
		self.punchin = 0
		self.punchout = 0
		self.record = 0
		self.solo = 0
		self.recmode = 0
		self.cycle = 0
		self.click = 0
		self.quantize = 0
		self.len = 1000000
		self.follow = 1
		self.midiDivision = 384
		self.sampleRate = 48000
		self.routes = []
		self.tempolist = muse_tempolist()
		self.siglist = []
		self.keylist = []
		self.marker = {}

	def add_track(self, tracktype):
		track_obj = muse_track(tracktype)
		self.tracks.append(track_obj)
		return track_obj

	def add_route(self):
		route_obj = muse_route()
		self.routes.append(route_obj)
		return route_obj

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for x_part in x_root:
			if x_part.tag == 'song':
				for x_song in x_part:
					#print(x_song.tag)
					if x_song.tag == 'info': self.info = x_song.text
					if x_song.tag == 'showinfo': self.showinfo = int(x_song.text)
					if x_song.tag == 'cpos': self.cpos = int(x_song.text)
					if x_song.tag == 'rpos': self.rpos = int(x_song.text)
					if x_song.tag == 'lpos': self.lpos = int(x_song.text)
					if x_song.tag == 'master': self.master = int(x_song.text)
					if x_song.tag == 'loop': self.loop = int(x_song.text)
					if x_song.tag == 'punchin': self.punchin = int(x_song.text)
					if x_song.tag == 'punchout': self.punchout = int(x_song.text)
					if x_song.tag == 'record': self.record = int(x_song.text)
					if x_song.tag == 'solo': self.solo = int(x_song.text)
					if x_song.tag == 'recmode': self.recmode = int(x_song.text)
					if x_song.tag == 'cycle': self.cycle = int(x_song.text)
					if x_song.tag == 'click': self.click = int(x_song.text)
					if x_song.tag == 'quantize': self.quantize = int(x_song.text)
					if x_song.tag == 'len': self.len = int(x_song.text)
					if x_song.tag == 'follow': self.follow = int(x_song.text)
					if x_song.tag == 'midiDivision': self.midiDivision = int(x_song.text)
					if x_song.tag == 'sampleRate': self.sampleRate = int(x_song.text)
					if x_song.tag in ['AudioOutput', 'miditrack', 'SynthI', 'newdrumtrack', 'wavetrack']: 
						track_obj = muse_track(x_song.tag)
						track_obj.read(x_song)
						self.tracks.append(track_obj)
					if x_song.tag == 'Route': 
						route_obj = muse_route()
						route_obj.read(x_song)
						self.routes.append(route_obj)
					if x_song.tag == 'tempolist': self.tempolist.read(x_song)
					if x_song.tag == 'siglist': 
						for x_siglist in x_song:
							if x_siglist.tag == 'sig':
								sig_obj = muse_sig()
								sig_obj.read(x_siglist)
								self.siglist.append(sig_obj)
					if x_song.tag == 'keylist': 
						for x_keylist in x_song:
							if x_keylist.tag == 'key':
								key_obj = muse_key()
								key_obj.read(x_keylist)
								self.keylist.append(key_obj)
					if x_song.tag == 'marker': 
						markerpos = x_song.attrib['tick'] if 'tick' in x_song.attrib else 0
						self.marker[markerpos] = x_song.attrib['name'] if 'name' in x_song.attrib else ''





	def save_to_file(self, out_file):
		muse_proj = ET.Element("muse")
		muse_proj.set('version', "3.4")
		songx = ET.SubElement(muse_proj, "song")

		ET.SubElement(songx, 'info').text = str(self.info) if self.info else ' '
		ET.SubElement(songx, 'showinfo').text = str(self.showinfo)
		ET.SubElement(songx, 'cpos').text = str(self.cpos)
		ET.SubElement(songx, 'rpos').text = str(self.rpos)
		ET.SubElement(songx, 'lpos').text = str(self.lpos)
		ET.SubElement(songx, 'master').text = str(self.master)
		ET.SubElement(songx, 'loop').text = str(self.loop)
		ET.SubElement(songx, 'punchin').text = str(self.punchin)
		ET.SubElement(songx, 'punchout').text = str(self.punchout)
		ET.SubElement(songx, 'record').text = str(self.record)
		ET.SubElement(songx, 'solo').text = str(self.solo)
		ET.SubElement(songx, 'recmode').text = str(self.recmode)
		ET.SubElement(songx, 'cycle').text = str(self.cycle)
		ET.SubElement(songx, 'click').text = str(self.click)
		ET.SubElement(songx, 'quantize').text = str(self.quantize)
		ET.SubElement(songx, 'len').text = str(self.len)
		ET.SubElement(songx, 'follow').text = str(self.follow)
		ET.SubElement(songx, 'midiDivision').text = str(self.midiDivision)
		ET.SubElement(songx, 'sampleRate').text = str(self.sampleRate)

		for track_obj in self.tracks:
			track_obj.write(songx)

		for track_obj in self.routes:
			track_obj.write(songx)

		self.tempolist.write(songx)

		x_siglist = ET.SubElement(songx, 'siglist')
		for mrk_obj in self.siglist: mrk_obj.write(x_siglist)

		x_keylist = ET.SubElement(songx, 'keylist')
		for mrk_obj in self.keylist: mrk_obj.write(x_keylist)

		for pos, name in self.marker.items(): 
			marker_x = ET.SubElement(songx, 'marker')
			marker_x.set('tick', str(pos))
			marker_x.set('name', name)

		outfile = ET.ElementTree(muse_proj)
		ET.indent(outfile)
		outfile.write(out_file, xml_declaration = True)

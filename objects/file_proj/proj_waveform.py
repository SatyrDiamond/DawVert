# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class waveform_transport:
	def __init__(self):
		self.looping = 0
		self.endToEnd = 1
		self.position = 0.5
		self.scrubInterval = 0.1581309034119588
		self.loopPoint1 = -1
		self.loopPoint2 = -1
		self.start = -1

	def load(self, xmldata):
		looping = xmldata.get('looping')
		endToEnd = xmldata.get('endToEnd')
		position = xmldata.get('position')
		scrubInterval = xmldata.get('scrubInterval')
		start = xmldata.get('start')
		loopPoint1 = xmldata.get('loopPoint1')
		loopPoint2 = xmldata.get('loopPoint2')
		if endToEnd != None: self.endToEnd = int(endToEnd)
		if position != None: self.position = float(position)
		if scrubInterval != None: self.scrubInterval = float(scrubInterval)
		if start != None: self.start = float(start)
		if looping != None: self.looping = int(start)
		if loopPoint1 != None: self.loopPoint1 = float(loopPoint1)
		if loopPoint2 != None: self.loopPoint2 = float(loopPoint2)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TRANSPORT")
		tempxml.set('endToEnd', str(self.endToEnd))
		tempxml.set('position', str(self.position))
		tempxml.set('scrubInterval', str(self.scrubInterval))
		tempxml.set('looping', str(int(self.looping)))
		if self.start >= 0: tempxml.set('start', str(self.start))
		if self.loopPoint1 >= 0: tempxml.set('loopPoint1', str(self.loopPoint1))
		if self.loopPoint2 >= 0: tempxml.set('loopPoint2', str(self.loopPoint2))

class waveform_macroparameters:
	def __init__(self):
		self.id_num = 0
		self.used = False

	def load(self, xmldata):
		self.used = True
		id_num = xmldata.get('id')
		if id_num != None: self.id_num = int(id_num)

	def write(self, xmldata):
		if self.used:
			tempxml = ET.SubElement(xmldata, "MACROPARAMETERS")
			tempxml.set('id', str(self.id_num))

class waveform_seq_pitch:
	def __init__(self):
		self.sequence = {}

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'PITCH': self.sequence[float(subxml.get('startBeat'))] = int(subxml.get('pitch'))

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PITCHSEQUENCE")
		for pos, pitch in self.sequence.items():
			pxml = ET.SubElement(tempxml, "PITCH")
			pxml.set('startBeat', str(pos))
			pxml.set('pitch', str(pitch))

class waveform_seq_tempo:
	def __init__(self):
		self.tempo = {}
		self.timesig = {}

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'TEMPO':
				curve = subxml.get('curve')
				self.tempo[float(subxml.get('startBeat'))] = [float(subxml.get('bpm')), str(curve) if curve != None else 1]
			if subxml.tag == 'TIMESIG':
				self.timesig[float(subxml.get('startBeat'))] = [int(subxml.get('numerator')), int(subxml.get('denominator'))]

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TEMPOSEQUENCE")
		for pos, data in self.tempo.items():
			bpm, curve = data
			pxml = ET.SubElement(tempxml, "TEMPO")
			pxml.set('startBeat', str(pos))
			pxml.set('bpm', str(bpm))
			pxml.set('curve', str(curve))
		for pos, data in self.timesig.items():
			numerator, denominator = data
			pxml = ET.SubElement(tempxml, "TIMESIG")
			pxml.set('numerator', str(numerator))
			pxml.set('denominator', str(denominator))
			pxml.set('startBeat', str(pos))

class waveform_automationcurve:
	def __init__(self):
		self.paramid = None
		self.points = []

	def load(self, xmldata):
		self.paramid = xmldata.get('paramID')
		for subxml in xmldata:
			if subxml.tag == 'POINT': 
				curve = float(subxml.get('c')) if 'c' in subxml.attrib else 0
				self.points.append([float(subxml.get('t')), float(subxml.get('v')), curve if curve else None])

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "AUTOMATIONCURVE")
		if self.paramid: tempxml.set('paramID', self.paramid)
		for t,v,c in self.points:
			pxml = ET.SubElement(tempxml, "POINT")
			pxml.set('t', str(t))
			pxml.set('v', str(v))
			if c: pxml.set('c', str(c))

class waveform_plugin:
	def __init__(self):
		self.plugtype = ''
		self.windowLocked = 0
		self.id_num = 0
		self.enabled = 1
		self.presetDirty = 0
		self.windowX = 0
		self.windowY = 0
		self.width = 0
		self.height = 0
		self.quickParamName = ''
		self.params = {}
		self.macroparameters = waveform_macroparameters()
		self.automationcurves = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'type': self.plugtype = v
			elif n == 'windowLocked': self.windowLocked = int(v)
			elif n == 'id': self.id_num = int(v)
			elif n == 'enabled': self.enabled = int(v)
			elif n == 'presetDirty': self.presetDirty = int(v)
			elif n == 'windowX': self.windowX = int(v)
			elif n == 'windowY': self.windowY = int(v)
			elif n == 'width': self.width = int(v)
			elif n == 'height': self.height = int(v)
			elif n == 'quickParamName': self.quickParamName = v
			else: self.params[n] = v
		for xmlpart in xmldata:
			if xmlpart.tag == 'MACROPARAMETERS': self.macroparameters.load(xmlpart)
			if xmlpart.tag == 'AUTOMATIONCURVE': 
				autocurve_obj = waveform_automationcurve()
				autocurve_obj.load(xmlpart)
				self.automationcurves.append(autocurve_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PLUGIN")
		if self.plugtype: tempxml.set('type', str(self.plugtype))
		if self.windowLocked: tempxml.set('windowLocked', str(self.windowLocked))
		if self.id_num: tempxml.set('id', str(self.id_num))
		if self.enabled: tempxml.set('enabled', str(self.enabled))
		if self.presetDirty: tempxml.set('presetDirty', str(self.presetDirty))
		if self.windowX: tempxml.set('windowX', str(self.windowX))
		if self.windowY: tempxml.set('windowY', str(self.windowY))
		if self.width: tempxml.set('width', str(self.width))
		if self.height: tempxml.set('height', str(self.height))
		for n, v in self.params.items():
			if ':' not in n:
				tempxml.set(n, str(v))
		for c in self.automationcurves:
			c.write(tempxml)
		self.macroparameters.write(tempxml)
		ET.SubElement(tempxml, "MODIFIERASSIGNMENTS")

class waveform_outputdevices:
	def __init__(self):
		self.devices = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'DEVICE': self.devices.append(subxml.attrib)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "OUTPUTDEVICES")
		for device in self.devices:
			devxml = ET.SubElement(tempxml, "DEVICE")
			for n, v in device.items(): devxml.set(n, str(v))

class waveform_foldertrack:
	def __init__(self):
		self.id_num = 0
		self.height = 35.41053828354546
		self.expanded = 0
		self.tracks = []
		self.plugins = []
		self.macroparameters = waveform_macroparameters()
		self.name = None
		self.colour = None

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'height': self.height = float(v)
			elif n == 'expanded': self.expanded = int(v)
			elif n == 'name': self.name = v
			elif n == 'colour': self.colour = v

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			if subxml.tag == 'TRACK':
				track_obj = waveform_track()
				track_obj.load(subxml)
				self.tracks.append(track_obj)
			if subxml.tag == 'PLUGIN':
				plugin_obj = waveform_plugin()
				plugin_obj.load(subxml)
				self.plugins.append(plugin_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "FOLDERTRACK")
		tempxml.set('id', str(self.id_num))
		tempxml.set('height', str(self.height))
		tempxml.set('expanded', str(self.expanded))
		self.macroparameters.write(tempxml)
		for track_obj in self.tracks:
			track_obj.write(tempxml)
		for plugin_obj in self.plugins:
			plugin_obj.write(tempxml)
		if self.name: tempxml.set('name', self.name)
		if self.colour: tempxml.set('colour', self.colour)


class waveform_control:
	def __init__(self):
		self.pos = 0
		self.ctype = 0
		self.val = 0
		self.metadata = 0

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'b': self.pos = float(v)
			if n == 'type': self.ctype = int(v)
			if n == 'val': self.val = int(v)
			if n == 'metadata': self.metadata = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CONTROL")
		tempxml.set('b', str(self.pos))
		tempxml.set('type', str(self.ctype))
		tempxml.set('val', str(self.val))
		tempxml.set('metadata', str(self.metadata))

class waveform_note:
	def __init__(self):
		self.pos = 0
		self.key = 0
		self.dur = 0
		self.vel = 0
		self.chan = 0
		self.auto = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'p': self.key = int(v)
			if n == 'b': self.pos = float(v)
			if n == 'l': self.dur = float(v)
			if n == 'v': self.vel = int(v)
			if n == 'c': self.chan = int(v)

		for subxml in xmldata:
			if subxml.tag not in self.auto:
				self.auto[subxml.tag] = {}
			if subxml.attrib:
				self.auto[subxml.tag][float(subxml.attrib['b'])] = float(subxml.attrib['v'])


	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "NOTE")
		tempxml.set('p', str(self.key))
		tempxml.set('b', str(self.pos))
		tempxml.set('l', str(self.dur))
		tempxml.set('v', str(self.vel))
		tempxml.set('c', str(self.chan))

		for a_name, a_val in self.auto.items():
			for c_pos, c_val in a_val.items():
				a_xml = ET.SubElement(tempxml, a_name)
				a_xml.set('p', str(c_pos))
				a_xml.set('v', str(c_val))

class waveform_sequence:
	def __init__(self):
		self.notes = []
		self.controls = []

	def load(self, xmldata):
		for subxml in xmldata:
			if subxml.tag == 'NOTE':
				note_obj = waveform_note()
				note_obj.load(subxml)
				self.notes.append(note_obj)
			if subxml.tag == 'CONTROL':
				control_obj = waveform_control()
				control_obj.load(subxml)
				self.controls.append(control_obj)

	def write(self, xmldata):
		seq_xml = ET.SubElement(xmldata, "SEQUENCE")
		seq_xml.set('ver', '1')
		seq_xml.set('channelNumber', '1')
		for note_obj in self.notes:
			note_obj.write(seq_xml)
		for control_obj in self.controls:
			control_obj.write(seq_xml)

class waveform_midiclip:
	def __init__(self):
		self.name = 'New MIDI Clip'
		self.start = 0
		self.length = 0
		self.offset = 0
		self.id_num = 0
		self.sync = 0
		self.colour = 'ff4cff4c'
		self.currentTake = 0
		self.mute = 0
		self.speed = 1.0
		self.volDb = 0.0
		self.originalLength = 0
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.sequence = waveform_sequence()

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'name': self.name = v
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'id_num': self.id_num = float(v)
			elif n == 'sync': self.sync = float(v)
			elif n == 'colour': self.colour = v
			elif n == 'mute': self.mute = int(v)
			elif n == 'currentTake': self.currentTake = int(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'volDb': self.volDb = float(v)
			elif n == 'originalLength': self.originalLength = float(v)
			elif n == 'loopStartBeats': self.loopStartBeats = float(v)
			elif n == 'loopLengthBeats': self.loopLengthBeats = float(v)
			else: print('[waveform] midiclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'SEQUENCE': self.sequence.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "MIDICLIP")
		tempxml.set('name', self.name)
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('sync', str(self.sync))
		tempxml.set('colour', self.colour)
		tempxml.set('currentTake', str(self.currentTake))
		tempxml.set('speed', str(self.speed))
		tempxml.set('volDb', str(self.volDb))
		if self.mute: tempxml.set('mute', str(self.mute))
		tempxml.set('originalLength', str(self.originalLength))
		tempxml.set('loopStartBeats', str(self.loopStartBeats))
		tempxml.set('loopLengthBeats', str(self.loopLengthBeats))
		ET.SubElement(tempxml, "QUANTISATION")
		ET.SubElement(tempxml, "GROOVE")
		self.sequence.write(tempxml)

class waveform_loopinfo:
	def __init__(self):
		self.rootNote = -1
		self.numBeats = 0.0
		self.oneShot = 0
		self.denominator = 4
		self.numerator = 4
		self.bpm = 0.0
		self.inMarker = 0
		self.outMarker = -1

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'rootNote': self.rootNote = int(v)
			elif n == 'numBeats': self.numBeats = float(v)
			elif n == 'oneShot': self.oneShot = int(v)
			elif n == 'denominator': self.denominator = int(v)
			elif n == 'numerator': self.numerator = int(v)
			elif n == 'bpm': self.bpm = float(v)
			elif n == 'inMarker': self.inMarker = int(v)
			elif n == 'outMarker': self.outMarker = int(v)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "LOOPINFO")
		tempxml.set('rootNote', str(self.rootNote))
		tempxml.set('numBeats', str(self.numBeats))
		tempxml.set('oneShot', str(self.oneShot))
		tempxml.set('denominator', str(self.denominator))
		tempxml.set('numerator', str(self.numerator))
		tempxml.set('bpm', str(self.bpm))
		tempxml.set('inMarker', str(self.inMarker))
		tempxml.set('outMarker', str(self.outMarker))

class waveform_audioclip_fx:
	def __init__(self):
		self.fx_type = ''
		self.plugin = waveform_plugin()

	def load(self, xmldata):
		fx_type = xmldata.get('type')
		if fx_type: self.fx_type = fx_type
		for subxml in xmldata:
			if subxml.tag == 'PLUGIN': self.plugin.load(subxml)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "EFFECT")
		tempxml.set('type', str(self.fx_type))
		self.plugin.write(tempxml)

class waveform_audioclip:
	def __init__(self):
		self.name = "qd - sleep"
		self.start = 0
		self.length = 0
		self.offset = 0.0
		self.id_num = 0
		self.source = ""
		self.sync = 0
		self.elastiqueMode = 0
		self.pan = 0.0
		self.colour = "ff00ff00"
		self.proxyAllowed = 1
		self.resamplingQuality = "lagrange"
		self.autoTempo = 1

		self.fadeIn = 0.0
		self.fadeOut = 0.0
		self.speed = 1.0
		self.showingTakes = 0
		self.gain = 0.0
		self.mute = 0
		self.channels = "L R"
		self.fadeInType = 1
		self.fadeOutType = 1
		self.autoCrossfade = 0
		self.fadeInBehaviour = 0
		self.fadeOutBehaviour = 0
		self.loopStart = 0.0
		self.loopLength = 0.0
		self.loopStartBeats = 0.0
		self.loopLengthBeats = 0.0
		self.transpose = 0
		self.pitchChange = 0.0
		self.beatSensitivity = 0.5
		self.elastiqueOptions = "1/0/0/0/64"
		self.autoPitch = 0
		self.autoPitchMode = 0
		self.isReversed = 0
		self.autoDetectBeats = 0
		self.warpTime = 0
		self.effectsVisible = 1

		self.loopinfo = waveform_loopinfo()
		self.effects = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'name': self.name = str(v)
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'source': self.source = str(v)
			elif n == 'sync': self.sync = int(v)
			elif n == 'elastiqueMode': self.elastiqueMode = int(v)
			elif n == 'pan': self.pan = float(v)
			elif n == 'colour': self.colour = str(v)
			elif n == 'proxyAllowed': self.proxyAllowed = int(v)
			elif n == 'resamplingQuality': self.resamplingQuality = str(v)
			elif n == 'autoTempo': self.autoTempo = int(v)

			elif n == 'fadeIn': self.fadeIn = float(v)
			elif n == 'fadeOut': self.fadeOut = float(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'showingTakes': self.showingTakes = int(v)
			elif n == 'gain': self.gain = float(v)
			elif n == 'mute': self.mute = int(v)
			elif n == 'channels': self.channels = str(v)
			elif n == 'fadeInType': self.fadeInType = int(v)
			elif n == 'fadeOutType': self.fadeOutType = int(v)
			elif n == 'autoCrossfade': self.autoCrossfade = int(v)
			elif n == 'fadeInBehaviour': self.fadeInBehaviour = int(v)
			elif n == 'fadeOutBehaviour': self.fadeOutBehaviour = int(v)
			elif n == 'loopStart': self.loopStart = float(v)
			elif n == 'loopLength': self.loopLength = float(v)
			elif n == 'loopStartBeats': self.loopStartBeats = float(v)
			elif n == 'loopLengthBeats': self.loopLengthBeats = float(v)
			elif n == 'transpose': self.transpose = int(v)
			elif n == 'pitchChange': self.pitchChange = float(v)
			elif n == 'beatSensitivity': self.beatSensitivity = float(v)
			elif n == 'elastiqueOptions': self.elastiqueOptions = str(v)
			elif n == 'autoPitch': self.autoPitch = int(v)
			elif n == 'autoPitchMode': self.autoPitchMode = int(v)
			elif n == 'isReversed': self.isReversed = int(v)
			elif n == 'autoDetectBeats': self.autoDetectBeats = int(v)
			elif n == 'warpTime': self.warpTime = int(v)
			elif n == 'effectsVisible': self.effectsVisible = int(v)
			else: print('[waveform] audioclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'LOOPINFO': self.loopinfo.load(subxml)
			if subxml.tag == 'EFFECTS': 
				for fxxml in subxml:
					afx_obj = waveform_audioclip_fx()
					afx_obj.load(fxxml)
					self.effects.append(afx_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "AUDIOCLIP")
		tempxml.set('name', str(self.name))
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('id', str(self.id_num))
		tempxml.set('source', str(self.source))
		tempxml.set('sync', str(self.sync))
		tempxml.set('elastiqueMode', str(self.elastiqueMode))
		tempxml.set('pan', str(self.pan))
		tempxml.set('colour', str(self.colour))
		tempxml.set('proxyAllowed', str(self.proxyAllowed))
		tempxml.set('resamplingQuality', str(self.resamplingQuality))
		tempxml.set('autoTempo', str(self.autoTempo))

		if self.fadeIn != 0: tempxml.set('fadeIn', str(self.fadeIn))
		if self.fadeOut != 0: tempxml.set('fadeOut', str(self.fadeOut))
		if self.speed != 1: tempxml.set('speed', str(self.speed))
		if self.showingTakes != 0: tempxml.set('showingTakes', str(self.showingTakes))
		if self.gain != 0: tempxml.set('gain', str(self.gain))
		if self.mute != 0: tempxml.set('mute', str(self.mute))
		if self.channels != "L R": tempxml.set('channels', str(self.channels))
		if self.fadeInType != 1: tempxml.set('fadeInType', str(self.fadeInType))
		if self.fadeOutType != 1: tempxml.set('fadeOutType', str(self.fadeOutType))
		if self.autoCrossfade != 0: tempxml.set('autoCrossfade', str(self.autoCrossfade))
		if self.fadeInBehaviour != 0: tempxml.set('fadeInBehaviour', str(self.fadeInBehaviour))
		if self.fadeOutBehaviour != 0: tempxml.set('fadeOutBehaviour', str(self.fadeOutBehaviour))
		if self.loopStart != 0: tempxml.set('loopStart', str(self.loopStart))
		if self.loopLength != 0: tempxml.set('loopLength', str(self.loopLength))
		if self.loopStartBeats != 0: tempxml.set('loopStartBeats', str(self.loopStartBeats))
		if self.loopLengthBeats != 0: tempxml.set('loopLengthBeats', str(self.loopLengthBeats))
		if self.transpose != 0: tempxml.set('transpose', str(self.transpose))
		if self.pitchChange != 0: tempxml.set('pitchChange', str(self.pitchChange))
		if self.beatSensitivity != 0.5: tempxml.set('beatSensitivity', str(self.beatSensitivity))
		if self.elastiqueOptions != "1/0/0/0/64": tempxml.set('elastiqueOptions', str(self.elastiqueOptions))
		if self.autoPitch != 0: tempxml.set('autoPitch', str(self.autoPitch))
		if self.autoPitchMode != 0: tempxml.set('autoPitchMode', str(self.autoPitchMode))
		if self.isReversed != 0: tempxml.set('isReversed', str(self.isReversed))
		if self.autoDetectBeats != 0: tempxml.set('autoDetectBeats', str(self.autoDetectBeats))
		if self.warpTime != 0: tempxml.set('warpTime', str(self.warpTime))
		if self.effectsVisible != 1: tempxml.set('effectsVisible', str(self.effectsVisible))

		self.loopinfo.write(tempxml)

		if self.effects:
			effects = ET.SubElement(tempxml, "EFFECTS")
			for afx_obj in self.effects:
				afx_obj.write(effects)


class waveform_stepclip_channel:
	def __init__(self):
		self.channel = 1
		self.note = 36
		self.velocity = 96
		self.name = ''

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'channel': self.channel = int(v)
			if n == 'note': self.note = int(v)
			if n == 'velocity': self.velocity = int(v)
			if n == 'name': self.name = v

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "CHANNEL")
		tempxml.set('channel', str(self.channel))
		tempxml.set('note', str(self.note))
		tempxml.set('velocity', str(self.velocity))
		tempxml.set('name', str(self.name))

class waveform_stepclip_pattern:
	def __init__(self):
		self.numNotes = 16
		self.noteLength = 0.25
		self.data = {}

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'numNotes': self.numNotes = int(v)
			if n == 'noteLength': self.noteLength = float(v)

		channum = 0
		for subxml in xmldata:
			if subxml.tag == 'CHANNEL':
				patdata = subxml.get('pattern')
				if patdata not in ['0', None]:
					self.data[channum] = patdata
				channum += 1

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "PATTERN")
		tempxml.set('numNotes', str(self.numNotes))
		tempxml.set('noteLength', str(self.noteLength))

		for n in range(max(self.data.keys())+1):
			chanxml = ET.SubElement(tempxml, "CHANNEL")
			if n in self.data: chanxml.set('pattern', self.data[n])
			else: chanxml.set('pattern', '0')

class waveform_stepclip:
	def __init__(self):
		self.id_num = 0
		self.name = ''
		self.start = 0
		self.length = 0
		self.offset = 0
		self.sequence = 0
		self.colour = 'ffff0000'
		self.repeatSequence = 1
		self.volDb = 0
		self.speed = 1
		self.source = ''
		self.sync = 0
		self.showingTakes = 0
		self.mute = 0
		self.channels = []
		self.patterns = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'name': self.name = str(v)
			elif n == 'start': self.start = float(v)
			elif n == 'length': self.length = float(v)
			elif n == 'offset': self.offset = float(v)
			elif n == 'sequence': self.sequence = int(v)
			elif n == 'colour': self.colour = str(v)
			elif n == 'repeatSequence': self.repeatSequence = int(v)
			elif n == 'volDb': self.volDb = float(v)
			elif n == 'speed': self.speed = float(v)
			elif n == 'source': self.source = str(v)
			elif n == 'sync': self.sync = int(v)
			elif n == 'showingTakes': self.showingTakes = int(v)
			elif n == 'mute': self.mute = int(v)
			else: print('[waveform] stepclip: unimplemented attrib: '+n)

		for subxml in xmldata:
			if subxml.tag == 'CHANNELS':
				for chanxml in subxml:
					if chanxml.tag == 'CHANNEL':
						chan_obj = waveform_stepclip_channel()
						chan_obj.load(chanxml)
						self.channels.append(chan_obj)

		for subxml in xmldata:
			if subxml.tag == 'PATTERNS':
				for chanxml in subxml:
					if chanxml.tag == 'PATTERN':
						pat_obj = waveform_stepclip_pattern()
						pat_obj.load(chanxml)
						self.patterns.append(pat_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "STEPCLIP")
		tempxml.set('id', str(self.id_num))
		if self.name: tempxml.set('name', str(self.name))
		tempxml.set('start', str(self.start))
		tempxml.set('length', str(self.length))
		tempxml.set('offset', str(self.offset))
		tempxml.set('sequence', str(self.sequence))
		tempxml.set('colour', str(self.colour))
		tempxml.set('repeatSequence', str(self.repeatSequence))
		tempxml.set('volDb', str(self.volDb))
		tempxml.set('speed', str(self.speed))
		tempxml.set('source', str(self.source))
		tempxml.set('sync', str(self.sync))
		tempxml.set('showingTakes', str(self.showingTakes))
		tempxml.set('mute', str(self.mute))
		if self.channels:
			chanxml = ET.SubElement(tempxml, "CHANNELS")
			for chan_obj in self.channels:
				chan_obj.write(chanxml)
		if self.patterns:
			patxml = ET.SubElement(tempxml, "PATTERNS")
			for chan_obj in self.patterns:
				chan_obj.write(patxml)

class waveform_track:
	def __init__(self):
		self.name = ''
		self.id_num = 0
		self.mute = 0
		self.solo = 0
		self.midiVProp = 0.28125
		self.midiVOffset = 0.359375
		self.colour = 'ffffaa00'
		self.height = 35.41053828354546
		self.plugins = []
		self.macroparameters = waveform_macroparameters()
		self.outputdevices = waveform_outputdevices()
		self.midiclips = []
		self.audioclips = []
		self.stepclips = []

	def load(self, xmldata):
		for n, v in xmldata.attrib.items():
			if n == 'id': self.id_num = int(v)
			elif n == 'midiVProp': self.midiVProp = float(v)
			elif n == 'midiVOffset': self.midiVOffset = float(v)
			elif n == 'colour': self.colour = v
			elif n == 'name': self.name = v
			elif n == 'height': self.height = float(v)
			elif n == 'mute': self.mute = int(v)
			elif n == 'solo': self.solo = int(v)

		for subxml in xmldata:
			if subxml.tag == 'MACROPARAMETERS': self.macroparameters.load(subxml)
			if subxml.tag == 'PLUGIN':
				plugin_obj = waveform_plugin()
				plugin_obj.load(subxml)
				self.plugins.append(plugin_obj)
			if subxml.tag == 'OUTPUTDEVICES':
				self.outputdevices.load(subxml)
			if subxml.tag == 'MIDICLIP':
				midiclip_obj = waveform_midiclip()
				midiclip_obj.load(subxml)
				self.midiclips.append(midiclip_obj)
			if subxml.tag == 'AUDIOCLIP':
				audioclip_obj = waveform_audioclip()
				audioclip_obj.load(subxml)
				self.audioclips.append(audioclip_obj)
			if subxml.tag == 'STEPCLIP':
				stepclip_obj = waveform_stepclip()
				stepclip_obj.load(subxml)
				self.stepclips.append(stepclip_obj)

	def write(self, xmldata):
		tempxml = ET.SubElement(xmldata, "TRACK")
		tempxml.set('id', str(self.id_num))
		tempxml.set('midiVProp', str(self.midiVProp))
		tempxml.set('midiVOffset', str(self.midiVOffset))
		tempxml.set('colour', str(self.colour))
		tempxml.set('height', str(self.height))
		if self.name: tempxml.set('name', str(self.name))
		if self.mute: tempxml.set('mute', str(self.mute))
		if self.solo: tempxml.set('solo', str(self.solo))
		self.macroparameters.write(tempxml)
		ET.SubElement(tempxml, "MODIFIERS")
		for audioclip_obj in self.audioclips: audioclip_obj.write(tempxml)
		for stepclip_obj in self.stepclips: stepclip_obj.write(tempxml)
		for plugin_obj in self.plugins: plugin_obj.write(tempxml)
		for midiclip_obj in self.midiclips: midiclip_obj.write(tempxml)
		self.outputdevices.write(tempxml)

class waveform_edit:
	def __init__(self):
		self.appVersion = None
		self.projectID = None
		self.creationTime = None
		self.lastSignificantChange = None
		self.modifiedBy = None
		self.transport = waveform_transport()
		self.macroparameters = waveform_macroparameters()
		self.pitchsequence = waveform_seq_pitch()
		self.temposequence = waveform_seq_tempo()
		self.clicktrack = 0.6
		self.id3vorbismetadata = {}
		self.mastervolume = waveform_plugin()
		self.masterplugins = []
		self.tracks = []

	def load_from_file(self, input_file):
		parser = ET.XMLParser(recover=True, encoding='utf-8')
		xml_data = ET.parse(input_file, parser)

		x_EDIT = xml_data.getroot()
		if x_EDIT == None: raise ProjectFileParserException('waveform_edit: no XML root found')

		self.appVersion = x_EDIT.get('appVersion')
		self.projectID = x_EDIT.get('projectID')
		self.creationTime = x_EDIT.get('creationTime')
		self.lastSignificantChange = x_EDIT.get('lastSignificantChange')
		self.modifiedBy = x_EDIT.get('modifiedBy')

		for xmlpart in x_EDIT:
			#print(xmlpart.tag)

			if xmlpart.tag == 'TRANSPORT': self.transport.load(xmlpart)
			elif xmlpart.tag == 'MACROPARAMETERS': self.macroparameters.load(xmlpart)
			elif xmlpart.tag == 'PITCHSEQUENCE': self.pitchsequence.load(xmlpart)
			elif xmlpart.tag == 'TEMPOSEQUENCE': self.temposequence.load(xmlpart)
			elif xmlpart.tag == 'CLICKTRACK':
				level = xmlpart.get('level')
				if level: self.clicktrack = float(level)
			elif xmlpart.tag == 'ID3VORBISMETADATA': self.id3vorbismetadata = xmlpart.attrib
			elif xmlpart.tag == 'MASTERVOLUME':
				for subxml in xmlpart:
					if subxml.tag == 'PLUGIN': self.mastervolume.load(subxml)
			elif xmlpart.tag == 'MASTERPLUGINS':
				for subxml in xmlpart:
					if subxml.tag == 'PLUGIN':
						t_plug = waveform_plugin()
						t_plug.load(subxml)
						self.masterplugins.append(t_plug)
			elif xmlpart.tag == 'TRACK':
				track_obj = waveform_track()
				track_obj.load(xmlpart)
				self.tracks.append(track_obj)
			elif xmlpart.tag == 'FOLDERTRACK':
				track_obj = waveform_foldertrack()
				track_obj.load(xmlpart)
				self.tracks.append(track_obj)

			#else:
			#	print(xmlpart.tag)
		return True


	def save_to_file(self, output_file):
		wf_proj = ET.Element("EDIT")
		if self.appVersion: wf_proj.set('appVersion', self.appVersion)
		if self.projectID: wf_proj.set('projectID', self.projectID)
		if self.creationTime: wf_proj.set('creationTime', self.creationTime)
		if self.lastSignificantChange: wf_proj.set('lastSignificantChange', self.lastSignificantChange)
		if self.modifiedBy: wf_proj.set('modifiedBy', self.modifiedBy)

		self.transport.write(wf_proj)
		self.macroparameters.write(wf_proj)
		self.pitchsequence.write(wf_proj)
		self.temposequence.write(wf_proj)
		ET.SubElement(wf_proj, "VIDEO")
		ET.SubElement(wf_proj, "AUTOMAPXML")
		wf_click = ET.SubElement(wf_proj, "CLICKTRACK")
		wf_click.set('level', str(self.clicktrack))
		id3_xml = ET.SubElement(wf_proj, "ID3VORBISMETADATA")
		for n, v in self.id3vorbismetadata.items(): id3_xml.set(n, str(v))
		wf_mv = ET.SubElement(wf_proj, "MASTERVOLUME")
		self.mastervolume.write(wf_mv)
		ET.SubElement(wf_proj, "RACKS")
		wf_mp = ET.SubElement(wf_proj, "MASTERPLUGINS")
		for plugin_obj in self.masterplugins:
			plugin_obj.write(wf_mp)
		ET.SubElement(wf_proj, "AUXBUSNAMES")

		ET.SubElement(wf_proj, "INPUTDEVICES")
		ET.SubElement(wf_proj, "TRACKCOMPS")
		ET.SubElement(wf_proj, "ARADOCUMENT")
		ET.SubElement(wf_proj, "CONTROLLERMAPPINGS")

		for track_obj in self.tracks:
			track_obj.write(wf_proj)

		outfile = ET.ElementTree(wf_proj)
		ET.indent(outfile)
		outfile.write(output_file, encoding='utf-8', xml_declaration = True)


#testin = waveform_edit()
#testin.load_from_file(
#'G:\\Projects\\dawproj_reverse/fefs Edit 3.tracktionedit'
#)

#testin.save_to_file(
#'G:\\Projects\\dawproj_reverse/out.tracktionedit'
#)
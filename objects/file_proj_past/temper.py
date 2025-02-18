# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class metaevent_key:
	def __init__(self):
		self.td = 0
		self.k_end_time = 0
		self.k_type = 0
		self.k_root = 0
		self.k_lo_bits = 0
		self.k_hi_bits = 0
		self.k_label = ''

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "k-end-time" in xmldata.attrib: cls.k_end_time = int(xmldata.attrib['k-end-time'])
		if "k-type" in xmldata.attrib: cls.k_type = int(xmldata.attrib['k-type'])
		if "k-root" in xmldata.attrib: cls.k_root = int(xmldata.attrib['k-root'])
		if "k-lo-bits" in xmldata.attrib: cls.k_lo_bits = int(xmldata.attrib['k-lo-bits'])
		if "k-hi-bits" in xmldata.attrib: cls.k_hi_bits = int(xmldata.attrib['k-hi-bits'])
		if "k-label" in xmldata.attrib: cls.k_label = xmldata.attrib['k-label']
		return cls

class metaevent_bpm:
	def __init__(self):
		self.td = 0
		self.bpm = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "bpm" in xmldata.attrib: cls.bpm = int(xmldata.attrib['bpm'])
		return cls

class metaevent_meter:
	def __init__(self):
		self.td = 0
		self.measure = 0
		self.beats = 0
		self.beat_value = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "measure" in xmldata.attrib: cls.measure = int(xmldata.attrib['measure'])
		if "beats" in xmldata.attrib: cls.beats = int(xmldata.attrib['beats'])
		if "beat-value" in xmldata.attrib: cls.beat_value = int(xmldata.attrib['beat-value'])
		return cls

class event_note:
	def __init__(self):
		self.td = 0
		self.d = 0
		self.p = ''
		self.v = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "d" in xmldata.attrib: cls.d = int(xmldata.attrib['d'])
		if "p" in xmldata.attrib: cls.p = xmldata.attrib['p']
		if "v" in xmldata.attrib: cls.v = int(xmldata.attrib['v'])
		return cls

class event_aftertouch:
	def __init__(self):
		self.td = 0
		self.v = 0
		self.ct = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "v" in xmldata.attrib: cls.v = float(xmldata.attrib['v'])
		if "ct" in xmldata.attrib: cls.ct = int(xmldata.attrib['ct'])
		return cls

class event_patch:
	def __init__(self):
		self.td = 0
		self.v = 0
		self.ct = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "v" in xmldata.attrib: cls.v = int(xmldata.attrib['v'])
		if "ct" in xmldata.attrib: cls.ct = int(xmldata.attrib['ct'])
		return cls

class event_pitch:
	def __init__(self):
		self.td = 0
		self.v = 0
		self.ct = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "v" in xmldata.attrib: cls.v = float(xmldata.attrib['v'])
		if "ct" in xmldata.attrib: cls.ct = int(xmldata.attrib['ct'])
		return cls

class event_control:
	def __init__(self):
		self.td = 0
		self.n = 0
		self.v = 0
		self.ct = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "n" in xmldata.attrib: cls.n = int(xmldata.attrib['n'])
		if "v" in xmldata.attrib: cls.v = float(xmldata.attrib['v'])
		if "ct" in xmldata.attrib: cls.ct = int(xmldata.attrib['ct'])
		return cls

class temper_phrase:
	def __init__(self):
		self.td = 0
		self.d = 0
		self.events = []

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "d" in xmldata.attrib: cls.d = int(xmldata.attrib['d'])

		cls.events = []
		for xmlpart in xmldata:
			if xmlpart.tag == 'note': cls.events.append(event_note.fromxml(xmlpart))
			if xmlpart.tag == 'patch': cls.events.append(event_patch.fromxml(xmlpart))
			if xmlpart.tag == 'ca': cls.events.append(event_aftertouch.fromxml(xmlpart))
			if xmlpart.tag == 'cp': cls.events.append(event_pitch.fromxml(xmlpart))
			if xmlpart.tag == 'cm': cls.events.append(event_control.fromxml(xmlpart))

		return cls

class event_audio:
	def __init__(self):
		self.td = 0
		self.file = 0
		self.end = 0
		self.off = 0
		self.flags = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "file" in xmldata.attrib: cls.file = xmldata.attrib['file']
		if "end" in xmldata.attrib: cls.end = int(xmldata.attrib['end'])
		if "off" in xmldata.attrib: cls.off = int(xmldata.attrib['off'])
		if "flags" in xmldata.attrib: cls.flags = int(xmldata.attrib['flags'])
		return cls

class temper_track:
	def __init__(self):
		self.name = ''
		self.customname = ''
		self.channel = 0
		self.sync = 0
		self.phrases = []
		self.audios = []

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "name" in xmldata.attrib: cls.name = xmldata.attrib['name']
		if "custom-name" in xmldata.attrib: cls.name = xmldata.attrib['custom-name']
		if "channel" in xmldata.attrib: cls.channel = int(xmldata.attrib['channel'])
		if "sync" in xmldata.attrib: cls.sync = float(xmldata.attrib['sync'])

		cls.phrases = []
		cls.audios = []
		for xmlpart in xmldata:
			if xmlpart.tag == 'phrase':
				cls.phrases.append(temper_phrase.fromxml(xmlpart))
			if xmlpart.tag == 'audio':
				cls.audios.append(event_audio.fromxml(xmlpart))

		return cls


class temper_song:
	def __init__(self):
		self.meta_track = []
		self.track = []

	def load_from_file(self, input_file):
		parser = ET.XMLParser(recover=True, encoding='utf-8')
		xml_data = ET.parse(input_file, parser)
		xml_musseq = xml_data.getroot()
		if xml_musseq == None: raise ProjectFileParserException('temper: no XML root found')

		for xmlpart in xml_musseq:
			#print(xmlpart)
			if xmlpart.tag == 'meta-track':
				for subxml in xmlpart:
					if subxml.tag == 'key': self.meta_track.append(metaevent_key.fromxml(subxml))
					if subxml.tag == 'tempo': self.meta_track.append(metaevent_bpm.fromxml(subxml))
					if subxml.tag == 'meter': self.meta_track.append(metaevent_meter.fromxml(subxml))
			if xmlpart.tag == 'track':
				self.track.append(temper_track.fromxml(xmlpart))
		#print(self.track)
		return True
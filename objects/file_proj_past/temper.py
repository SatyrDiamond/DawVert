# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

# ============================================= metaevent ============================================= 

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

# ============================================= event ============================================= 

class event_note:
	def __init__(self):
		self.td = 0
		self.d = 0
		self.p = ''
		self.v = 0
		self.r = 0

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "d" in xmldata.attrib: cls.d = int(xmldata.attrib['d'])
		if "p" in xmldata.attrib: cls.p = xmldata.attrib['p']
		if "v" in xmldata.attrib: cls.v = int(xmldata.attrib['v'])
		if "r" in xmldata.attrib: cls.r = int(xmldata.attrib['r'])
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

# ============================================= clips ============================================= 

class temper_clip_ui:
	def __init__(self):
		self.name = None
		self.color_bg = None
		self.color_fg = None

	@classmethod
	def fromxml(cls, xmldata):
		cls.name = None
		cls.color_bg = None
		cls.color_fg = None
		cnum=0
		for xmlpart in xmldata:
			if xmlpart.tag == 's': 
				cls.name = xmlpart.get('v')
			if xmlpart.tag == 'c': 
				color = [xmlpart.get('r'), xmlpart.get('g'), xmlpart.get('b')]
				if None in color: color = None
				else: color = [int(x) for x in color]
				if cnum==0: cls.color_bg = color
				elif cnum==1: cls.color_fg = color
				cnum += 1
		return cls

class temper_phrase:
	def __init__(self):
		self.td = 0
		self.d = 0
		self.events = []
		self.ui = None

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
			if xmlpart.tag == 'ui': cls.ui = temper_clip_ui.fromxml(xmlpart)
		return cls

class event_audio:
	def __init__(self):
		self.td = 0
		self.file = 0
		self.end = 0
		self.off = 0
		self.flags = 0
		self.ui = None

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "td" in xmldata.attrib: cls.td = int(xmldata.attrib['td'])
		if "file" in xmldata.attrib: cls.file = xmldata.attrib['file']
		if "end" in xmldata.attrib: cls.end = int(xmldata.attrib['end'])
		if "off" in xmldata.attrib: cls.off = int(xmldata.attrib['off'])
		if "flags" in xmldata.attrib: cls.flags = int(xmldata.attrib['flags'])
		for xmlpart in xmldata:
			if xmlpart.tag == 'ui': cls.ui = temper_clip_ui.fromxml(xmlpart)
		return cls

class temper_keynames_keyname:
	def __init__(self):
		self.key = ''
		self.name = ''

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "key" in xmldata.attrib: cls.key = xmldata.attrib['key']
		if "name" in xmldata.attrib: cls.name = xmldata.attrib['name']
		return cls

class temper_keynames:
	def __init__(self):
		self.maps = []
		self.name = None

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "n" in xmldata.attrib: cls.name = xmldata.attrib['n']
		for xp in xmldata:
			if xp.tag == 'map':
				cls.maps.append(temper_keynames_keyname.fromxml(xp))
		return cls

# ============================================= project ============================================= 

class temper_track_metrics_part:
	def __init__(self):
		self.s = ''
		self.n = ''
		self.h = -1
		self.fcfg = b''

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "s" in xmldata.attrib: cls.s = xmldata.attrib['s']
		if "n" in xmldata.attrib: cls.n = xmldata.attrib['n']
		if "h" in xmldata.attrib: cls.h = int(xmldata.attrib['h'])
		if "fcfg" in xmldata.attrib: 
			cls.fcfg = xmldata.attrib['fcfg']
			cls.fcfg = bytes.fromhex(cls.fcfg)
		return cls

# ============================================= track ============================================= 

class temper_track:
	def __init__(self):
		self.name = ''
		self.customname = ''
		self.channel = 0
		self.sync = 0
		self.mode = 0
		self.phrases = []
		self.audios = []

	@classmethod
	def fromxml(cls, xmldata):
		cls = cls()
		if "name" in xmldata.attrib: cls.name = xmldata.attrib['name']
		if "custom-name" in xmldata.attrib: cls.customname = xmldata.attrib['custom-name']
		if "channel" in xmldata.attrib: cls.channel = int(xmldata.attrib['channel'])
		if "sync" in xmldata.attrib: cls.sync = float(xmldata.attrib['sync'])
		if "mode" in xmldata.attrib: cls.mode = int(xmldata.attrib['mode'])

		cls.phrases = []
		cls.audios = []
		cls.metrics = {}
		cls.keynames = None
		for xmlpart in xmldata:
			if xmlpart.tag == 'phrase':
				cls.phrases.append(temper_phrase.fromxml(xmlpart))
			elif xmlpart.tag == 'audio':
				cls.audios.append(event_audio.fromxml(xmlpart))
			elif xmlpart.tag == 'key-names':
				cls.keynames = temper_keynames.fromxml(xmlpart)
			elif xmlpart.tag == 'metrics':
				for inpartxml in xmlpart:
					metric_part = temper_track_metrics_part.fromxml(inpartxml)
					cls.metrics[inpartxml.tag] = metric_part

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
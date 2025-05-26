# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
from objects.data_bytes import bytereader
import os
import numpy as np

def list_fixnat(ind):
	out = {}
	for k, v in ind.items():
		if v in ['true', 'false']: out[k] = v=='true'
		elif v.replace('.','',1).isdigit(): out[k] = float(v) if '.' in v else int(v)
		else: out[k] = v
	return out

# ============================================= fx ============================================= 

class nanostudio_fxslot:
	def __init__(self, xmldata):
		self.type = None
		self.patch = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		if 'Type' in xmldata.attrib: self.type = xmldata.attrib['Type']
		for x_part in xmldata:
			if x_part.tag == 'Patch': self.patch = x_part.attrib.copy()

class nanostudio_insertfx:
	def __init__(self, xmldata):
		self.node_in = None
		self.node_slot1 = nanostudio_fxslot(None)
		self.node_slot2 = nanostudio_fxslot(None)
		self.node_slot3 = nanostudio_fxslot(None)
		self.node_slot4 = nanostudio_fxslot(None)
		self.node_out = None
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		if 'Vol' in xmldata.attrib: self.vol = float(xmldata.attrib['Vol'])
		if 'Pan' in xmldata.attrib: self.pan = float(xmldata.attrib['Pan'])
		for x_part in xmldata:
			if x_part.tag == 'Nodes':
				for x_inpart in x_part:
					if x_inpart.tag == 'SLOT1': self.node_slot1.read(x_inpart)
					if x_inpart.tag == 'SLOT2': self.node_slot2.read(x_inpart)
					if x_inpart.tag == 'SLOT3': self.node_slot3.read(x_inpart)
					if x_inpart.tag == 'SLOT4': self.node_slot4.read(x_inpart)

class nanostudio_mixerchannel:
	def __init__(self, xmldata):
		self.vol = 1
		self.Pan = 0.5
		self.insertfx = nanostudio_insertfx(None)
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		if 'Vol' in xmldata.attrib: self.vol = float(xmldata.attrib['Vol'])
		if 'Pan' in xmldata.attrib: self.pan = float(xmldata.attrib['Pan'])
		for x_part in xmldata:
			if x_part.tag == 'InsertFX': self.insertfx.read(x_part)

def parse_mixerchannels(xmldata, startswith):
	out = {}
	for x_part in xmldata:
		if x_part.tag.startswith(startswith):
			mixchan_obj = nanostudio_mixerchannel(x_part)
			out[int(x_part.tag[len(startswith):])] = mixchan_obj
	return out

# ============================================= instrument ============================================= 

class nanostudio_instrument:
	def __init__(self, xmldata):
		self.type = None
		self.data = {}
		self.mixerchannels = {}
		self.name = None
		self.am = {}
		self.sends = {}
		if xmldata is not None: self.read(xmldata)

	def read(self, xmldata):
		self.data = list_fixnat(xmldata.attrib)
		del self.data['Index']

		if 'Type' in self.data: 
			self.type = self.data['Type']
			self.name = self.type
			del self.data['Type']

		for x_part in xmldata:
			if x_part.tag == 'MixerChannels': self.mixerchannels = parse_mixerchannels(x_part, 'Channel')
			elif x_part.tag == 'UI': 
				if 'Name' in x_part.attrib: self.name = x_part.attrib['Name']
			elif x_part.tag == 'AM':
				self.am = x_part.attrib.copy()
				self.sends = parse_mixerchannels(x_part, 'Send')
				for x_inpart in x_part:
					if not x_inpart.tag.startswith('Send0'):
						self.am[x_inpart.tag] = list_fixnat(x_inpart.attrib)

# ============================================= main ============================================= 

dt_event = np.dtype([
	('type', '<B'), 
	('key', '<B'), 
	('vol_val', '<B'), 
	('ctrl_param', '<B'), 
	('position', '<I'), 
	('duration', '<I'), 
	])

dt_ev2 = np.dtype([
	('event_assoc', '<I'), 
	('_unk1', '<B'), 
	('_unk2', '<B'), 
	('_unk3', '<B'), 
	('_unk4', '<H'), 
	('position', '<I'), 
	('duration', '<H'), 
	('_unk7', '<B'), 
	])

class nanostudio_song:
	def __init__(self):
		self.loop = 0
		self.patterns = []
		self.clips = []
		self.tempo = 120
		self.click = 0
		self.unknowns = []
		self.trackmap = {}
		self.instruments = {}

	def load_from_folder(self, input_folder):
		if os.path.exists(input_folder):
			self.project__load_from_file(os.path.join(input_folder, 'Package.prj'))
			self.events__load_from_file(os.path.join(input_folder, 'Package.sng'))
			return True

	def project__load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for x_part in x_root:
			if x_part.tag == 'TrackMap': self.trackmap = x_part.attrib
			if x_part.tag == 'Instruments': 
				for inpart in x_part:
					if inpart.tag == 'Instr': 
						if 'Index' in inpart.attrib:
							self.instruments[int(inpart.attrib['Index'])] = nanostudio_instrument(inpart)

	def events__load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		byr_stream.skip(4) # version
		byr_stream.skip(4) # full size
		self.unknowns.append(byr_stream.l_uint32(32))
		self.tempo = byr_stream.float()
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.loop = byr_stream.uint32()
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.float())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.uint32())
		self.unknowns.append(byr_stream.float())
		self.click = byr_stream.uint32()

		for n in range(byr_stream.uint32()):
			vtype = byr_stream.uint32()
			stype = vtype>>8

			eventd = [stype, []]
			data_len = byr_stream.uint32()
			eventbytes = byr_stream.raw(12*data_len)
			eventd[1] = np.frombuffer(eventbytes, dtype=dt_event)

			self.patterns.append(eventd)

		for _ in range(byr_stream.uint32()):
			v = byr_stream.uint32()==0
			
			clipsize = byr_stream.uint16()
			byr_stream.skip(3)
			data_len = byr_stream.uint32()

			eventd = [clipsize, None]
			if data_len!=0:
				eventbytes = byr_stream.raw(16*data_len)
				eventd[1] = np.frombuffer(eventbytes, dtype=dt_ev2)
			self.clips.append(eventd)
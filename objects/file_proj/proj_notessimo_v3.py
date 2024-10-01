# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import zlib
import zipfile
from objects.data_bytes import bytereader
import xml.etree.ElementTree as ET
from functions import note_data
import os

from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

class note_note:
	__slots__ = ['pos','note','layer','inst','sharp','flat','vol','pan','dur','vars']
	def __init__(self):
		self.pos = 0
		self.note = 0
		self.inst = None
		self.sharp = False
		self.flat = False
		self.vol = None
		self.pan = 0
		self.dur = 0
		self.vars = {}

	def get_note(self):
		n_key = (self.note-42)*-1
		out_oct = int(n_key/7)
		out_key = n_key - out_oct*7
		out_note = note_data.keynum_to_note(out_key, out_oct-5)
		out_offset = 0
		if self.sharp: out_offset = 1
		if self.flat: out_offset = -1
		return out_note+out_offset

# ============================== V3 ==============================

def parse_items(xmldata, i_list):
	for item in xmldata:
		entry_data = notev3_entry(item)
		i_list[entry_data.id] = entry_data
		if entry_data.isBranch:
			parse_items(item.findall('item'), i_list)

def parse_xmlitems(zip_data, filename, i_list):
	try:
		if filename in zip_data.namelist():
			p_items = ET.fromstring(zip_data.read(filename))
			items = p_items.findall('items')[0]
			parse_items(items, i_list)
	except:
		pass

def var_in(xml_data):
	for i in xml_data.findall('var'): 
		t = i.get('type')
		v = i.get('value')
		if t == 'float': v = float(v)
		if t == 'int': v = int(v)
		yield i.get('id'), t, v

def var_get(xml_data):
	vars_o = []
	sets_o = []
	for v in xml_data.findall('vars'):
		for i in v.findall('var'): 
			t = i.get('type')
			pv = i.get('value')
			if t == 'float': pv = float(pv)
			if t == 'int': pv = int(float(pv))
			vars_o.append([i.get('id'), t, pv])
		for i in v.findall('set'): 
			sets_o.append([i.get('id'), [x for x in var_in(i)]])
	return vars_o, sets_o

class notev3_entry:
	def __init__(self, xml_data):
		self.isBranch = xml_data.get('isBranch') == 'true'
		self.isOpen = xml_data.get('isOpen') == 'true'
		self.name = xml_data.get('name')
		self.id = xml_data.get('id')
		self.date = xml_data.get('date')
		self.order = xml_data.get('order')
		self.parent = xml_data.get('parent')

class notev3_sample:
	def __init__(self):
		self.accidental = 'Natural'
		self.author = 'S'
		self.cent = 0
		self.color = ''
		self.comments = 'Taken'
		self.current_begin = ''
		self.current_end = ''
		self.current_start = ''
		self.current_stop = ''
		self.data = ''
		self.end = 0
		self.frequency = '44100'
		self.icon = ''
		self.license = 'Custom'
		self.loop_type = 'Loop'
		self.octave = 0
		self.pan = 0
		self.pitch = 'A'
		self.sample_end = 0
		self.sample_start = 0
		self.start = 0
		self.volume = 0

		self.name = ''
		self.date = ''
		self.type = 0
		self.hash = ''

	def load(self, zip_data, filename):
		try:
			x_samp = ET.fromstring(zip_data.read(filename))
			self.name = x_samp.get('name')
			self.date = x_samp.get('date')
			self.type = x_samp.get('type')
			self.hash = x_samp.get('hash')

			vars_o, sets_o = var_get(x_samp)

			for i, t, v in vars_o:
				if i == 'frequency': self.frequency = v
				elif i == 'pitch': self.pitch = v
				elif i == 'data': self.data = v
				elif i == 'color': self.color = v
				elif i == 'accidental': self.accidental = v
				elif i == 'icon': self.icon = v
				elif i == 'cent': self.cent = v
				elif i == 'volume': self.volume = v
				elif i == 'octave': self.octave = v
				elif i == 'pan': self.pan = v
				elif i == 'current_begin': self.current_begin = v
				elif i == 'sample_start': self.sample_start = v
				elif i == 'current_start': self.current_start = v
				elif i == 'current_stop': self.current_stop = v
				elif i == 'loop_type': self.loop_type = v
				elif i == 'start': self.start = v
				elif i == 'end': self.end = v
				elif i == 'current_end': self.current_end = v
				elif i == 'sample_end': self.sample_end = v
				elif i == 'comments': self.comments = v
				elif i == 'author': self.author = v
				elif i == 'license': self.license = v
			return True
		except:
			return False

class notev3_instrument_set:
	def __init__(self):
		self.accidental_end_1 = 'Natural'
		self.accidental_start_1 = 'Natural'
		self.octave_end_1 = 1
		self.octave_start_1 = 1
		self.pan_sample = 0
		self.pitch_end_1 = 'C'
		self.pitch_start_1 = 'C'
		self.sample_1 = ''
		self.semiton_sample = 0
		self.set = 0
		self.set_max = 0
		self.volume_sample = 0

class notev3_instrument:
	def __init__(self):
		self.set = notev3_instrument_set()
		self.sets = {}
		self.accidental = 'Natural'
		self.name = None
		self.author = ''
		self.biquad = 'Low Pass'
		self.biquad_active = 0
		self.biquad_frequency = 1000
		self.biquad_q = 1
		self.color = None
		self.comments = ''
		self.fadeIn = 0
		self.fadeOut = 0
		self.icon = ''
		self.license = 'Undefined'
		self.midi = -1
		self.octave = 4
		self.octave0 = 0
		self.octave1 = ''
		self.octave2 = ''
		self.octave3 = ''
		self.octave4 = ''
		self.octave6 = ''
		self.octave7 = ''
		self.octave8 = ''
		self.pan = 0
		self.pitch = 'C'
		self.pitch_mod_y1 = 0
		self.pitch_mod_y2 = 0
		self.plugin = ''
		self.priority = 0
		self.sample = ''
		self.scale_inst = 1
		self.v1 = -1
		self.v2 = -1
		self.vol_a = 0
		self.vol_d = 0
		self.vol_h = 0
		self.vol_r = 0
		self.vol_s = 0
		self.volume = 0

	def load(self, zip_data, id):
		filename = 'instruments/'+id+'.xml'
		if filename in zip_data.namelist():
			#print(filename)
			try:
				x_inst = ET.fromstring(zip_data.read(filename))

				self.name = x_inst.get('name')

				vars_o, sets_o = var_get(x_inst)

				for i, t, v in vars_o:
					if t == 'float': v = float(v)
					if t == 'int': v = int(v)

					if i == 'accidental': self.accidental = v
					elif i == 'author': self.author = v
					elif i == 'biquad': self.biquad = v
					elif i == 'biquad_active': self.biquad_active = v
					elif i == 'biquad_frequency': self.biquad_frequency = v
					elif i == 'biquad_q': self.biquad_q = v
					elif i == 'color': self.color = v
					elif i == 'comments': self.comments = v
					elif i == 'fadeIn': self.fadeIn = v
					elif i == 'fadeOut': self.fadeOut = v
					elif i == 'icon': self.icon = v
					elif i == 'license': self.license = v
					elif i == 'midi': self.midi = v
					elif i == 'octave': self.octave = v
					elif i == 'octave0': self.octave0 = v
					elif i == 'octave1': self.octave1 = v
					elif i == 'octave2': self.octave2 = v
					elif i == 'octave3': self.octave3 = v
					elif i == 'octave4': self.octave4 = v
					elif i == 'octave6': self.octave6 = v
					elif i == 'octave7': self.octave7 = v
					elif i == 'octave8': self.octave8 = v
					elif i == 'pan': self.pan = v
					elif i == 'pitch': self.pitch = v
					elif i == 'pitch_mod_y1': self.pitch_mod_y1 = v
					elif i == 'pitch_mod_y2': self.pitch_mod_y2 = v
					elif i == 'plugin': self.plugin = v
					elif i == 'priority': self.priority = v
					elif i == 'sample': self.sample = v
					elif i == 'scale_inst': self.scale_inst = v
					elif i == 'v1': self.v1 = v
					elif i == 'v2': self.v2 = v
					elif i == 'vol_a': self.vol_a = v
					elif i == 'vol_d': self.vol_d = v
					elif i == 'vol_h': self.vol_h = v
					elif i == 'vol_r': self.vol_r = v
					elif i == 'vol_s': self.vol_s = v
					elif i == 'volume': self.volume = v

					elif i == 'accidental_end_1': self.set.accidental_end_1 = v
					elif i == 'accidental_start_1': self.set.accidental_start_1 = v
					elif i == 'octave_end_1': self.set.octave_end_1 = v
					elif i == 'octave_start_1': self.set.octave_start_1 = v
					elif i == 'pan_sample': self.set.pan_sample = v
					elif i == 'pitch_end_1': self.set.pitch_end_1 = v
					elif i == 'pitch_start_1': self.set.pitch_start_1 = v
					elif i == 'sample_1': self.set.sample_1 = v
					elif i == 'semiton_sample': self.set.semiton_sample = v
					elif i == 'set': self.set.set = v
					elif i == 'set_max': self.set.set_max = v
					elif i == 'volume_sample': self.set.volume_sample = v

				for s_id, s_vars in sets_o:
					set_data = notev3_instrument_set()
					for i, t, v in s_vars:
						if i == 'accidental_end_1': set_data.accidental_end_1 = v
						elif i == 'accidental_start_1': set_data.accidental_start_1 = v
						elif i == 'octave_end_1': set_data.octave_end_1 = v
						elif i == 'octave_start_1': set_data.octave_start_1 = v
						elif i == 'pan_sample': set_data.pan_sample = v
						elif i == 'pitch_end_1': set_data.pitch_end_1 = v
						elif i == 'pitch_start_1': set_data.pitch_start_1 = v
						elif i == 'sample_1': set_data.sample_1 = v
						elif i == 'semiton_sample': set_data.semiton_sample = v
						elif i == 'set': set_data.set = v
						elif i == 'set_max': set_data.set_max = v
						elif i == 'volume_sample': set_data.volume_sample = v
					self.sets[s_id] = set_data
				return True
			except: return False
		else: return False

class notev3_sheet_layer:
	def __init__(self):
		self.name = ''
		self.parent = ''
		self.noDelete = False
		self.date = ''

		self.color = ''
		self.volume = 0
		self.icon = ''
		self.pan = 0
		self.comments = ''

		self.notes = []

class notev3_sheet:
	def __init__(self):
		self.pan = 0
		self.signature = 'C / A'
		self.name = None
		self.offset = 0
		self.width = 1
		self.timescale = 1
		self.valueSignature = 4
		self.nSignature = 4
		self.tempo = 120
		self.volume = 0
		self.icon = ''
		self.iconLabel = ''
		self.style = ''
		self.color = '0x000000'
		self.comments = ''
		self.author = ''
		self.license = 'Undefined'
		self.layers = {}

	def load(self, zip_data, id):
		filename = 'sheets/'+id+'.xml'
		if filename in zip_data.namelist():
			x_sheet = ET.fromstring(zip_data.read(filename))

			self.name = x_sheet.get('name')

			x_layers = x_sheet.findall('layers')

			if x_layers:
				x_layerdata = x_layers[0]
				x_items = x_layerdata.findall('items')
				if x_items:
					for x_item in x_items[0]:
						if x_item.tag == 'item':
							idd = x_item.get('id')
							layer_obj = notev3_sheet_layer()
							layer_obj.name = x_item.get('name')
							layer_obj.parent = x_item.get('parent')
							layer_obj.noDelete = x_item.get('noDelete') == 'true'
							self.layers[idd] = layer_obj

				x_objects = x_layerdata.findall('objects')
				if x_objects:
					for x_object in x_objects[0]:
						if x_object.tag == 'object':
							idd = x_item.get('id')
							layer_obj = self.layers[idd]
							layer_obj.date = x_object.get('date')
							vars_o, sets_o = var_get(x_object)
							for i, t, v in vars_o:
								if i == 'color': layer_obj.color = v
								if i == 'volume': layer_obj.volume = v
								if i == 'icon': layer_obj.icon = v
								if i == 'pan': layer_obj.pan = v
								if i == 'comments': layer_obj.comments = v

							notes = x_object.findall('obj')
							for note in notes:
								note_obj = note_note()
								note_obj.pos = float(note.get('x'))*2
								note_obj.note = int(note.get('y'))
								note_obj.sharp = note.get('isSharp') == 'true'
								note_obj.flat = note.get('isFlat') == 'true'
								note_obj.inst = note.get('id')
								note_obj.dur = float(note.get('l'))
								layer_obj.notes.append(note_obj)
								vars_o, sets_o = var_get(note)
								for i, t, v in vars_o:
									if i == 'volume': note_obj.vol = v
									else: note_obj.vars[i] = v

			vars_o, sets_o = var_get(x_sheet)
			for i, t, v in vars_o:
				if i == 'pan': self.pan = v
				elif i == 'pitch': self.pitch = v
				elif i == 'pitch_mod_y1': self.pitch_mod_y1 = v
				elif i == 'pitch_mod_y2': self.pitch_mod_y2 = v
				elif i == 'plugin': self.plugin = v
				elif i == 'priority': self.priority = v
				elif i == 'sample': self.sample = v
				elif i == 'scale_inst': self.scale_inst = v
				elif i == 'v1': self.v1 = v
				elif i == 'v2': self.v2 = v
				elif i == 'vol_a': self.vol_a = v
				elif i == 'vol_d': self.vol_d = v
				elif i == 'vol_h': self.vol_h = v
				elif i == 'vol_r': self.vol_r = v
				elif i == 'vol_s': self.vol_s = v
				elif i == 'volume': self.volume = v
				elif i == 'width': self.width = v
				elif i == 'tempo': self.tempo = v
				elif i == 'color': self.color = v

			return True
		else: return False

	def get_allnotes(self):
		outnotes = []
		for _, layer in self.layers.items(): 
			for x in layer.notes: outnotes.append(x)
		return outnotes


class note_placement:
	def __init__(self):
		self.pos = 0
		self.len = 0
		self.id = ''
		self.z = 0
		self.uid = 0

class notev3_song_layer:
	def __init__(self):
		self.name = ''
		self.parent = ''
		self.noDelete = False
		self.date = ''

		self.color = ''
		self.volume = 0
		self.icon = ''
		self.pan = 0
		self.comments = ''

		self.spots = []

class notev3_song:
	def __init__(self):
		self.height = 20
		self.width = 25
		self.volume = 0
		self.pan = 0
		self.color = '0xcccccc'
		self.icon = ''
		self.iconLabel = ''
		self.license = 'Undefined'
		self.author = ''
		self.comments = ''
		self.video_y = 0
		self.video_darken = 'true'
		self.video_render = 'Notessimo'
		self.video_currentZoom = ''
		self.video_image = ''
		self.video_automatic = 'true'
		self.video_time = 4
		self.video_signature = 'C'
		self.video_beat = 4
		self.video_tempo = 120

		self.layers = {}

	def load(self, zip_data, id):
		filename = 'songs/'+id+'.xml'
		if filename in zip_data.namelist():
			x_sheet = ET.fromstring(zip_data.read(filename))

			x_layers = x_sheet.findall('layers')

			if x_layers:
				x_layerdata = x_layers[0]
				x_items = x_layerdata.findall('items')
				if x_items:
					for x_item in x_items[0]:
						if x_item.tag == 'item':
							iid = int(x_item.get('id'))-1
							layer_obj = notev3_song_layer()
							layer_obj.name = x_item.get('name')
							layer_obj.parent = x_item.get('parent')
							layer_obj.noDelete = x_item.get('noDelete') == 'true'
							self.layers[iid] = layer_obj

				x_objects = x_layerdata.findall('objects')
				if x_objects:
					for x_object in x_objects[0]:
						if x_object.tag == 'object':
							iid = int(x_object.get('id'))-1
							layer_obj = self.layers[iid]
							layer_obj.date = x_object.get('date')
							vars_o, sets_o = var_get(x_object)
							for i, t, v in vars_o:
								if i == 'color': layer_obj.color = v
								if i == 'volume': layer_obj.volume = v
								if i == 'icon': layer_obj.icon = v
								if i == 'pan': layer_obj.pan = v
								if i == 'comments': layer_obj.comments = v

							pls = x_object.findall('obj')
							for pl in pls:
								pl_obj = note_placement()
								pl_obj.pos = float(pl.get('x'))
								row = int(pl.get('y'))
								pl_obj.len = float(pl.get('l2'))
								pl_obj.id = pl.get('id')
								zval = pl.get('z')
								if zval: pl_obj.z = float(zval)
								pl_obj.uid = int(pl.get('uid'))
								if row not in self.layers: self.layers[row] = notev3_song_layer()
								self.layers[row].spots.append(pl_obj)

			vars_o, sets_o = var_get(x_sheet)
			for i, t, v in vars_o:
				if i == 'height': self.height = v
				elif i == 'width': self.width = v
				elif i == 'volume': self.volume = v
				elif i == 'pan': self.pan = v
				elif i == 'color': self.color = v
				elif i == 'icon': self.icon = v
				elif i == 'iconLabel': self.iconLabel = v
				elif i == 'license': self.license = v
				elif i == 'author': self.author = v
				elif i == 'comments': self.comments = v
				elif i == 'video_y': self.video_y = v
				elif i == 'video_darken': self.video_darken = v
				elif i == 'video_render': self.video_render = v
				elif i == 'video_currentZoom': self.video_currentZoom = v
				elif i == 'video_image': self.video_image = v
				elif i == 'video_automatic': self.video_automatic = v
				elif i == 'video_time': self.video_time = v
				elif i == 'video_signature': self.video_signature = v
				elif i == 'video_beat': self.video_beat = v
				elif i == 'video_tempo': self.video_tempo = v

			return True
		else: return False

class notev3_file:
	def __init__(self):
		self.instruments_def = {}
		self.samples_def = {}
		self.sheets_def = {}
		self.songs_def = {}

		self.instruments = {}
		self.samples = {}
		self.sheets = {}
		self.songs = {}

		self.zip_data = {}
		
	def load_from_file(self, input_file):
		try:
			self.zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('notessimo: Bad ZIP File: '+str(t))

		sngfile = os.path.basename(input_file)

		parse_xmlitems(self.zip_data, 'instruments.xml', self.instruments_def)
		parse_xmlitems(self.zip_data, 'samples.xml', self.samples_def)
		parse_xmlitems(self.zip_data, 'sheets.xml', self.sheets_def)
		parse_xmlitems(self.zip_data, 'songs.xml', self.songs_def)

		if self.instruments_def: logger_projparse.info('notessimo: '+sngfile+': '+str(len(self.instruments_def))+' Instruments')

		for id, data in self.instruments_def.items():
			inst_data = notev3_instrument()
			ifvalid = inst_data.load(self.zip_data, id)
			self.instruments[id] = inst_data

		if self.samples_def: logger_projparse.info('notessimo: '+sngfile+': '+str(len(self.samples_def))+' Samples')
		for filename in self.zip_data.namelist():
			if filename.startswith('samples/'):
				id = filename.split('/')[1].split('.')[0]
				samp_data = notev3_sample()
				ifvalid = samp_data.load(self.zip_data, filename)
				self.samples[id] = samp_data

		if self.sheets_def: logger_projparse.info('notessimo: '+sngfile+': '+str(len(self.sheets_def))+' Sheets')
		for id, data in self.sheets_def.items():
			sheet_obj = notev3_sheet()
			ifvalid = sheet_obj.load(self.zip_data, id)
			self.sheets[id] = sheet_obj

		if self.songs_def: logger_projparse.info('notessimo: '+sngfile+': '+str(len(self.songs_def))+' Songs')
		for id, data in self.songs_def.items():
			song_obj = notev3_song()
			ifvalid = song_obj.load(self.zip_data, id)
			self.songs[id] = song_obj

		return True
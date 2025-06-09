# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions.dawspecific import flp_plugchunks
from objects.data_bytes import bytewriter
from objects.dawspecific import flp_plugins_directwave

def utf16decode(event_data):
	return event_data.decode('utf-16le').rstrip('\x00\x00')

def utf16encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-16le') + b'\x00\x00'

def utf8encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-8') + b'\x00'

class flp_autopoint:
	def __init__(self, event_bio):
		self.pos = 0
		self.val = 0
		self.tension = 0
		self.type = 0
		self.selected = 0
		self.t_sign = 0
		if event_bio is not None:
			self.read(event_bio)

	def read(self, event_bio):
		self.pos = event_bio.double()
		self.val = event_bio.double()
		self.tension = event_bio.float()
		self.type = event_bio.uint16()
		self.selected = event_bio.uint8()
		self.t_sign = event_bio.uint8()

VERBOSE = False

# ---------------------------------------------------- FPC ----------------------------------------------------

class fpc_plugin_layer:
	def __init__(self):
		self.filename = b''
		self.vol = 80
		self.pan = 0
		self.vel_min = 0
		self.vel_max = 127
		self.flags = [0]
		self.tune = 0
		self.unk = -1

	def read(self, byr_stream):
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 

				if VERBOSE:
					print('\t\t\t',chunktype, chunksize, end='')
					if chunktype not in [105]:
						print( byr_stream.raw(byr_stream.remaining()).hex() )
						byr_stream.seek(0)
					else:
						print()

				if chunktype == 300: 
					self.filename = bye_stream.raw(chunksize)
				if chunktype == 301: 
					self.vol = bye_stream.int32()
					self.pan = bye_stream.int32()
					self.vel_min = bye_stream.int32()
					self.vel_max = bye_stream.int32()
					self.flags = bye_stream.flags32()
					self.tune = bye_stream.int32()
					self.unk = bye_stream.int32() # -1

	def dump(self):
		info_writer = bytewriter.bytewriter()
		info_writer.int32(self.vol)
		info_writer.int32(self.pan)
		info_writer.int32(self.vel_min)
		info_writer.int32(self.vel_max)
		info_writer.flags32(self.flags)
		info_writer.int32(self.tune)
		info_writer.int32(self.unk)

		total_writer = bytewriter.bytewriter()
		flp_plugchunks.write_chunk(total_writer, 300, self.filename)
		flp_plugchunks.write_chunk(total_writer, 301, info_writer.getvalue())
		flp_plugchunks.write_chunk(total_writer, 302, b'')
		return total_writer.getvalue()

class fpc_plugin_pad:
	def __init__(self):
		self.pads = []
		self.key = 0
		self.vol = 99
		self.pan = 0
		self.flags = 0
		self.key = 37
		self.output = 0
		self.cut = -1
		self.cut_by = -1
		self.tune = 0
		self.color = 0
		self.icon = 0
		self.name = b''
		self.auto_vol = []
		self.auto_pan = []
		self.layers = [fpc_plugin_layer()]

	def read(self, byr_stream):
		self.layers = []
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if VERBOSE:
					print('\t\t',chunktype, chunksize, end='')
					if chunktype not in [105]:
						print( byr_stream.raw(byr_stream.remaining()).hex() )
						byr_stream.seek(0)
					else:
						print()

				if chunktype == 100:
					self.vol = bye_stream.int32()
					self.pan = bye_stream.int32()
					self.flags = bye_stream.int32()
					self.key = bye_stream.int32()
					self.output = bye_stream.int32()
					self.cut = bye_stream.int32()
					self.cut_by = bye_stream.int32()
					self.tune = bye_stream.int32()
					self.color = bye_stream.int32()
					self.icon = bye_stream.int32()
					# 000000000000000000000000000000000000000000000000
				elif chunktype == 101:
					self.name = bye_stream.raw(chunksize)
				elif chunktype == 102:
					# b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
					pass
				elif chunktype == 103:
					autonum = bye_stream.int32()
				elif chunktype == 104:
					bye_stream.skip(4)
					version = bye_stream.int32()
					numpoints = bye_stream.int32()
					points = [flp_autopoint(bye_stream) for x in range(numpoints)]
					if autonum == 0: self.auto_vol = points
					if autonum == 1: self.auto_pan = points
					b'\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00'
				elif chunktype == 105:
					layer_obj = fpc_plugin_layer()
					layer_obj.read(bye_stream)
					self.layers.append(layer_obj)

	def dump(self):
		total_writer = bytewriter.bytewriter()

		info_padinfo = bytewriter.bytewriter()
		info_padinfo.int32(self.vol)
		info_padinfo.int32(self.pan)
		info_padinfo.int32(self.flags)
		info_padinfo.int32(self.key)
		info_padinfo.int32(self.output)
		info_padinfo.int32(self.cut)
		info_padinfo.int32(self.cut_by)
		info_padinfo.int32(self.tune)
		info_padinfo.int32(self.color)
		info_padinfo.int32(self.icon)
		info_padinfo.l_int32([0,0,0,0,0,0], 6)
		flp_plugchunks.write_chunk(total_writer, 100, info_padinfo.getvalue())
		flp_plugchunks.write_chunk(total_writer, 101, self.name)
		flp_plugchunks.write_chunk(total_writer, 102, b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

		for layer_obj in self.layers:
			flp_plugchunks.write_chunk(total_writer, 105, layer_obj.dump())
		flp_plugchunks.write_chunk(total_writer, 103, b'\x00\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 104, b'\x01\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8?\x00\x00\x00\x00\x00\x00\xf0?\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xf8?\x00\x00\x00\x00\x00\x00\xe0?\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\xd0?\x00\x00\x00\x00\x00\x00\x00\x00\xcd\xccL>\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xff\xff\xff\xff\x02\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 103, b'\x01\x00\x00\x00\x00\x00\x00\x00')
		flp_plugchunks.write_chunk(total_writer, 104, b'\x01\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0?\xcd\xccL>\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00')

		flp_plugchunks.write_chunk(total_writer, 106, b'')
		return total_writer.getvalue()

class fpc_plugin:
	def __init__(self):
		self.midifile = None
		self.pads = [fpc_plugin_pad() for _ in range(32)]
		self.version = 1000014

	def read(self, byr_stream):
		self.pads = []
		self.version = byr_stream.uint32()
		#print('START')
		while byr_stream.remaining():
			chunktype, chunksize = flp_plugchunks.read_header(byr_stream)
			#print('\t',chunktype, chunksize)
			with byr_stream.isolate_size(chunksize, True) as bye_stream: 
				if chunktype == 2:
					pad_obj = fpc_plugin_pad()
					pad_obj.read(bye_stream)
					self.pads.append(pad_obj)
				if chunktype == 1:
					self.midifile = bye_stream.raw(chunksize)

		#byr_stream.seek(0)
		#compd = byr_stream.rest()
		#compo = self.dump()

		#f = open('test_i.bin', 'wb')
		#f.write(compd)

		#d = open('test_o.bin', 'wb')
		#d.write(compo)

	def dump(self):
		total_writer = bytewriter.bytewriter()
		total_writer.uint32(self.version)
		for pad_obj in self.pads:
			flp_plugchunks.write_chunk(total_writer, 2, pad_obj.dump())
		flp_plugchunks.write_chunk(total_writer, 1, b'')
		return total_writer.getvalue()

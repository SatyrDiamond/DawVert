# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import varint
import argparse
import struct
from io import BytesIO
from functions import data_bytes
from functions_plugin import format_flp_tlv

from objects_file._flp import fx
from objects_file._flp import channel
from objects_file._flp import auto
from objects_file._flp import arrangement

def decodetext(version_split, event_data):
	if event_data not in [b'\x00\x00', b'\x00']:
		try:
			if version_split[0] > 10: return event_data.decode('utf-16le').rstrip('\x00\x00')
			else: return event_data.decode('utf-8').rstrip('\x00')
		except:
			return event_data.decode('utf-8').rstrip('\x00')
	else:
		return ''

def utf16encode(text):
	out_text = text if text != None else ''
	return out_text.encode('utf-16le') + b'\x00\x00'

def make_flevent(FLdt_bytes, value, data):
	if value <= 63 and value >= 0: # int8
		FLdt_bytes.write(value.to_bytes(1, "little"))
		FLdt_bytes.write(data.to_bytes(1, "little"))
	if value <= 127 and value >= 64 : # int16
		FLdt_bytes.write(value.to_bytes(1, "little"))
		FLdt_bytes.write(data.to_bytes(2, "little"))
	if value <= 191 and value >= 128 : # int32
		FLdt_bytes.write(value.to_bytes(1, "little"))
		FLdt_bytes.write(data.to_bytes(4, "little"))
	if value <= 224 and value >= 192 : # text
		FLdt_bytes.write(value.to_bytes(1, "little"))
		FLdt_bytes.write(varint.encode(len(data)))
		FLdt_bytes.write(data)
	if value <= 255 and value >= 225 : # data
		FLdt_bytes.write(value.to_bytes(1, "little"))
		FLdt_bytes.write(varint.encode(len(data)))
		FLdt_bytes.write(data)

class flp_note:
	__slots__ = ["pos","flags","rack","dur","key","group","finep","u1","rel","midich","pan","velocity","mod_x","mod_y"]
	def __init__(self):
		self.pos = 0
		self.flags = 16384
		self.rack = 0
		self.dur = 48
		self.key = 60
		self.group = 0
		self.finep = 120
		self.u1 = 0
		self.rel = 64
		self.midich = 0
		self.pan = 64
		self.velocity = 100
		self.mod_x = 128
		self.mod_y = 128

class flp_pattern:
	def __init__(self):
		self.color = None
		self.automation = {}
		self.notes = []
		self.name = None

class flp_project:
	def __init__(self):
		self.main = {}
		self.channels = {}
		self.patterns = {}
		self.patterns[0] = flp_pattern()
		self.mixer = {}
		for fxnum in range(127): self.mixer[fxnum] = fx.flp_fxchan()
		self.initfxvals = auto.flp_initvals()
		self.startvals = auto.flp_initvals()
		self.arrangements = {}
		self.arrangements[0] = arrangement.flp_arrangement()
		self.timemarkers = []
		self.changroupname = []
		self.nonsong_patnum = 1
		self.truncate_clip_notes = 1
		self.loop_active = 1
		self.automatic_crossfades = 0
		self.panning_law = 0
		self.fx_num = -1
		self.ppq = 96
		self.num_channels = 0

		self.fx_color = None
		self.fx_icon = None
		self.fxcreationmode = 0
		self.def_pluginname = ''

		self.current_arr = 0
		self.current_arr_obj = self.arrangements[0]

		self.current_pat = 0
		self.current_pat_obj = self.patterns[0]

		self.current_ch = 0
		self.current_ch_obj = None

		self.current_track = 0

		self.slotstore = None

		self.tempo = 120
		self.mainpitch = 0
		self.numerator = 4
		self.denominator = 4
		self.shuffle = 0
		self.title = ''
		self.genre = ''
		self.author = ''
		self.projectdatapath = ''
		self.comment = ''
		self.url = ''
		self.projecttime = None
		self.showinfo = 0
		self.version = ''
		self.version_split = [0]

		self.remote_assoc = {}
		self.fx_name = ''

		#with open('flp_eventname.txt') as f:
		#	self.lines = f.readlines()

	def do_event(self, event_id, event_data):
		if event_id == 199: 
			FLVersion = event_data.decode('utf-8').rstrip('\x00')
			print('FL Version:', FLVersion)
			self.version_split = [int(x) for x in FLVersion.split('.')]
			if self.version_split[0] < 12:
				print('[error] FL version '+str(self.version_split[0])+' is not supported.') 
				exit()
			self.version = FLVersion
		elif event_id == 156: self.tempo = event_data/1000
		elif event_id == 80:  self.mainpitch = struct.unpack('h', struct.pack('H', event_data))[0]
		elif event_id == 17:  self.numerator = event_data
		elif event_id == 18:  self.denominator = event_data
		elif event_id == 11:  self.shuffle = event_data
		elif event_id == 9:   self.loop_active = event_data
		elif event_id == 23:  self.panning_law = event_data
		elif event_id == 30:  self.truncate_clip_notes = event_data
		elif event_id == 67:  self.nonsong_patnum = event_data
		elif event_id == 44:  self.automatic_crossfades = event_data
		elif event_id == 194: self.title = decodetext(self.version_split, event_data)
		elif event_id == 206: self.genre = decodetext(self.version_split, event_data)
		elif event_id == 207: self.author = decodetext(self.version_split, event_data)
		elif event_id == 202: self.projectdatapath = decodetext(self.version_split, event_data)
		elif event_id == 195: self.comment = decodetext(self.version_split, event_data)
		elif event_id == 197: self.url = decodetext(self.version_split, event_data)
		elif event_id == 237: self.projecttime = event_data
		elif event_id == 10:  self.showinfo = event_data
		elif event_id == 231: self.changroupname.append(decodetext(self.version_split, event_data))



		#Pattern
		elif event_id == 65: 
			self.current_pat = event_data
			if self.current_pat not in self.patterns: self.patterns[self.current_pat] = flp_pattern()
			self.current_pat_obj = self.patterns[self.current_pat] 

		elif event_id == 223:
			event_bio = BytesIO(event_data)
			while event_bio.tell() < len(event_data):
				pos, autov, val = struct.unpack('III', event_bio.read(12))
				if autov not in self.current_pat_obj.automation: self.current_pat_obj.automation[autov] = []
				self.current_pat_obj.automation[autov].append([pos, val])

			keyreplace = {}
			for n, x in self.current_pat_obj.automation.items():
				autoloc = auto.flp_autoloc()
				autoloc.decode(n)
				autotxt = autoloc.to_loctxt()
				keyreplace[autotxt] = x

			self.current_pat_obj.automation = keyreplace

		elif event_id == 224: #PatternNotes
			event_bio = BytesIO(event_data)
			#if self.version_split[0] <= 8:
			#	while event_bio.tell() < len(event_data):
			##		n_pos,n_flags,n_rack,n_dur,n_key,n_finep,n_u1,n_midich,n_pan,n_velocity,n_mod_x,n_mod_y = struct.unpack('IHHIBBBBBBBB', event_bio.read(20))
			#		self.current_pat_obj.notes.append([n_pos,n_flags,n_rack,n_dur,n_key,0,n_finep,n_u1,0,n_midich,n_pan,n_velocity,n_mod_x,n_mod_y])
			#else:
			while event_bio.tell() < len(event_data):
				n_pos,n_flags,n_rack,n_dur,n_key,n_group,n_finep,n_u1,n_rel,n_midich,n_pan,n_velocity,n_mod_x,n_mod_y = struct.unpack('IHHIHHBBBBBBBB', event_bio.read(24))
				fl_note = flp_note()
				fl_note.pos = n_pos
				fl_note.flags = n_flags
				fl_note.rack = n_rack
				fl_note.dur = n_dur
				fl_note.key = n_key
				fl_note.group = n_group
				fl_note.finep = n_finep
				fl_note.u1 = n_u1
				fl_note.rel = n_rel
				fl_note.midich = n_midich
				fl_note.pan = n_pan
				fl_note.velocity = n_velocity
				fl_note.mod_x = n_mod_x
				fl_note.mod_y = n_mod_y
				self.current_pat_obj.notes.append(fl_note)

		elif event_id == 150: self.current_pat_obj.color = event_data

		elif event_id == 193: self.current_pat_obj.name = decodetext(self.version_split, event_data)

		elif event_id == 99: 
			self.current_arr = event_data
			if self.current_arr not in self.arrangements: self.arrangements[self.current_arr] = arrangement.flp_arrangement()
			self.current_arr_obj = self.arrangements[self.current_arr] 

		elif event_id == 241: self.current_arr_obj.name = decodetext(self.version_split, event_data)

		elif event_id == 233:
			event_bio = BytesIO(event_data)
			while event_bio.tell() < len(event_data):
				fla = arrangement.flp_arrangement_clip()
				fla.read(event_bio, self.version_split)
				self.current_arr_obj.items.append(fla)

		#Tracks
		elif event_id == 238:
			event_bio = BytesIO(event_data)
			flp_track_obj = arrangement.flp_track()
			flp_track_obj.read(event_bio, len(event_data), self.version_split)
			self.current_track = flp_track_obj.id
			self.current_arr_obj.tracks[flp_track_obj.id] = flp_track_obj

		elif event_id == 239:
			self.current_arr_obj.tracks[self.current_track].name = decodetext(self.version_split, event_data)


		#Timemarker
		elif event_id == 148: 
			timemarker_obj = arrangement.flp_timemarker()
			timemarker_obj.type = event_data >> 24
			timemarker_obj.pos = event_data & 0x00ffffff
			self.current_arr_obj.timemarkers.append(timemarker_obj)

		elif event_id == 205: self.current_arr_obj.timemarkers[-1].name = decodetext(self.version_split, event_data)
		elif event_id == 33: self.current_arr_obj.timemarkers[-1].numerator = event_data
		elif event_id == 34: self.current_arr_obj.timemarkers[-1].denominator = event_data
	


		#Init Controls
		elif event_id == 216: self.startvals.read(event_data)
		elif event_id == 225: self.initfxvals.read(event_data)
		#elif event_id == 227: 
		#	event_bio = BytesIO(event_data)
		#	autoloc = auto.flp_autoloc()
		#	event_bio.read(2)
		#	remote_id = int.from_bytes(event_bio.read(4), "little")
		#	event_bio.read(2)
		#	remote_auto = int.from_bytes(event_bio.read(4), "little")
		#	autoloc.decode(remote_auto)
		#	self.remote_assoc[remote_id] = autoloc

		#Channel
		elif event_id == 64: 
			self.current_ch = event_data
			if self.current_ch not in self.channels: self.channels[self.current_ch] = channel.flp_channel()
			self.current_ch_obj = self.channels[self.current_ch]

		elif event_id == 21: self.current_ch_obj.type = event_data

		elif event_id == 236 and not self.fxcreationmode: 
			self.fx_color = None
			self.fx_icon = None
			self.fxcreationmode = True
			self.fx_num = -1

		if not self.fxcreationmode:
			if event_id == 201: self.def_pluginname = decodetext(self.version_split, event_data)
			elif event_id == 212: 
				self.current_ch_obj.plugin.name = self.def_pluginname
				self.current_ch_obj.plugin.read(event_data)
			elif event_id == 203: self.current_ch_obj.name = decodetext(self.version_split, event_data)
			elif event_id == 155: self.current_ch_obj.icon = event_data
			elif event_id == 128: self.current_ch_obj.color = event_data
			elif event_id == 213: self.current_ch_obj.plugin.params = event_data
			elif event_id == 0:   self.current_ch_obj.enabled = event_data
			elif event_id == 218: 
				envlfo_obj = channel.flp_env_lfo()
				envlfo_obj.read(event_data)
				self.current_ch_obj.env_lfo.append(envlfo_obj)
			elif event_id == 209: self.current_ch_obj.delay = event_data
			elif event_id == 138: self.current_ch_obj.delayreso = event_data
			elif event_id == 139: self.current_ch_obj.reverb = event_data
			elif event_id == 89:  self.current_ch_obj.shiftdelay = event_data
			elif event_id == 69:  self.current_ch_obj.fx = event_data
			elif event_id == 86:  self.current_ch_obj.fx3 = event_data
			elif event_id == 71:  self.current_ch_obj.cutoff = event_data
			elif event_id == 83:  self.current_ch_obj.resonance = event_data
			elif event_id == 74:  self.current_ch_obj.preamp = event_data
			elif event_id == 75:  self.current_ch_obj.decay = event_data
			elif event_id == 76:  self.current_ch_obj.attack = event_data
			elif event_id == 85:  self.current_ch_obj.stdel = event_data
			elif event_id == 131: self.current_ch_obj.fxsine = event_data
			elif event_id == 70:  self.current_ch_obj.fadestereo = event_data
			elif event_id == 22:  self.current_ch_obj.fxchannel = event_data
			elif event_id == 94:  self.current_ch_obj.layer_chans.append(event_data)
			elif event_id == 228: 
				trk_obj = channel.flp_channel_tracking()
				trk_obj.read(event_data)
				self.current_ch_obj.tracking.append(trk_obj)
			elif event_id == 219: self.current_ch_obj.basicparams.read(event_data)
			elif event_id == 221: self.current_ch_obj.poly.read(event_data)


			#elif event_id == 234: 
			#	event_bio = BytesIO(event_data)
			#	print( 'header', struct.unpack('biiii', event_bio.read(20) ))
			#	num_points = int.from_bytes(event_bio.read(4), "little")
				#print( event_bio.read(4).hex() )

			#	print(num_points)
			#	for _ in range(num_points):
			#		print( struct.unpack('ddfBBBB', event_bio.read(24)) )
			#	print( event_bio.read(4) )
			#	print( event_bio.read(16) )
			#	print( event_bio.read().hex() )



				#exit()




			elif event_id == 215: self.current_ch_obj.params.read(event_data)
			elif event_id == 229: self.current_ch_obj.ofslevels = event_data
			elif event_id == 132: self.current_ch_obj.cutcutby = event_data
			elif event_id == 144: self.current_ch_obj.layerflags = event_data
			elif event_id == 145: self.current_ch_obj.filtergroup = event_data
			elif event_id == 143: self.current_ch_obj.sampleflags = event_data
			elif event_id == 20:  self.current_ch_obj.looptype = event_data
			elif event_id == 135: self.current_ch_obj.middlenote = event_data
			elif event_id == 196: self.current_ch_obj.samplefilename = decodetext(self.version_split, event_data)
		else:
			if event_id == 149: self.fx_color = event_data
			elif event_id == 95:  self.fx_icon = event_data
			elif event_id == 236: 
				self.fx_num += 1
				self.mixer[self.fx_num].name = self.fx_name
				self.mixer[self.fx_num].color = self.fx_color
				self.mixer[self.fx_num].icon = self.fx_icon
				self.mixer[self.fx_num].read(event_data)
				self.fx_color = None
				self.fx_icon = None
				self.fx_name = None

				#if self.fx_num == 8: exit()







			elif event_id == 201: self.def_pluginname = decodetext(self.version_split, (event_data))
			elif event_id == 212: 
				self.slotstore = fx.flp_fxslot(self.fx_num)
				self.slotstore.plugin.name = self.def_pluginname
				self.slotstore.plugin.read(event_data)
			elif event_id == 155: self.slotstore.icon = event_data
			elif event_id == 128: self.slotstore.color = event_data
			elif event_id == 203: self.slotstore.name = decodetext(self.version_split, event_data)
			elif event_id == 98:  
				if event_data < 10: 
					if self.slotstore:
						self.slotstore.plugin.slotnum = event_data
						self.mixer[self.fx_num].slots[event_data] = self.slotstore
				self.slotstore = None
			elif event_id == 213: self.slotstore.plugin.params = event_data
			elif event_id == 235: 
				for num, on in enumerate(event_data):
					if on: self.mixer[self.fx_num].routing.append(num)
			elif event_id == 154: self.mixer[self.fx_num].inchannum = event_data
			elif event_id == 147: self.mixer[self.fx_num].outchannum = event_data
			elif event_id == 204: self.fx_name = decodetext(self.version_split, event_data)

		#if event_id not in [228,44,30,23,67,9,0,10,11,128,131,132,135,138,139,143,144,145,147,148,149,150,154,155,156,17,18,193,194,195,196,197,199,20,201,202,203,204,205,206,207,209,21,212,213,215,218,219,22,221,223,224,225,229,231,233,235,236,237,238,239,241,33,34,38,64,65,69,70,71,74,75,76,80,83,85,86,89,95,98,99]:
		#	print('unknown event: ',self.lines[event_id].strip())
		#	print(event_data)

	def read(self, inputfile):
		fileobject = open(inputfile, 'rb')
		headername = fileobject.read(4)
		rifftable = data_bytes.iff_read(fileobject, 0)
		for chunk_id, chunk_data in rifftable:
			if chunk_id == b'FLhd':
				self.num_channels = int.from_bytes(chunk_data[0:3], "big")
				self.ppq = int.from_bytes(chunk_data[4:6], "little")
			if chunk_id == b'FLdt':
				for event_id, event_data in format_flp_tlv.decode(chunk_data): self.do_event(event_id, event_data)

	def make(self, outputfile):

		flpout = open(outputfile, 'wb')
		#FLhd
		data_FLhd = BytesIO()
		data_FLhd.write(self.num_channels.to_bytes(3, 'big'))
		data_FLhd.write(b'\x00')
		data_FLhd.write(self.ppq.to_bytes(2, 'little'))

		#FLdt
		data_FLdt = BytesIO()
		make_flevent(data_FLdt, 199, '20.7.2.1852'.encode('utf8') + b'\x00')
		make_flevent(data_FLdt, 159, 1852)
		make_flevent(data_FLdt, 37, 1)
		make_flevent(data_FLdt, 200, b'\x00\x00')
		make_flevent(data_FLdt, 156, int(self.tempo)*1000)
		make_flevent(data_FLdt, 67, self.nonsong_patnum)
		make_flevent(data_FLdt, 9, self.loop_active)
		make_flevent(data_FLdt, 11, self.shuffle)
		make_flevent(data_FLdt, 80, struct.unpack('h', struct.pack('H', self.mainpitch))[0])
		make_flevent(data_FLdt, 17, self.numerator)
		make_flevent(data_FLdt, 18, self.denominator)
		make_flevent(data_FLdt, 35, 1)
		make_flevent(data_FLdt, 23, self.panning_law)
		make_flevent(data_FLdt, 30, self.truncate_clip_notes)
		make_flevent(data_FLdt, 10, self.showinfo)
		make_flevent(data_FLdt, 194, utf16encode(self.title))
		make_flevent(data_FLdt, 206, utf16encode(self.genre))
		make_flevent(data_FLdt, 207, utf16encode(self.author))
		make_flevent(data_FLdt, 202, utf16encode(self.projectdatapath))
		make_flevent(data_FLdt, 195, utf16encode(self.comment))
		if self.url: make_flevent(data_FLdt, 197, utf16encode(self.url))
		make_flevent(data_FLdt, 146, 4294967295)
		make_flevent(data_FLdt, 216, self.startvals.write())

		for patnum, patdat in self.patterns.items():
			if patdat.automation or patdat.notes or patdat.color or (patdat.name != None):
				make_flevent(data_FLdt, 65, patnum)
				if patdat.automation:
					autobytes = b''
					#for pos, autov, val in patdat.automation: autobytes += struct.pack('III', pos, autov, val)
					#make_flevent(data_FLdt, 223, autobytes)
				if patdat.notes:
					flnotes = b''
					for fln in patdat.notes: 
						flnotes += struct.pack('IHHIHHBBBBBBBB', fln.pos,fln.flags,fln.rack,fln.dur,fln.key,fln.group,fln.finep,fln.u1,fln.rel,fln.midich,fln.pan,fln.velocity,fln.mod_x,fln.mod_y)
					make_flevent(data_FLdt, 224, flnotes)
				if patdat.color != None: make_flevent(data_FLdt, 150, patdat.color)
				if patdat.name != None: make_flevent(data_FLdt, 193, utf16encode(patdat.name))

		make_flevent(data_FLdt, 226, b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
		make_flevent(data_FLdt, 226, b'\xfd\x00\x00\x00\x00\x00\x00\x00\x80\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
		make_flevent(data_FLdt, 226, b'\xff\x00\x00\x00\xff\x00\x00\x00\x04\x00\xff\x0f\x04\x00\x00\x00\x00\xfe\xff\xff')

		#print('')

		for chnum, chdat in self.channels.items():
			make_flevent(data_FLdt, 64, chnum)
			make_flevent(data_FLdt, 21, chdat.type)
			if chdat.type == 2:
				if chdat.plugin.name != None: make_flevent(data_FLdt, 201, utf16encode(chdat.plugin.name))
				make_flevent(data_FLdt, 212, chdat.plugin.write())
			if chdat.name != None: make_flevent(data_FLdt, 203, utf16encode(chdat.name))
			if chdat.icon != None: make_flevent(data_FLdt, 155, chdat.icon)
			if chdat.color != None: make_flevent(data_FLdt, 128, chdat.color)
			if chdat.plugin.params != None: make_flevent(data_FLdt, 213, chdat.plugin.params)

			make_flevent(data_FLdt, 0, chdat.enabled)
			make_flevent(data_FLdt, 209, chdat.delay)
			make_flevent(data_FLdt, 138, chdat.delayreso)
			make_flevent(data_FLdt, 139, chdat.reverb)
			make_flevent(data_FLdt, 89, chdat.shiftdelay)
			make_flevent(data_FLdt, 97, 128)
			make_flevent(data_FLdt, 69, chdat.fx)
			make_flevent(data_FLdt, 86, chdat.fx3)
			make_flevent(data_FLdt, 71, chdat.cutoff)
			make_flevent(data_FLdt, 83, chdat.resonance)
			make_flevent(data_FLdt, 74, chdat.preamp)
			make_flevent(data_FLdt, 75, chdat.decay)
			make_flevent(data_FLdt, 76, chdat.attack)
			make_flevent(data_FLdt, 85, chdat.stdel)
			make_flevent(data_FLdt, 131, chdat.fxsine)
			make_flevent(data_FLdt, 70, chdat.fadestereo)
			make_flevent(data_FLdt, 22, chdat.fxchannel)
			for layer_chan in chdat.layer_chans: make_flevent(data_FLdt, 94, layer_chan)
			make_flevent(data_FLdt, 219, chdat.basicparams.write())
			make_flevent(data_FLdt, 229, chdat.ofslevels)
			make_flevent(data_FLdt, 221, chdat.poly.write())
			make_flevent(data_FLdt, 215, chdat.params.write())
			make_flevent(data_FLdt, 132, chdat.cutcutby)
			make_flevent(data_FLdt, 144, chdat.layerflags)
			make_flevent(data_FLdt, 145, 0)
			make_flevent(data_FLdt, 32, 0)
			for trking_obj in chdat.tracking: make_flevent(data_FLdt, 228, trking_obj.write())
			for env_lfo_obj in chdat.env_lfo: make_flevent(data_FLdt, 218, env_lfo_obj.write())
			make_flevent(data_FLdt, 143, chdat.sampleflags)
			make_flevent(data_FLdt, 20, chdat.looptype)

			if chdat.samplefilename: make_flevent(data_FLdt, 196, utf16encode(chdat.samplefilename))
			if chdat.middlenote != 60: make_flevent(data_FLdt, 135, chdat.middlenote)

		for arrnum, arrdat in self.arrangements.items():
			make_flevent(data_FLdt, 99, arrnum)
			if arrdat.name != None: make_flevent(data_FLdt, 241, utf16encode(arrdat.name))
			arr_bytes = b''
			for item in arrdat.items:
				arr_bytes += item.write()

			make_flevent(data_FLdt, 36, 0)
			make_flevent(data_FLdt, 233, arr_bytes) #PlayListItems
			for track_num, track_obj in arrdat.tracks.items():
				make_flevent(data_FLdt, 238, track_obj.write())
				if track_obj.name: make_flevent(data_FLdt, 239, utf16encode(track_obj.name))

			for timem_obj in arrdat.timemarkers:
				make_flevent(data_FLdt, 148, (timem_obj.type << 24)+timem_obj.pos)
				make_flevent(data_FLdt, 33, timem_obj.numerator)
				make_flevent(data_FLdt, 34, timem_obj.denominator)
				if timem_obj.name != None: make_flevent(data_FLdt, 205, utf16encode(timem_obj.name))
				else: make_flevent(data_FLdt, 205, b'\x20\x00\x00\x00')

			#make_trackinfo(data_FLdt, arrangements[arrangement]['tracks'])
		make_flevent(data_FLdt, 100, 0)
		make_flevent(data_FLdt, 29, 1)
		make_flevent(data_FLdt, 39, 1)
		make_flevent(data_FLdt, 31, 0)
		make_flevent(data_FLdt, 38, 1)

		for mixernum, mixerdat in self.mixer.items():
			#print(mixernum, mixerdat)
			make_flevent(data_FLdt, 236, mixerdat.write())
			if mixerdat.color != None: make_flevent(data_FLdt, 149, mixerdat.color)
			if mixerdat.name != None: make_flevent(data_FLdt, 204, utf16encode(mixerdat.name))
			if mixerdat.icon != None: make_flevent(data_FLdt, 95, mixerdat.icon)
			for slotnum, slotdata in enumerate(mixerdat.slots):
				if slotdata:
					if slotdata.plugin.name != None: make_flevent(data_FLdt, 201, utf16encode(slotdata.plugin.name))
					make_flevent(data_FLdt, 212, slotdata.plugin.write())
					if slotdata.name != None: make_flevent(data_FLdt, 203, utf16encode(slotdata.name))
					if slotdata.icon != None: make_flevent(data_FLdt, 155, slotdata.icon)
					if slotdata.color != None: make_flevent(data_FLdt, 128, slotdata.color)
					if slotdata.plugin.params != None: make_flevent(data_FLdt, 213, slotdata.plugin.params)
				make_flevent(data_FLdt, 98, slotnum)
			fxrouting_fl = [0 for _ in range(127)]
			for route in mixerdat.routing: fxrouting_fl[route] = 1
			make_flevent(data_FLdt, 235, bytearray(fxrouting_fl))
			make_flevent(data_FLdt, 154, mixerdat.inchannum)
			make_flevent(data_FLdt, 147, mixerdat.outchannum)

		make_flevent(data_FLdt, 225, self.initfxvals.write())
		make_flevent(data_FLdt, 133, 216)

		#self.tracks = {}
		#self.items = []
		#self.timemarkers = []
		#self.name = None



		data_FLhd.seek(0)
		flpout.write(b'FLhd')
		data_FLhd_out = data_FLhd.read()
		flpout.write(len(data_FLhd_out).to_bytes(4, 'little'))
		flpout.write(data_FLhd_out)

		data_FLdt.seek(0)
		flpout.write(b'FLdt')
		data_FLdt_out = data_FLdt.read()
		flpout.write(len(data_FLdt_out).to_bytes(4, 'little'))
		flpout.write(data_FLdt_out)




















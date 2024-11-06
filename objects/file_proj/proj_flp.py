# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
import zipfile
import logging
from io import BytesIO
from functions import data_bytes
from functions_plugin import format_flp_tlv
from objects.data_bytes import bytereader
from objects.data_bytes import bytewriter

from objects.file_proj._flp import fx
from objects.file_proj._flp import channel
from objects.file_proj._flp import auto
from objects.file_proj._flp import arrangement
from objects.exceptions import ProjectFileParserException

logger_projparse = logging.getLogger('projparse')

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
		self.timemarkers = []


class debug_eventview:
	def __init__(self):
		self.eventtable = None

	def load(self):
		if not self.eventtable:
			with open('data_debug/flp_eventname.txt') as f:
			    lines = f.readlines()

			self.eventtable = []
			for line in lines:
			    idname = line.rstrip().split()
			    if len(idname) > 1:
			        self.eventtable.append([idname[0], idname[1]])
			    else:
			        self.eventtable.append([idname[0], '_unknown'])

	def view_event(self, event_id, eeval):
		d = self.eventtable[event_id]

		if event_id <= 63 and event_id >= 0: print('INT8, ', end=' ')
		if event_id <= 127 and event_id >= 64: print('INT16,', end=' ')
		if event_id <= 191 and event_id >= 128: print('INT32,', end=' ')
		if event_id <= 224 and event_id >= 192: 
			print('TEXT, ', end=' ')
			eeval = 'HEX '+eeval.hex()
		if event_id <= 255 and event_id >= 225: 
			print('RAW,  ', end=' ')
			eeval = 'HEX '+eeval.hex()

		print(str(d[0]).ljust(5), d[1].ljust(18), eeval)

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

		self.current_ctrl = None

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

		self.zipped = False
		self.zipfile = None
		#with open('flp_eventname.txt') as f:
		#	self.lines = f.readlines()

	def do_event(self, event_id, event_data):
		if event_id == 199: 
			FLVersion = event_data.decode('utf-8').rstrip('\x00')
			logger_projparse.info('FL: Version: ' + FLVersion)
			self.version_split = [int(x) for x in FLVersion.split('.')]
			if self.version_split[0] < 12 and self.version_split[0] != 24:
				raise ProjectFileParserException('FL: Version '+str(self.version_split[0])+' is not supported.') 
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
			self.internal_cur_timemarkers = self.current_pat_obj.timemarkers

		elif event_id == 223:
			event_bio = bytereader.bytereader(event_data)
			while event_bio.remaining():
				pos, autov, val = struct.unpack('IIi', event_bio.read(12))
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
			self.internal_cur_timemarkers = self.current_arr_obj.timemarkers

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
			self.internal_cur_timemarkers.append(timemarker_obj)

		elif event_id == 205: self.internal_cur_timemarkers[-1].name = decodetext(self.version_split, event_data)
		elif event_id == 33: self.internal_cur_timemarkers[-1].numerator = event_data
		elif event_id == 34: self.internal_cur_timemarkers[-1].denominator = event_data
	


		#Init Controls
		elif event_id == 216: self.startvals.read(event_data)
		elif event_id == 225: self.initfxvals.read(event_data)
		elif event_id == 227: 
			self.current_ctrl = flp_auto = auto.flp_remotecontrol()
			flp_auto.read(event_data)
			if flp_auto.channel not in self.remote_assoc: self.remote_assoc[flp_auto.channel] = []
			self.remote_assoc[flp_auto.channel].append(flp_auto)
		elif event_id == 230: 
			self.current_ctrl.formula = decodetext(self.version_split, event_data)

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
			elif event_id == 209: 
				self.current_ch_obj.delay.read(event_data)
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
			elif event_id == 70:  self.current_ch_obj.fxflags = event_data
			elif event_id == 22:  self.current_ch_obj.fxchannel = event_data
			elif event_id == 94:  self.current_ch_obj.layer_chans.append(event_data)
			elif event_id == 228: 
				trk_obj = channel.flp_channel_tracking()
				trk_obj.read(event_data)
				self.current_ch_obj.tracking.append(trk_obj)
			elif event_id == 219: self.current_ch_obj.basicparams.read(event_data)
			elif event_id == 221: self.current_ch_obj.poly.read(event_data)


			elif event_id == 234: 
				auto_obj = auto.flp_autopoints()
				auto_obj.read(event_data)
				self.current_ch_obj.autopoints = auto_obj

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

	def view_tlv(self, inputfile):
		song_data = bytereader.bytereader()
		song_data.load_file(inputfile)

		debugv = debug_eventview()
		debugv.load()

		main_iff_obj = song_data.chunk_objmake()
		tlvfound = False
		for chunk_obj in main_iff_obj.iter(0, song_data.end):
			if chunk_obj.id == b'FLdt':
				tlvfound = True
				for event_id, event_data in format_flp_tlv.decode(song_data, chunk_obj.end): 
					debugv.view_event(event_id, event_data)

	def read(self, inputfile):
		song_data = bytereader.bytereader()
		song_data.load_file(inputfile)

		if song_data.read(2) == b'PK':
			self.zipped = True
			self.zipfile = zipfile.ZipFile(inputfile, 'r')
			flpfound = False
			for filename in self.zipfile.namelist():
				if filename.endswith('.flp'):
					song_data.load_raw(self.zipfile.read(filename))
					flpfound = True
			if not flpfound:
				raise ProjectFileParserException('FL: FLP file not found in zip')

		main_iff_obj = song_data.chunk_objmake()
		tlvfound = False
		for chunk_obj in main_iff_obj.iter(0, song_data.end):
			if chunk_obj.id == b'FLhd':
				song_data.skip(2)
				self.num_channels = song_data.uint16()
				self.ppq = song_data.uint16()
			if chunk_obj.id == b'FLdt':
				tlvfound = True
				for event_id, event_data in format_flp_tlv.decode(song_data, chunk_obj.end): self.do_event(event_id, event_data)
		if not tlvfound:
			raise ProjectFileParserException('FL: TLV data not found')

	def make(self, outputfile):

		flpout = open(outputfile, 'wb')

		flpwriter = bytewriter.bytewriter()
		with flpwriter.chunk(b'FLhd') as chunkdata:
			chunkdata.raw(self.num_channels.to_bytes(3, 'big'))
			chunkdata.raw(b'\x00')
			chunkdata.raw(self.ppq.to_bytes(2, 'little'))

		with flpwriter.chunk(b'FLdt') as chunkdata:
			format_flp_tlv.write_tlv(chunkdata, 199, '20.7.2.1852'.encode('utf8') + b'\x00')
			format_flp_tlv.write_tlv(chunkdata, 159, 1852)
			format_flp_tlv.write_tlv(chunkdata, 37, 1)
			format_flp_tlv.write_tlv(chunkdata, 200, b'\x00\x00')
			format_flp_tlv.write_tlv(chunkdata, 156, int(self.tempo)*1000)
			format_flp_tlv.write_tlv(chunkdata, 67, self.nonsong_patnum)
			format_flp_tlv.write_tlv(chunkdata, 9, self.loop_active)
			format_flp_tlv.write_tlv(chunkdata, 11, self.shuffle)
			format_flp_tlv.write_tlv(chunkdata, 80, self.mainpitch)
			format_flp_tlv.write_tlv(chunkdata, 17, self.numerator)
			format_flp_tlv.write_tlv(chunkdata, 18, self.denominator)
			format_flp_tlv.write_tlv(chunkdata, 35, 1)
			format_flp_tlv.write_tlv(chunkdata, 23, self.panning_law)
			format_flp_tlv.write_tlv(chunkdata, 30, self.truncate_clip_notes)
			format_flp_tlv.write_tlv(chunkdata, 10, self.showinfo)
			format_flp_tlv.write_tlv(chunkdata, 194, utf16encode(self.title))
			format_flp_tlv.write_tlv(chunkdata, 206, utf16encode(self.genre))
			format_flp_tlv.write_tlv(chunkdata, 207, utf16encode(self.author))
			format_flp_tlv.write_tlv(chunkdata, 202, utf16encode(self.projectdatapath))
			format_flp_tlv.write_tlv(chunkdata, 195, utf16encode(self.comment))
			if self.url: format_flp_tlv.write_tlv(chunkdata, 197, utf16encode(self.url))
			format_flp_tlv.write_tlv(chunkdata, 146, 4294967295)
			format_flp_tlv.write_tlv(chunkdata, 216, self.startvals.write())

			for patnum, patdat in self.patterns.items():
				if patdat.automation or patdat.notes or patdat.color or (patdat.name != None):
					format_flp_tlv.write_tlv(chunkdata, 65, patnum)
					if patdat.automation:
						autobytes = b''
						#for pos, autov, val in patdat.automation: autobytes += struct.pack('III', pos, autov, val)
						#format_flp_tlv.write_tlv(chunkdata, 223, autobytes)
					if patdat.notes:
						flnotes = b''
						for fln in patdat.notes: 
							if fln.pos >= 0 and fln.key>=0:
								flnotes += struct.pack('IHHIHHBBBBBBBB', fln.pos,fln.flags,fln.rack,fln.dur,fln.key,fln.group,fln.finep,fln.u1,fln.rel,fln.midich,fln.pan,fln.velocity,fln.mod_x,fln.mod_y)
						format_flp_tlv.write_tlv(chunkdata, 224, flnotes)
					if patdat.color != None: format_flp_tlv.write_tlv(chunkdata, 150, patdat.color)
					if patdat.name != None: format_flp_tlv.write_tlv(chunkdata, 193, utf16encode(patdat.name))

					for timem_obj in patdat.timemarkers:
						format_flp_tlv.write_tlv(chunkdata, 148, (timem_obj.type << 24)+timem_obj.pos)
						format_flp_tlv.write_tlv(chunkdata, 33, timem_obj.numerator)
						format_flp_tlv.write_tlv(chunkdata, 34, timem_obj.denominator)
						if timem_obj.name != None: format_flp_tlv.write_tlv(chunkdata, 205, utf16encode(timem_obj.name))
						else: format_flp_tlv.write_tlv(chunkdata, 205, b'\x20\x00\x00\x00')

			format_flp_tlv.write_tlv(chunkdata, 226, b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
			format_flp_tlv.write_tlv(chunkdata, 226, b'\xfd\x00\x00\x00\x00\x00\x00\x00\x80\x90\xff\x0f\x04\x00\x00\x00\xd5\x01\x00\x00')
			format_flp_tlv.write_tlv(chunkdata, 226, b'\xff\x00\x00\x00\xff\x00\x00\x00\x04\x00\xff\x0f\x04\x00\x00\x00\x00\xfe\xff\xff')

			for _, m in self.remote_assoc.items():
				for remotectrl in m:
					bytes_remote, isvalid = remotectrl.write()
					if isvalid: 
						format_flp_tlv.write_tlv(chunkdata, 227, bytes_remote)
						if remotectrl.formula:
							format_flp_tlv.write_tlv(chunkdata, 230, utf16encode(remotectrl.formula))

			for chnum, chdat in self.channels.items():
				format_flp_tlv.write_tlv(chunkdata, 64, chnum)
				format_flp_tlv.write_tlv(chunkdata, 21, chdat.type)
				if chdat.type == 2:
					if chdat.plugin.name != None: format_flp_tlv.write_tlv(chunkdata, 201, utf16encode(chdat.plugin.name))
					format_flp_tlv.write_tlv(chunkdata, 212, chdat.plugin.write())
				if chdat.name != None: format_flp_tlv.write_tlv(chunkdata, 203, utf16encode(chdat.name))
				if chdat.icon != None: format_flp_tlv.write_tlv(chunkdata, 155, chdat.icon)
				if chdat.color != None: format_flp_tlv.write_tlv(chunkdata, 128, chdat.color)
				if chdat.plugin.params != None: format_flp_tlv.write_tlv(chunkdata, 213, chdat.plugin.params)

				format_flp_tlv.write_tlv(chunkdata, 0, chdat.enabled)
				format_flp_tlv.write_tlv(chunkdata, 209, chdat.delay.write())
				format_flp_tlv.write_tlv(chunkdata, 138, chdat.delayreso)
				format_flp_tlv.write_tlv(chunkdata, 139, chdat.reverb)
				format_flp_tlv.write_tlv(chunkdata, 89, chdat.shiftdelay)
				format_flp_tlv.write_tlv(chunkdata, 97, 128)
				format_flp_tlv.write_tlv(chunkdata, 69, chdat.fx)
				format_flp_tlv.write_tlv(chunkdata, 86, chdat.fx3)
				format_flp_tlv.write_tlv(chunkdata, 71, chdat.cutoff)
				format_flp_tlv.write_tlv(chunkdata, 83, chdat.resonance)
				format_flp_tlv.write_tlv(chunkdata, 74, chdat.preamp)
				format_flp_tlv.write_tlv(chunkdata, 75, chdat.decay)
				format_flp_tlv.write_tlv(chunkdata, 76, chdat.attack)
				format_flp_tlv.write_tlv(chunkdata, 85, chdat.stdel)
				format_flp_tlv.write_tlv(chunkdata, 131, chdat.fxsine)
				format_flp_tlv.write_tlv(chunkdata, 70, chdat.fxflags)
				format_flp_tlv.write_tlv(chunkdata, 22, chdat.fxchannel)
				for layer_chan in chdat.layer_chans: format_flp_tlv.write_tlv(chunkdata, 94, layer_chan)
				format_flp_tlv.write_tlv(chunkdata, 219, chdat.basicparams.write())
				format_flp_tlv.write_tlv(chunkdata, 229, chdat.ofslevels)
				format_flp_tlv.write_tlv(chunkdata, 221, chdat.poly.write())
				format_flp_tlv.write_tlv(chunkdata, 215, chdat.params.write())
				format_flp_tlv.write_tlv(chunkdata, 132, chdat.cutcutby)
				format_flp_tlv.write_tlv(chunkdata, 144, chdat.layerflags)
				format_flp_tlv.write_tlv(chunkdata, 145, 0)
				format_flp_tlv.write_tlv(chunkdata, 32, 0)
				for trking_obj in chdat.tracking: format_flp_tlv.write_tlv(chunkdata, 228, trking_obj.write())
				for env_lfo_obj in chdat.env_lfo: format_flp_tlv.write_tlv(chunkdata, 218, env_lfo_obj.write())
				format_flp_tlv.write_tlv(chunkdata, 143, chdat.sampleflags)
				format_flp_tlv.write_tlv(chunkdata, 20, chdat.looptype)

				if chdat.samplefilename: format_flp_tlv.write_tlv(chunkdata, 196, utf16encode(chdat.samplefilename))
				if chdat.middlenote != 60: format_flp_tlv.write_tlv(chunkdata, 135, chdat.middlenote)

			for arrnum, arrdat in self.arrangements.items():
				format_flp_tlv.write_tlv(chunkdata, 99, arrnum)
				if arrdat.name != None: format_flp_tlv.write_tlv(chunkdata, 241, utf16encode(arrdat.name))
				arr_bytes = b''
				for item in arrdat.items:
					arr_bytes += item.write()

				format_flp_tlv.write_tlv(chunkdata, 36, 0)
				format_flp_tlv.write_tlv(chunkdata, 233, arr_bytes) #PlayListItems
				for track_num, track_obj in arrdat.tracks.items():
					format_flp_tlv.write_tlv(chunkdata, 238, track_obj.write())
					if track_obj.name: format_flp_tlv.write_tlv(chunkdata, 239, utf16encode(track_obj.name))

				for timem_obj in arrdat.timemarkers:
					format_flp_tlv.write_tlv(chunkdata, 148, (timem_obj.type << 24)+timem_obj.pos)
					format_flp_tlv.write_tlv(chunkdata, 33, timem_obj.numerator)
					format_flp_tlv.write_tlv(chunkdata, 34, timem_obj.denominator)
					if timem_obj.name != None: format_flp_tlv.write_tlv(chunkdata, 205, utf16encode(timem_obj.name))
					else: format_flp_tlv.write_tlv(chunkdata, 205, b'\x20\x00\x00\x00')

				#make_trackinfo(data_FLdt, arrangements[arrangement]['tracks'])
			format_flp_tlv.write_tlv(chunkdata, 100, 0)
			format_flp_tlv.write_tlv(chunkdata, 29, 1)
			format_flp_tlv.write_tlv(chunkdata, 39, 1)
			format_flp_tlv.write_tlv(chunkdata, 31, 0)
			format_flp_tlv.write_tlv(chunkdata, 38, 1)

			for mixernum, mixerdat in self.mixer.items():
				#print(mixernum, mixerdat)
				format_flp_tlv.write_tlv(chunkdata, 236, mixerdat.write())
				if mixerdat.color != None: format_flp_tlv.write_tlv(chunkdata, 149, mixerdat.color)
				if mixerdat.name != None: format_flp_tlv.write_tlv(chunkdata, 204, utf16encode(mixerdat.name))
				if mixerdat.icon != None: format_flp_tlv.write_tlv(chunkdata, 95, mixerdat.icon)
				for slotnum, slotdata in enumerate(mixerdat.slots):
					if slotdata:
						if slotdata.plugin.name != None: format_flp_tlv.write_tlv(chunkdata, 201, utf16encode(slotdata.plugin.name))
						format_flp_tlv.write_tlv(chunkdata, 212, slotdata.plugin.write())
						if slotdata.name != None: format_flp_tlv.write_tlv(chunkdata, 203, utf16encode(slotdata.name))
						if slotdata.icon != None: format_flp_tlv.write_tlv(chunkdata, 155, slotdata.icon)
						if slotdata.color != None: format_flp_tlv.write_tlv(chunkdata, 128, slotdata.color)
						if slotdata.plugin.params != None: format_flp_tlv.write_tlv(chunkdata, 213, slotdata.plugin.params)
					format_flp_tlv.write_tlv(chunkdata, 98, slotnum)
				fxrouting_fl = [0 for _ in range(127)]
				for route in mixerdat.routing: fxrouting_fl[route] = 1
				format_flp_tlv.write_tlv(chunkdata, 235, bytearray(fxrouting_fl))
				format_flp_tlv.write_tlv(chunkdata, 154, mixerdat.inchannum)
				format_flp_tlv.write_tlv(chunkdata, 147, mixerdat.outchannum)

			format_flp_tlv.write_tlv(chunkdata, 225, self.initfxvals.write())
			format_flp_tlv.write_tlv(chunkdata, 133, 216)

		flpout.write(flpwriter.getvalue())




















# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj_past._cakewalk_wrk import events

class cakewalk_chunk_globalsettings:
	def __init__(self, byr_stream):
		self.Now = 1344
		self.From = 0
		self.Thru = 0
		self.KeySig = 0
		self.Clock = 4
		self.AutoSave = 0
		self.PlayDelay = 0
		self.ZeroCtrls = True
		self.SendSPP = False
		self.SendCont = True
		self.PatchSearch = True
		self.AutoStop = False
		self.StopTime = 0
		self.AutoRewind = False
		self.RewindTime = 0
		self.MetroPlay = False
		self.MetroRecord = True
		self.MetroAccent = True
		self.CountIn = 0
		self.ThruOn = True
		self.AutoRestart = False
		self.CurTempoOfs = 1
		self.TempoOfs1 = 32
		self.TempoOfs2 = 64
		self.TempoOfs3 = 128
		self.PunchEnabled = False
		self.PunchInTime = 0
		self.PunchOutTime = 0
		self.EndAllTime = 576
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.Now = byr_stream.uint32()
		self.From = byr_stream.uint32()
		self.Thru = byr_stream.uint32()
		self.KeySig = byr_stream.uint8()
		self.Clock = byr_stream.uint8()
		self.AutoSave = byr_stream.uint8()
		self.PlayDelay = byr_stream.uint8()
		byr_stream.skip(1)
		self.ZeroCtrls = bool(byr_stream.uint8())
		self.SendSPP = bool(byr_stream.uint8())
		self.SendCont = bool(byr_stream.uint8())
		self.PatchSearch = bool(byr_stream.uint8())
		self.AutoStop = bool(byr_stream.uint8())
		self.StopTime = byr_stream.uint32()
		self.AutoRewind = bool(byr_stream.uint8())
		self.RewindTime = byr_stream.uint32()
		self.MetroPlay = bool(byr_stream.uint8())
		self.MetroRecord = bool(byr_stream.uint8())
		self.MetroAccent = bool(byr_stream.uint8())
		self.CountIn = byr_stream.uint8()
		byr_stream.skip(2)
		self.ThruOn = bool(byr_stream.uint8())
		byr_stream.skip(19)
		self.AutoRestart = bool(byr_stream.uint8())
		self.CurTempoOfs = byr_stream.uint8()
		self.TempoOfs1 = byr_stream.uint8()
		self.TempoOfs2 = byr_stream.uint8()
		self.TempoOfs3 = byr_stream.uint8()
		byr_stream.skip(2)
		self.PunchEnabled = bool(byr_stream.uint8())
		self.PunchInTime = byr_stream.uint32()
		self.PunchOutTime = byr_stream.uint32()
		self.EndAllTime = byr_stream.uint32()

	#def write(self, byw_stream):
	#	byw_stream.uint32(self.Now)
	#	byw_stream.uint32(self.From)
	#	byw_stream.uint32(self.Thru)
	#	byw_stream.uint8(self.KeySig)
	#	byw_stream.uint8(self.Clock)
	#	byw_stream.uint8(self.AutoSave)
	#	byw_stream.uint8(self.PlayDelay)
	#	byw_stream.raw(b'\x00')
	#	byw_stream.uint8(int(self.ZeroCtrls))
	#	byw_stream.uint8(int(self.SendSPP))
	#	byw_stream.uint8(int(self.SendCont))
	#	byw_stream.uint8(int(self.PatchSearch))
	#	byw_stream.uint8(int(self.AutoStop))
	#	byw_stream.uint32(self.StopTime)
	#	byw_stream.uint8(int(self.AutoRewind))
	#	byw_stream.uint32(self.RewindTime)
	#	byw_stream.uint8(int(self.MetroPlay))
	#	byw_stream.uint8(int(self.MetroRecord))
	#	byw_stream.uint8(int(self.MetroAccent))
	#	byw_stream.uint8(self.CountIn)
	#	byw_stream.raw(b'\xff\xff')
	#	byw_stream.uint8(int(self.ThruOn))
	#	byw_stream.raw(b'[\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
	#	byw_stream.uint8(int(self.AutoRestart))
	#	byw_stream.uint8(self.CurTempoOfs)
	#	byw_stream.uint8(self.TempoOfs1)
	#	byw_stream.uint8(self.TempoOfs2)
	#	byw_stream.uint8(self.TempoOfs3)
	#	byw_stream.raw(b'\x00\x00')
	#	byw_stream.uint8(int(self.PunchEnabled))
	#	byw_stream.uint32(self.PunchInTime)
	#	byw_stream.uint32(self.PunchOutTime)
	#	byw_stream.uint32(self.EndAllTime)
	#	byw_stream.raw(b'\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class cakewalk_chunk_timebase:
	def __init__(self, byr_stream):
		self.timebase = 120
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.timebase = byr_stream.uint16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.timebase)

class cakewalk_chunk_comment:
	def __init__(self, byr_stream):
		self.data = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.data = byr_stream.c_raw__int16(False)

	#def write(self, byw_stream):
	#	byw_stream.c_raw__int16(self.data, False)

class cakewalk_chunk_variable:
	def __init__(self, byr_stream):
		self.name = ''
		self.value = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.name = byr_stream.string(32)
		self.value = byr_stream.rest()

	#def write(self, byw_stream):
	#	byw_stream.string(self.name, 32)
	#	byw_stream.raw(self.value)

class cakewalk_chunk_stringtable:
	def __init__(self, byr_stream):
		self.data = {}
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		num = byr_stream.uint16()
		for _ in range(num):
			data = byr_stream.c_raw__int8()
			self.data[byr_stream.uint8()] = data

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.data))
	#	for k, v in self.data.items():
	#		byw_stream.c_raw__int8(v)
	#		byw_stream.uint8(k)

class cakewalk_chunk_smpte_time:
	def __init__(self, byr_stream):
		self.fmt = 30
		self.ofs = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.fmt = byr_stream.uint16()
		self.ofs = byr_stream.uint16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.fmt)
	#	byw_stream.uint16(self.ofs)

class cakewalk_chunk_ext_thru:
	def __init__(self, byr_stream):
		self.port = 0
		self.channel = 0
		self.keyPlus = 0
		self.velPlus = 0
		self.localPort = 0
		self.mode = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		byr_stream.skip(2)
		self.port = byr_stream.uint8()
		self.channel = byr_stream.uint8()
		self.keyPlus = byr_stream.uint8()
		self.velPlus = byr_stream.uint8()
		self.localPort = byr_stream.uint8()
		self.mode = byr_stream.uint8()

	#def write(self, byw_stream):
	#	byw_stream.raw('\0\0')
	#	byw_stream.uint8(self.port)
	#	byw_stream.uint8(self.channel)
	#	byw_stream.uint8(self.keyPlus)
	#	byw_stream.uint8(self.velPlus)
	#	byw_stream.uint8(self.localPort)
	#	byw_stream.uint8(self.mode)

class cakewalk_chunk_tracknewoffset:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.offset = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.offset = byr_stream.int32()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.int32(self.offset)

class cakewalk_chunk_markers:
	def __init__(self, byr_stream):
		self.markers = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		numevents = byr_stream.uint32()
		for _ in range(numevents):
			smpte = byr_stream.uint8()
			byr_stream.skip(1)
			time = byr_stream.uint24()
			byr_stream.skip(5)
			data = byr_stream.c_raw__int8()
			self.markers.append([smpte, time, data])

	#def write(self, byw_stream):
	#	byw_stream.uint32(len(self.markers))
	#	for smpte, time, data in self.markers: 
	#		byw_stream.uint8(smpte)
	#		byw_stream.zeros(1)
	#		byw_stream.uint24(time)
	#		byw_stream.zeros(5)
	#		byw_stream.c_raw__int8(data)

class cakewalk_chunk_tempo:
	def __init__(self, byr_stream):
		self.points = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		numevents = byr_stream.uint16()
		for _ in range(numevents):
			time = byr_stream.uint32()
			byr_stream.skip(4)
			tempo = byr_stream.uint16()
			byr_stream.skip(8)
			self.points.append([time, tempo])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for time, tempo in self.points: 
	#		byw_stream.uint32(time)
	#		byw_stream.zeros(4)
	#		byw_stream.uint16(tempo)
	#		byw_stream.zeros(8)

class cakewalk_chunk_meter_map:
	def __init__(self, byr_stream):
		self.points = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		numevents = byr_stream.uint16()
		for _ in range(numevents):
			byr_stream.skip(4)
			measure = byr_stream.uint16()
			num = byr_stream.uint8()
			den = byr_stream.uint8()
			byr_stream.skip(4)
			self.points.append([measure, num, den])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for measure, num, den in self.points: 
	#		byw_stream.zeros(4)
	#		byw_stream.uint16(measure)
	#		byw_stream.uint8(num)
	#		byw_stream.uint8(den)
	#		byw_stream.zeros(4)

class cakewalk_chunk_meter_key:
	def __init__(self, byr_stream):
		self.points = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		numevents = byr_stream.uint16()
		for _ in range(numevents):
			measure = byr_stream.uint16()
			num = byr_stream.uint8()
			den = byr_stream.uint8()
			alt = byr_stream.uint8()
			self.points.append([measure, num, den, alt])

	#def write(self, byw_stream):
	#	byw_stream.uint16(len(self.points))
	#	for measure, num, den, alt in self.points: 
	#		byw_stream.uint16(measure)
	#		byw_stream.uint8(num)
	#		byw_stream.uint8(den)
	#		byw_stream.uint8(alt)

class cakewalk_chunk_sysex:
	def __init__(self, byr_stream):
		self.bank = 0
		self.autosend = 0
		self.name = b''
		self.data = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.bank = byr_stream.uint8()
		length = byr_stream.uint16()
		self.autosend = byr_stream.uint8()
		self.name = byr_stream.c_raw__int8()
		self.data = byr_stream.raw(length)

	#def write(self, byw_stream):
	#	byw_stream.uint8(self.bank)
	#	byw_stream.uint16(len(self.data))
	#	byw_stream.uint8(self.autosend)
	#	byw_stream.c_raw__int8(self.name)
	#	byw_stream.raw(self.data)

class cakewalk_chunk_newsysex:
	def __init__(self, byr_stream):
		self.bank = 0
		self.autosend = 0
		self.port = 0
		self.name = b''
		self.data = b''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.bank = byr_stream.uint16()
		length = byr_stream.uint32()
		self.port = byr_stream.uint16()
		self.autosend = byr_stream.uint8()
		self.name = byr_stream.c_raw__int8()
		self.data = byr_stream.raw(length)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.bank)
	#	byw_stream.uint32(len(self.data))
	#	byw_stream.uint16(self.port)
	#	byw_stream.uint8(self.autosend)
	#	byw_stream.c_raw__int8(self.name)
	#	byw_stream.raw(self.data)

# --------------------------------------------------------- TRACKS ---------------------------------------------------------

class cakewalk_chunk_track:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.name = ''
		self.channel = 0
		self.pitch = 0
		self.velocity = 100
		self.port = 0
		self.flags = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.name = byr_stream.c_raw__int8()
		self.pitch = byr_stream.uint8()
		self.channel = byr_stream.uint8()
		self.velocity = byr_stream.uint8()
		self.port = byr_stream.uint8()
		self.flags = byr_stream.uint8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.c_raw__int8(self.name)
	#	byw_stream.uint8(self.channel)
	#	byw_stream.uint8(self.pitch)
	#	byw_stream.uint8(self.velocity)
	#	byw_stream.uint8(self.port)
	#	byw_stream.uint8(self.flags)

class cakewalk_chunk_trackname:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.name = ''
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.name = byr_stream.c_raw__int8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.c_string__int8(self.name)

class cakewalk_chunk_trackpatch:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.patch = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.patch = byr_stream.uint8()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint8(self.patch)

class cakewalk_chunk_trackbank:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.bank = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.bank = byr_stream.uint16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(self.bank)

class cakewalk_chunk_trackvol:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.vol = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.vol = byr_stream.uint16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(self.vol)


class cakewalk_chunk_trackoffset:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.offset = 0
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		self.offset = byr_stream.int16()

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.int16(self.offset)


class cakewalk_chunk_eventstream:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.events = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		numevents = byr_stream.uint16()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_old(byr_stream)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint16(len(self.events))
	#	for x in self.events: x.write_old(byw_stream)

class cakewalk_chunk_eventsext:
	def __init__(self, byr_stream):
		self.trackno = 0
		self.events = []
		if byr_stream: self.read(byr_stream)

	def read(self, byr_stream):
		self.trackno = byr_stream.uint16()
		numevents = byr_stream.uint32()
		for _ in range(numevents):
			event = events.cakewalk_event()
			event.read_new(byr_stream)
			self.events.append(event)

	#def write(self, byw_stream):
	#	byw_stream.uint16(self.trackno)
	#	byw_stream.uint32(len(self.events))
	#	for x in self.events: x.write_new(byw_stream)

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from dataclasses import dataclass
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

verbose = False

def calc_gatetime_3(song_file):
	t_durgate = []
	t_durgate_value = song_file.uint8()
	t_durgate.append(t_durgate_value&127)
	if bool(t_durgate_value&128) == True: 
		t_durgate_value = song_file.uint8()
		t_durgate.append(t_durgate_value&127)
		if bool(t_durgate_value&128) == True: 
			t_durgate_value = song_file.uint8()
			t_durgate.append(t_durgate_value&127)
	t_durgate.reverse()

	out_duration = 0
	for shift, note_durbyte in enumerate(t_durgate): out_duration += note_durbyte << shift*7
	return out_duration

class smaf_track_ma3:
	def __init__(self, song_file, end):
		self.format_type = song_file.uint8()
		self.sequence_type = song_file.uint8()
		self.timebase_dur = song_file.uint8()
		self.timebase_gate = song_file.uint8()

		self.channel_stat = song_file.l_uint32(4)
		self.sequence = None
		self.setup = None
		self.audio = {}

		trk_iff_obj = song_file.chunk_objmake()
		trk_iff_obj.set_sizes(4, 4, True)
		for chunk_obj in trk_iff_obj.iter(song_file.tell(), end):
			logger_projparse.info('mmf: MA3 chunk '+str(chunk_obj.id))

			if chunk_obj.id == b'Mtsq':
				self.sequence = []
				while song_file.tell() < chunk_obj.end-1:
					resttime = calc_gatetime_3(song_file)
					if verbose: print(song_file.tell(), chunk_obj.end, end=' | ')
					if verbose: print(str(resttime).ljust(5)+'| ', end='')
					event_id, channel = song_file.bytesplit()
					if verbose: print(str(event_id).ljust(3), end=' ')

					if event_id == 0:
						if verbose: print('|	  NULL	')
						self.sequence.append([resttime, event_id])
			
					elif event_id == 8:
						note_note = song_file.uint8()
						note_durgate = calc_gatetime_3(song_file)
						if verbose: print('| '+str(channel).ljust(4), 'NOTE	   ', str(note_note).ljust(4), '     dur ', note_durgate)
						self.sequence.append([resttime, event_id, channel, note_note, note_durgate])
			
					elif event_id == 9:
						note_note = song_file.uint8()
						note_vol = song_file.uint8()
						note_durgate = calc_gatetime_3(song_file)
						if verbose: print('| '+str(channel).ljust(4), 'NOTE+V  ', str(note_note).ljust(4), str(note_vol).ljust(4), 'dur ', note_durgate)
						self.sequence.append([resttime, event_id, channel, note_note, note_vol, note_durgate])
			
					elif event_id == 11:
						cntltype = song_file.uint8()
						cntldata = song_file.uint8()
						if verbose: print('| '+str(channel).ljust(4), 'CONTROL ', str(cntltype).ljust(4), str(cntldata).ljust(4))
						self.sequence.append([resttime, event_id, channel, cntltype, cntldata])
			
					elif event_id == 12:
						prognumber = song_file.uint8()
						if verbose: print('| '+str(channel).ljust(4), 'PROGRAM ', prognumber)
						self.sequence.append([resttime, event_id, channel, prognumber])
			
					elif event_id == 14:
						pitch = song_file.uint16()
						if verbose: print('| '+str(channel).ljust(4), 'PITCH   ', str(pitch).ljust(4))
						self.sequence.append([resttime, event_id, channel, pitch])
			
					elif event_id == 15 and channel == 0:
						sysexdata = song_file.raw(song_file.uint8())
						if verbose: print('| '+str(channel).ljust(4), 'SYSEX   ', sysexdata.hex())
						self.sequence.append([resttime, event_id, sysexdata])
			
					elif event_id == 15 and channel == 15:
						song_file.skip(1)
						if verbose: print('| '+str(channel).ljust(4), 'NOP	 ')
						self.sequence.append([resttime, 16])
			
					else:
						raise ProjectFileParserException('mmf: Unknown Command', event_id, "0x%X" % event_id)

			if chunk_obj.id == b'Mtsu': self.setup = song_file.raw(chunk_obj.size)

			if chunk_obj.id == b'Mtsp': 
				for mtsp_chunk_obj in chunk_obj.iter(0):
					if mtsp_chunk_obj.id[:3] == b'Mwa':
						audnum = mtsp_chunk_obj.id[3:][0]
						song_file.skip(1)
						hz = song_file.uint16_b()
						self.audio[audnum] = [hz, song_file.raw(mtsp_chunk_obj.size-3)]

VERBOSE_FILTER_CHANNEL = -2

def calc_gatetime_2(song_file):
	t_durgate = []
	t_durgate_value = song_file.uint8()
	t_durgate.append(t_durgate_value&127)
	if bool(t_durgate_value&128) == True: 
		t_durgate_value = song_file.uint8()
		t_durgate.append(t_durgate_value&127)
	t_durgate.reverse()

	out_duration = 0
	for shift, note_durbyte in enumerate(t_durgate): out_duration += note_durbyte << shift*7
	return out_duration

class smaf_event_ma2:
	def __init__(self, song_file):
		self.deltaTime = 0
		self.channel = 0
		self.event_type = ''
		self.value = 0
		self.is_short = False
		self.note_key = 0
		self.note_oct = 0
		self.duration = 0
		self.data = b''

		self.resttime = calc_gatetime_2(song_file)
		self.ch_oc, self.notenum = song_file.bytesplit()

		if (self.ch_oc, self.notenum) == (0, 0):
			ch_b, p_type = song_file.bytesplit()
			channel = ch_b>>2
			shortcmd = ch_b&3

			if shortcmd==2:
				self.channel = channel
				self.is_short = True
				self.event_type = 'modulation'
				self.value = p_type

			elif shortcmd==0:
				self.channel = channel
				self.is_short = True
				self.event_type = 'expression'
				self.value = p_type

			elif shortcmd==3 and p_type==0:
				self.channel = channel
				self.event_type = 'program'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==1:
				self.channel = channel
				self.event_type = 'bank'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==2:
				self.channel = channel
				self.event_type = 'octave_shift'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==3:
				self.channel = channel
				self.event_type = 'modulation'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==7:
				self.channel = channel
				self.event_type = 'volume'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==10:
				self.channel = channel
				self.event_type = 'pan'
				self.value = song_file.uint8()

			elif shortcmd==3 and p_type==11:
				self.channel = channel
				self.event_type = 'expression'
				self.value = song_file.uint8()

			else:
				logger_projparse.info('mmf: unknown type: '+str(ch_b)+' '+str(p_type))

			if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
				print(self.channel, '|', self.event_type.ljust(16), '|', self.resttime, self.value)

		elif (self.ch_oc, self.notenum) == (15, 15):
			nval = song_file.uint8()
			if nval:
				self.event_type = 'sysex'
			else:
				self.event_type = 'nop'

			if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
				print(self.channel, '|', self.event_type.ljust(16), '|', self.resttime, self.data)

		else:
			self.note_key = self.notenum
			self.note_oct = self.ch_oc&3
			self.channel = self.ch_oc>>2
			self.duration = calc_gatetime_2(song_file)
			self.event_type = 'note'

			if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
				print(self.channel, '|', self.event_type.ljust(16), '|', self.note_key, self.note_oct)

class smaf_track_ma2:
	def __init__(self, song_file, end):
		self.format_type = song_file.uint8()
		self.sequence_type = song_file.uint8()
		self.timebase_dur = song_file.uint8()
		self.timebase_gate = song_file.uint8()

		self.channel_stat = song_file.bytesplit16()

		self.sequence = None
		self.setup = None

		trk_iff_obj = song_file.chunk_objmake()
		trk_iff_obj.set_sizes(4, 4, True)
		for chunk_obj in trk_iff_obj.iter(song_file.tell(), end):
			logger_projparse.info('mmf: MA2 chunk '+str(chunk_obj.id))

			if chunk_obj.id == b'Mtsu': self.setup = song_file.raw(chunk_obj.size)

			if chunk_obj.id == b'Mtsq':
				self.sequence = []
				while song_file.tell() < chunk_obj.end-1:
					self.sequence.append(smaf_event_ma2(song_file))
					
class smaf_song:
	def __init__(self):
		self.title = None
		self.comment = None
		self.software = None
		self.tracks2 = [None for _ in range(4)]
		self.tracks3 = [None for _ in range(4)]

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: song_file.magic_check(b'MMMD')
		except ValueError as t: raise ProjectFileParserException('mmf: '+str(t))
		
		end_file = song_file.uint32_b()

		main_iff_obj = song_file.chunk_objmake()
		main_iff_obj.set_sizes(4, 4, True)
		for chunk_obj in main_iff_obj.iter(8, end_file+6):
			logger_projparse.info('mmf: MMMD chunk '+str(chunk_obj.id))

			if chunk_obj.id == b'CNTI':
				self.cnti_class = song_file.uint8()
				self.cnti_type = song_file.uint8()
				self.cnti_codetype = song_file.uint8()
				self.cnti_status = song_file.uint8()
				self.cnti_counts = song_file.uint8()

			if chunk_obj.id == b'OPDA':
				for trk_subchunk_obj in chunk_obj.iter(0):
					opda_iff_obj = song_file.chunk_objmake()
					opda_iff_obj.set_sizes(2, 2, True)
					for opda_chunk_obj in opda_iff_obj.iter(trk_subchunk_obj.start, trk_subchunk_obj.end):
						if opda_chunk_obj.id == b'ST': self.title = song_file.raw(opda_chunk_obj.size)
						elif opda_chunk_obj.id == b'CR': self.comment = song_file.raw(opda_chunk_obj.size)
						elif opda_chunk_obj.id == b'VN': self.software = song_file.raw(opda_chunk_obj.size)
						#else: logger_projparse.info('mmf: OPDA chunk: '+str(opda_chunk_obj.id), song_file.raw(opda_chunk_obj.size))

			if chunk_obj.id[:3] == b'MTR':
				mmf_tracknum = chunk_obj.id[3:][0]
				if mmf_tracknum in range(5, 8): self.tracks3[mmf_tracknum-5] = smaf_track_ma3(song_file, chunk_obj.end)
				if mmf_tracknum in range(1, 5): self.tracks2[mmf_tracknum-1] = smaf_track_ma2(song_file, chunk_obj.end)
		
		return True
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from objects.exceptions import ProjectFileParserException
from external.easybinrw import easybinrw
from external.easybinrw import chunked

import logging
logger_projparse = logging.getLogger('projparse')

verbose = 0

chunk_size_data = chunked.chunk_part_size()
chunk_size_data.size_endian = True

meta_chunk_size_data = chunked.chunk_part_size()
meta_chunk_size_data.name_size = 2
meta_chunk_size_data.size_size = 2
meta_chunk_size_data.size_endian = True

def calc_gatetime_3(ebrw_readstr):
	t_durgate = []
	t_durgate_value = ebrw_readstr.int_u8()
	t_durgate.append(t_durgate_value&127)
	if bool(t_durgate_value&128) == True: 
		t_durgate_value = ebrw_readstr.int_u8()
		t_durgate.append(t_durgate_value&127)
		if bool(t_durgate_value&128) == True: 
			t_durgate_value = ebrw_readstr.int_u8()
			t_durgate.append(t_durgate_value&127)
	t_durgate.reverse()

	out_duration = 0
	for shift, note_durbyte in enumerate(t_durgate): out_duration += note_durbyte << shift*7
	return out_duration

class smaf_track_ma3:
	def __init__(self, ebrw_readstr, end):
		self.format_type = ebrw_readstr.int_u8()
		self.sequence_type = ebrw_readstr.int_u8()
		self.timebase_dur = ebrw_readstr.int_u8()
		self.timebase_gate = ebrw_readstr.int_u8()

		self.channel_stat = ebrw_readstr.raw(16)
		self.sequence = None
		self.setup = None
		self.audio = {}

		if self.format_type==3:
			self.channel_stat = ebrw_readstr.skip(16)

		if verbose: print('------------------- MA3 TRACK %i -------------------' % self.format_type)
		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			logger_projparse.info('mmf: MA3 chunk '+str(part_obj.id))

			if part_obj.id == b'Mtsq':
				self.sequence = []
				if self.format_type in [2]:
					while (ebrw_readstr.remaining()-6)>0:
						resttime = calc_gatetime_3(ebrw_readstr)
						if verbose: print(str( ebrw_readstr.remaining() ).ljust(7), end=' | ')
						if verbose: print(str(resttime).ljust(5)+'| ', end='')
						event_id, channel = ebrw_readstr.int_u4_2()
						if verbose: print(str(channel).ljust(2), end=' ')
						if verbose: print(str(event_id).ljust(2), end=' ')

						if event_id == 0:
							if verbose: print('|-|	  NULL	')
							self.sequence.append([resttime, event_id])
				
						elif event_id == 2:
							val = ebrw_readstr.raw(2).hex()
							if verbose: print('|-|	  UNK 2	', str(val).ljust(4))
							self.sequence.append([resttime, event_id])
				
						elif event_id == 3:
							val = ebrw_readstr.raw(2).hex()
							if verbose: print('|-|	  UNK 3	', str(val).ljust(4))
							self.sequence.append([resttime, event_id])
				
						elif event_id == 4:
							val = ebrw_readstr.raw(1).hex()
							if verbose: print('|-|	  UNK 4	', str(val).ljust(4))
							self.sequence.append([resttime, event_id])

						elif event_id == 8:
							note_note = ebrw_readstr.int_u8()
							note_durgate = calc_gatetime_3(ebrw_readstr)
							if verbose: print('|-|', 'NOTE    ', str(note_note).ljust(4), '     dur ', note_durgate)
							self.sequence.append([resttime, event_id, channel, note_note, note_durgate])
				
						elif event_id == 9:
							note_note = ebrw_readstr.int_u8()
							note_vol = ebrw_readstr.int_u8()
							note_durgate = calc_gatetime_3(ebrw_readstr)
							if verbose: print('|-|', 'NOTE+V  ', str(note_note).ljust(4), str(note_vol).ljust(4), 'dur ', note_durgate)
							self.sequence.append([resttime, event_id, channel, note_note, note_vol, note_durgate])
				
						elif event_id == 10:
							if verbose: print('|-|', 'SKIP_10 ')
							ebrw_readstr.skip(2)
							self.sequence.append([resttime, event_id])
				
						elif event_id == 11:
							cntltype = ebrw_readstr.int_u8()
							cntldata = ebrw_readstr.int_u8()
							if verbose: print('|-|', 'CONTROL ', str(cntltype).ljust(4), str(cntldata).ljust(4))
							self.sequence.append([resttime, event_id, channel, cntltype, cntldata])
				
						elif event_id == 12:
							prognumber = ebrw_readstr.int_u8()
							if verbose: print('|-|', 'PROGRAM ', prognumber)
							self.sequence.append([resttime, event_id, channel, prognumber])
				
						elif event_id == 13:
							if verbose: print('|-|', 'SKIP_13 ')
							ebrw_readstr.skip(1)
							self.sequence.append([resttime, event_id])
				
						elif event_id == 14:
							pitch = ebrw_readstr.int_u16()
							if verbose: print('|-|', 'PITCH   ', str(pitch).ljust(4))
							self.sequence.append([resttime, event_id, channel, pitch])
				
						elif event_id == 15 and channel == 0:
							sysexdata = ebrw_readstr.raw(ebrw_readstr.int_u8())
							if verbose: print('|-|', 'SYSEX   ', sysexdata.hex())
							self.sequence.append([resttime, event_id, sysexdata])
				
						elif event_id == 15 and channel == 15:
							ebrw_readstr.skip(1)
							if verbose: print('|-|', 'NOP	 ')
							self.sequence.append([resttime, 16])
				
						else:
							raise ProjectFileParserException('mmf: Unknown Command 0x%X, 0x%X' % (event_id, channel))

			if part_obj.id == b'Mtsu': self.setup = ebrw_readstr.raw(part_obj.size)

			if part_obj.id == b'Mtsp': 
				for mtsp_part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
					if mtsp_part_obj.id[:3] == b'Mwa':
						audnum = mtsp_part_obj.id[3:][0]
						ebrw_readstr.skip(1)
						hz = ebrw_readstr.int_u16_b()
						self.audio[audnum] = [hz, ebrw_readstr.raw(mtsp_part_obj.size-3)]

VERBOSE_FILTER_CHANNEL = -2

def calc_gatetime_2(ebrw_readstr):
	t_durgate = []
	t_durgate_value = ebrw_readstr.int_u8()
	t_durgate.append(t_durgate_value&127)
	if bool(t_durgate_value&128) == True: 
		t_durgate_value = ebrw_readstr.int_u8()
		t_durgate.append(t_durgate_value&127)
	t_durgate.reverse()

	out_duration = 0
	for shift, note_durbyte in enumerate(t_durgate): out_duration += note_durbyte << shift*7
	return out_duration

class smaf_event_ma2:
	def __init__(self, ebrw_readstr):
		self.deltaTime = 0
		self.channel = 0
		self.event_type = ''
		self.value = 0
		self.is_short = False
		self.note_key = 0
		self.note_oct = 0
		self.duration = 0
		self.data = b''

		self.resttime = calc_gatetime_2(ebrw_readstr)
		self.ch_oc, self.notenum = ebrw_readstr.int_u4_2()

		if (self.ch_oc, self.notenum) == (0, 0):
			ch_b, p_type = ebrw_readstr.int_u4_2()
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
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==1:
				self.channel = channel
				self.event_type = 'bank'
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==2:
				self.channel = channel
				self.event_type = 'octave_shift'
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==3:
				self.channel = channel
				self.event_type = 'modulation'
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==7:
				self.channel = channel
				self.event_type = 'volume'
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==10:
				self.channel = channel
				self.event_type = 'pan'
				self.value = ebrw_readstr.int_u8()

			elif shortcmd==3 and p_type==11:
				self.channel = channel
				self.event_type = 'expression'
				self.value = ebrw_readstr.int_u8()

			else:
				logger_projparse.info('mmf: unknown type: '+str(ch_b)+' '+str(p_type))

			#if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
			#print(str(self.resttime).ljust(6), self.channel, '|', self.event_type.ljust(16), '|', self.value)

		elif (self.ch_oc, self.notenum) == (15, 15):
			nval = ebrw_readstr.int_u8()
			if nval==240:
				self.event_type = 'sysex'
				sysexsize = ebrw_readstr.int_u8()
				self.data = ebrw_readstr.raw(sysexsize)
			else:
				self.event_type = 'nop'

			#if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
			#print(str(self.resttime).ljust(6), self.channel, '|', self.event_type.ljust(16), '|', self.data.hex())

		else:
			self.note_key = self.notenum
			self.note_oct = self.ch_oc&3
			self.channel = self.ch_oc>>2
			self.duration = calc_gatetime_2(ebrw_readstr)
			self.event_type = 'note'

			#if VERBOSE_FILTER_CHANNEL==-1 or VERBOSE_FILTER_CHANNEL==self.channel:
			#print(str(self.resttime).ljust(6), self.channel, '|', self.event_type.ljust(16), '|', self.note_key, self.note_oct)

		#if not self.event_type:
		#	exit()

class smaf_track_ma2:
	def __init__(self, ebrw_readstr, end):
		self.format_type = ebrw_readstr.int_u8()
		self.sequence_type = ebrw_readstr.int_u8()
		self.timebase_dur = ebrw_readstr.int_u8()
		self.timebase_gate = ebrw_readstr.int_u8()

		self.channel_stat = ebrw_readstr.list_int_u4(2)

		self.sequence = None
		self.setup = None

		for part_obj in chunked.chunk_part_read_all_iso(ebrw_readstr, chunk_size_data):
			logger_projparse.info('mmf: MA2 chunk '+str(part_obj.id))

			if part_obj.id == b'Mtsu': self.setup = ebrw_readstr.raw(part_obj.size)

			if part_obj.id == b'Mtsq':
				self.sequence = []
				try:
					while (ebrw_readstr.remaining())>0:
						#print(str( ebrw_readstr.remaining() ).ljust(6), end=' > ')
						self.sequence.append(smaf_event_ma2(ebrw_readstr))
				except:
				#	print('error')
					pass
				#print(  ebrw_readstr.rest().hex()  )
					
class smaf_song:
	def __init__(self):
		self.title = None
		self.comment = None
		self.software = None
		self.tracks2 = [None for _ in range(4)]
		self.tracks3 = [None for _ in range(4)]

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: ebrw_readstr.magic_check(b'MMMD')
		except ValueError as t: raise ProjectFileParserException('mmf: '+str(t))
		
		end_file = ebrw_readstr.int_u32_b()

		for part_obj in chunked.chunk_part_read_end_iso(ebrw_readstr, chunk_size_data, end_file+6):
			logger_projparse.info('mmf: MMMD chunk '+str(part_obj.id))

			if part_obj.id == b'CNTI':
				self.cnti_class = ebrw_readstr.int_u8()
				self.cnti_type = ebrw_readstr.int_u8()
				self.cnti_codetype = ebrw_readstr.int_u8()
				self.cnti_status = ebrw_readstr.int_u8()
				self.cnti_counts = ebrw_readstr.int_u8()

			#if part_obj.id == b'OPDA':
			#	print(  ebrw_readstr.rest()  )
			#	for trk_subpart_obj in part_obj.iter(0):
			#		opda_iff_obj = ebrw_readstr.part_objmake()
			#		opda_iff_obj.set_sizes(2, 2, True)
			#		for opda_part_obj in opda_iff_obj.iter(trk_subpart_obj.start, trk_subpart_obj.end):
			#			if opda_part_obj.id == b'ST': self.title = ebrw_readstr.raw(opda_part_obj.size)
			#			elif opda_part_obj.id == b'CR': self.comment = ebrw_readstr.raw(opda_part_obj.size)
			#			elif opda_part_obj.id == b'VN': self.software = ebrw_readstr.raw(opda_part_obj.size)
			#			#else: logger_projparse.info('mmf: OPDA chunk: '+str(opda_part_obj.id), ebrw_readstr.raw(opda_part_obj.size))

			if part_obj.id[:3] == b'MTR':
				mmf_tracknum = part_obj.id[3:][0]
				match mmf_tracknum:
					case 0: self.tracks2[0] = smaf_track_ma2(ebrw_readstr, part_obj.end)
					case 1: self.tracks2[1] = smaf_track_ma2(ebrw_readstr, part_obj.end)
					case 2: self.tracks2[2] = smaf_track_ma2(ebrw_readstr, part_obj.end)
					case 3: self.tracks2[3] = smaf_track_ma2(ebrw_readstr, part_obj.end)
					case 4: self.tracks3[0] = smaf_track_ma3(ebrw_readstr, part_obj.end)
					case 5: self.tracks3[1] = smaf_track_ma3(ebrw_readstr, part_obj.end)
					case 6: self.tracks3[2] = smaf_track_ma3(ebrw_readstr, part_obj.end)
					case 7: self.tracks3[3] = smaf_track_ma3(ebrw_readstr, part_obj.end)

				#print(part_obj.id, mmf_tracknum, mmf_tracknum in range(5, 8), mmf_tracknum in range(1, 5))
				#if mmf_tracknum in range(5, 8): self.tracks3[mmf_tracknum-5] = smaf_track_ma3(ebrw_readstr, part_obj.end)
				#if mmf_tracknum in range(1, 5): self.tracks2[mmf_tracknum-1] = smaf_track_ma2(ebrw_readstr, part_obj.end)
		
		return True
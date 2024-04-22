# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects_params import fm_opl
from io import BytesIO
import struct

def decode_events(song_file):
	sop_eventdata = []
	track_numEvents = int.from_bytes(song_file.read(2), "little")
	track_dataSize = int.from_bytes(song_file.read(4), "little")
	for _ in range(track_numEvents):
		sop_event_pos = int.from_bytes(song_file.read(2), "little")
		sop_event_code = song_file.read(1)[0]
		if sop_event_code == 1: sop_eventdata.append([sop_event_pos, 'SPECIAL', song_file.read(1)[0]])
		elif sop_event_code == 2: 
			note_pitch = song_file.read(1)[0]
			note_length = int.from_bytes(song_file.read(2), "little")
			sop_eventdata.append([sop_event_pos, 'NOTE', note_pitch, note_length])
		elif sop_event_code == 3: sop_eventdata.append([sop_event_pos, 'TEMPO', song_file.read(1)[0]])
		elif sop_event_code == 4: sop_eventdata.append([sop_event_pos, 'VOL', song_file.read(1)[0]])
		elif sop_event_code == 5: sop_eventdata.append([sop_event_pos, 'PITCH', song_file.read(1)[0]])
		elif sop_event_code == 6: sop_eventdata.append([sop_event_pos, 'INST', song_file.read(1)[0]])
		elif sop_event_code == 7: sop_eventdata.append([sop_event_pos, 'PAN', song_file.read(1)[0]])
		elif sop_event_code == 8: sop_eventdata.append([sop_event_pos, 'GVOL', song_file.read(1)[0]])
		else:
			print('[error] unknown event code:', sop_event_code)
			exit()
	return sop_eventdata

class adlib_sop_track:
	def __init__(self):
		self.chanmode = 0
		self.events = []

class adlib_sop_project:
	def __init__(self):
		self.tracks = []
		self.insts = []
		self.majorVersion = 0
		self.minorVersion = 1
		self.fileName = ''
		self.title = ''
		self.opl_rhythm = 1
		self.tickBeat = 8
		self.beatMeasure = 4
		self.basicTempo = 120
		self.comment = ''
		self.controltrack = []

	def load_from_file(self, input_file):
		song_file = open(input_file, 'rb')
		if song_file.read(7) != b'sopepos': print('[error] sopepos magic mismatch'); exit()
		self.majorVersion, self.minorVersion = struct.unpack("BB", song_file.read(2))
		song_file.read(1)
		self.fileName = data_bytes.readstring_fixedlen(song_file, 13, None)
		self.title = data_bytes.readstring_fixedlen(song_file, 31, None)

		self.opl_rhythm, self.tickBeat, self.beatMeasure, self.basicTempo = struct.unpack("BxBxBB", song_file.read(6))

		self.comment = data_bytes.readstring_fixedlen(song_file, 13, None)
		num_tracks, num_insts = struct.unpack("BBx", song_file.read(3))
		self.tracks = [adlib_sop_track() for x in range(num_tracks)]

		for n in range(num_tracks): self.tracks[n].chanmode = song_file.read(1)[0]

		for _ in range(num_insts):
			insttype = song_file.read(1)[0]
			opli = fm_opl.opl_inst()
			opli.name = data_bytes.readstring_fixedlen(song_file, 8, "latin-1")
			opli.name_long = data_bytes.readstring_fixedlen(song_file, 19, "latin-1")
			if insttype in [0]: 
				iModChar, iModScale, iModAttack, iModSustain, iModWaveSel, iFeedback = song_file.read(6)
				opli.ops[0].avekf(iModChar)
				opli.ops[0].ksl_lvl(iModScale)
				opli.ops[0].att_dec(iModAttack)
				opli.ops[0].sus_rel(iModSustain)
				opli.ops[0].waveform = iModWaveSel
				opli.fmfb1(iFeedback)
				iCarChar, iCarScale, iCarAttack, iCarSustain, iCarWaveSel = song_file.read(5)
				opli.ops[1].avekf(iCarChar)
				opli.ops[1].ksl_lvl(iCarScale)
				opli.ops[1].att_dec(iCarAttack)
				opli.ops[1].sus_rel(iCarSustain)
				opli.ops[1].waveform = iCarWaveSel
				iModChar, iModScale, iModAttack, iModSustain, iModWaveSel, iFeedback = song_file.read(6)
				opli.ops[2].avekf(iModChar)
				opli.ops[2].ksl_lvl(iModScale)
				opli.ops[2].att_dec(iModAttack)
				opli.ops[2].sus_rel(iModSustain)
				opli.ops[2].waveform = iModWaveSel
				opli.fmfb2(iFeedback)
				iCarChar, iCarScale, iCarAttack, iCarSustain, iCarWaveSel = song_file.read(5)
				opli.ops[3].avekf(iCarChar)
				opli.ops[3].ksl_lvl(iCarScale)
				opli.ops[3].att_dec(iCarAttack)
				opli.ops[3].sus_rel(iCarSustain)
				opli.ops[3].waveform = iCarWaveSel
			elif insttype in [1,6,7,8,9,10]:
				opli.set_opl2()
				if insttype>5:
					opli.perc_on = True
					opli.perc_type = insttype-5
				iModChar, iModScale, iModAttack, iModSustain, iModWaveSel, iFeedback = song_file.read(6)
				opli.ops[0].avekf(iModChar)
				opli.ops[0].ksl_lvl(iModScale)
				opli.ops[0].att_dec(iModAttack)
				opli.ops[0].sus_rel(iModSustain)
				opli.ops[0].waveform = iModWaveSel
				opli.fmfb1(iFeedback)
				iCarChar, iCarScale, iCarAttack, iCarSustain, iCarWaveSel = song_file.read(5)
				opli.ops[1].avekf(iCarChar)
				opli.ops[1].ksl_lvl(iCarScale)
				opli.ops[1].att_dec(iCarAttack)
				opli.ops[1].sus_rel(iCarSustain)
				opli.ops[1].waveform = iCarWaveSel
			self.insts.append(opli)

		for n in range(num_tracks): self.tracks[n].events = decode_events(song_file)
		self.controltrack = decode_events(song_file)

		#chunks_ins = data_bytes.iff_read(chunks_main[0][1], 0)
		#for inc_name, inc_data in chunks_ins:
		#	if inc_name == b'CNTI': self.parse_cnti(inc_data)
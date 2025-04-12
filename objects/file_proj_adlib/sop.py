# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from objects.data_bytes import bytereader
from objects.inst_params import fm_opl

def decode_events(song_file):
	sop_eventdata = []
	track_numEvents = song_file.uint16()
	track_dataSize = song_file.uint32()
	for _ in range(track_numEvents):
		sop_event_pos = song_file.uint16()
		sop_event_code = song_file.uint8()
		if sop_event_code == 1: sop_eventdata.append([sop_event_pos, 'SPECIAL', song_file.uint8()])
		elif sop_event_code == 2: 
			note_pitch = song_file.uint8()
			note_length = song_file.uint16()
			sop_eventdata.append([sop_event_pos, 'NOTE', note_pitch, note_length])
		elif sop_event_code == 3: sop_eventdata.append([sop_event_pos, 'TEMPO', song_file.uint8()])
		elif sop_event_code == 4: sop_eventdata.append([sop_event_pos, 'VOL', song_file.uint8()])
		elif sop_event_code == 5: sop_eventdata.append([sop_event_pos, 'PITCH', song_file.uint8()])
		elif sop_event_code == 6: sop_eventdata.append([sop_event_pos, 'INST', song_file.uint8()])
		elif sop_event_code == 7: sop_eventdata.append([sop_event_pos, 'PAN', song_file.uint8()])
		elif sop_event_code == 8: sop_eventdata.append([sop_event_pos, 'GVOL', song_file.uint8()])
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
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: 
			song_file.magic_check(b'sopepos')
		except ValueError as t:
			raise ProjectFileParserException('adlib_sop: '+str(t))

		self.majorVersion = song_file.uint8()
		self.minorVersion = song_file.uint8()
		song_file.skip(1)
		self.fileName = song_file.string(13)
		self.title = song_file.string(31)

		self.opl_rhythm = song_file.uint8()
		song_file.skip(1)
		self.tickBeat = song_file.uint8()
		song_file.skip(1)
		self.beatMeasure = song_file.uint8()
		self.basicTempo = song_file.uint8()

		self.comment = song_file.string(13)
		num_tracks = song_file.uint8()
		num_insts = song_file.uint8()
		song_file.skip(1)
		self.tracks = [adlib_sop_track() for x in range(num_tracks)]

		for n in range(num_tracks): self.tracks[n].chanmode = song_file.uint8()

		for _ in range(num_insts):
			insttype = song_file.uint8()
			opli = fm_opl.opl_inst()
			opli.name = song_file.string(8, encoding="latin-1")
			opli.name_long = song_file.string(19, encoding="latin-1")
			if insttype in [0]: 
				opli.ops[0].avekf(song_file.uint8())
				opli.ops[0].ksl_lvl(song_file.uint8())
				opli.ops[0].att_dec(song_file.uint8())
				opli.ops[0].sus_rel(song_file.uint8())
				opli.ops[0].waveform = song_file.uint8()
				opli.fmfb1(song_file.uint8())

				opli.ops[1].avekf(song_file.uint8())
				opli.ops[1].ksl_lvl(song_file.uint8())
				opli.ops[1].att_dec(song_file.uint8())
				opli.ops[1].sus_rel(song_file.uint8())
				opli.ops[1].waveform = song_file.uint8()

				opli.ops[2].avekf(song_file.uint8())
				opli.ops[2].ksl_lvl(song_file.uint8())
				opli.ops[2].att_dec(song_file.uint8())
				opli.ops[2].sus_rel(song_file.uint8())
				opli.ops[2].waveform = song_file.uint8()
				opli.fmfb2(song_file.uint8())

				opli.ops[3].avekf(song_file.uint8())
				opli.ops[3].ksl_lvl(song_file.uint8())
				opli.ops[3].att_dec(song_file.uint8())
				opli.ops[3].sus_rel(song_file.uint8())
				opli.ops[3].waveform = song_file.uint8()

			elif insttype in [1,6,7,8,9,10]:
				opli.set_opl2()
				if insttype>5:
					opli.perc_on = True
					opli.perc_type = insttype-5

				opli.ops[0].avekf(song_file.uint8())
				opli.ops[0].ksl_lvl(song_file.uint8())
				opli.ops[0].att_dec(song_file.uint8())
				opli.ops[0].sus_rel(song_file.uint8())
				opli.ops[0].waveform = song_file.uint8()
				opli.fmfb1(song_file.uint8())
				
				opli.ops[1].avekf(song_file.uint8())
				opli.ops[1].ksl_lvl(song_file.uint8())
				opli.ops[1].att_dec(song_file.uint8())
				opli.ops[1].sus_rel(song_file.uint8())
				opli.ops[1].waveform = song_file.uint8()
			self.insts.append(opli)

		for n in range(num_tracks): self.tracks[n].events = decode_events(song_file)
		self.controltrack = decode_events(song_file)

		return True
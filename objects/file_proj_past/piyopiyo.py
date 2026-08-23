# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from external.easybinrw import easybinrw
from objects.exceptions import ProjectFileParserException
import logging

logger_projparse = logging.getLogger('projparse')

class piyopiyo_melo_track:
	def __init__(self, ebrw_readstr):
		self.octave = ebrw_readstr.int_u8()
		self.icon = ebrw_readstr.int_u8()
		self.unk = ebrw_readstr.int_u16()
		self.length = ebrw_readstr.int_u32()
		self.volume = ebrw_readstr.int_u32()
		self.unk2 = ebrw_readstr.skip(8)
		self.waveform = ebrw_readstr.list_int_s8(256)
		self.envelope = ebrw_readstr.list_int_u8(64)
		logger_projparse.info("piyopiyo: Track:  Oct:" + str(self.octave) + ", Icon:" + str(self.icon) + ", Len:" + str(self.length) + ", Vol:" + str(self.volume))

class piyopiyo_song:
	def __init__(self):
		self.loopend = 0
		self.loopstart = 0
		self.musicwait = 1
		self.notes_data = []
		self.perc_volume = 0
		self.tracks = []

	def load_from_file(self, input_file):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_file(input_file)

		try: ebrw_readstr.magic_check(b'PMD')
		except ValueError as t: raise ProjectFileParserException('piyopiyo: '+str(t))

		ebrw_readstr.skip(1)

		ptr__tracks = ebrw_readstr.int_u32()
		self.musicwait = ebrw_readstr.int_u32()
		logger_projparse.info("piyopiyo: MusicWait: " + str(self.musicwait))
		self.loopstart = ebrw_readstr.int_u32()
		logger_projparse.info("piyopiyo: Loop Beginning: " + str(self.loopstart))
		self.loopend = ebrw_readstr.int_u32()
		logger_projparse.info("piyopiyo: Loop End: " + str(self.loopend))
		records_per_track = ebrw_readstr.int_u32()
		logger_projparse.info("piyopiyo: Records Per Track: " + str(records_per_track))
		self.tracks = [piyopiyo_melo_track(ebrw_readstr) for _ in range(3)]
		self.perc_volume = ebrw_readstr.int_u32()
		ebrw_readstr.seek(ptr__tracks)
		self.notes_data = [ [[ebrw_readstr.flags_i24(), ebrw_readstr.int_u8()] for _ in range(records_per_track)] for _ in range(4)]
		return True
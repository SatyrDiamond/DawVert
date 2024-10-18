# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
from objects.exceptions import ProjectFileParserException
import logging

logger_projparse = logging.getLogger('projparse')

class piyopiyo_melo_track:
	def __init__(self, song_file):
		self.octave = song_file.uint8()
		self.icon = song_file.uint8()
		self.unk = song_file.uint16()
		self.length = song_file.uint32()
		self.volume = song_file.uint32()
		self.unk2 = song_file.skip(8)
		self.waveform = song_file.l_int8(256)
		self.envelope = song_file.l_uint8(64)

		logger_projparse.info("piyopiyo: Track:  Oct:" + str(self.octave) + ", Icon:" + str(self.icon) + ", Len:" + str(self.length) + ", Vol:" + str(self.volume))

class piyopiyo_song:
	def __init__(self):
		pass

	def load_from_file(self, input_file):
		song_file = bytereader.bytereader()
		song_file.load_file(input_file)

		try: song_file.magic_check(b'PMD')
		except ValueError as t: raise ProjectFileParserException('piyopiyo: '+str(t))

		song_file.skip(1)

		ptr__tracks = song_file.uint32()
		self.musicwait = song_file.uint32()
		self.loopstart = song_file.uint32()
		self.loopend = song_file.uint32()
		self.records_per_track = song_file.uint32()
		logger_projparse.info("piyopiyo: MusicWait: " + str(self.musicwait))
		logger_projparse.info("piyopiyo: Loop Beginning: " + str(self.loopstart))
		logger_projparse.info("piyopiyo: Loop End: " + str(self.loopend))
		logger_projparse.info("piyopiyo: Records Per Track: " + str(self.records_per_track))
		self.tracks = [piyopiyo_melo_track(song_file) for _ in range(3)]
		self.perc_volume = song_file.uint32()
		song_file.seek(ptr__tracks)
		self.notes_data = [ [[song_file.flags24(), song_file.uint8()] for _ in range(self.records_per_track)] for _ in range(4)]
		return True
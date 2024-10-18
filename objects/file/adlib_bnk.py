# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.inst_params import fm_opl
from objects.data_bytes import bytereader

class bnk_file:
	def __init__(self):
		self.index = []
		self.used = []
		self.names = []
		self.num_used = 0
		self.offset_data = 0
		self.byr_stream = None

	def read_file(self, oplifile):
		bio_in = open(oplifile, 'rb')

		byr_stream = self.byr_stream = bytereader.bytereader()
		byr_stream.load_file(oplifile)

		verMajor = byr_stream.uint8()
		verMinor = byr_stream.uint8()
		byr_stream.magic_check(b'ADLIB-')
		self.num_used = byr_stream.uint16()
		num_insts = byr_stream.uint16()
		offset_name = byr_stream.uint32()
		self.offset_data = byr_stream.uint32()
		byr_stream.skip(8)

		byr_stream.seek(offset_name)
		for _ in range(num_insts):
			self.index.append(byr_stream.uint16())
			self.used.append(byr_stream.uint8())
			self.names.append(byr_stream.string(9))

	def get_inst_index(self, num):
		instindex = self.index[num]
		instused = self.used[num]
		instname = self.names[num]

		opli = fm_opl.opl_inst()
		opli.set_opl2()

		if instused and self.byr_stream:
			opli.name = instname
			instloc = (30*(instindex))+self.offset_data
			self.byr_stream.seek(instloc)
			opli.perc_mode = bool(self.byr_stream.uint8())
			opli.perc_voicenum = self.byr_stream.uint8()
			for n in range(2):
				opd = opli.ops[n]
				opd.ksl = self.byr_stream.uint8()
				opd.freqmul = self.byr_stream.uint8()
				fb = self.byr_stream.uint8()
				opd.env_attack = self.byr_stream.uint8()
				opd.env_sustain = self.byr_stream.uint8()
				opd.sustained = bool(self.byr_stream.uint8())
				opd.env_decay = self.byr_stream.uint8()
				opd.env_release = self.byr_stream.uint8()
				opd.level = self.byr_stream.uint8()
				opd.tremolo = bool(self.byr_stream.uint8())
				opd.vibrato = bool(self.byr_stream.uint8())
				opd.ksr = bool(self.byr_stream.uint8())
				con = self.byr_stream.uint8()

				if n == 0: 
					opli.feedback_1 = fb
					opli.fm_1 = not bool(con)

			for n in range(2): opli.ops[1-n].waveform = self.byr_stream.uint8()

		else: opli.is_blank = True

		return opli
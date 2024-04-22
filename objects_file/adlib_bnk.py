# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from objects_params import fm_opl
from functions import data_bytes

class bnk_file:
	def __init__(self):
		self.index = []
		self.used = []
		self.names = []

	def read_file(self, oplifile):
		global bio_in
		bio_in = open(oplifile, 'rb')
		verMajor, verMinor = struct.unpack('BB', bio_in.read(2))
		if bio_in.read(6) != b'ADLIB-': exit('[error] ADLIB magic mismatch')
		self.numUsed, numInstruments, offsetName, self.offsetData = struct.unpack('HHIIxxxxxxxx', bio_in.read(20))
		bio_in.seek(offsetName)
		for _ in range(numInstruments):
			index, flags = struct.unpack('HB', bio_in.read(3))
			name = data_bytes.readstring_fixedlen(bio_in, 9, None)
			self.index.append(index)
			self.used.append(flags)
			self.names.append(name)

	def get_inst_index(self, num):
		global bio_in
		instindex = self.index[num]
		instused = self.used[num]
		instname = self.names[num]
		opli = fm_opl.opl_inst()
		opli.set_opl2()

		if instused:
			opli.name = instname
			instloc = (30*(instindex))+self.offsetData

			bio_in.seek(instloc)

			iPercussive, iVoiceNum = struct.unpack('BB', bio_in.read(2))
			opli.perc_mode = bool(iPercussive)
			opli.perc_voicenum = iVoiceNum

			for n in range(2):
				opd = opli.ops[n]
				ksl, mul, fb, att, sus, eg, dec, rel, lvl, am, vib, ksr, con = struct.unpack('BBBBBBBBBBBBB', bio_in.read(13))

				if n == 0: 
					opli.feedback_1 = fb
					opli.fm_1 = not bool(con)
				opd.ksl = ksl
				opd.freqmul = mul
				opd.env_attack = att
				opd.env_decay = dec
				opd.env_sustain = sus
				opd.env_release = rel
				opd.level = lvl
				opd.sustained = bool(eg)
				opd.tremolo = bool(am)
				opd.vibrato = bool(vib)
				opd.ksr = bool(ksr)

			for n in range(2): 
				opli.ops[1-n].waveform = bio_in.read(1)[0]

		else:
			opli.is_blank = True

		return opli
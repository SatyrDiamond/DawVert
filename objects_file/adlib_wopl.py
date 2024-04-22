# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import struct
from objects_params import fm_opl
from functions import data_bytes

def read_inst(bio_in, oplo, isbank):
	oplo.name = data_bytes.readstring_fixedlen(bio_in, 32, 'ascii')
	oplo.key_offs1, oplo.key_offs2, oplo.vel_offset, oplo.second_detune = struct.unpack('HHbb', bio_in.read(6))
	oplo.perc_key, bitflags = struct.unpack('BB', bio_in.read(2))
	if not bitflags&1: oplo.numops = 2
	if bitflags&2: oplo.pseudo4 = True
	if bitflags&4: oplo.is_blank = True
	oplo.perc_type = bitflags>>4
	fbc1, fbc2 = struct.unpack('BB', bio_in.read(2))
	oplo.fmfb1(fbc1)
	oplo.fmfb2(fbc2)
	for x in oplo.ops:
		x.avekf(bio_in.read(1)[0])
		x.ksl_lvl(bio_in.read(1)[0])
		x.att_dec(bio_in.read(1)[0])
		x.sus_rel(bio_in.read(1)[0])
		x.waveform = bio_in.read(1)[0]

class opli_file:
	def __init__(self):
		self.patch = fm_opl.opl_inst()

	def read_file(self, oplifile):
		bio_in = open(oplifile, 'rb')
		if bio_in.read(11) != b'WOPL3-INST\x00': exit('[error] WOPL3-INST magic mismatch')
		version, is_perc = struct.unpack('HB', bio_in.read(3))
		self.patch.perc_on = bool(is_perc)
		read_inst(bio_in, self.patch, False)

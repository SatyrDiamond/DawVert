# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

from objects.inst_params import fm_opl
from objects.data_bytes import bytereader

def read_inst(byr_stream, oplo, isbank):
	oplo.name = byr_stream.string(32, encoding='ascii')
	oplo.key_offs1 = byr_stream.uint16()
	oplo.key_offs2 = byr_stream.uint16()
	oplo.vel_offset = byr_stream.int8()
	oplo.second_detune = byr_stream.int8()
	oplo.perc_key = byr_stream.uint8()
	bitflags = byr_stream.uint8()
	if not bitflags&1: oplo.numops = 2
	if bitflags&2: oplo.pseudo4 = True
	if bitflags&4: oplo.is_blank = True
	oplo.perc_type = bitflags>>4
	oplo.fmfb1(byr_stream.uint8())
	oplo.fmfb2(byr_stream.uint8())
	for x in oplo.ops:
		x.avekf(byr_stream.uint8())
		x.ksl_lvl(byr_stream.uint8())
		x.att_dec(byr_stream.uint8())
		x.sus_rel(byr_stream.uint8())
		x.waveform = byr_stream.uint8()

class opli_file:
	def __init__(self):
		self.patch = fm_opl.opl_inst()

	def read_file(self, oplifile):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(oplifile)

		byr_stream.magic_check(b'WOPL3-INST\x00')
		version = byr_stream.uint16()
		is_perc = byr_stream.uint8()
		self.patch.perc_on = bool(is_perc)
		read_inst(byr_stream, self.patch, False)

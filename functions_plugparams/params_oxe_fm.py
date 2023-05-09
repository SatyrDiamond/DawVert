# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import struct
from io import BytesIO

def read_global(oxedata):
	oxedata_j = {}
	oxedata_j['reverb_time'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['reverb_damp'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['delay_time'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['delay_feedback'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['delay_lfo_rate'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['delay_lfo_amt'] = struct.unpack('f', oxedata.read(4))[0]
	for unusednum in range(10):
		oxedata_j['unused'+str(unusednum+1)] = struct.unpack('f', oxedata.read(4))[0]
	return oxedata_j

def read_program(oxedata):
	oxedata_j = {}
	oxedata_j['name'] = data_bytes.readstring_fixedlen(oxedata, 16, None)
	for opletter in ['a','b','c','d','e','f','x','z']:
		opjsonobj = 'op_'+opletter+'_'
		if opletter in ['x','z']: oxedata_j[opjsonobj+'on'], oxedata_j[opjsonobj+'cutoff'], oxedata_j[opjsonobj+'reso'], oxedata_j[opjsonobj+'amount'], oxedata_j[opjsonobj+'bypass'] = struct.unpack('fffff', oxedata.read(20) )
		else: oxedata_j[opjsonobj+'on'], oxedata_j[opjsonobj+'wave'], oxedata_j[opjsonobj+'coarse'], oxedata_j[opjsonobj+'fine'], oxedata_j[opjsonobj+'kbdtrk'] = struct.unpack('fffff', oxedata.read(20) )
		oxedata_j[opjsonobj+'kbdscaling'], oxedata_j[opjsonobj+'velsen'] = struct.unpack('ff', oxedata.read(8) )
		oxedata_j[opjsonobj+'delay_time'], oxedata_j[opjsonobj+'attack_time'], oxedata_j[opjsonobj+'decay_time'] = struct.unpack('fff', oxedata.read(12) )
		oxedata_j[opjsonobj+'sustain_lvl'], oxedata_j[opjsonobj+'sustain_time'], oxedata_j[opjsonobj+'release_time'] = struct.unpack('fff', oxedata.read(12) )
	opmodletters = ['a','b','c','d','e','f','x','z','out','pan']
	for minusparams in range(6):
		for numrange in range(10-minusparams):
			oxedata_j['mod_'+opmodletters[minusparams]+'_'+opmodletters[numrange+minusparams]] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_x_z'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_x_o'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_x_p'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_z_o'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_z_p'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['lfo_wave'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['lfo_rate'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['lfo_depth'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['lfo_delay'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['lfo_dest'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['portamento'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['pitch_curve'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['pitch_time'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['mod_wheel_dest'] = struct.unpack('f', oxedata.read(4))[0]
	oxedata_j['hq'] = struct.unpack('f', oxedata.read(4))[0]
	for unusednum in range(9):
		oxedata_j['unused'+str(unusednum+1)] = struct.unpack('f', oxedata.read(4))[0]
	return oxedata_j

def read_bank(oxedata):
	oxeglobal = read_global(oxedata)
	oxeprograms = []
	for _ in range(128):
		oxeprograms.append(read_program(oxedata))
	return oxeglobal, oxeprograms




def write_value(biodata, jsontag, jsonname, fallback):
	if jsonname in jsontag: biodata.write(struct.pack('f', jsontag[jsonname]))
	else: biodata.write(struct.pack('f', fallback))


def write_program(oxedata_out, oxeprogram):
	oxedata_out.write(b'Converted\x00\x00\x00\x00\x00\x00\x00')

	for opletter in ['a','b','c','d','e','f','x','z']:
		opjsonobj = 'op_'+opletter+'_'
		
		if opletter in ['x','z']: 
			write_value(oxedata_out, oxeprogram, opjsonobj+'on', 0), 
			write_value(oxedata_out, oxeprogram, opjsonobj+'cutoff', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'reso', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'amount', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'bypass', 0)
		else: 
			write_value(oxedata_out, oxeprogram, opjsonobj+'on', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'wave', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'coarse', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'fine', 0)
			write_value(oxedata_out, oxeprogram, opjsonobj+'kbdtrk', 0) 

		write_value(oxedata_out, oxeprogram, opjsonobj+'kbdscaling', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'velsen', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'delay_time', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'attack_time', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'decay_time', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'sustain_lvl', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'sustain_time', 0)
		write_value(oxedata_out, oxeprogram, opjsonobj+'release_time', 0)

	opmodletters = ['a','b','c','d','e','f','x','z','out','pan']
	for minusparams in range(6):
		for numrange in range(10-minusparams):
			write_value(oxedata_out, oxeprogram, 'mod_'+opmodletters[minusparams]+'_'+opmodletters[numrange+minusparams], 0)

	write_value(oxedata_out, oxeprogram, 'mod_x_z', 0)
	write_value(oxedata_out, oxeprogram, 'mod_x_o', 0)
	write_value(oxedata_out, oxeprogram, 'mod_x_p', 0)
	write_value(oxedata_out, oxeprogram, 'mod_z_o', 0)
	write_value(oxedata_out, oxeprogram, 'mod_z_p', 0)
	write_value(oxedata_out, oxeprogram, 'lfo_wave', 0)
	write_value(oxedata_out, oxeprogram, 'lfo_rate', 0)
	write_value(oxedata_out, oxeprogram, 'lfo_depth', 0)
	write_value(oxedata_out, oxeprogram, 'lfo_delay', 0)
	write_value(oxedata_out, oxeprogram, 'lfo_dest', 0)
	write_value(oxedata_out, oxeprogram, 'portamento', 0)
	write_value(oxedata_out, oxeprogram, 'pitch_curve', 0)
	write_value(oxedata_out, oxeprogram, 'pitch_time', 0)
	write_value(oxedata_out, oxeprogram, 'mod_wheel_dest', 0)
	write_value(oxedata_out, oxeprogram, 'hq', 0)

	for unusednum in range(9):
		oxedata_out.write(struct.pack('f', 0))


def writedata(oxeglobal, oxeprograms):
	oxedata_out = BytesIO()
	write_value(oxedata_out, oxeglobal, 'reverb_time', 0)
	write_value(oxedata_out, oxeglobal, 'reverb_damp', 0)
	write_value(oxedata_out, oxeglobal, 'delay_time', 0)
	write_value(oxedata_out, oxeglobal, 'delay_feedback', 0)
	write_value(oxedata_out, oxeglobal, 'delay_lfo_rate', 0)
	write_value(oxedata_out, oxeglobal, 'delay_lfo_amt', 0)
	for unusednum in range(10):
		oxedata_out.write(struct.pack('f', 0))

	out_programs = [{} for x in range(128)]

	for prognum in range(len(oxeprograms)):
		out_programs[prognum] = oxeprograms[prognum]

	for prognum in range(128):
		oxeprogram = out_programs[prognum]
		write_program(oxedata_out, oxeprogram)
		
	oxedata_out.seek(0)

	return oxedata_out.read()

# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct

from functions_midi_exdata import roland as sysex_roland
from functions_midi_exdata import yamaha as sysex_yamaha
from functions_midi_exdata import sony as sysex_sony
from functions_midi_exdata import universal as sysex_universal

from functions import data_bytes
from functions import idvals

idvals_sysex_brands = idvals.parse_idvalscsv('data_idvals/midi_sysex.csv')

def decode_exdata(sysexdata, isseqspec):
	exdata = data_bytes.to_bytesio(struct.pack("B"*len(sysexdata),*sysexdata))

	manufac = [exdata.read(1)[0]]

	if manufac == [0]:
		for _ in range(2):
			manufac.append(exdata.read(1)[0])

	if isseqspec == True:
		return manufac, exdata.read()
	else:
		model = exdata.read(1)[0]
		devid = exdata.read(1)[0]
		cmd = exdata.read(1)[0]
		code = exdata.read()
		return manufac, model, devid, cmd, code

def decode(i_sysexdata):
	exdata = data_bytes.to_bytesio(struct.pack("B"*len(i_sysexdata),*i_sysexdata))

	#print(idvals_sysex_brands)

	out_vendor = exdata.read(1)
	out_vendor_ext = False
	out_brandname = str(out_vendor[0])
	if out_vendor[0] == 0:
		out_vendor_ext = True
		out_vendor += exdata.read(2)
	
	idval_venid = '#'+bytes.hex(out_vendor)

	if idval_venid in idvals_sysex_brands: 
		out_brandname = idvals.get_idval(idvals_sysex_brands, str(idval_venid), 'name')

	datlen = len(exdata.getvalue())

	if datlen > 4:
		out_device = exdata.read(1)[0]
		out_model = exdata.read(1)[0]
		out_command = exdata.read(1)[0]
		out_data = exdata.read()
		out_parsed = {}

		devicename, groups, nameval = None, [None,None], [None,None]

		if out_vendor_ext == False:
			s_vendor = out_vendor[0]

			if s_vendor == 127 and out_model in [3, 4]: 
				devicename, groups, nameval = sysex_universal.decode(out_model, out_device, out_command, out_data)

			elif s_vendor == 76: 
				devicename, groups, nameval = sysex_sony.decode(out_model, out_device, out_command, out_data)

			elif s_vendor == 65: 
				devicename, groups, nameval = sysex_roland.decode(out_model, out_device, out_command, out_data)

			elif s_vendor == 67: 
				devicename, groups, nameval = sysex_yamaha.decode(out_model, out_device, out_command, out_data)

		return out_vendor, out_vendor_ext, out_brandname, out_device, out_model, out_command, out_data, devicename, groups, nameval

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
import numpy as np

fm_dtype = np.dtype([
	('op1', np.int8, 8),
	('op2', np.int8, 8),
	('op3', np.int8, 8),
	('op4', np.int8, 8),
	('other', np.int8, 2),
	])

def decode(sysex_obj, bstream):
	if sysex_obj.device == 127 and sysex_obj.model_id == 81:
		sysex_obj.model_name = 'aibo'
		if sysex_obj.command == 0: 
			sysex_obj.known = True
			sysex_obj.category = 'system?'
			sysex_obj.param = 'on?'
			sysex_obj.value = bstream.read(1)[0]
		if sysex_obj.command == 2:
			sysex_obj.known = True
			sysex_obj.category = 'synth?'
			sysex_obj.param = 'patch?'
			firstnum = int.from_bytes(bstream.read(2), 'big')
			bstream.read(2)
			sysex_obj.value = firstnum, np.frombuffer(bstream.read(34), dtype=fm_dtype)
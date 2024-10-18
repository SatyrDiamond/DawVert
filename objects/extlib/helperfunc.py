# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from ctypes import *

def castptr_ubyte_data(indata):
	insize = len(indata)
	casd = (c_ubyte*insize)()[0:insize] = indata
	return cast(casd, POINTER(c_ubyte))

def castptr_ubyte_blank(insize):
	casd = (c_ubyte*insize)()
	return cast(casd, POINTER(c_ubyte))

def castptr_int16_data(indata):
	insize = len(indata)
	casd = (c_int16*(insize*2))()[0:insize] = indata
	return cast(casd, POINTER(c_int16))

def castptr_int16_blank(insize):
	casd = (c_int16*(insize*2))()
	return cast(casd, POINTER(c_int16))

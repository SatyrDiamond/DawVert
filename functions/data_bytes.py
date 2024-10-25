# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# ----- Bytes -----

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def get_bitnums_int(x):
    return [i for i in range(x.bit_length()) if ((1 << i) & x)]

def get_bitnums(x):
    return get_bitnums_int(int.from_bytes(x, 'little'))

def set_bitnums(x, n):
	outvals = 0
	for v in x: outvals += (1 << v)
	return outvals.to_bytes(n, 'little') 
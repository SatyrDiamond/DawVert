# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def read_header(byr_stream):
	chunktype = byr_stream.uint32()
	chunksize = byr_stream.uint32()
	byr_stream.skip(4)
	return chunktype, chunksize

def write_chunk(byr_stream, chunkid, chunkdata):
	byr_stream.uint32(chunkid)
	byr_stream.uint32(len(chunkdata))
	byr_stream.uint32(0)
	byr_stream.raw(chunkdata)

# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from io import BytesIO

# ----- Bytes -----

def bytearray2BytesIO(bytearray):
	riffinsideriffobj = BytesIO()
	riffinsideriffobj.write(bytearray)
	riffinsideriffobj.seek(0)
	return riffinsideriffobj

# ----- RIFF -----

def riff_read_debug(riffbytebuffer, offset):
	if isinstance(riffbytebuffer, (bytes, bytearray)) == True:
		riffbytebuffer = bytearray2BytesIO(riffbytebuffer)
	riffobjects = []
	riffbytebuffer.seek(0,2)
	filesize = riffbytebuffer.tell()
	riffbytebuffer.seek(offset)
	while filesize > riffbytebuffer.tell():
		chunkname = riffbytebuffer.read(4)
		chunksize = int.from_bytes(riffbytebuffer.read(4), "little")
		chunkdata = riffbytebuffer.read(chunksize)
		riffobjects.append([chunkname, chunkdata])
	print('--------')
	count = 0
	for riffobject in riffobjects:
		print(str(count) + " " + str(riffobject[0])+ " " + str(len(riffobject[1])))
		count = count + 1
	print('--------')
	return riffobjects

def riff_read(riffbytebuffer, offset):
	if isinstance(riffbytebuffer, (bytes, bytearray)) == True:
		riffbytebuffer = bytearray2BytesIO(riffbytebuffer)
	riffobjects = []
	riffbytebuffer.seek(0,2)
	filesize = riffbytebuffer.tell()
	riffbytebuffer.seek(offset)
	while filesize > riffbytebuffer.tell():
		chunkname = riffbytebuffer.read(4)
		chunksize = int.from_bytes(riffbytebuffer.read(4), "little")
		chunkdata = riffbytebuffer.read(chunksize)
		riffobjects.append([chunkname, chunkdata])
	return riffobjects

def riff_make(riffobjects):
	riffobjectsbytes = BytesIO()
	for riffobject in riffobjects:
		riffobjectsbytes.write(riffobject[0])
		riffobjectsbytes.write(len(riffobject[1]).to_bytes(4, "little"))
		riffobjectsbytes.write(riffobject[1])
	riffobjectsbytes.seek(0)
	return riffobjectsbytes.read()

def getmultival(stream, table):
	output = []
	riffinsideriffobj = BytesIO(stream)
	for entry in table:
		output.append(riffinsideriffobj.read(entry))
	return output
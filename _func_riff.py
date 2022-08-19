# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

from io import BytesIO

def bytearray2BytesIO(bytearray):
	riffinsideriffobj = BytesIO()
	riffinsideriffobj.write(bytearray)
	return riffinsideriffobj

def readriffdata_debug(riffbytebuffer, offset):
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

def readriffdata(riffbytebuffer, offset):
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

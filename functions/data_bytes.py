# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from io import BytesIO
import numpy as np

# ----- Bytes -----

def bytearray2BytesIO(input):
	data = BytesIO()
	data.write(input)
	data.seek(0)
	return data

def readstring(data):
	output = b''
	terminated = 0
	while terminated == 0:
		char = data.read(1)
		if char != b'\x00' and char != b'': output += char
		else: terminated = 1
	return output.decode('ascii')

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

# ----- audio -----

def unsign_8(sampledata):
    sampledatabytes = np.frombuffer(sampledata, dtype='uint8')
    sampledatabytes = np.array(sampledatabytes) + 128
    return sampledatabytes.tobytes('C')

def unsign_16(sampledata):
    sampledatabytes = np.frombuffer(sampledata, dtype='uint16')
    sampledatabytes = np.array(sampledatabytes) + 32768
    return sampledatabytes.tobytes('C')

def mono2stereo(leftdata, rightdata, samplebytes):
	leftdata_stream = bytearray2BytesIO(leftdata)
	rightdata_stream = bytearray2BytesIO(rightdata)
	output_stream = BytesIO()
	for _ in range(int(len(leftdata)/samplebytes)):
		output_stream.write(leftdata_stream.read(samplebytes))
		output_stream.write(rightdata_stream.read(samplebytes))
	output_stream.seek(0)
	return output_stream.read()

# ----- RIFF -----

def riff_read_debug_big(riffbytebuffer, offset):
	return customchunk_read(riffbytebuffer, offset, 4, 4, "big", True)

def riff_read_big(riffbytebuffer, offset):
	return customchunk_read(riffbytebuffer, offset, 4, 4, "big", False)

def riff_read_debug(riffbytebuffer, offset):
	return customchunk_read(riffbytebuffer, offset, 4, 4, "little", True)

def riff_read(riffbytebuffer, offset):
	return customchunk_read(riffbytebuffer, offset, 4, 4, "little", False)

def customchunk_read(riffbytebuffer, offset, in_namesize, in_chunksize, endian, debugtxt):
	if isinstance(riffbytebuffer, (bytes, bytearray)) == True: riffbytebuffer = bytearray2BytesIO(riffbytebuffer)
	riffobjects = []
	riffbytebuffer.seek(0,2)
	filesize = riffbytebuffer.tell()
	riffbytebuffer.seek(offset)
	while filesize > riffbytebuffer.tell():
		chunkname = riffbytebuffer.read(in_namesize)
		chunksize = int.from_bytes(riffbytebuffer.read(in_chunksize), endian)
		chunkdata = riffbytebuffer.read(chunksize)
		riffobjects.append([chunkname, chunkdata])
	if debugtxt == True:
		print('--------')
		count = 0
		for riffobject in riffobjects:
			print(str(count) + " " + str(riffobject[0])+ " " + str(len(riffobject[1])))
			count = count + 1
		print('--------')
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
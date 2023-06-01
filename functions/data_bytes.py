# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from io import BytesIO
import numpy as np

# ----- Bytes -----

def to_bytesio(input):
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

def readstring_lenbyte(file_stream, length_size, length_endian, codec):
	stringlen = int.from_bytes(file_stream.read(length_size), length_endian)
	if stringlen != 0: return readstring_fixedlen(file_stream, stringlen, codec)
	else: return ''

def readstring_fixedlen(file_stream, length, codec):
	if codec != None: return file_stream.read(length).split(b'\x00')[0].decode(codec).translate(dict.fromkeys(range(32)))
	else: return file_stream.read(length).split(b'\x00')[0].decode().translate(dict.fromkeys(range(32)))

def splitbyte(value):
    first = value >> 4
    second = value & 0x0F
    return (first, second)

def to_bin(value, length):
	return [int(d) for d in bin(value)[2:].zfill(length)]

def crc16(data: bytes):
    table = [ 
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7, 0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6, 0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485, 0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4, 0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
        0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823, 0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
        0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12, 0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
        0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41, 0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
        0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70, 0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
        0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F, 0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E, 0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D, 0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C, 0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB, 0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
        0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A, 0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
        0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9, 0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
        0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8, 0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
    ]
    
    crc = 0xFFFF
    for byte in data:
        crc = (crc << 8) ^ table[(crc >> 8) ^ byte]
        crc &= 0xFFFF
    return crc

def swap32(x):
    return (((x << 24) & 0xFF000000) |
            ((x <<  8) & 0x00FF0000) |
            ((x >>  8) & 0x0000FF00) |
            ((x >> 24) & 0x000000FF))

def swap16(x):
    return (((x << 8) & 0xFF00) |
            ((x >> 8) & 0x00FF))

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
	leftdata_stream = to_bytesio(leftdata)
	rightdata_stream = to_bytesio(rightdata)
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
	if isinstance(riffbytebuffer, (bytes, bytearray)) == True: riffbytebuffer = to_bytesio(riffbytebuffer)
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
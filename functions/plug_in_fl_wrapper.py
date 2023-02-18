# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

ChunkType = {}
ChunkType[1] = 'MIDI'
ChunkType[2] = 'Flags'
ChunkType[30] = 'IO'
ChunkType[31] = 'Inputs'
ChunkType[32] = 'Outputs'
ChunkType[50] = 'PluginInfo'
ChunkType[51] = 'FourCC'
ChunkType[52] = 'GUID'
ChunkType[53] = 'State'
ChunkType[54] = 'Name'
ChunkType[55] = 'PluginPath'
ChunkType[56] = 'Vendor'
ChunkType[57] = 'Unknown57'

def decode_wrapper(bio_data): 
	bio_data.seek(0,2)
	bio_data_size = bio_data.tell()
	bio_data.seek(0)

	bio_data.read(4) # b'\n\x00\x00\x00'

	out_wrapper = {}

	while bio_data.tell() < bio_data_size:
		chunktype = int.from_bytes(bio_data.read(4), "little")
		chunksize = int.from_bytes(bio_data.read(4), "little")
		bio_data.read(4)
		chunkdata = bio_data.read(chunksize)
		#print(chunktype, ChunkType[chunktype], chunksize)
		if chunktype == 1:
			print('[native-fl-wrapper] MIDI')
			out_wrapper['midi'] = chunkdata
		if chunktype == 2:
			print('[native-fl-wrapper] Flags:', chunkdata)
			out_wrapper['flags'] = chunkdata
		if chunktype == 30:
			print('[native-fl-wrapper] IO', chunkdata)
			out_wrapper['io'] = chunkdata
		if chunktype == 32:
			print('[native-fl-wrapper] Outputs', chunkdata)
			out_wrapper['outputs'] = chunkdata
		if chunktype == 50:
			print('[native-fl-wrapper] PluginInfo', chunkdata)
			out_wrapper['plugin_info'] = chunkdata
		if chunktype == 51:
			print('[native-fl-wrapper] FourID:', int.from_bytes(chunkdata, "little"))
			out_wrapper['fourid'] = int.from_bytes(chunkdata, "little")
		if chunktype == 53:
			print('[native-fl-wrapper] State')
			out_wrapper['state'] = chunkdata
		if chunktype == 54:
			print('[native-fl-wrapper] Name:', chunkdata.decode())
			out_wrapper['name'] = chunkdata.decode()
		if chunktype == 55:
			print('[native-fl-wrapper] Plugin Path:', chunkdata.decode())
			out_wrapper['file'] = chunkdata.decode()
		if chunktype == 56:
			print('[native-fl-wrapper] Vendor:', chunkdata.decode())
			out_wrapper['vendor'] = chunkdata.decode()
		if chunktype == 57:
			print('[native-fl-wrapper] 57:', chunkdata)
			out_wrapper['57'] = chunkdata
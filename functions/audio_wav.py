# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from io import BytesIO

def makesmpl(instdata):
	if instdata != None:
		chunk_wavdata_smpl = BytesIO()
		temp_manufacturer = 0
		temp_product = 0
		temp_sampleperiod = 22676
		temp_midinote = 60
		temp_midipitchfraction = 0
		temp_smpteformat = 0
		temp_smpteoffset = 0
		temp_num_loops = 0
		temp_num_data = 0

		if 'loop' in instdata: 
			loopentry = instdata['loop']
			instdata['loops'] = {'1886351212': {'type': 0, 'start': loopentry[0], 'end': loopentry[1], 'fraction': 0, 'num_times': 0}}

		if 'manufacturer' in instdata: temp_manufacturer = instdata['manufacturer']
		if 'product' in instdata: temp_product = instdata['product']
		if 'sampleperiod' in instdata: temp_sampleperiod = instdata['sampleperiod']
		if 'midinote' in instdata: temp_midinote = instdata['midinote']
		if 'midipitchfraction' in instdata: temp_midipitchfraction = instdata['midipitchfraction']
		if 'smpteformat' in instdata: temp_smpteformat = instdata['smpteformat']
		if 'smpteoffset' in instdata: temp_smpteoffset = instdata['smpteoffset']
		chunk_wavdata_smpl.write(temp_manufacturer.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_product.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_sampleperiod.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_midinote.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_midipitchfraction.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_smpteformat.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_smpteoffset.to_bytes(4, 'little'))
		if 'loops' in instdata: 
			temp_num_loops = len(instdata['loops'])
		chunk_wavdata_smpl.write(temp_num_loops.to_bytes(4, 'little'))
		chunk_wavdata_smpl.write(temp_num_data.to_bytes(4, 'little'))
		if 'loops' in instdata: 
			looplist = instdata['loops']
			for loopentry in looplist:
				loopdata = looplist[loopentry]
				chunk_wavdata_smpl.write(int(loopentry).to_bytes(4, 'little'))
				chunk_wavdata_smpl.write(loopdata['type'].to_bytes(4, 'little'))
				chunk_wavdata_smpl.write(loopdata['start'].to_bytes(4, 'little'))
				chunk_wavdata_smpl.write(loopdata['end'].to_bytes(4, 'little'))
				chunk_wavdata_smpl.write(loopdata['fraction'].to_bytes(4, 'little'))
				chunk_wavdata_smpl.write(loopdata['num_times'].to_bytes(4, 'little'))

		chunk_wavdata_smpl.seek(0)
		wav_CHUNK_smpl = chunk_wavdata_smpl.read()
		return [b'smpl',wav_CHUNK_smpl]

def decode(wavfile):
	#print("[audio-wav] Decode Sample")
	out_wavinfo = {}
	out_wavdata = None
	out_instdata = {}
	file_wav = open(wavfile, 'rb')
	chunks_main = data_bytes.riff_read(file_wav, 0)
	bytes_wavdata = chunks_main[0][1]
	chunk_data_bytes = bytes_wavdata[0:4]
	if chunk_data_bytes == b'WAVE':
		chunks_wavdata = data_bytes.riff_read(bytes_wavdata, 4)
		for chunk_wavdata in chunks_wavdata:
			if chunk_wavdata[0] == b'fmt ':
				bytevalues_fmt_chunk = data_bytes.getmultival(chunk_wavdata[1], [2,2,4,4,2,2])
				out_wavinfo['format'] = int.from_bytes(bytevalues_fmt_chunk[0], "little")
				out_wavinfo['channels'] = int.from_bytes(bytevalues_fmt_chunk[1], "little")
				out_wavinfo['samplesec'] = int.from_bytes(bytevalues_fmt_chunk[2], "little")
				out_wavinfo['bytessec'] = int.from_bytes(bytevalues_fmt_chunk[3], "little")
				out_wavinfo['datablocksize'] = int.from_bytes(bytevalues_fmt_chunk[4], "little")
				out_wavinfo['bits'] = int.from_bytes(bytevalues_fmt_chunk[5], "little")
			if chunk_wavdata[0] == b'smpl':
				bytevalues_smpl_chunk = data_bytes.bytearray2BytesIO(chunk_wavdata[1])
				out_instdata['manufacturer'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['product'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['sampleperiod'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['midinote'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['midipitchfraction'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['smpteformat'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['smpteoffset'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['num_loops'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_instdata['num_data'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
				out_loops = {}
				for loop in range(out_instdata['num_loops']):
					loopid = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loop = {}
					out_loop['type'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loop['start'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loop['end'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loop['fraction'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loop['num_times'] = int.from_bytes(bytevalues_smpl_chunk.read(4), "little")
					out_loops[str(loopid)] = out_loop
				out_instdata['loops'] = out_loops
			if chunk_wavdata[0] == b'data':
				out_wavdata = chunk_wavdata[1]
	return (out_wavinfo, out_wavdata, out_instdata)

def generate(file, data, channels, freq, bits, instdata):
	print("[audio-wav] Generating Sample:",end=' ')
	print('Channels: ' + str(channels),end=', ')
	print('Freq: ' + str(freq),end=', ')
	print('Bits: ' + str(bits))
	file_object = open(file, 'wb')
	datasize = int(len(data)/channels)
	table_chunks = []

	# ----- fmt -----
	wav_wFormatTag = 1
	wav_nChannels = channels
	wav_nSamplesPerSec = freq
	wav_nAvgBytesPerSec = freq*channels
	wav_nBlockAlign = int((bits/8)*channels)
	wav_wBitsPerSample = bits
	chunk_wavdata_fmt = BytesIO()
	chunk_wavdata_fmt.write(wav_wFormatTag.to_bytes(2, 'little'))
	chunk_wavdata_fmt.write(wav_nChannels.to_bytes(2, 'little'))
	chunk_wavdata_fmt.write(wav_nSamplesPerSec.to_bytes(4, 'little'))
	chunk_wavdata_fmt.write(wav_nAvgBytesPerSec.to_bytes(4, 'little'))
	chunk_wavdata_fmt.write(wav_nBlockAlign.to_bytes(2, 'little'))
	chunk_wavdata_fmt.write(wav_wBitsPerSample.to_bytes(2, 'little'))
	chunk_wavdata_fmt.seek(0)
	wav_CHUNK_fmt = chunk_wavdata_fmt.read()
	table_chunks.append([b'fmt ',wav_CHUNK_fmt])
	# ----- data -----
	table_chunks.append([b'data',data])
	# ----- smpl -----
	wav_CHUNK_smpl = makesmpl(instdata)
	if wav_CHUNK_smpl != None:
		table_chunks.append(wav_CHUNK_smpl)

	chunk_data_bytes = data_bytes.riff_make(table_chunks)
	bytes_wavdata = b'WAVE' + chunk_data_bytes
	chunks_main = data_bytes.riff_make([[b'RIFF',bytes_wavdata]])

	file_object.write(chunks_main)

#def inject_smpl(instdata):
#	print("[audio-wav] Injecting 'smpl' chunk")
#	file_wav = open(wavfile, 'rb')
#	chunks_main = data_bytes.riff_read(file_wav, 0)
#	bytes_wavdata = chunks_main[0][1]
#	chunk_data_bytes = bytes_wavdata[0:4]
#	if chunk_data_bytes == b'WAVE':
#		chunks_wavdata = data_bytes.riff_read(bytes_wavdata, 4)
#		wav_CHUNK_smpl = makesmpl(instdata)
#		if wav_CHUNK_smpl != None:
#			table_chunks.append(wav_CHUNK_smpl)
#
#		for table_chunk in table_chunks:
#			print(table_chunk[0])
#
#	chunk_data_bytes = data_bytes.riff_make(table_chunks)
#	bytes_wavdata = b'WAVE' + chunk_data_bytes
#	chunks_main = data_bytes.riff_make([[b'RIFF',bytes_wavdata]])
#
#	file_object.write(chunks_main)
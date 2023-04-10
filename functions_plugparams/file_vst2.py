# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import base64
from functions import data_bytes
from functions import list_vst

def read_vst2_fxProgram(in_stream):
	#print('[vst-data] Program')
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = in_stream.read(4)
	fx_num_params = int.from_bytes(in_stream.read(4), "big")
	fx_prgname = in_stream.read(28).decode().split('\x00')[0]
	fx_params = struct.unpack('>'+('f'*fx_num_params), in_stream.read(4*fx_num_params))
	out_cvpj_data = {}
	out_cvpj_data['datatype'] = 'params'
	out_cvpj_data['fourid'] = fx_fourid
	out_cvpj_data['numparams'] = fx_num_params
	out_cvpj_data['params'] = {}
	for paramnum in range(fx_num_params):
		out_cvpj_data['params'][str(paramnum+1)] = {'value': float(fx_params[paramnum])}

	out_cvpj_data['program_name'] = fx_prgname
	return out_cvpj_data

def read_vst2_fxChunkSet(in_stream, is_bank):
	#print('[vst-data] fxChunkSet')
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = in_stream.read(4)
	fx_num_programs = int.from_bytes(in_stream.read(4), "big")
	fx_prgname = in_stream.read(28).decode().split('\x00')[0]
	fx_future = in_stream.read(100)
	fx_chunk_size = int.from_bytes(in_stream.read(4), "big")
	fx_chunk = in_stream.read(fx_chunk_size)
	out_cvpj_data = {}
	out_cvpj_data['fourid'] = fx_fourid
	if is_bank == False: out_cvpj_data['datatype'] = 'raw'
	if is_bank == True: out_cvpj_data['datatype'] = 'raw-bank'
	out_cvpj_data['data'] = base64.b64encode(fx_chunk).decode('ascii')
	out_cvpj_data['program_name'] = fx_prgname
	return out_cvpj_data

def read_vst2_fxSet(in_stream):
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = in_stream.read(4)
	fx_num_program = int.from_bytes(in_stream.read(4), "big")
	fx_future = in_stream.read(128)
	out_cvpj_data = {}
	out_cvpj_data['datatype'] = 'bank'
	out_cvpj_data['fourid'] = fx_fourid
	out_cvpj_data['programs'] = []
	for _ in range(fx_num_program):
		vst2_header = in_stream.read(4)
		if vst2_header == b'CcnK':
			vst2_datasize = int.from_bytes(in_stream.read(4), "big")
			vst2_data = data_bytes.bytearray2BytesIO(in_stream.read(vst2_datasize))
			vst2_ccnk_chunktype = vst2_data.read(4)
			vst2_ccnk_chunksize = int.from_bytes(vst2_data.read(4), "big")
			print(vst2_header, vst2_ccnk_chunktype)
			if vst2_ccnk_chunktype == b'FxCk': out_cvpj_data['programs'].append( read_vst2_fxProgram(vst2_data) )
	return out_cvpj_data

def read_vst2_chunk(in_stream, platform, pefer_cpu_arch):
	vst2_ccnk_chunktype = in_stream.read(4)
	vst2_ccnk_chunksize = int.from_bytes(in_stream.read(4), "big")
	print(vst2_ccnk_chunktype, vst2_ccnk_chunksize)
	if vst2_ccnk_chunktype == b'FPCh': return read_vst2_fxChunkSet(in_stream, False)
	if vst2_ccnk_chunktype == b'FBCh': return read_vst2_fxChunkSet(in_stream, True)
	if vst2_ccnk_chunktype == b'FxCh': return read_vst2_fxChunkSet(in_stream, False)
	if vst2_ccnk_chunktype == b'FxCk': return read_vst2_fxProgram(in_stream)
	if vst2_ccnk_chunktype == b'FxBk': return read_vst2_fxSet(in_stream)

def read_vst2_data(in_stream, platform, pefer_cpu_arch):
	output_data = {}
	vst2_header = in_stream.read(4)
	if vst2_header == b'CcnK':
		vst2_datasize = int.from_bytes(in_stream.read(4), "big")
		vst2_data = data_bytes.bytearray2BytesIO(in_stream.read(vst2_datasize))
		cvpj_plugindata = read_vst2_chunk(vst2_data, platform, pefer_cpu_arch)
	return cvpj_plugindata


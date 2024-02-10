
import json
import struct
import base64

from io import BytesIO

def read_vst2_fxProgram(in_stream):
	print('[vst-data] Program')
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = in_stream.read(4)
	fx_num_params = int.from_bytes(in_stream.read(4), "big")
	fx_prgname_bytes = in_stream.read(28)
	#print(fx_prgname_bytes)
	#fx_prgname = fx_prgname_bytes.decode().split('\x00')[0]
	fx_params = struct.unpack('>'+('f'*fx_num_params), in_stream.read(4*fx_num_params))
	out_cvpj_data = {}
	out_cvpj_data['datatype'] = 'params'
	out_cvpj_data['plugin'] = {}
	out_cvpj_data['plugin']['fourid'] = fx_fourid
	out_cvpj_data['numparams'] = fx_num_params
	out_cvpj_data['params'] = {}
	for paramnum in range(fx_num_params):
		out_cvpj_data['params'][str(paramnum+1)] = {'value': float(fx_params[paramnum])}

	#out_cvpj_data['program_name'] = fx_prgname
	return out_cvpj_data

def read_vst2_fxChunkSet(in_stream):
	#print('[vst-data] Chunks')
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = in_stream.read(4)
	fx_num_programs = int.from_bytes(in_stream.read(4), "big")
	fx_prgname_bytes = in_stream.read(28)
	#print(fx_prgname_bytes)
	#fx_prgname = fx_prgname_bytes.decode().split('\x00')[0]
	fx_chunk_size = int.from_bytes(in_stream.read(4), "big")
	fx_chunk = in_stream.read(fx_chunk_size)
	out_cvpj_data = {}
	out_cvpj_data['datatype'] = 'raw'
	out_cvpj_data['plugin'] = {}
	out_cvpj_data['plugin']['fourid'] = fx_fourid
	out_cvpj_data['data'] = fx_chunk
	#out_cvpj_data['program_name'] = fx_prgname
	return out_cvpj_data

def read_vst2_chunk(in_stream):
	vst2_ccnk_chunktype = in_stream.read(4)
	vst2_ccnk_chunksize = int.from_bytes(in_stream.read(4), "big")
	print(vst2_ccnk_chunktype, vst2_ccnk_chunksize)
	if vst2_ccnk_chunktype == b'FPCh': return read_vst2_fxChunkSet(in_stream)
	if vst2_ccnk_chunktype == b'FxCk': return read_vst2_fxProgram(in_stream)

def read_vst2_data(in_stream):
	output_data = {}
	vst2_header = in_stream.read(4)
	if vst2_header == b'CcnK':
		vst2_datasize = int.from_bytes(in_stream.read(4), "big")
		vst2_data = BytesIO(in_stream.read(vst2_datasize))
		return read_vst2_chunk(vst2_data)



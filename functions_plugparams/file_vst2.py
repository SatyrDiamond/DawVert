# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import struct
import base64
from functions import data_bytes
from functions import list_vst
from io import BytesIO

def read_vst2_chunk(in_stream):
	vst2_ccnk_chunktype = in_stream.read(4)
	in_stream.read(4)
	fx_fourid = int.from_bytes(in_stream.read(4), "big")
	fx_version = int.from_bytes(in_stream.read(4), "big")
	fx_num_val = int.from_bytes(in_stream.read(4), "big")

	out_cvpj_data = {}

	if vst2_ccnk_chunktype in [b'FPCh', b'FBCh', b'FxCh']:
		if vst2_ccnk_chunktype == b'FBCh': is_bank = True
		else: is_bank = False
		fx_prgname = in_stream.read(28).decode().split('\x00')[0]
		if is_bank == True: 
			fx_future = in_stream.read(100)
			out_cvpj_data['datatype-subtype'] = 'bank'
		fx_chunk_size = int.from_bytes(in_stream.read(4), "big")
		fx_chunk = in_stream.read(fx_chunk_size)
		out_cvpj_data['fourid'] = fx_fourid
		out_cvpj_data['datatype'] = 'chunk'
		out_cvpj_data['version'] = fx_version
		out_cvpj_data['data'] = base64.b64encode(fx_chunk).decode('ascii')
		out_cvpj_data['program_name'] = fx_prgname

	if vst2_ccnk_chunktype == b'FxCk':
		num_params = fx_num_val+1
		fx_prgname = data_bytes.readstring_fixedlen(in_stream, 24, None)
		floatbytes = in_stream.read(4*num_params)
		fx_params = struct.unpack('>'+('f'*num_params), floatbytes)
		out_cvpj_data['datatype'] = 'params'
		out_cvpj_data['fourid'] = fx_fourid
		out_cvpj_data['version'] = fx_version
		out_cvpj_data['numparams'] = num_params
		out_cvpj_data['params'] = {}
		for paramnum in range(num_params):
			out_cvpj_data['params'][str(paramnum+1)] = {'value': float(fx_params[paramnum])}
		out_cvpj_data['program_name'] = fx_prgname

	if vst2_ccnk_chunktype == b'FxBk':
		fx_future = in_stream.read(128)
		out_cvpj_data['datatype'] = 'bank'
		out_cvpj_data['fourid'] = fx_fourid
		out_cvpj_data['version'] = fx_version
		out_cvpj_data['programs'] = []
		for _ in range(fx_num_val):
			programdata = read_vst2_data(in_stream)
			out_cvpj_data['programs'].append(programdata)

	return out_cvpj_data

def read_vst2_data(in_stream):
	vst2_header = in_stream.read(4)
	if vst2_header == b'CcnK':
		in_stream.read(4)
		cvpj_plugindata = read_vst2_chunk(in_stream)
	return cvpj_plugindata










def write_chunk(vstdata, vst_fourid, fx_version, fx_num_programs, isbank):
	chunkdata = base64.b64decode(vstdata['data'])
	bio_vstdata = BytesIO()
	bio_vstdata.write(vst_fourid.to_bytes(4, "big"))
	bio_vstdata.write(fx_version.to_bytes(4, "big"))
	bio_vstdata.write(fx_num_programs.to_bytes(4, "big"))
	bio_vstdata.write(b'\x00'*28)
	if isbank == True: bio_vstdata.write(b'\x00'*100)
	bio_vstdata.write(len(chunkdata).to_bytes(4, "big"))
	bio_vstdata.write(chunkdata)
	bio_vstdata.seek(0)
	out_chunk = bio_vstdata.read()
	if isbank == False: out_params = b'FPCh\x00\x00\x00\x01' + out_chunk
	else: out_params = b'FBCh\x00\x00\x00\x01' + out_chunk
	outdata = b'CcnK' + (len(out_params)).to_bytes(4,"big") + out_params
	return len(out_params), outdata

def write_params(vstdata, vst_fourid, fx_version):
	numparams = vstdata['numparams']-1
	bio_vstdata = BytesIO()
	bio_vstdata.write(vst_fourid.to_bytes(4, "big"))
	bio_vstdata.write(fx_version.to_bytes(4, "big"))
	bio_vstdata.write(numparams.to_bytes(4, "big"))
	bio_vstdata.write(b'\x00'*24)
	paramvals = [0 for x in range(numparams+1)]
	for paramnum in vstdata['params']:
		paramvals[int(paramnum)-1] = vstdata['params'][paramnum]['value']
	for paramval in paramvals:
		bio_vstdata.write(struct.pack('>f', paramval))
	bio_vstdata.seek(0)
	out_params = b'FxCk\x00\x00\x00\x02' + bio_vstdata.read()
	outdata = b'CcnK' + (len(out_params)+4).to_bytes(4,"big") + out_params
	return len(out_params), outdata



def write_vst2_data(vstdata, fx_num_programs, fx_prgname):
	isbank = False
	vst_datatype = vstdata['datatype']
	vst_fourid = vstdata['fourid']
	fx_version = 65536
	if 'version' in vstdata: 
		fx_version = vstdata['version']
	if 'datatype-subtype' in vstdata: 
		if vstdata['datatype-subtype'] == 'bank': isbank = True

	bio_vstdata = BytesIO()

	out_size = 0

	if vst_datatype == 'chunk':
		vstout = write_chunk(vstdata, vst_fourid, fx_version, fx_num_programs, isbank)
		out_data = vstout[1]

	if vst_datatype == 'params':
		vstout = write_params(vstdata, vst_fourid, fx_version)
		out_data = vstout[1]

	if vst_datatype == 'bank':
		bio_vstdata.write(vst_fourid.to_bytes(4, "big"))
		bio_vstdata.write(fx_version.to_bytes(4, "big"))
		bio_vstdata.write(len(vstdata['programs']).to_bytes(4, "big"))
		bio_vstdata.write(b'\x00'*128)
		bio_vstdata.seek(0)
		out_header_data = b'FxBk\x00\x00\x00\x02' + bio_vstdata.read()
		out_bank_data = out_header_data
		bank_size = len(out_header_data)
		for progdata in vstdata['programs']:
			vst_progdatatype = progdata['datatype']
			if vst_progdatatype == 'params':
				vstout = write_params(progdata, vst_fourid, fx_version)
				bank_size += vstout[0]+4
				out_bank_data += vstout[1]
		out_data = b'CcnK' + (bank_size+4).to_bytes(4,"big") + out_bank_data

	bio_outdata = BytesIO()
	bio_outdata.write(out_data)
	bio_outdata.seek(0)

	return bio_outdata.read()


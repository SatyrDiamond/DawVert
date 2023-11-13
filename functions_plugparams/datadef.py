# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugins
import struct

def to_plugdata(cvpj_plugindata, in_datadef, bytestream):
	try:
		for datapart in in_datadef:
			if datapart[0] != 'x':
				if datapart[0] == 'i': valueout, valtype = struct.unpack('i', bytestream.read(4))[0], 'int'
				if datapart[0] == 'I': valueout, valtype = struct.unpack('I', bytestream.read(4))[0], 'int'
				if datapart[0] == 'b': valueout, valtype = struct.unpack('b', bytestream.read(1))[0], 'int'
				if datapart[0] == 'f': valueout, valtype = struct.unpack('f', bytestream.read(4))[0], 'float'
				if datapart[0] == 'd': valueout, valtype = struct.unpack('d', bytestream.read(8))[0], 'float'

				if datapart[1]: cvpj_plugindata.param_add(datapart[2], valueout, valtype, datapart[3])
				else: cvpj_plugindata.dataval_add(datapart[2], valueout)
			else: bytestream.read(datapart[1])
	except:
		pass

def from_plugdata(cvpj_plugindata, in_datadef):
	outdata = b''
	for datapart in in_datadef:
		if datapart[0] != 'x':
			if datapart[1]: paramval = cvpj_plugindata.param_get(datapart[2], 0)[0]
			else: paramval = cvpj_plugindata.dataval_get(datapart[2], 0)

			if datapart[0] == 'i': outdata += struct.pack('i', paramval)
			if datapart[0] == 'I': outdata += struct.pack('I', paramval)
			if datapart[0] == 'b': outdata += struct.pack('b', paramval)
			if datapart[0] == 'f': outdata += struct.pack('f', paramval)
			if datapart[0] == 'd': outdata += struct.pack('d', paramval)

		else: outdata += b'\x00'*datapart[1]

	return outdata
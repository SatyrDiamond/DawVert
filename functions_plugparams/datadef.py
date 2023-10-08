# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugins
import struct

def to_plugdata(cvpj_l, pluginid, in_datadef, bytestream):
	for datapart in in_datadef:
		if datapart[0] != 'x':
			if datapart[0] == 'i': valueout, valtype = struct.unpack('i', bytestream.read(4))[0], 'int'
			if datapart[0] == 'I': valueout, valtype = struct.unpack('I', bytestream.read(4))[0], 'int'
			if datapart[0] == 'b': valueout, valtype = struct.unpack('b', bytestream.read(1))[0], 'bool'
			if datapart[0] == 'f': valueout, valtype = struct.unpack('f', bytestream.read(4))[0], 'float'
			if datapart[0] == 'd': valueout, valtype = struct.unpack('d', bytestream.read(8))[0], 'float'

			if datapart[1]: plugins.add_plug_param(cvpj_l, pluginid, datapart[2], valueout, valtype, datapart[3])
			else: plugins.add_plug_data(cvpj_l, pluginid, datapart[2], valueout)
		else: bytestream.read(datapart[1])
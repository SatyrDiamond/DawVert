# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64

def decode_chunk(statedata):
	statedata = statedata.replace('.', '/')
	return base64.b64decode(statedata)

def encode_chunk(inbytes):
	statedata = base64.b64encode(inbytes).decode("ascii")
	statedata = statedata.replace('/', '.')
	return statedata

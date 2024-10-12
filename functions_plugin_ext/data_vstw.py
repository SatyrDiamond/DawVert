# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get(chunkdata):
	if chunkdata[0:4] == b'VstW' and len(chunkdata)>176: 
		chunkdata = chunkdata[172:]
		chunkdata = chunkdata[4:int.from_bytes(chunkdata[0:4])+8]
		return chunkdata
	else:
		return chunkdata

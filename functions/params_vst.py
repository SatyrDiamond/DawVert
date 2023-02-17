# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import json

def add_param(paramlist, num, name, value):
	paramlist[str(num)] = {}
	paramlist[str(num)]['name'] = name
	paramlist[str(num)]['value'] = str(value)

# -------------------- JsonString --------------------

def json_get(vstdata):
	return json.loads(vstdata.decode().split('\x00',1)[0])

# -------------------- NullByteGroup --------------------

def nullbytegroup_get(vstdata):
	nbpvstdata = vstdata.split(b'\x00')
	nbp = [{}]
	groupnum = 0
	isvalname = False
	for datavalue in nbpvstdata:
		print(datavalue)
		if isvalname == True:
			nbp[groupnum][valname] = datavalue.decode()
			isvalname = False
		else:
			if datavalue == b'':
				groupnum += 1
				nbp.append({})
			else:
				isvalname = True
				valname = datavalue.decode()
	return nbp

def nullbytegroup_make(larr):
	nbp = bytes()
	for grouplist in larr:
		for param in grouplist:
			nbp += str(param).encode('utf-8')+b'\x00'+str(grouplist[param]).encode('utf-8')+b'\x00'
		nbp += b'\x00'
	return nbp

# -------------------- VC2 XML --------------------

def vc2xml_get(vstdata):
	vc2magic = vstdata[0:4]
	if vc2magic == b'VC2!':
		vc2size = int.from_bytes(vstdata[4:8], "little")
		vc2data = vstdata[8:8+vc2size]
		return ET.fromstring(vc2data)
	else:
		return None

def vc2xml_make(xmldata):
	xmlout = ET.tostring(xmldata, encoding='utf-8')
	vst2data = b'VC2!' + len(xmlout).to_bytes(4, "little") + xmlout
	return vst2data

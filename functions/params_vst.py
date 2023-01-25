# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def add_param(paramlist, num, name, value):
	paramlist[str(num)] = {}
	paramlist[str(num)]['name'] = name
	paramlist[str(num)]['value'] = str(value)

def make_nullbytegroup(larr):
	nbp = bytes()
	for grouplist in larr:
		for param in grouplist:
			nbp += str(param).encode('utf-8')+b'\x00'+str(grouplist[param]).encode('utf-8')+b'\x00'
		nbp += b'\x00'
	return nbp

def make_vc2_xml(xmldata):
	xmlout = ET.tostring(xmldata, encoding='utf-8')
	vst2data = b'VC2!' + len(xmlout).to_bytes(4, "little") + xmlout
	return vst2data
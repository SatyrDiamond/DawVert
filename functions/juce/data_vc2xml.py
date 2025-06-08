# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def get(vstdata):
	vc2magic = vstdata[0:4]
	if vc2magic == b'VC2!':
		vc2size = int.from_bytes(vstdata[4:8], "little")
		vc2data = vstdata[8:8+vc2size]
		return ET.fromstring(vc2data)
	else:
		return None

def make(xmldata):
	xmlout = ET.tostring(xmldata, encoding='utf-8')
	vst2data = b'VC2!' + len(xmlout).to_bytes(4, "little") + xmlout
	return vst2data

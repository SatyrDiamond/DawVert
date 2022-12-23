
from functions import vst_params
import xml.etree.ElementTree as ET

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
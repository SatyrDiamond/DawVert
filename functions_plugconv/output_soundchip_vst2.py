from functions import audio_wav
from functions import list_vst
from functions import vst_inst
from functions import params_vst
import xml.etree.ElementTree as ET
import pathlib

def convert_inst(instdata, out_daw):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'opn2':
		xmlout = vst_inst.opnplug_convert(plugindata)
		list_vst.replace_data(instdata, 2, 'any', 'OPNplug', 'raw', params_vst.vc2xml_make(xmlout), None)

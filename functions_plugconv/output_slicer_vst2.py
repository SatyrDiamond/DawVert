from functions import audio_wav
from functions import list_vst
from functions import vst_inst
from functions import params_vst
import xml.etree.ElementTree as ET
import pathlib

def convert_inst(instdata):
	slicerdata = instdata['plugindata']
	vst_inst.ninjas2_init()
	vst_inst.ninjas2_slicerdata(slicerdata)
	ninjas2out = vst_inst.ninjas2_get()
	list_vst.replace_data(instdata, 2, 'any', 'Ninjas 2', 'raw', params_vst.nullbytegroup_make(ninjas2out), None)
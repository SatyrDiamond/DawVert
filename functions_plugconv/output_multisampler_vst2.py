from functions import audio_wav
from functions import list_vst
from functions import vst_inst
import xml.etree.ElementTree as ET
import pathlib

def convert_inst(instdata, platform_id):
	if platform_id == 'win':
		msmpl_data = instdata
		msmpl_p_data = instdata['plugindata']
		vst2_dll_vstpaths = list_vst.vstpaths()
		if vst2_dll_vstpaths['2-dll']:
			if 'Grace' in vst2_dll_vstpaths['2-dll']:
				regions = msmpl_p_data['regions']
				gx_root = vst_inst.grace_create_main()
				for regionparams in regions:
					vst_inst.grace_create_region(gx_root, regionparams)
				xmlout = ET.tostring(gx_root, encoding='utf-8')
				list_vst.replace_data(instdata, 2, 'any', 'Grace', 'raw', xmlout, None)
			else:
				print('[plug-conv] Unchanged, Plugin Grace not Found')

from functions import audio_wav
from functions import plugin_vst2
from functions import vst_inst
import xml.etree.ElementTree as ET
import pathlib

def convert_inst(instdata, platform_id):
	if platform_id == 'win':
		msmpl_data = instdata
		msmpl_p_data = instdata['plugindata']
		vst2_dll_vstpaths = plugin_vst2.vstpaths()
		if 'Grace' in vst2_dll_vstpaths['dll']:
			if 'regions' in msmpl_p_data:
				regions = msmpl_p_data['regions']
				gx_root = vst_inst.grace_create_main()
				for regionparams in regions:
					vst_inst.grace_create_region(gx_root, regionparams)
				xmlout = ET.tostring(gx_root, encoding='utf-8')
				plugin_vst2.replace_data(instdata, 'any', 'Grace', 'raw', xmlout, None)
		else:
			print('[plug-conv] Unchanged, Plugin Grace not Found')

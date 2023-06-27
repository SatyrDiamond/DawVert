# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import struct
import math
import base64
from functions import data_values
from functions import plugin_vst2
from functions import plugins

from functions_plugparams import data_vc2xml
from functions_plugparams import params_various_fx
from functions_plugparams import params_various_inst
from functions_plugparams import params_vital

from functions_plugconv import vst2_simple
from functions_plugconv import vst2_lmms
from functions_plugconv import vst2_piyopiyo
from functions_plugconv import vst2_flstudio
from functions_plugconv import vst2_retro
from functions_plugconv import sf2_gmmidi

#from functions_plugconv import input_pxtone
#from functions_plugconv import input_jummbox
#from functions_plugconv import input_soundchip
#from functions_plugconv import input_audiosauna
#
#from functions_plugconv import output_vst2_sampler
#from functions_plugconv import output_vst2_multisampler
#from functions_plugconv import output_vst2_slicer
#
#from functions_plugconv import output_vst2_soundchip
#
#from functions_plugconv import output_vst2_onlineseq
#from functions_plugconv import output_vst2_namco163_famistudio
#
#from functions_plugconv import output_vst2nonfree_flstudio

# -------------------- convproj --------------------

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, out_supportedplugins, extra_json):#
	global supportedplugins
	supportedplugins = out_supportedplugins
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if 'plugins' in cvpj_l:
			cvpj_plugins = cvpj_l['plugins']
		for pluginid in cvpj_plugins:
				plugintype = plugins.get_plug_type(cvpj_l, pluginid)

				if plugintype[0] == 'general-midi':
					if 'soundfont' in extra_json:
						sf2_gmmidi.convert(cvpj_l, pluginid, plugintype, extra_json)
						print('[plug-conv] GM MIDI > soundfont2')
					else: print('[plug-conv] Soundfont argument not defined.')

				replacingdone = None
				if 'vst2' in supportedplugins:
					if replacingdone == None and plugintype[0] == 'retro' :
						print('[plug-conv] '+pluginid+' | Retro '+str(plugintype[1]))
						replacingdone = vst2_retro.convert(cvpj_l, pluginid, plugintype) 

					if replacingdone == None and plugintype[0] == 'simple' :
						print('[plug-conv] '+pluginid+' | Simple '+str(plugintype[1]))
						replacingdone = vst2_simple.convert(cvpj_l, pluginid, plugintype) 

					if replacingdone == None and plugintype[0] == 'native-flstudio' and out_daw != 'flp':
						print('[plug-conv] '+pluginid+' | FL Studio: '+str(plugintype[1]))
						replacingdone = vst2_flstudio.convert(cvpj_l, pluginid, plugintype) 

					if replacingdone == None and plugintype[0] == 'native-lmms' and plugintype[1] not in ['arpeggiator', 'chordcreator'] and out_daw != 'lmms':
						print('[plug-conv] '+pluginid+' | LMMS: '+str(plugintype[1]))
						replacingdone = vst2_lmms.convert(cvpj_l, pluginid, plugintype) 

					if replacingdone == None and plugintype == ['native-piyopiyo', 'wave']:
						print('[plug-conv] '+pluginid+' | PiyoPiyo '+str(plugintype[1]))
						replacingdone = vst2_piyopiyo.convert(cvpj_l, pluginid, plugintype) 

		return json.dumps(cvpj_l, indent=2)

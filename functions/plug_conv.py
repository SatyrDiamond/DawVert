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

from functions_plugconv import vst2_lmms

#from functions_plugconv import input_flstudio
#from functions_plugconv import input_pxtone
#from functions_plugconv import input_jummbox
#from functions_plugconv import input_soundchip
#from functions_plugconv import input_audiosauna
#
#from functions_plugconv import output_vst2_simple
#from functions_plugconv import output_vst2_sampler
#from functions_plugconv import output_vst2_multisampler
#from functions_plugconv import output_vst2_slicer
#
#from functions_plugconv import output_vst2_retro
#from functions_plugconv import output_vst2_soundchip
#
#from functions_plugconv import output_vst2_flstudio
#from functions_plugconv import output_vst2_onlineseq
#from functions_plugconv import output_vst2_piyopiyo
#from functions_plugconv import output_vst2_namco163_famistudio
#
#from functions_plugconv import output_vst2nonfree_flstudio

# -------------------- convproj --------------------

def do_inst(track_data, in_daw, out_daw, extra_json, nameid, platform_id):
	if 'instdata' in track_data:
		instdata = track_data['instdata']
		print('[plug-conv] --- Inst: '+nameid)
		convplug_inst(instdata, in_daw, out_daw, extra_json, nameid, platform_id)

def do_fxchain_audio(fxdata, in_daw, out_daw, extra_json, textin):
	if 'chain_fx_audio' in fxdata:
		for fxslot in fxdata['chain_fx_audio']:
			print('[plug-conv] --- FX ('+textin+')')
			convplug_fx(fxslot, in_daw, out_daw, extra_json)

def do_sends(master_data, in_daw, out_daw, extra_json, platform_id, intext):
	if 'sends_audio' in master_data:
		mastersends = master_data['sends_audio']
		for sendid in mastersends:
			do_fxchain_audio(mastersends[sendid], in_daw, out_daw, extra_json,intext+' Send: '+sendid)

def convproj(cvpjdata, platform_id, in_type, out_type, in_daw, out_daw, out_supportedplugins, extra_json):#
	global supportedplugins
	supportedplugins = out_supportedplugins
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if 'plugins' in cvpj_l:
			cvpj_plugins = cvpj_l['plugins']
		for pluginid in cvpj_plugins:
				plugintype = plugins.get_plug_type(cvpj_l, pluginid)

				replacingdone = None

				if replacingdone == None and plugintype[0] == 'native-lmms' and plugintype[1] not in ['arpeggiator', 'chordcreator'] and out_daw != 'lmms':
					print('[plug-conv] '+pluginid+' | LMMS Native: '+str(plugintype[1]))
					replacingdone = output_vst2_lmms.convert(cvpj_l, pluginid, plugintype) 

		return json.dumps(cvpj_l, indent=2)

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

from functions_plugconv import sf2__gmmidi
from functions_plugconv import opl2__vrc7
from functions_plugconv import opn2__epsm
from functions_plugconv import opm__valsound

from functions_plugconv import vst2__simple
from functions_plugconv import vst2__sampler_slicer
from functions_plugconv import vst2__retro

from functions_plugconv import vst2__opn2
#from functions_plugconv import vst2__opl2

from functions_plugconv import vst2__lmms
from functions_plugconv import vst2__piyopiyo
from functions_plugconv import vst2__flstudio
from functions_plugconv import vst2__onlineseq
from functions_plugconv import vst2__namco163_famistudio

from functions_plugconv import vst2_nonfree__flstudio

#from functions_plugconv import vst2__jummbox
#from functions_plugconv import input_pxtone
#
#
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

					# ------------------------ #1 ------------------------

					if plugintype[0] == 'general-midi':
						if 'soundfont' in extra_json:
							print('[plug-conv] '+pluginid+' | GM MIDI > soundfont2')
							sf2__gmmidi.convert(cvpj_l, pluginid, plugintype, extra_json)
						else: print('[plug-conv] Soundfont argument not defined.')

					elif plugintype == ['fm', 'vrc7']:
						print('[plug-conv] '+pluginid+' | VRC7 to OPL2')
						opl2__vrc7.convert(cvpj_l, pluginid, plugintype) 

					elif plugintype == ['fm', 'epsm']:
						print('[plug-conv] '+pluginid+' | EPSM to OPN2')
						opn2__epsm.convert(cvpj_l, pluginid, plugintype) 

					elif plugintype[0] == 'valsound':
						print('[plug-conv] '+pluginid+' | ValSound to OPM')
						opm__valsound.convert(cvpj_l, pluginid, plugintype) 

					plugintype = plugins.get_plug_type(cvpj_l, pluginid)

					# ------------------------ #2 ------------------------

					replacingdone = None
					if 'vst2' in supportedplugins:
						if replacingdone == None and plugintype[0] in ['retro', 'gameboy']:
							print('[plug-conv] '+pluginid+' | Retro '+str(plugintype[1]))
							replacingdone = vst2__retro.convert(cvpj_l, pluginid, plugintype) 

						if replacingdone == None and plugintype[0] == 'simple' :
							print('[plug-conv] '+pluginid+' | Simple '+str(plugintype[1]))
							replacingdone = vst2__simple.convert(cvpj_l, pluginid, plugintype) 

						if replacingdone == None and plugintype == ['sampler', 'slicer']:
							print('[plug-conv] '+pluginid+' | Slicer')
							replacingdone = vst2__sampler_slicer.convert(cvpj_l, pluginid, plugintype) 




						if replacingdone == None and plugintype == ['fm', 'opn2']:
							print('[plug-conv] '+pluginid+' | OPN2 '+str(plugintype[1]))
							replacingdone = vst2__opn2.convert(cvpj_l, pluginid, plugintype) 



						#if replacingdone == None and plugintype[0] == 'native-jummbox':
						#	print('[plug-conv] '+pluginid+' | Jummbox: '+str(plugintype[1]))
						#	replacingdone = vst2__jummbox.convert(cvpj_l, pluginid, plugintype) 

						if plugintype[0] == 'native-flstudio' and out_daw != 'flp':
							print('[plug-conv] '+pluginid+' | FL Studio: '+str(plugintype[1]))
							if replacingdone == None: 
								replacingdone = vst2__flstudio.convert(cvpj_l, pluginid, plugintype) 
							if replacingdone == None and 'nonfree-plugins' in extra_json: 
								replacingdone = vst2_nonfree__flstudio.convert(cvpj_l, pluginid, plugintype) 

						if replacingdone == None and plugintype[0] == 'native-lmms' and out_daw != 'lmms':
							print('[plug-conv] '+pluginid+' | LMMS: '+str(plugintype[1]))
							replacingdone = vst2__lmms.convert(cvpj_l, pluginid, plugintype) 

						if replacingdone == None and plugintype[0] == 'native-onlineseq':
							print('[plug-conv] '+pluginid+' | Online Sequencer: '+str(plugintype[1]))
							replacingdone = vst2__onlineseq.convert(cvpj_l, pluginid, plugintype) 
							
						if replacingdone == None and plugintype == ['native-piyopiyo', 'wave']:
							print('[plug-conv] '+pluginid+' | PiyoPiyo '+str(plugintype[1]))
							replacingdone = vst2__piyopiyo.convert(cvpj_l, pluginid, plugintype) 

						if replacingdone == None and  plugintype[0] == 'namco163_famistudio':
							print('[plug-conv] '+pluginid+' | FamiStudio N163 '+str(plugintype[1]))
							replacingdone = vst2__namco163_famistudio.convert(cvpj_l, pluginid, plugintype)

		return json.dumps(cvpj_l, indent=2)

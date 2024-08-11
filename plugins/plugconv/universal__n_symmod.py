# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.inst_params import fx_delay
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.priority = 50
		plugconv_obj.in_plugins = [['native-symmod', None]]
		plugconv_obj.in_daws = []
		plugconv_obj.out_plugins = [['universal', None]]
		plugconv_obj.out_daws = []
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):

		if plugin_obj.type.subtype == 'echo':
			extpluglog.convinternal('SymMOD', 'Echo', 'Universal', 'Delay')

			p_type = plugin_obj.params.get("type", 0).value
			p_delay = plugin_obj.params.get("delay", 0).value/50
			p_fb = 1/(plugin_obj.params.get("fb", 0).value+1)

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = True
			timing_obj = delay_obj.timing_add(0)
			timing_obj.set_seconds(p_delay)
			delay_obj.feedback[0] = p_fb

			if p_type in [2, 3]:
				delay_obj.mode = 'pingpong'
				delay_obj.submode = 'normal'
				delay_obj.feedback[0] = p_fb if p_type == 2 else 1-p_fb

			if p_type: plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)
			return 1
			
		return 2
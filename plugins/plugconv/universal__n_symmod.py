# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.inst_params import fx_delay
from functions import extpluglog

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv'

	def get_priority(self):
		return 0

	def get_prop(self, in_dict): 
		in_dict['in_plugins'] = [['native', 'symmod', None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'symmod', 'echo'):
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
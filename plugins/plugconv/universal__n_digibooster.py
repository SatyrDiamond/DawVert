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
		in_dict['in_plugins'] = [['native', 'digibooster', None]]
		in_dict['in_daws'] = []
		in_dict['out_plugins'] = [['universal', None, None]]
		in_dict['out_daws'] = []

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		if plugin_obj.type.check_wildmatch('native', 'digibooster', 'pro_echo'):
			extpluglog.convinternal('DigiBooster', 'Pro Echo', 'Universal', 'Delay')
			p_delay = plugin_obj.params.get("delay", 0).value*0.004
			p_fb = plugin_obj.params.get("fb", 0).value/255
			p_wet = plugin_obj.params.get("wet", 0).value/255
			p_cross_echo = plugin_obj.params.get("cross_echo", 0).value/255
			if p_delay == 0: p_delay = 0.334

			delay_obj = fx_delay.fx_delay()
			delay_obj.feedback_first = False
			delay_obj.dry = 0
			delay_obj.feedback[0] = p_fb*(1-p_cross_echo)
			delay_obj.feedback_cross[0] = p_cross_echo
			timing_obj = delay_obj.timing_add(0)
			timing_obj.set_seconds(p_delay)
			plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, pluginid)

			plugin_obj.fxdata_add(None, p_wet)
			return 1
			
		return 2
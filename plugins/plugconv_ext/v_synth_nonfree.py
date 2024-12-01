# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

from objects import globalstore
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml
from functions import extpluglog
import lxml.etree as ET

class plugconv(plugins.base):
	def is_dawvert_plugin(self):
		return 'plugconv_ext'

	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['synth-nonfree', None, None]
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['shareware']

	def convert(self, convproj_obj, plugin_obj, pluginid, dawvert_intent, extplugtype):
		globalstore.dataset.load('synth_nonfree', './data_ext/dataset/synth_nonfree.dset')

		plugname = plugin_obj.type.subtype

		if plugname == 'Europa' and 'vst2' in extplugtype:
			extpluglog.extpluglist.add('Shareware', 'VST2', 'Europa', '')
			if plugin_vst2.check_exists('id', 1165324911):
				extpluglog.extpluglist.success('Synth', 'Europa')
				europa_patch = ET.Element("JukeboxPatch")
				europa_patch.set('patchname', "DawVert")
				europa_samp = ET.SubElement(europa_patch, "Samples")
				europa_prop = ET.SubElement(europa_patch, "Properties")
				europa_obj = ET.SubElement(europa_prop, "Object")
				europa_obj.set('name', "custom_properties")
				paramlist = dataset_synth_nonfree.params_list('plugin', 'europa')
				for paramname in paramlist:
					dset_paramdata = dataset_synth_nonfree.params_i_get('plugin', 'europa', paramname)
					eur_value_name = dset_paramdata[5]
					if dset_paramdata[0] == False:
						eur_value_type = 'number'
						eur_value_value = plugin_obj.params.get(paramname, 1).value
					else:
						eur_value_type = 'string'
						eur_value_value = plugin_obj.datavals.get(paramname, 1)
						if eur_value_name in ['Curve1','Curve2','Curve3','Curve4','Curve']:
							eur_value_value = bytes(eur_value_value).hex().upper()

					europa_value_obj = ET.SubElement(europa_obj, "Value")
					europa_value_obj.set('property',eur_value_name)
					europa_value_obj.set('type',eur_value_type)
					europa_value_obj.text = str(eur_value_value)

				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1165324911, 'chunk', data_vc2xml.make(europa_patch), None)
				return True

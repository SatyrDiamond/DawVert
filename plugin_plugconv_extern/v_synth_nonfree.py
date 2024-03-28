# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

from objects import dv_dataset
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml
from functions import errorprint
import lxml.etree as ET

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['synth-nonfree', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        dataset_synth_nonfree = dv_dataset.dataset('./data_dset/synth_nonfree.dset')

        plugname = plugin_obj.plugin_subtype

        if plugname == 'Europa' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1165324911):
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
            else: errorprint.printerr('ext_notfound', ['Shareware VST2', 'Europa by Reason'])
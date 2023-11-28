# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

from functions import data_dataset
from functions import plugin_vst2
from functions_plugdata import data_vc2xml
import lxml.etree as ET

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['synth-nonfree', None], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        plugintype = cvpj_plugindata.type_get()
        dataset_synth_nonfree = data_dataset.dataset('./data_dset/synth_nonfree.dset')

        plugname = plugintype[1]

        if plugname == 'Europa' and extplugtype == 'vst2':
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
                    eur_value_value = cvpj_plugindata.param_get(paramname, 1)[0]
                else:
                    eur_value_type = 'string'
                    eur_value_value = cvpj_plugindata.dataval_get(paramname, 1)
                    if paramname in ['Curve1','Curve2','Curve3','Curve4','Curve']: 
                        eur_value_value = bytes(eur_value_value).hex().upper()

                europa_value_obj = ET.SubElement(europa_obj, "Value")
                europa_value_obj.set('property',eur_value_name)
                europa_value_obj.set('type',eur_value_type)
                europa_value_obj.text = str(eur_value_value)

            plugin_vst2.replace_data(cvpj_plugindata, 'name', 'any', 'Europa by Reason', 'chunk', data_vc2xml.make(europa_patch), None)
            return True
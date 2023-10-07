# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import auto
from functions import params

def add_pl(cvpj_l, val_type, autolocation, in_autopoints):
    if autolocation != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+autolocation+['type'], val_type)
        data_values.nested_dict_add_to_list(cvpj_l, ['automation']+autolocation+['placements'], in_autopoints)

def iter(cvpj_l):
    outdata = []
    if 'automation' in cvpj_l:
        cvpj_auto = cvpj_l['automation']
        for autotype in cvpj_auto:
            if autotype in ['main', 'master']:
                for autovarname in cvpj_auto[autotype]:
                    outdata.append([False, [autotype, autovarname], cvpj_auto[autotype][autovarname]])
            else:
                for autonameid in cvpj_auto[autotype]:
                    for autovarname in cvpj_auto[autotype][autonameid]:
                        outdata.append([True, [autotype, autonameid, autovarname], cvpj_auto[autotype][autonameid][autovarname]])
    return outdata

def move(cvpj_l, old_autolocation, new_autolocation):
    print('[tracks] Moving Automation:','/'.join(old_autolocation),'to','/'.join(new_autolocation))
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation']+old_autolocation)
    if dictvals != None:
        data_values.nested_dict_add_value(cvpj_l, ['automation']+new_autolocation, dictvals)
        if old_autolocation[0] in ['main', 'master']:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]]
        else:
            del cvpj_l['automation'][old_autolocation[0]][old_autolocation[1]][old_autolocation[2]]

def del_plugin(cvpj_l, pluginid):
    print('[tracks] Removing Plugin Automation:',pluginid)
    dictvals = data_values.nested_dict_get_value(cvpj_l, ['automation', 'plugin', pluginid])
    if dictvals != None: del cvpj_l['automation', 'plugin', pluginid]

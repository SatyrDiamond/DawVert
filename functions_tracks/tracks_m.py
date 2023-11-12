# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params
from functions import plugins

def inst_create(cvpj_l, instid):
    if 'instruments_data' not in cvpj_l: cvpj_l['instruments_data'] = {}
    cvpj_inst = {}
    cvpj_l['instruments_data'][instid] = cvpj_inst
    if 'instruments_order' not in cvpj_l: cvpj_l['instruments_order'] = []
    if instid not in cvpj_l['instruments_order']: cvpj_l['instruments_order'].append(instid)

def inst_visual(cvpj_l, instid, **kwargs):
    cvpj_inst = cvpj_l['instruments_data'][instid]
    if 'name' in kwargs: 
        if kwargs['name'] != None: cvpj_inst['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: cvpj_inst['color'] = kwargs['color']

def inst_pluginid(cvpj_l, instid, pluginid):
    data_values.nested_dict_add_value(cvpj_l, ['instruments_data', instid, 'instdata', 'pluginid'], pluginid)

def inst_param_add(cvpj_l, trackid, p_id, p_value, p_type):
    params.add(cvpj_l, ['instruments_data', trackid], p_id, p_value, p_type)

def inst_param_get(cvpj_l, trackid, p_id, p_fallback):
    return params.get(cvpj_l, ['instruments_data', trackid], p_id, p_fallback)

def inst_dataval_add(cvpj_l, trackid, datagroup, i_name, i_value):
    if datagroup == None: datagroup = 'data'
    data_values.nested_dict_add_value(cvpj_l, ['instruments_data', trackid, datagroup, i_name], i_value)

def inst_dataval_get(cvpj_l, trackid, datagroup, i_name, i_fallback):
    if datagroup == None: datagroup = 'data'
    value = data_values.nested_dict_get_value(cvpj_l, ['instruments_data', trackid, datagroup, i_name])
    return value

def inst_fxrackchan_add(cvpj_l, instid, fxrack_channel):
    data_values.nested_dict_add_value(cvpj_l, ['instruments_data', instid, 'fxrack_channel'], fxrack_channel)

def inst_fxrackchan_get(cvpj_l, instid):
    value = data_values.nested_dict_get_value(cvpj_l, ['instruments_data', instid, 'fxrack_channel'])
    return value if value != None else 0



def playlist_add(cvpj_l, idnum):
    if 'playlist' not in cvpj_l: cvpj_l['playlist'] = {}
    if str(idnum) not in cvpj_l: cvpj_l['playlist'][str(idnum)] = {}

def playlist_visual(cvpj_l, idnum, **kwargs):
    if 'playlist' not in cvpj_l: cvpj_l['playlist'] = {}
    if str(idnum) not in cvpj_l: cvpj_l['playlist'][str(idnum)] = {}
    pl_data = cvpj_l['playlist'][str(idnum)]
    if 'name' in kwargs: 
        if kwargs['name'] != None: pl_data['name'] = kwargs['name']
    if 'color' in kwargs: 
        if kwargs['color'] != None: pl_data['color'] = kwargs['color']

def add_pl(cvpj_l, idnum, pl_type, placements_data):
    placement_name = 'placements_'+pl_type
    if placements_data != None: 
        data_values.nested_dict_add_to_list(cvpj_l, ['playlist', str(idnum), placement_name], placements_data)


def import_dset(cvpj_l, trackid, instid, main_dataset, midi_dataset, def_name, def_color):
    m_bank, m_inst, m_drum = main_dataset.midito_get('inst', instid)
    di_name, di_color = main_dataset.object_get_name_color('inst', instid)
    if m_inst != None:
        dm_name, dm_color = midi_dataset.object_get_name_color('inst', str(m_inst))
        out_name = data_values.list_usefirst([def_name, di_name, instid])
        out_color = data_values.list_usefirst([def_color, di_color, dm_color])
        inst_create(cvpj_l, instid)
        inst_visual(cvpj_l, instid, name=out_name, color=out_color)
        inst_plugindata = plugins.cvpj_plugin('midi', m_bank, m_inst)
        inst_plugindata.to_cvpj(cvpj_l, str(m_inst))
        if m_drum == True: 
            inst_param_add(cvpj_l, instid, 'usemasterpitch', False, 'bool')
            inst_dataval_add(cvpj_l, instid, 'midi', 'output', {'drums': True})
        else: 
            inst_plugindata = plugins.cvpj_plugin('midi', m_bank, m_inst)
            inst_param_add(cvpj_l, instid, 'usemasterpitch', True, 'bool')
            inst_dataval_add(cvpj_l, instid, 'midi', 'output', {'program': m_inst, 'bank': m_bank})
        inst_pluginid(cvpj_l, instid, str(m_inst))
        return True, m_bank, m_inst, m_drum, out_name, out_color
    else:
        out_name = data_values.list_usefirst([def_name, di_name, instid])
        out_color = data_values.list_usefirst([def_color, di_color])
        inst_create(cvpj_l, instid)
        inst_visual(cvpj_l, instid, name=out_name, color=out_color)
        return False, None, None, None, out_name, out_color
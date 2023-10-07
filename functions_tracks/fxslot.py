# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params

def get_fxcvpjlocation(fxloc):
    out_location = None
    if fxloc[0] == 'track': out_location = ['track_data', fxloc[1]]
    if fxloc[0] == 'instrument': out_location = ['instruments_data', fxloc[1]]
    if fxloc[0] == 'master': out_location = ['track_master']
    if fxloc[0] == 'fxrack': out_location = ['fxrack', str(fxloc[1])]
    if fxloc[0] == 'group': out_location = ['groups', fxloc[1]]
    if fxloc[0] == 'return': 
        if fxloc[1] == None: out_location = ['track_master', 'returns', fxloc[2]]
        else: out_location = ['groups', fxloc[1], 'returns', fxloc[2]]
    return out_location

def insert(cvpj_l, fxloc, fxtype, pluginid):
    out_location = get_fxcvpjlocation(fxloc)
    if fxtype == 'audio': 
        data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_audio'], pluginid)
    if fxtype == 'notes': 
        data_values.nested_dict_add_to_list(cvpj_l, out_location+['chain_fx_notes'], pluginid)

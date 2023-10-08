# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import params
from functions_tracks import auto_data

# ------------------------ autoid to cvpjauto ------------------------

in_data = {}

def in_define(i_id, i_loc, i_type, i_addmul):
    #print('in_define', i_id, i_loc, i_type, i_addmul)
    if i_id not in in_data: 
        in_data[i_id] = [i_loc, i_type, i_addmul, []]
    else:
        in_data[i_id][0] = i_loc
        in_data[i_id][1] = i_type
        in_data[i_id][2] = i_addmul

def in_add_pl(i_id, i_autopl):
    #print('in_add_pl', i_id, len(i_autopl))
    if i_id not in in_data: in_data[i_id] = [None, None, None, []]
    in_data[i_id][3].append(i_autopl)

def in_output(cvpj_l):
    for i_id in in_data:
        out_auto_loc = in_data[i_id][0]
        out_auto_type = in_data[i_id][1]
        out_auto_addmul = in_data[i_id][2]
        out_auto_data = in_data[i_id][3]
        #print(i_id, in_data[i_id][0:3], out_auto_data)
        if in_data[i_id][0:4] != [None, None, None] and out_auto_data != []:
            if out_auto_addmul != None: out_auto_data = auto.multiply(out_auto_data, out_auto_addmul[0], out_auto_addmul[1])
            auto_data.add_pl(cvpj_l, out_auto_type, out_auto_loc, out_auto_data)

# ------------------------ cvpjauto to autoid ------------------------

out_num = 340000
out_ids = {}
out_data = {}

def out_getlist(i_id):
    global out_num
    global out_data
    dictvals = data_values.nested_dict_get_value(out_ids, i_id)
    return dictvals

def out_get(i_id):
    global out_num
    global out_data
    idvalue = data_values.nested_dict_get_value(out_ids, i_id)

    if idvalue != None and idvalue in out_data: 
        output = idvalue, out_data[idvalue]
        del out_data[idvalue]
        return output
    else: return None, None

def out_load(cvpj_l):
    global out_num
    global out_data

    for autopart in auto_data.iter(cvpj_l):
        data_values.nested_dict_add_value(out_ids, autopart[1], out_num)
        out_data[out_num] = autopart[2]
        out_num += 1
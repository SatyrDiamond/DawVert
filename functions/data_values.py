# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def nested_dict_add_value(i_dict, i_keys, i_value):
    if len(i_keys) == 1: i_dict.setdefault(i_keys[0], i_value)
    else:
        key = i_keys[0]
        if key not in i_dict: i_dict[key] = {}
        nested_dict_add_value(i_dict[key], i_keys[1:], i_value)

def nested_dict_add_to_list(i_dict, i_keys, i_value):
    if len(i_keys) == 1: 
        i_dict.setdefault(i_keys[0], [])
        if isinstance(i_value, list) == True: i_dict[i_keys[0]] = i_value
        else: i_dict[i_keys[0]].append(i_value)
    else:
        key = i_keys[0]
        if key not in i_dict: i_dict[key] = {}
        nested_dict_add_to_list(i_dict[key], i_keys[1:], i_value)

def nested_dict_add_to_list_exists(i_dict, i_keys, i_value):
    if len(i_keys) == 1: 
        i_dict.setdefault(i_keys[0], [])
        if isinstance(i_value, list) == True: i_dict[i_keys[0]] = i_value
        elif i_value not in i_dict[i_keys[0]]: i_dict[i_keys[0]].append(i_value)
    else:
        key = i_keys[0]
        if key not in i_dict: i_dict[key] = {}
        nested_dict_add_to_list_exists(i_dict[key], i_keys[1:], i_value)

def get_value(i_dict, i_tag, i_fallback):
    if i_tag in i_dict: outvalue = i_dict[i_tag]
    else: outvalue = i_fallback
    return outvalue

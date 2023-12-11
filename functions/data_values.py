# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import re

class counter:
    def __init__(self, starting_num):
        self.current = starting_num

    def get(self):
        self.current += 1
        return self.current

    def get_str(self):
        self.current += 1
        return str(self.current)

    def next(self):
        return self.current+1



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

def nested_dict_get_value(i_data, i_keys):
    temp_dict = i_data
    while len(i_keys) != 0:
        if i_keys[0] in temp_dict:
            temp_dict = temp_dict[i_keys[0]]
            i_keys = i_keys[1:]
        else:
            temp_dict = None
            break
    return temp_dict

def get_value(i_dict, i_tag, i_fallback):
    if i_tag in i_dict: outvalue = i_dict[i_tag]
    else: outvalue = i_fallback
    return outvalue

def sort_pos(datapart):
    t_datapart_bsort = {}
    t_datapart_sorted = {}
    new_datapart = []
    for point in datapart:
        if point['position'] not in t_datapart_bsort:
            t_datapart_bsort[point['position']] = []
        t_datapart_bsort[point['position']].append(point)
    t_datapart_sorted = dict(sorted(t_datapart_bsort.items(), key=lambda item: item[0]))
    for t_pointpos in t_datapart_sorted:
        for point in t_datapart_sorted[t_pointpos]:
            new_datapart.append(point)
    return new_datapart

def list_chunks(i_list, i_amount):
    return [i_list[i:i + i_amount] for i in range(0, len(i_list), i_amount)]

def list_to_reigons(i_list, offsetval):
    output = []
    i_list_p = None
    mscount = 0
    for i_list_e in i_list:
        if i_list_e != i_list_p: 
            i_list_p = i_list_e
            output.append([i_list_p, mscount-offsetval, mscount-1-offsetval])
        output[-1][2] += 1
        mscount += 1
    return output

def list_to_reigons_bool(i_list):
    found_regs = []
    i_list_p = None
    mscount = 0
    for i_list_e in i_list:
        if i_list_e != i_list_p: 
            i_list_p = i_list_e
            found_regs.append([i_list_p, mscount, mscount])
        found_regs[-1][2] += 1
        mscount += 1

    output = []
    for found_reg in found_regs:
        if found_reg[0]: output.append(found_reg[1:])

    return output

def list_findrepeat(i_list):
    outdata = []
    for part in i_list:
        if outdata == []: outdata.append([part, 1])
        else:
            if outdata[-1][0] == part: outdata[-1][1] += 1
            else: outdata.append([part, 1])
    return outdata

def tempo_to_rate(i_in, i_mode):
    if i_mode == True: return (120/i_in)
    if i_mode == False: return (i_in/120)

def time_from_steps(i_dict, i_name, i_stretched, i_value, i_rate):
    in_bpm = 1
    in_stretch = 1

    if i_rate != None: in_stretch = i_rate

    if i_stretched == False:
        out_nonstretch = i_value
        out_normal = i_value*in_stretch
        i_dict[i_name+'_nonstretch'] = out_nonstretch
        i_dict[i_name] = out_normal
    else:
        out_nonstretch = i_value/in_stretch
        out_normal = i_value
        i_dict[i_name+'_nonstretch'] = i_value/in_stretch
        i_dict[i_name] = i_value

    out_real_nonstretch = (out_nonstretch/8)*in_bpm
    out_real = out_real_nonstretch/in_stretch

    i_dict[i_name+'_real_nonstretch'] = out_real_nonstretch
    i_dict[i_name+'_real'] = out_real

def time_from_seconds(i_dict, i_name, i_stretched, i_value, i_rate):
    in_bpm = 1
    in_stretch = 1

    if i_rate != None: in_stretch = i_rate

    if i_stretched == False:
        out_real_nonstretch = i_value
        out_real = out_real_nonstretch/in_stretch
        i_dict[i_name+'_real_nonstretch'] = out_real_nonstretch
        i_dict[i_name+'_real'] = out_real

    else:
        out_real = i_value
        out_real_nonstretch = out_real*in_stretch
        i_dict[i_name+'_real_nonstretch'] = out_real_nonstretch
        i_dict[i_name+'_real'] = out_real

    out_nonstretch = (out_real_nonstretch*8)*in_bpm
    out_normal = out_nonstretch*in_stretch

    i_dict[i_name+'_nonstretch'] = out_nonstretch
    i_dict[i_name] = out_normal


def list_traits_supported(i_required, i_supported):
    print(i_required)
    print(i_supported)
    for part in i_supported:
        if part in i_required: i_required.remove(part)
    return i_required == []

def ifallsame(i_list):
    return all(item == i_list[0] for item in i_list) 

def closest(i_dict, in_value):
    outnum = 0
    for num in i_dict:
        if num <= in_value: outnum = num
    return outnum

def most_frequent(i_list): return max(set(i_list), key = i_list.count)

def xml_compat(i_text):
    return re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', i_text)

def list_tab_closest(i_list, v_target, v_num):
    closestnumlist = [None, None, None]
    for num in range(len(i_list)):
        list_part = i_list[num]
        #print(list_part, abs(v_target-list_part[v_num]) )
        howclose = abs(v_target-list_part[v_num])
        if closestnumlist[2] != None: 
            if howclose < closestnumlist[2]: 
                closestnumlist[0] = list_part
                closestnumlist[1] = num
                closestnumlist[2] = howclose
        else: 
            closestnumlist[0] = list_part
            closestnumlist[1] = num
            closestnumlist[2] = howclose
    return closestnumlist

def list_samesimilar(first, second):
    out = 0
    for x in range(len(first)):
        if first[x] == second[x]: out += 1
    return out/len(first)

def list_usefirst(i_list):
    finalval = None
    for p in i_list:
        if p != None: 
            finalval = p
            break
    return finalval

def get_all_keys(i_dict, nestedval):
    for key, value in i_dict.items():
        if isinstance(value, dict):
            yield from get_all_keys(value, nestedval+[key])
        else:
            yield nestedval+[key], value

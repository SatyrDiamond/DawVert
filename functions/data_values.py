# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import re

class dif_val:
	def __init__(self, inval):
		self.cur_val = inval

	def do_value(self, inval):
		out_val = inval-self.cur_val if self.cur_val != None else None
		self.cur_val = inval
		return out_val

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

def get_value(i_dict, i_tag, i_fallback):
	if i_tag in i_dict: outvalue = i_dict[i_tag]
	else: outvalue = i_fallback
	return outvalue

# -------------------- dict nested --------------------

def dict__nested_add_value(i_dict, i_keys, i_value):
	if len(i_keys) == 1: i_dict.setdefault(i_keys[0], i_value)
	else:
		key = i_keys[0]
		if key not in i_dict: i_dict[key] = {}
		dict__nested_add_value(i_dict[key], i_keys[1:], i_value)

def dict__nested_add_to_list(i_dict, i_keys, i_value):
	if len(i_keys) == 1: 
		i_dict.setdefault(i_keys[0], [])
		if isinstance(i_value, list) == True: i_dict[i_keys[0]] = i_value
		else: i_dict[i_keys[0]].append(i_value)
	else:
		key = i_keys[0]
		if key not in i_dict: i_dict[key] = {}
		dict__nested_add_to_list(i_dict[key], i_keys[1:], i_value)

def dict__nested_add_to_list_exists(i_dict, i_keys, i_value):
	if len(i_keys) == 1: 
		i_dict.setdefault(i_keys[0], [])
		if isinstance(i_value, list) == True: i_dict[i_keys[0]] = i_value
		elif i_value not in i_dict[i_keys[0]]: i_dict[i_keys[0]].append(i_value)
	else:
		key = i_keys[0]
		if key not in i_dict: i_dict[key] = {}
		dict__nested_add_to_list_exists(i_dict[key], i_keys[1:], i_value)

def dict__nested_get_value(i_data, i_keys):
	temp_dict = i_data
	while len(i_keys) != 0:
		print
		if i_keys[0] in temp_dict:
			temp_dict = temp_dict[i_keys[0]]
			i_keys = i_keys[1:]
		else:
			temp_dict = None
			break
	return temp_dict

# -------------------- dict --------------------

def dict__get_all_keys(i_dict, nestedval):
	for key, value in i_dict.items():
		if isinstance(value, dict):
			yield from get_all_keys(value, nestedval+[key])
		else:
			yield nestedval+[key], value

def dict__closest(i_dict, in_value): # UNUSED
	outnum = 0
	for num in i_dict:
		if num <= in_value: outnum = num
	return outnum

# -------------------- list --------------------

def list__ifallsame(i_list):
	return all(item == i_list[0] for item in i_list) 

def list__only_values(i_required, i_supported):
	i_required = i_required.copy()
	i_supported = i_supported.copy()
	for part in i_supported:
		if part in i_required: 
			i_required.remove(part)
	return i_required == []

def list__to_reigons(i_list, offsetval):
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

def list__fancysort(i_list):
	if all(ele.isdigit() for ele in i_list):
		i_list = [int(x) for x in i_list]
		i_list.sort()
		i_list = [str(x) for x in i_list]
	return i_list

def list__chunks(i_list, i_amount):
	return [i_list[i:i + i_amount] for i in range(0, len(i_list), i_amount)]

def list__optionalindex(i_number, i_fallback, i_list):
	if i_number >= 0: return i_list[i_number] if i_number<len(i_list) else i_fallback
	else: return i_fallback

def list__in_both(i_list, o_list): # UNUSED
	return [x for x in i_list if x in o_list]

def list__usefirst(i_list): # UNUSED
	for p in i_list:
		if p != None: return p
	return None

def list__samesimilar(first, second): # UNUSED
	out = 0
	for x in range(len(first)):
		if first[x] == second[x]: out += 1
	return out/len(first)

def list__tab_closest(i_list, v_target, v_num): # UNUSED
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

def list__most_frequent(i_list): # UNUSED
	return max(set(i_list), key = i_list.count)

def list__to_reigons_bool(i_list): # UNUSED
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

def list__dif_val(i_list, startnum):
	outvals = []
	prev = dif_val(startnum)
	for x in i_list:
		outv = prev.do_value(x)
		if outv != None: outvals.append(outv)
	return outvals

def list__findrepeat(i_list): # UNUSED
	outdata = []
	for part in i_list:
		if outdata == []: outdata.append([part, 1])
		else:
			if outdata[-1][0] == part: outdata[-1][1] += 1
			else: outdata.append([part, 1])
	return outdata

# -------------------- generator --------------------

def gen__rangepos(posval, dur):
	for num in range(len(posval)-1): yield posval[num][0], posval[num+1][0], posval[num][1]
	yield posval[-1][0], dur, posval[-1][1]

# -------------------- text --------------------

def text__xml_compat(i_text): # UNUSED
	return re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', i_text)

def text__insidename(name, subname):
	if name and subname: return subname+' ('+name+')'
	elif name: return name
	elif subname: return subname
	return None

def text__insidename_type(name, subname, itype):
	return subname+' ('+name+')' if name else subname+' ('+itype+')'

# -------------------- other --------------------

def assoc_remap(i_assoc_org, i_assoc_new):
	nextnew = len(i_assoc_org)
	outputs = i_assoc_org.copy()
	remap = []
	for n in i_assoc_new:
		if n in i_assoc_org: remap.append(i_assoc_org.index(n))
		else:
			remap.append(nextnew)
			nextnew += 1
			outputs.append(n)
	return outputs, remap

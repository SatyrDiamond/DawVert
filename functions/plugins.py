# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params
from functions import data_values

pluginid_num = 1000


def get_id():
	global pluginid_num
	pluginid_num += 1
	return 'plugin'+str(pluginid_num)


# -------------------------------------------------- plugdata

def add_plug(cvpj_l, pluginid, i_type, i_subtype):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], i_type)
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'subtype'], i_subtype)

def get_plug_type(cvpj_l, pluginid):
	p_type = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'type'])
	p_subtype = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'subtype'])
	return [p_type,p_subtype]

def replace_plug(cvpj_l, pluginid, i_type, i_subtype):
	plugdata = cvpj_l['plugins'][pluginid]
	for name in ['params', 'data', 'type', 'subtype']:
		if name in plugdata: del plugdata[name]
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], i_type)
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'subtype'], i_subtype)

# -------------------------------------------------- fxdata

def add_plug_fxdata(cvpj_l, pluginid, i_enabled, i_wet):
	if i_enabled != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'enabled'], i_enabled)
	if i_wet != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wet'], i_wet)

def get_plug_fxdata(cvpj_l, pluginid):
	enabled = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'enabled'])
	wet = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'wet'])
	if enabled == None: enabled = True
	if wet == None: wet = 1
	return enabled, wet

def add_plug_fxvisual(cvpj_l, pluginid, v_name, v_color):
	if v_name != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'name'], v_name)
	if v_color != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'color'], v_color)

# -------------------------------------------------- data

def add_plug_data(cvpj_l, pluginid, i_name, i_value):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'data', i_name], i_value)

def get_plug_data(cvpj_l, pluginid):
	return data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'data'])

def get_plug_dataval(cvpj_l, pluginid, paramname, fallbackval):
	paramdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'data', paramname])
	if paramdata != None: return paramdata
	return fallbackval

# -------------------------------------------------- param

def add_plug_param(cvpj_l, pluginid, i_name, p_value, p_type, p_name):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'params', i_name], 
		params.make(p_value, p_type, p_name)
		)

def get_plug_param(cvpj_l, pluginid, paramname, fallbackval):
	paramdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'params', paramname])
	if paramdata != None: return paramdata['value'], paramdata['type'], paramdata['name']
	return fallbackval, 'notfound', ''

def get_plug_paramlist(cvpj_l, pluginid):
	output = []
	paramdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'params'])
	if paramdata == None: return []
	else:
		for paramname in paramdata: 
			output.append(paramname)
		return output

# -------------------------------------------------- data

def add_plug_gm_midi(cvpj_l, pluginid, i_bank, i_inst):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], 'general-midi')
	add_plug_data(cvpj_l, pluginid, 'bank', i_bank)
	add_plug_data(cvpj_l, pluginid, 'inst', i_inst)

def add_plug_sampler_singlefile(cvpj_l, pluginid, i_file):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], 'sampler')
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'subtype'], 'single')
	add_plug_data(cvpj_l, pluginid, 'file', i_file)

def add_plug_multisampler(cvpj_l, pluginid):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], 'sampler')
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'subtype'], 'multi')

def add_plug_multisampler_region(cvpj_l, pluginid, regiondata):
	data_values.nested_dict_add_to_list(cvpj_l, ['plugins', pluginid, 'data', 'regions'], regiondata)




# -------------------------------------------------- param

def add_filter(cvpj_l, pluginid, i_enabled, i_cutoff, i_reso, i_type, i_subtype):
	filterdata = {}
	filterdata['cutoff'] = i_cutoff
	filterdata['reso'] = i_reso
	filterdata['type'] = i_type
	filterdata['enabled'] = i_enabled
	if i_subtype != None: filterdata['subtype'] = i_subtype
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'filter'], filterdata)

def get_filter(cvpj_l, pluginid):
	filterdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'filter'])
	if filterdata == None: return 0, 44100, 0, None, None
	else:
		p_enabled = data_values.get_value(filterdata, 'enabled', 0)
		p_cutoff = data_values.get_value(filterdata, 'cutoff', 44100)
		p_reso = data_values.get_value(filterdata, 'reso', 0)
		p_type = data_values.get_value(filterdata, 'type', None)
		p_subtype = data_values.get_value(filterdata, 'subtype', None)
		return p_enabled, p_cutoff, p_reso, p_type, p_subtype

# -------------------------------------------------- asdr_env

def add_asdr_env(cvpj_l, pluginid, a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount):
	asdrdata = {}
	asdrdata['predelay'] = a_predelay
	asdrdata['attack'] = a_attack
	asdrdata['hold'] = a_hold
	asdrdata['decay'] = a_decay
	asdrdata['sustain'] = a_sustain
	asdrdata['release'] = a_release
	asdrdata['amount'] = a_amount
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'env_asdr', a_type], asdrdata)

def get_asdr_env(cvpj_l, pluginid, a_type):
	asdr = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'env_asdr', a_type])
	if asdr != None: return asdr['predelay'], asdr['attack'], asdr['hold'], asdr['decay'], asdr['sustain'], asdr['release'], asdr['amount']
	else: return 0,0,0,0,1,0,0

# -------------------------------------------------- LFO

def add_lfo(cvpj_l, pluginid, a_type, a_shape, a_time_type, a_speed, a_predelay, a_attack, a_amount):
	lfodata = {}
	lfodata['predelay'] = a_predelay
	lfodata['attack'] = a_attack
	lfodata['shape'] = a_shape
	lfodata['speed_type'] = a_time_type
	lfodata['speed_time'] = a_speed
	lfodata['amount'] = a_amount
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'lfo', a_type], lfodata)

def get_lfo(cvpj_l, pluginid, a_type):
	lfo = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'lfo', a_type])
	if lfo != None: return lfo['predelay'], lfo['attack'], lfo['shape'], lfo['speed_type'], lfo['speed_time'], lfo['amount']
	else: return 0,0,'sine','seconds',1,0

# -------------------------------------------------- asdr_env

def add_env_point(cvpj_l, pluginid, a_type, p_position, p_value, **kwargs):
	pointdata = {}
	pointdata['position'] = p_position
	pointdata['value'] = p_value
	for key, value in kwargs.items():
		pointdata[key] = value
	data_values.nested_dict_add_to_list(cvpj_l, ['plugins', pluginid, 'env_points', a_type, 'points'], pointdata)

def add_env_point_var(cvpj_l, pluginid, a_type, p_name, p_value):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'env_points', a_type, p_name], p_value)

def add_env_blocks(cvpj_l, pluginid, a_type, a_vals, a_loop, a_release):
	asdrdata = {}
	asdrdata['values'] = a_vals
	if a_loop != None: asdrdata['loop'] = a_loop
	if a_release != None: asdrdata['release'] = a_release
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'env_block', a_type], asdrdata)

def add_wave(cvpj_l, pluginid, i_name, i_wavepoints, i_min, i_max):
	wavedata = {}
	wavedata['range'] = [i_min,i_max]
	wavedata['points'] = i_wavepoints
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wave', i_name], wavedata)
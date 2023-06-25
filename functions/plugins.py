# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params
from functions import data_values

pluginid_num = 1000


def get_plug(cvpj_l, pluginid):
	return data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid])

def get_plug_param(cvpj_l, pluginid, paramname):
	return data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'params', paramname])

def add_plug_fxdata(cvpj_l, pluginid):
	enabled = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'enabled'])
	wet = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'wet'])
	if enabled == None: enabled = True
	if wet == None: wet = 1
	return enabled, wet


def get_id():
	global pluginid_num
	pluginid_num += 1
	return 'plugin'+str(pluginid_num)

def add_plug(cvpj_l, pluginid, i_type, i_subtype):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'type'], i_type)
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'subtype'], i_subtype)

def add_plug_fxdata(cvpj_l, pluginid, i_enabled, i_wet):
	if i_enabled != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'enabled'], i_enabled)
	if i_wet != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wet'], i_wet)

def add_plug_fxvisual(cvpj_l, pluginid, v_name, v_color):
	if v_name != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'name'], v_name)
	if v_color != None: data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'color'], v_color)

def add_plug_data(cvpj_l, pluginid, i_name, i_value):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'data', i_name], i_value)

def add_plug_param(cvpj_l, pluginid, i_name, p_value, p_type, p_name):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'params', i_name], 
		params.make(p_value, p_type, p_name)
		)

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




def add_filter(cvpj_l, pluginid, i_enabled, i_cutoff, i_reso, i_type, i_subtype):
	filterdata = {}
	filterdata['cutoff'] = i_cutoff
	filterdata['reso'] = i_reso
	filterdata['type'] = i_type
	if i_subtype != None: filterdata['subtype'] = i_subtype
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'filter'], filterdata)

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

def add_lfo(cvpj_l, pluginid, a_type, a_shape, a_time_type, a_speed, a_predelay, a_attack, a_amount):
	lfodata = {}
	lfodata['amount'] = a_amount
	lfodata['shape'] = a_shape
	lfodata['speed'] = {'type': a_time_type, 'speed': a_speed}
	lfodata['predelay'] = a_predelay
	lfodata['attack'] = a_attack
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'lfo', a_type], lfodata)

def add_wave(cvpj_l, pluginid, i_name, i_wavepoints, i_min, i_max):
	wavedata = {}
	wavedata['range'] = [i_min,i_max]
	wavedata['points'] = i_wavepoints
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wave', i_name], wavedata)
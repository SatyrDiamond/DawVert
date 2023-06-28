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
	for name in ['type', 'subtype']:
		if name in plugdata: del plugdata[name]
	if 'params' in plugdata: 
		plugdata['params_old'] = plugdata['params'].copy()
		del plugdata['params']
	if 'data' in plugdata: 
		plugdata['data_old'] = plugdata['data'].copy()
		del plugdata['data']
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

def get_plug_olddataval(cvpj_l, pluginid, paramname, fallbackval):
	paramdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'data_old', paramname])
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

def get_plug_oldparam(cvpj_l, pluginid, paramname, fallbackval):
	paramdata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'params_old', paramname])
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

# -------------------------------------------------- env_blocks

def add_env_blocks(cvpj_l, pluginid, a_type, a_vals, a_max, a_loop, a_release):
	envdata = {}
	envdata['values'] = a_vals
	if a_max != None: envdata['max'] = a_max
	if a_loop != None: envdata['loop'] = a_loop
	if a_release != None: envdata['release'] = a_release
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'env_block', a_type], envdata)

def get_env_blocks(cvpj_l, pluginid, a_type):
	return data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'env_block', a_type])

# -------------------------------------------------- env_point

def add_env_point(cvpj_l, pluginid, a_type, p_position, p_value, **kwargs):
	pointdata = {}
	pointdata['position'] = p_position
	pointdata['value'] = p_value
	for key, value in kwargs.items():
		pointdata[key] = value
	data_values.nested_dict_add_to_list(cvpj_l, ['plugins', pluginid, 'env_points', a_type, 'points'], pointdata)

def add_env_point_var(cvpj_l, pluginid, a_type, p_name, p_value):
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'env_points', a_type, p_name], p_value)

def get_env_points(cvpj_l, pluginid, a_type):
	return data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'env_points', a_type])

def one_invert(input):
	return (input*-1)+1

def env_point_to_asdr(cvpj_l, pluginid, a_type):
	env_pointsdata = get_env_points(cvpj_l, pluginid, a_type)
	if env_pointsdata != None:
		sustainpoint = data_values.get_value(env_pointsdata, 'sustain', None)
		if 'points' in env_pointsdata:
			pointsdata = env_pointsdata['points']
			numpoints = len(pointsdata)

			a_predelay = 0
			a_attack = 0
			a_hold = 0
			a_decay = 0
			a_sustain = 1
			a_release = 0
			a_amount = 1

			if (sustainpoint == None or sustainpoint == numpoints): sustainnum = None
			else: sustainnum = sustainpoint

			#print(pointsdata, numpoints, sustainpoint)
			
			if numpoints == 2:
				env_duration = pointsdata[1]['position']
				env_value = pointsdata[0]['value'] - pointsdata[1]['value']

				if sustainnum == None:
					if env_value > 0:
						a_decay = env_duration
						a_sustain = 0
					if env_value < 0: a_attack = env_duration

				elif sustainnum == 1:
					if env_value > 0: a_release = env_duration
					if env_value < 0:
						a_release = env_duration
						a_amount = -1

			elif numpoints == 3:
				envp_middle = pointsdata[1]['position']
				envp_end = pointsdata[2]['position']
				envv_first = pointsdata[0]['value']
				envv_middle = pointsdata[1]['value']
				envv_end = pointsdata[2]['value']
				firstmid_s = envv_first-envv_middle
				midend_s = envv_end-envv_middle
				#print(0, envv_first)
				#print(envp_middle, envv_middle, firstmid_s)
				#print(envp_end-envp_middle, envv_end, midend_s)
				if firstmid_s > 0 and sustainnum == None: a_sustain = 0

				if firstmid_s > 0 and midend_s == 0:
					#print("^__")
					if sustainnum == None: a_decay = envp_middle
					if sustainnum == 1: a_release = envp_middle

				elif firstmid_s > 0 and midend_s < 0: #to-do: tension
					#print("^._")
					if sustainnum == None: a_decay = envp_end
					if sustainnum == 1: a_release = envp_end
					if sustainnum == 2: 
						a_decay = envp_middle
						a_release = envp_end-envp_middle
						a_sustain = envv_middle

				elif firstmid_s < 0 and midend_s < 0:
					#print("_^.")
					if sustainnum in [None, 1]: 
						a_attack = envp_middle
						a_decay = (envp_end-envp_middle)
						a_sustain = envv_end
					if sustainnum == 2: 
						a_attack = envp_middle
						a_release = (envp_end-envp_middle)
						if envv_end != 0: a_release /= one_invert(envv_end)

				elif firstmid_s == 0 and midend_s < 0:
					#print("^^.")
					if sustainnum in [None, 1]:
						a_hold = envp_middle
						a_decay = envp_end-envp_middle
						a_sustain = envv_end
					if sustainnum == 2: 
						a_hold = envp_middle
						a_release = envp_end-envp_middle
						if envv_end != 0: a_release /= one_invert(envv_end)

				elif firstmid_s < 0 and midend_s > 0: #to-do: tension
					#print("_.^")
					a_attack = envp_end

				elif firstmid_s == 0 and midend_s > 0:
					#print("__^")
					a_predelay = envp_middle
					a_attack = envp_end

				elif firstmid_s < 0 and midend_s == 0:
					#print("_^^")
					a_attack = envp_middle
					a_hold = envp_end-envp_middle

				elif firstmid_s > 0 and midend_s > 0:
					#print("^.^")
					if sustainnum in [None, 1]:
						a_attack = envp_middle
						a_decay = (envp_end-envp_middle)
						a_amount = envv_middle-1
					if sustainnum == 2: 
						a_attack = envp_middle
						a_release = (envp_end-envp_middle)
						a_amount = envv_middle-1



			susinvert = (a_sustain*-1)+1
			if susinvert != 0:
				a_decay /= susinvert

			#exit()
			
			add_asdr_env(cvpj_l, pluginid, a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount)

# -------------------------------------------------- wave

def add_wave(cvpj_l, pluginid, i_name, i_wavepoints, i_min, i_max):
	wavedata = {}
	wavedata['range'] = [i_min,i_max]
	wavedata['points'] = i_wavepoints
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wave', i_name], wavedata)

def get_wave(cvpj_l, pluginid, wave_name):
	wavedata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'wave'])
	if wavedata != None:
		if wave_name != None: 
			return wavedata[wave_name]
		else:
			firstwave = list(wavedata.keys())[0]
			return wavedata[firstwave]

# -------------------------------------------------- wave

def add_wavetable(cvpj_l, pluginid, i_name, i_wavenames, i_wavelocs, i_phase):
	wavedata = {}
	wavedata['ids'] = i_wavenames
	if i_wavelocs != None: wavedata['locs'] = i_wavelocs
	if i_phase != None: wavedata['phase'] = i_phase
	data_values.nested_dict_add_value(cvpj_l, ['plugins', pluginid, 'wavetable', i_name], wavedata)

def get_wavetable(cvpj_l, pluginid, wave_name):
	wavedata = data_values.nested_dict_get_value(cvpj_l, ['plugins', pluginid, 'wavetable'])
	if wavedata != None:
		if wave_name != None: 
			return wavedata[wave_name]
		else:
			firstwave = list(wavedata.keys())[0]
			return wavedata[firstwave]

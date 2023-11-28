# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params
from functions import xtramath
from functions import data_values
import base64

def namegroup_add(i_dict, i_group, i_name, i_data):
    data_values.nested_dict_add_value(i_dict, [i_group, i_name], i_data)

def namegroup_get_a(i_dict, i_group, i_name):
    outdata = data_values.nested_dict_get_value(i_dict, [i_group])
    if outdata != None:
        if i_name in outdata: 
            return outdata[i_name]
        else:
            firstname = list(outdata.keys())[0]
            return outdata[firstname]

def namegroup_get(i_dict, i_group, i_name):
    outdata = data_values.nested_dict_get_value(i_dict, [i_group])
    if outdata != None:
        if i_name in outdata: 
            return outdata[i_name]

def namegroup_list(i_dict, i_group):
        out_list = []
        if i_group in i_dict: 
            for a_type in i_dict[i_group]: 
                out_list.append(a_type)
        return out_list

pluginid_num = 1000
def get_id():
    global pluginid_num
    pluginid_num += 1
    return 'plugin'+str(pluginid_num)


class cvpj_plugin:
    def __init__(self, i_init, i_data1, i_data2):
        self.cvpjdata = {}

        if i_init == 'deftype':
            self.cvpjdata['type'] = i_data1
            if i_data2 != None: self.cvpjdata['subtype'] = i_data2

        if i_init == 'cvpj':
            out_data = data_values.nested_dict_get_value(i_data1, ['plugins', i_data2])
            if out_data != None: self.cvpjdata = out_data.copy()

        if i_init == 'midi':
            self.cvpjdata['type'] = 'midi'
            self.dataval_add('bank', i_data1)
            self.dataval_add('inst', i_data2)

        if i_init == 'sampler':
            self.cvpjdata['type'] = 'sampler'
            self.cvpjdata['subtype'] = 'single'
            self.dataval_add('file', i_data1)

        if i_init == 'multisampler':
            self.cvpjdata['type'] = 'sampler'
            self.cvpjdata['subtype'] = 'multi'

    # -------------------------------------------------- replace
    def replace(self, i_type, i_subtype):
        self.cvpjdata['type'] = i_type
        if i_subtype != None: self.cvpjdata['subtype'] = i_subtype
        elif 'subtype' in self.cvpjdata: del self.cvpjdata['subtype']
        if 'params' in self.cvpjdata: del self.cvpjdata['params']
        if 'data' in self.cvpjdata: del self.cvpjdata['data']

    def replace_keep(self, i_type, i_subtype):
        self.cvpjdata['type'] = i_type
        if i_subtype != None: self.cvpjdata['subtype'] = i_subtype
        elif 'subtype' in self.cvpjdata: del self.cvpjdata['subtype']

    # -------------------------------------------------- type
    def type_set(self, i_type, i_subtype):
        self.cvpjdata['type'] = i_type
        if i_subtype != None: self.cvpjdata['subtype'] = i_subtype
    def type_get(self):
        return [self.cvpjdata['type'] if 'type' in self.cvpjdata else None, self.cvpjdata['subtype'] if 'subtype' in self.cvpjdata else None]

    # -------------------------------------------------- fxdata
    def fxdata_add(self, i_enabled, i_wet):
        if i_enabled != None: params.add(self.cvpjdata, [], 'enabled', i_enabled, 'bool', groupname='params_slot')
        if i_wet != None: params.add(self.cvpjdata, [], 'wet', i_wet, 'float', groupname='params_slot')
    def fxdata_get(self):
        i_enabled = params.get(self.cvpjdata, [], 'enabled', True, groupname='params_slot')[0]
        i_wet = params.get(self.cvpjdata, [], 'wet', 1, groupname='params_slot')[0]
        return i_enabled, i_wet

    # -------------------------------------------------- fxvisual
    def fxvisual_add(self, v_name, v_color):
        if v_name != None: self.cvpjdata['name'] = v_name
        if v_color != None: self.cvpjdata['color'] = v_color
    def fxvisual_get(self):
        name = self.cvpjdata['name'] if 'name' in self.cvpjdata else None
        color = self.cvpjdata['color'] if 'color' in self.cvpjdata else None
        return name, color

    # -------------------------------------------------- param
    def param_add(self, p_id, p_value, p_type, p_name): 
        params.add(self.cvpjdata, [], p_id, p_value, p_type, visname=p_name)

    def param_add_minmax(self, p_id, p_value, p_type, p_name, p_minmax): 
        if None in p_minmax: p_minmax = None
        params.add(self.cvpjdata, [], p_id, p_value, p_type, visname=p_name, minmax=p_minmax)

    def param_add_dset(self, p_id, p_value, dset, ds_cat, ds_group): 
        defparams = dset.params_i_get(ds_cat, ds_group, p_id)
        if defparams != None:
            if p_value == None: p_value = defparams[2]
            if defparams[0] == False:
                self.param_add_minmax(p_id, p_value, defparams[1], defparams[5], [defparams[3], defparams[4]])
            else:
                self.dataval_add(p_id, p_value)
        else:
            if p_value == None: p_value = 0
            self.param_add(p_id, p_value, 'float', '')

    def param_get(self, paramname, fallbackval): 
        return params.get(self.cvpjdata, [], paramname, fallbackval)

    def param_get_minmax(self, paramname, fallbackval): 
        return params.get_minmax(self.cvpjdata, [], paramname, fallbackval)

    def param_list(self): 
        paramlist = []
        if 'params' in self.cvpjdata:
            for paramname in self.cvpjdata['params']:
                paramlist.append(paramname)
        return paramlist

    # -------------------------------------------------- gm_midi
    def gm_midi(self, i_bank, i_inst): 
        if 'data' not in self.cvpjdata: self.cvpjdata['data'] = {}
        self.cvpjdata['data']['bank'] = i_bank
        self.cvpjdata['data']['inst'] = i_inst

    # -------------------------------------------------- dataval
    def dataval_add(self, i_name, i_value):
        if 'data' not in self.cvpjdata: self.cvpjdata['data'] = {}
        self.cvpjdata['data'][i_name] = i_value
    def dataval_get(self, paramname, fallbackval):
        outval = fallbackval
        if 'data' in self.cvpjdata: 
            if paramname in self.cvpjdata['data']: outval = self.cvpjdata['data'][paramname]
        return outval

    def dataval_list(self): 
        datavallist = []
        if 'data' in self.cvpjdata:
            for datavalname in self.cvpjdata['data']:
                datavallist.append(datavalname)
        return datavallist

    # -------------------------------------------------- rawdata
    def rawdata_add(self, i_value):
        self.cvpjdata['rawdata'] = base64.b64encode(i_value).decode('ascii')

    def rawdata_add_b64(self, i_value):
        self.cvpjdata['rawdata'] = i_value

    def rawdata_get(self):
        if 'rawdata' in self.cvpjdata: return base64.b64decode(self.cvpjdata['rawdata'])
        else: return b''

    def rawdata_get_b64(self):
        if 'rawdata' in self.cvpjdata: return self.cvpjdata['rawdata']
        else: return b''
    # -------------------------------------------------- regions
    def region_add(self, regiondata):
        data_values.nested_dict_add_to_list(self.cvpjdata, ['regions'], regiondata)

    # -------------------------------------------------- asdr_env
    def asdr_env_add(self, a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount):
        asdrdata = {}
        asdrdata['predelay'] = a_predelay
        asdrdata['attack'] = a_attack
        asdrdata['hold'] = a_hold
        asdrdata['decay'] = a_decay
        asdrdata['sustain'] = a_sustain
        asdrdata['release'] = a_release
        asdrdata['amount'] = a_amount
        if 'env_asdr' not in self.cvpjdata: self.cvpjdata['env_asdr'] = {}
        self.cvpjdata['env_asdr'][a_type] = asdrdata

    def asdr_env_get(self, a_type):
        outdata = 0,0,0,0,1,0,0
        if 'env_asdr' in self.cvpjdata: 
            if a_type in self.cvpjdata['env_asdr']: 
                asdr = self.cvpjdata['env_asdr'][a_type]
                outdata = asdr['predelay'], asdr['attack'], asdr['hold'], asdr['decay'], asdr['sustain'], asdr['release'], asdr['amount']
        return outdata

    def asdr_env_list(self):
        return namegroup_list(self.cvpjdata, 'env_asdr')

    def env_asdr_from_points(self, a_type):
        env_pointsdata = self.env_points_get(a_type)
    
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
    
                t_attack = 0
                t_decay = 0
                t_release = 0
    
                sustainnum = None if (sustainpoint == None or sustainpoint == numpoints) else sustainpoint
    
                isenvconverted = False
    
                if numpoints == 2:
                    env_duration = pointsdata[1]['position']
                    env_value = pointsdata[0]['value'] - pointsdata[1]['value']
    
                    if sustainnum == None:
                        if env_value > 0:
                            a_decay = env_duration
                            a_sustain = 0
                        if env_value < 0: a_attack = env_duration
                        isenvconverted = True
    
                    elif sustainnum == 1:
                        if env_value > 0: a_release = env_duration
                        if env_value < 0:
                            a_release = env_duration
                            a_amount = -1
                        isenvconverted = True
    
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
                        isenvconverted = True
    
                    elif firstmid_s > 0 and midend_s < 0: #to-do: tension
                        #print("^._")
                        if sustainnum == None: 
                            a_decay = envp_end
    
                        if sustainnum == 1: 
                            a_release = envp_end
                            t_release = ((((envp_middle/envp_end)/2)+(envv_middle/2))-0.5)*2
    
                        if sustainnum == 2: 
                            a_decay = envp_middle
                            a_release = envp_end-envp_middle
                            a_sustain = envv_middle
                        isenvconverted = True
    
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
                        isenvconverted = True
    
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
                        isenvconverted = True
    
                    elif firstmid_s < 0 and midend_s > 0: #to-do: tension
                        #print("_.^")
                        a_attack = envp_end
                        isenvconverted = True
    
                    elif firstmid_s == 0 and midend_s > 0:
                        #print("__^")
                        a_predelay = envp_middle
                        a_attack = envp_end
                        isenvconverted = True
    
                    elif firstmid_s < 0 and midend_s == 0:
                        #print("_^^")
                        a_attack = envp_middle
                        a_hold = envp_end-envp_middle
                        isenvconverted = True
    
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
                        isenvconverted = True
    
                if isenvconverted == True and a_sustain != 0 and a_release == 0: a_release = data_values.get_value(env_pointsdata, 'fadeout', 0)
    
                susinvert = (a_sustain*-1)+1
                if susinvert != 0:
                    a_decay /= susinvert
    
                if a_type == 'cutoff': a_amount *= 6000
    
                self.asdr_env_add(a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount)
                self.asdr_env_tension_add(a_type, t_attack, t_decay, t_release)
    
    def asdr_env_get_fake_tension(self, asdrtype):
        a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount = self.asdr_env_get(asdrtype)
        t_attack, t_decay, t_release = self.asdr_env_tension_get(asdrtype)
        a_attack *= pow(2, min(t_attack*3.14, 0))
        a_decay *= pow(2, min(t_decay*3.14, 0))
        a_release *= pow(2, min(t_release*3.14, 0))
        return a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount

    # -------------------------------------------------- asdr_env_tension
    def asdr_env_tension_add(self, a_type, t_attack, t_decay, t_release):
        if 'env_asdr' not in self.cvpjdata: self.cvpjdata['env_asdr'] = {}
        if a_type not in self.cvpjdata['env_asdr']: self.cvpjdata['env_asdr'][a_type] = {}
        envdata = self.cvpjdata['env_asdr'][a_type]
        envdata['attack_tension'] = t_attack
        envdata['decay_tension'] = t_decay
        envdata['release_tension'] = t_release

    def asdr_env_tension_get(self, a_type):
        outdata = [0,0,0]
        if 'env_asdr' in self.cvpjdata: 
            if a_type in self.cvpjdata['env_asdr']: 
                asdr = self.cvpjdata['env_asdr'][a_type]
                if 'attack_tension' in asdr: outdata[0] = asdr['attack_tension']
                if 'decay_tension' in asdr: outdata[1] = asdr['decay_tension']
                if 'release_tension' in asdr: outdata[2] = asdr['release_tension']
        return outdata

    # -------------------------------------------------- env_blocks
    def env_blocks_add(self, a_type, a_vals, a_time, a_max, a_loop, a_release):
        if 'env_blocks' not in self.cvpjdata: self.cvpjdata['env_blocks'] = {}
        envdata = {}
        envdata['values'] = a_vals
        if a_time != None: envdata['time'] = a_time
        if a_max != None: envdata['max'] = a_max
        if a_loop != None: envdata['loop'] = a_loop
        if a_release != None: envdata['release'] = a_release
        self.cvpjdata['env_blocks'][a_type] = envdata

    def env_blocks_get(self, a_type): 
        if 'env_blocks' in self.cvpjdata: 
            if a_type in self.cvpjdata['env_blocks']: 
                return self.cvpjdata['env_blocks'][a_type]

    def env_blocks_list(self):
        return namegroup_list(self.cvpjdata, 'env_blocks')

    # -------------------------------------------------- env_points
    def env_points_add(self, a_type, p_position, p_value, **kwargs):
        pointdata = {}
        pointdata['position'] = p_position
        pointdata['value'] = p_value
        for key, value in kwargs.items():
            pointdata[key] = value
        data_values.nested_dict_add_to_list(self.cvpjdata, ['env_points', a_type, 'points'], pointdata)

    def env_points_get(self, a_type):
        if 'env_points' in self.cvpjdata: 
            if a_type in self.cvpjdata['env_points']: 
                return self.cvpjdata['env_points'][a_type]

    def env_points_addvar(self, a_type, p_name, p_value):
        data_values.nested_dict_add_value(self.cvpjdata, ['env_points', a_type, p_name], p_value)

    def env_points_from_blocks(self, a_type):
        blocksdata = self.env_blocks_get(a_type)
        if blocksdata != None:
            blocksvalues = blocksdata['values']
            numblocks = len(blocksdata['values'])

            min_val = data_values.get_value(blocksdata, 'min', 0)
            max_val = data_values.get_value(blocksdata, 'max', 1)
            blockdur = data_values.get_value(blocksdata, 'time', 0.018)

            for numblock in range(numblocks):
                self.env_points_add(a_type, numblock*blockdur, xtramath.between_to_one(min_val, max_val, blocksvalues[numblock]))

    def env_points_list(self):
        return namegroup_list(self.cvpjdata, 'env_points')


    # -------------------------------------------------- filter
    def filter_add(self, i_enabled, i_cutoff, i_reso, i_type, i_subtype):
        filterdata = {}
        filterdata['cutoff'] = i_cutoff
        filterdata['reso'] = i_reso
        filterdata['type'] = i_type
        filterdata['enabled'] = i_enabled
        if i_subtype != None: filterdata['subtype'] = i_subtype
        self.cvpjdata['filter'] = filterdata

    def filter_get(self):
        if 'filter' in self.cvpjdata: 
            filterdata = self.cvpjdata['filter']
            p_enabled = data_values.get_value(filterdata, 'enabled', 0)
            p_cutoff = data_values.get_value(filterdata, 'cutoff', 44100)
            p_reso = data_values.get_value(filterdata, 'reso', 0)
            p_type = data_values.get_value(filterdata, 'type', None)
            p_subtype = data_values.get_value(filterdata, 'subtype', None)
            return p_enabled, p_cutoff, p_reso, p_type, p_subtype
        else:
            return 0, 44100, 0, None, None

    # -------------------------------------------------- lfo
    def lfo_add(self, a_type, a_shape, a_time_type, a_speed, a_predelay, a_attack, a_amount):
        if 'lfo' not in self.cvpjdata: self.cvpjdata['lfo'] = {}
        if a_type not in self.cvpjdata['lfo']: self.cvpjdata['lfo'][a_type] = {}
        lfodata = self.cvpjdata['lfo'][a_type]
        lfodata['predelay'] = a_predelay
        lfodata['attack'] = a_attack
        lfodata['shape'] = a_shape
        lfodata['speed_type'] = a_time_type
        lfodata['speed_time'] = a_speed
        lfodata['amount'] = a_amount

    def lfo_get(self, a_type):
        outdata = 0,0,'sine','seconds',1,0
        if 'lfo' in self.cvpjdata: 
            if a_type in self.cvpjdata['lfo']: 
                lfo = self.cvpjdata['lfo'][a_type]
                outdata = lfo['predelay'], lfo['attack'], lfo['shape'], lfo['speed_type'], lfo['speed_time'], lfo['amount']
        return outdata

    def lfo_list(self):
        return namegroup_list(self.cvpjdata, 'lfo')

    # -------------------------------------------------- eqbands
    def eqband_add(self, b_on, b_freq, b_gain, b_type, b_var, group):
        banddata = {}
        banddata['on'] = b_on
        banddata['freq'] = b_freq
        banddata['gain'] = b_gain
        banddata['type'] = b_type
        banddata['var'] = b_var
        groupdataname = 'eqbands' if group == None else 'eqbands_'+group
        if groupdataname not in self.cvpjdata: self.cvpjdata[groupdataname] = []
        self.cvpjdata[groupdataname].append(banddata)

    def eqband_get(self, group):
        groupdataname = 'eqbands' if group == None else 'eqbands_'+group
        if groupdataname in self.cvpjdata: return self.cvpjdata[groupdataname]
        else: return []

    def eqband_get_limited(self, group):
        #used, active, freq, gain, res/bw

        data_LP =        [False,0,0,0,0]
        data_Lowshelf =  [False,0,0,0,0]
        data_Peaks =     [[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0],[False,0,0,0,0]]
        data_HighShelf = [False,0,0,0,0]
        data_HP =        [False,0,0,0,0]
        banddata = self.eqband_get(group)

        data_auto = [None, None, [None,None,None,None], None, None]

        bandnum = 1
        for s_band in banddata:
            bandtype = s_band['type']

            band_on = s_band['on']
            band_freq = s_band['freq']
            band_gain = s_band['gain']
            band_res = s_band['var']

            part = [True, band_on, band_freq, band_gain, band_res]

            if bandtype == 'low_pass': 
                data_LP = part
                data_auto[0] = bandnum
            if bandtype == 'low_shelf': 
                data_Lowshelf = part
                data_auto[1] = bandnum
            if bandtype == 'peak' and band_on: 
                for peaknum in range(4):
                    peakdata = data_Peaks[peaknum]
                    if peakdata[0] == False: 
                        data_Peaks[peaknum] = part
                        data_auto[2][peaknum] = bandnum
                        break
            if bandtype == 'high_shelf': 
                data_HighShelf = part
                data_auto[3] = bandnum
            if bandtype == 'high_pass': 
                data_HP = part
                data_auto[4] = bandnum
            bandnum += 1
        return data_LP, data_Lowshelf, data_Peaks, data_HighShelf, data_HP, data_auto

    # -------------------------------------------------- wave
    def wave_add(self, i_name, i_wavepoints, i_min, i_max):
        namegroup_add(self.cvpjdata, 'wave', i_name, {'range': [i_min,i_max],'points': i_wavepoints})

    def wave_get(self, i_name):
        return namegroup_get_a(self.cvpjdata, 'wave', i_name)

    def wave_list(self):
        return namegroup_list(self.cvpjdata, 'wave')

    # -------------------------------------------------- harmonics
    def harmonics_add(self, i_name, i_harmonics):
        namegroup_add(self.cvpjdata, 'harmonics', i_name, {'harmonics': i_harmonics})

    def harmonics_get(self, i_name):
        return namegroup_get_a(self.cvpjdata, 'harmonics', i_name)

    def harmonics_list(self):
        return namegroup_list(self.cvpjdata, 'harmonics')

    # -------------------------------------------------- wavetable
    def wavetable_add(self, i_name, i_wavenames, i_wavelocs, i_phase):
        wavedata = {}
        wavedata['ids'] = i_wavenames
        if i_wavelocs != None: wavedata['locs'] = i_wavelocs
        if i_phase != None: wavedata['phase'] = i_phase
        namegroup_add(self.cvpjdata, 'wavetable', i_name, wavedata)

    def wavetable_get(self, i_name):
        return namegroup_get_a(self.cvpjdata, 'wavetable', i_name)

    def wavetable_list(self):
        return namegroup_list(self.cvpjdata, 'wavetable')

    # -------------------------------------------------- wavetable

    def fileref_add(self, i_name, i_location):
        filerefdata = {}
        filerefdata['path'] = i_location
        namegroup_add(self.cvpjdata, 'file_ref', i_name, filerefdata)

    def fileref_get(self, i_name):
        return namegroup_get(self.cvpjdata, 'file_ref', i_name)

    # -------------------------------------------------- oscillator

    def osc_num_oscs(self, i_amount):
        self.cvpjdata['osc'] = [{} for _ in range(i_amount)]

    def osc_opparam_set(self, i_oscnum, i_name, i_value):
        self.cvpjdata['osc'][i_oscnum][i_name] = i_value

    def osc_op_getall(self, i_oscnum, i_name, i_value):
        if 'osc' in self.cvpjdata: return self.cvpjdata['osc']



    def oscdata_add(self, i_name, i_value):
        if 'osc_data' not in self.cvpjdata: self.cvpjdata['osc_data'] = {}
        self.cvpjdata['osc_data'][i_name] = i_value

    def oscdata_get(self, i_name):
        if i_name in self.cvpjdata['osc_data']:
            return self.cvpjdata['osc_data'][i_name]

    # -------------------------------------------------- dsf_import

    def param_dict_dataset_get(self, i_dict, dataset, catname, pluginname):
        paramlist = dataset.params_list(catname, pluginname)
        if paramlist:
            for param in paramlist:
                outval = data_values.nested_dict_get_value(i_dict, param.split('/'))
                self.param_add_dset(param, outval, dataset, catname, pluginname)

    def param_dict_dataset_set(self, dataset, catname, pluginname):
        paramlist = dataset.params_list(catname, pluginname)
        outdict = {}
        if paramlist:
            for param in paramlist:
                defparams = dataset.params_i_get(catname, pluginname, param)
                if not defparams[0]: outdata = self.param_get(param, defparams[2])[0]
                else: outdata = self.dataval_get(param, defparams[2])
                data_values.nested_dict_add_value(outdict, param.split('/'), outdata)
        return outdict

    # -------------------------------------------------- to_cvpj
    def to_cvpj(self, cvpj_l, pluginid):
        if 'plugins' not in cvpj_l: cvpj_l['plugins'] = {}
        cvpj_l['plugins'][pluginid] = self.cvpjdata
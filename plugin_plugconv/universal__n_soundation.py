# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

def get_freq(i_val):
    return 20 * 1000**i_val

def get_gain(i_val):
    return min((math.sqrt(i_val**1.15)*40)-20, 0)

def eq_calc_q(band_type, q_val):
    if band_type in ['low_pass', 'high_pass']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, 0.5)
    elif band_type in ['low_shelf', 'high_shelf']:
        q_val = q_val*math.log(162)
        q_val = 0.1 * math.exp(q_val)
    else:
        q_val = q_val*math.log(162)
        #q_val = 0.1 * math.exp(q_val)
        q_val = xtramath.logpowmul(q_val, -1) if q_val != 0 else q_val
    return q_val

autotune_chords = {
    0: [0,2,4,5,7,9,11],
    1: [0,4,7],
    2: [0,2,4,7,9],
    3: [0,2,3,5,7,8,10],
    4: [0,2,3,5,7,8,11],
    5: [0,2,3,5,7,9,11],
    6: [0,3,7],
    7: [0,3,5,7,10],
    9: [0,3,5,6,7,10],
    10: [0,1,2,3,4,5,6,7,8,9,10,11]
}


class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-soundation', None, 'soundation'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'com.soundation.filter':
            print('[plug-conv] Soundation to Universal: Filter:',pluginid)
            filter_cutoff = plugin_obj.params.get('cutoff', 0).value
            filter_resonance = plugin_obj.params.get('resonance', 0).value
            filter_mode = plugin_obj.params.get('mode', 0).value

            plugin_obj.replace('universal', 'filter')
            plugin_obj.filter.on = True
            plugin_obj.filter.type = 'low_pass' if filter_mode else 'high_pass'
            plugin_obj.filter.freq = get_freq(filter_cutoff)
            plugin_obj.filter.q = filter_resonance
            return 1

        if plugin_obj.plugin_subtype == 'com.soundation.parametric-eq':
            print('[plug-conv] Soundation to Universal: EQ > EQ 8-Limited:',pluginid)

            #HP
            filter_obj = plugin_obj.named_filter_add('high_pass')
            filter_obj.type = 'high_pass'
            filter_obj.on = bool(plugin_obj.params.get('hpf_enable', 0).value)
            filter_obj.freq = get_freq(plugin_obj.params.get('hpf_freq', 0).value)
            filter_obj.gain = (plugin_obj.params.get('hpf_gain', 0).value-0.5)*40
            filter_obj.q = eq_calc_q('hpf', plugin_obj.params.get('hpf_q', 0).value)

            #low_shelf
            filter_obj = plugin_obj.named_filter_add('low_shelf')
            filter_obj.type = 'low_shelf'
            filter_obj.on = bool(plugin_obj.params.get('lowshelf_enable', 0).value)
            filter_obj.freq = get_freq(plugin_obj.params.get('lowshelf_freq', 0).value)
            filter_obj.gain = (plugin_obj.params.get('lowshelf_gain', 0).value-0.5)*40
            filter_obj.q = eq_calc_q('lowshelf', plugin_obj.params.get('lowshelf_q', 0).value)

            #peak
            for peak_num in range(4):
                peak_txt = 'peak'+str(peak_num+1)
                cvpj_txt = 'peak_'+str(peak_num+1)
                filter_obj = plugin_obj.named_filter_add(cvpj_txt)
                filter_obj.type = 'peak'
                filter_obj.on = bool(plugin_obj.params.get(peak_txt+'_enable', 0).value)
                filter_obj.freq = get_freq(plugin_obj.params.get(peak_txt+'_freq', 0).value)
                filter_obj.gain = (plugin_obj.params.get(peak_txt+'_gain', 0).value-0.5)*40
                filter_obj.q = eq_calc_q('peak', plugin_obj.params.get(peak_txt+'_q', 0).value)

            #low_shelf
            filter_obj = plugin_obj.named_filter_add('high_shelf')
            filter_obj.type = 'high_shelf'
            filter_obj.on = bool(plugin_obj.params.get('highshelf_enable', 0).value)
            filter_obj.freq = get_freq(plugin_obj.params.get('highshelf_freq', 0).value)
            filter_obj.gain = (plugin_obj.params.get('highshelf_gain', 0).value-0.5)*40
            filter_obj.q = eq_calc_q('highshelf', plugin_obj.params.get('highshelf_q', 0).value)

            #low_shelf
            filter_obj = plugin_obj.named_filter_add('low_shelf')
            filter_obj.type = 'low_pass'
            filter_obj.on = bool(plugin_obj.params.get('lpf_enable', 0).value)
            filter_obj.freq = get_freq(plugin_obj.params.get('lpf_freq', 0).value)
            filter_obj.gain = (plugin_obj.params.get('lpf_gain', 0).value-0.5)*40
            filter_obj.q = eq_calc_q('lpf', plugin_obj.params.get('lpf_q', 0).value)


            master_gain = plugin_obj.params.get('master_gain', 0).value
            master_gain = (master_gain-0.5)*40

            plugin_obj.replace('universal', 'eq-8limited')

            plugin_obj.params.add('gain_out', master_gain, 'float')
            return 1
            
        if plugin_obj.plugin_subtype == 'com.soundation.compressor':
            print('[plug-conv] Soundation to Universal: Compressor:',pluginid)

            comp_attack = plugin_obj.params.get('attack', 0).value
            comp_ratio = plugin_obj.params.get('ratio', 0).value
            comp_release = plugin_obj.params.get('release', 0).value
            comp_threshold = plugin_obj.params.get('threshold', 0).value

            comp_gain = plugin_obj.params.get('gain', 0).value

            comp_attack = ((comp_attack**2)*200)/1000
            comp_release = (comp_release**2)*5
            comp_threshold = (comp_threshold*50)-50
            comp_gain = get_gain(comp_gain)
            comp_ratio = 1/(max(1-(comp_ratio**0.25), 0.0001))

            plugin_obj.replace('universal', 'compressor')
            plugin_obj.params.add('ratio', comp_ratio, 'float')
            plugin_obj.params.add('threshold', comp_threshold, 'float')
            plugin_obj.params.add('attack', comp_attack, 'float')
            plugin_obj.params.add('release', comp_release, 'float')
            plugin_obj.params.add('postgain', comp_gain, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'com.soundation.degrader':
            print('[plug-conv] Soundation to Universal: Degrader > Bitcrush:',pluginid)
            crush_bits = plugin_obj.params.get('reduction', 0).value
            crush_rate = plugin_obj.params.get('rate', 0).value
            crush_mix = plugin_obj.params.get('mix', 0).value
            crush_bits = 48-int(crush_bits*50)
            crush_rate = xtramath.between_from_one(44100, 1000, crush_rate**0.1)
            plugin_obj.replace('universal', 'bitcrush')
            plugin_obj.params.add('bits', crush_bits, 'float')
            plugin_obj.params.add('freq', crush_rate, 'float')
            plugin_obj.params_slot.add('wet', crush_mix, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'com.soundation.delay':
            print("[plug-conv] Soundation to Universal: Delay:",pluginid)
            feedback = plugin_obj.params.get('feedback', 0).value
            feedback_filter = plugin_obj.params.get('feedback_filter', 0).value
            timeBpmSync = plugin_obj.params.get('timeBpmSync', 0).value
            timeL = plugin_obj.params.get('timeL', 0).value
            timeLSynced = plugin_obj.params.get('timeLSynced', 0).value
            timeR = plugin_obj.params.get('timeR', 0).value
            timeRSynced = plugin_obj.params.get('timeRSynced', 0).value
            wet = plugin_obj.params.get('wet', 0).value
            dry = plugin_obj.params.get('dry', 0).value

            plugin_obj.replace('universal', 'delay')
            plugin_obj.datavals.add('traits', ['stereo'])
            plugin_obj.datavals.add('traits_seperated', ['time'])
            plugin_obj.datavals.add('c_fb', feedback)

            for n in range(2):
                timing_obj = plugin_obj.timing_add('left' if not n else 'right')
                if timeBpmSync: timing_obj.set_steps(16/(1/(timeLSynced if not n else timeRSynced)), convproj_obj)
                else: timing_obj.set_seconds(timeL if not n else timeR)

            plugin_obj.datavals.add('cut_high', get_freq(feedback_filter**0.5))
            plugin_obj.params_slot.add('wet', xtramath.wetdry(wet, dry), 'float')
            return 1
            
        if plugin_obj.plugin_subtype == 'com.soundation.limiter':
            print("[plug-conv] Soundation to Universal: Delay:",pluginid)

            comp_attack = plugin_obj.params.get('attack', 0).value
            comp_gain = plugin_obj.params.get('gain', 0).value
            comp_release = plugin_obj.params.get('release', 0).value
            comp_threshold = plugin_obj.params.get('threshold', 0).value

            comp_attack = ((comp_attack**2)*200)/1000
            comp_release = (comp_release**2)*5
            comp_gain = get_gain(comp_gain)
            comp_threshold = ((1-comp_threshold)**3)*50

            plugin_obj.replace('universal', 'limiter')
            plugin_obj.params.add('attack', comp_attack, 'float')
            plugin_obj.params.add('release', comp_release, 'float')
            plugin_obj.params.add('postgain', comp_gain, 'float')
            plugin_obj.params.add('threshold', comp_threshold, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'com.soundation.pitch-correction':
            tune_amount = plugin_obj.params.get('amount', 0).value
            tune_glide = plugin_obj.params.get('glide', 0).value
            tune_key = int(plugin_obj.params.get('key', 0).value)
            tune_mode = int(plugin_obj.params.get('mode', 0).value)
            plugin_obj.replace('universal', 'autotune')

            if tune_mode in autotune_chords:
                for p_key in autotune_chords[tune_mode]: 
                    plugin_obj.params.add('key_on_'+str((p_key+tune_key)%12), True, 'bool')

        return 2
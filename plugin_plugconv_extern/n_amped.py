# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern

import struct
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_nullbytegroup
from functions_plugin_ext import params_os_vital
from objects_convproj import wave
from functions import errorprint
from functions import xtramath
import math

wavestore = {}


def eg_vital(plugin_obj, starttxt, env_num, params_vital):
    eg_A = plugin_obj.params.get(starttxt+"A", 0).value*10
    eg_D = plugin_obj.params.get(starttxt+"D", 0).value*10
    eg_S = plugin_obj.params.get(starttxt+"S", 0).value
    eg_R = plugin_obj.params.get(starttxt+"R", 0).value*10

    eg_curveA = plugin_obj.params.get(starttxt+"curveA", 0).value
    eg_curveD = plugin_obj.params.get(starttxt+"curveD", 0).value
    eg_curveR = plugin_obj.params.get(starttxt+"curveR", 0).value

    params_vital.setvalue_timed('env_'+str(env_num)+'_attack', eg_A)
    params_vital.setvalue_timed('env_'+str(env_num)+'_decay', eg_D)
    params_vital.setvalue('env_'+str(env_num)+'_sustain', eg_S)
    params_vital.setvalue_timed('env_'+str(env_num)+'_release', eg_R)

    params_vital.setvalue('env_'+str(env_num)+'_attack_power', eg_curveA)
    params_vital.setvalue('env_'+str(env_num)+'_decay_power', eg_curveD)
    params_vital.setvalue('env_'+str(env_num)+'_release_power', eg_curveR)

def lfo_vital(plugin_obj, starttxt, lfo_num, params_vital, randomnum):
    lfo_wave = int(plugin_obj.params.get(starttxt+"wave", 0).value)
    lfo_rate = plugin_obj.params.get(starttxt+"rate", 0).value
    lfo_amp = plugin_obj.params.get(starttxt+"amp", 0).value
    lfo_delay = plugin_obj.params.get(starttxt+"delay", 0).value

    vidlfo_txt = 'lfo_'+str(lfo_num)

    params_vital.setvalue(vidlfo_txt+'_sync', 0)
    params_vital.setvalue(vidlfo_txt+'_frequency', -math.log2(1/lfo_rate) if lfo_rate else 0)

    is_random = False

    params_vital.setvalue(vidlfo_txt+'_delay_time', lfo_delay)

    if lfo_wave == 0: params_vital.set_lfo(lfo_num, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], True, 'Sine')
    if lfo_wave == 1: params_vital.set_lfo(lfo_num, 3, [0.0,1.0,0.5,0.0,1.0,1.0], [0.0,0.0,0.0], False, 'Triangle')
    if lfo_wave == 2: params_vital.set_lfo(lfo_num, 5, [0.0,1.0,0.0,0.0,0.5,0.0,0.5,1.0,1.0,1.0], [0.0,0.0,0.0,0.0,0.0], False, 'Square')
    if lfo_wave == 3: params_vital.set_lfo(lfo_num, 2, [0.0,1.0,1.0,0.0], [0.0,0.0], False, 'Saw')
    if lfo_wave == 4:
        is_random = True
        random_txt = 'random_'+str(randomnum)
        params_vital.setvalue(random_txt+'_style', 1)
        params_vital.setvalue(random_txt+'_sync', 0)
        params_vital.setvalue(random_txt+'_frequency', -math.log2(1/(lfo_rate)) if lfo_rate else 0)
    return randomnum, is_random, lfo_amp

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['native-amped', None], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype, plugtransform):
        global loaded_plugtransform
        global plugts_obj
        global wavestore

        if plugin_obj.plugin_subtype == 'VoltMini' and params_os_vital.checksupport(extplugtype):
            params_vital = params_os_vital.vital_data(plugin_obj)

            osc_active = plugin_obj.params.get("part/1/osc/1/active", 0).value
            osc_wave = int(plugin_obj.params.get("part/1/osc/1/wave", 0).value)
            osc_active = plugin_obj.params.get("part/1/osc/1/active", 0).value
            osc_unison = plugin_obj.params.get("part/1/osc/1/unison", 0).value
            osc_detune = plugin_obj.params.get("part/1/osc/1/detune", 0).value
            osc_octave = plugin_obj.params.get("part/1/osc/1/octave", 0).value
            osc_coarse = plugin_obj.params.get("part/1/osc/1/coarse", 0).value
            osc_fine = plugin_obj.params.get("part/1/osc/1/fine", 0).value
            osc_shape = plugin_obj.params.get("part/1/osc/1/shape", 0).value
            osc_gain = plugin_obj.params.get("part/1/osc/1/gain", 0).value
            osc_pan = plugin_obj.params.get("part/1/osc/1/pan", 0).value

            filt_bypass = plugin_obj.params.get("part/1/filter/bypass", 0).value
            filt_fc = plugin_obj.params.get("part/1/filter/fc", 0).value
            filt_Q = plugin_obj.params.get("part/1/filter/Q", 0).value

            params_vital.setvalue('filter_1_resonance', filt_Q/5)
            params_vital.setvalue('filter_1_cutoff', filt_fc*130)
            params_vital.setvalue('filter_1_on', int(not filt_bypass))

            eg_vital(plugin_obj, 'part/1/eg/4/', 1, params_vital)
            eg_vital(plugin_obj, 'part/1/eg/3/', 2, params_vital)
            filt_lvl = plugin_obj.params.get("part/1/eg/3/L", 0).value
            params_vital.set_modulation(1, 'env_2', 'filter_1_cutoff', filt_lvl, 0, 0, 0, 0)
            eg_vital(plugin_obj, 'part/1/eg/1/', 3, params_vital)
            modlvl = plugin_obj.params.get("part/1/eg/1/L", 0).value
            mod_pitch = plugin_obj.params.get("part/1/eg/1/pitch", 0).value
            mod_shape = plugin_obj.params.get("part/1/eg/1/shape", 0).value
            mod_detune = plugin_obj.params.get("part/1/eg/1/detune", 0).value
            params_vital.set_modulation(2, 'env_3', 'osc_1_transpose', (mod_pitch*modlvl)/4, 0, 1, 0, 0)
            params_vital.set_modulation(3, 'env_3', 'osc_1_wave_frame', mod_shape*modlvl, 0, 1, 0, 0)
            params_vital.set_modulation(4, 'env_3', 'osc_1_unison_detune', (mod_detune*modlvl)*2, 0, 1, 0, 0)

            randomnum = 1
            randomnum, is_random, lfo_amp = lfo_vital(plugin_obj, 'part/1/lfo/1/', 1, params_vital, randomnum)
            wlfo_pitch = plugin_obj.params.get("part/1/lfo/1/pitch", 0).value
            wlfo_shape = plugin_obj.params.get("part/1/lfo/1/shape", 0).value
            wlfo_gain = plugin_obj.params.get("part/1/lfo/1/gain", 0).value
            wlfo_pan = plugin_obj.params.get("part/1/lfo/1/pan", 0).value

            modfrom = 'lfo_1' if not is_random else 'random_'+str(randomnum)
            params_vital.set_modulation(5, modfrom, 'osc_1_transpose', (wlfo_pitch)/4, 0, 1, 0, 0)
            params_vital.set_modulation(6, modfrom, 'osc_1_level', wlfo_gain/2, 0, 1, 0, 0)
            params_vital.set_modulation(7, modfrom, 'osc_1_pan', wlfo_pan, 0, 1, 0, 0)
            params_vital.set_modulation(8, modfrom, 'osc_1_wave_frame', wlfo_shape, 0, 1, 0, 0)

            if is_random: randomnum += 1

            randomnum, is_random, lfo_amp = lfo_vital(plugin_obj, 'part/1/lfo/3/', 2, params_vital, randomnum)
            modfrom = 'lfo_2' if not is_random else 'random_'+str(randomnum)
            params_vital.set_modulation(9, modfrom, 'filter_1_cutoff', lfo_amp, 0, 0, 0, 0)

            waveids = []
            if osc_wave == 0:
                wave_obj = wave.cvpj_wave()
                wave_obj.set_numpoints(2048)
                wave_obj.add_wave('sine', 0, 1, 1)
                params_vital.replacewave(0, wave_obj.get_wave(2048))

            wavesize = 1028
            rangeval = 128
            wavestorep = []

            if osc_wave == 1:
                if 'triangle' not in wavestore:
                    print('[amped to vital] Generating triangle wavetable...')
                    for n in range(rangeval):
                        wavedata = [(x/wavesize) for x in range(wavesize)]
                        pos = n/rangeval
                        endpos = 1-(pos/1.1)
                        new_wavedata = []
                        for n in wavedata:
                            x = (n/endpos)+0.75
                            x = (abs((x*2)%(2)-1)-0.5)*2 if n<endpos else 0
                            new_wavedata.append(x)
                        wavestorep.append(new_wavedata)
                    wavestore['triangle'] = wavestorep

            if osc_wave == 2:
                if 'square' not in wavestore:
                    print('[amped to vital] Generating square wavetable...')
                    for n in range(rangeval):
                        wavedata = [(x/wavesize) for x in range(wavesize)]
                        new_wavedata = [(1 if f>(((n/rangeval)/2.2)+0.5) else -1) for f in wavedata]
                        wavestorep.append(new_wavedata)
                    wavestore['square'] = wavestorep

            if osc_wave == 3:
                if 'saw' not in wavestore:
                    print('[amped to vital] Generating saw wavetable...')
                    for n in range(rangeval):
                        pos = n/rangeval
                        wavedata = [(x/wavesize) for x in range(wavesize)]
                        wavedata = [x*(1+(pos*2)) for x in wavedata]
                        new_wavedata = [(x-math.floor(x)-0.5)*2 for x in wavedata]
                        wavestorep.append(new_wavedata)
                    wavestore['saw'] = wavestorep

            if osc_wave in [1, 2, 3]:
                if osc_wave == 1: wavetdata = wavestore['triangle']
                if osc_wave == 2: wavetdata = wavestore['square']
                if osc_wave == 3: wavetdata = wavestore['saw']
                for n, wavedata in enumerate(wavetdata):
                    wave_obj = plugin_obj.wave_add(str(n))
                    wave_obj.set_all(wavedata)
                    waveids.append(str(n))

                wavetable_obj = plugin_obj.wavetable_add('shape')
                wavetable_obj.ids = waveids
                wavetable_obj.locs = None
                params_vital.importcvpj_wavetable(0, 1, 'shape')

            params_vital.setvalue('osc_1_on', osc_active)
            params_vital.setvalue('osc_1_level', osc_gain/2)
            params_vital.setvalue('osc_1_pan', (osc_pan-0.5)*2)
            params_vital.setvalue('osc_1_unison_detune', osc_detune*5)
            if osc_detune: params_vital.setvalue('osc_1_unison_voices', osc_unison)
            params_vital.setvalue('osc_1_transpose',(osc_octave*12)+osc_coarse)
            params_vital.setvalue('osc_1_tune', osc_fine/100)
            params_vital.setvalue('osc_1_wave_frame', osc_shape)

            params_vital.to_cvpj_any(convproj_obj, extplugtype)
            return True

        if plugin_obj.plugin_subtype == 'Reverb' and 'vst2' in extplugtype:
            if plugin_vst2.check_exists('id', 1279878002):
                print("[plug-conv] Amped to VST2: Reverb > Castello Reverb:",pluginid)
                plugtransform.transform('./data_plugts/amped_vst2.pltr', 'vst2_reverb', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1279878002, 'chunk', 
                    data_nullbytegroup.make(
                        [{'ui_size': ''}, 
                        {
                        'mix': str(plugtransform.get_storedval('mix')), 
                        'size': str(plugtransform.get_storedval('fb')), 
                        'brightness': str(plugtransform.get_storedval('lpf'))
                        }]), 
                    None)
                return True
            else: errorprint.printerr('ext_notfound', ['VST2', 'Castello Reverb'])

        elif plugin_obj.plugin_subtype == 'Distortion' and 'vst2' in extplugtype:
            distmode = plugin_obj.params.get('mode', 0).value
            boost = plugin_obj.params.get('boost', 0).value
            mix = plugin_obj.params.get('mix', 0).value

            if distmode in [0,1,4,5,6,7,8]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Amped to VST2: Density > Airwindows Density:',pluginid)
                    p_density = 0.2+(boost*0.3)
                    p_outlvl = 1-(boost*(0.3 if distmode != 5 else 0.2))
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1685219702, 'chunk', struct.pack('<ffff', p_density, 0, p_outlvl, 1), 0)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Density [Airwindows]'])

            if distmode in [2,3]:
                if plugin_vst2.check_exists('id', 1685219702):
                    print('[plug-conv] Amped to VST2: Distortion > Airwindows Drive:',pluginid)
                    p_drive = [0.6,0.8,1][int(boost)]
                    plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1685219702, 'chunk', struct.pack('<ffff', p_drive, 0, 0.5, 1), 0)
                else: errorprint.printerr('ext_notfound', ['VST2', 'Drive [Airwindows]'])

            plugin_obj.params_slot.add('wet', mix, 'float')

        elif plugin_obj.plugin_subtype == 'CompressorMini':
            if plugin_vst2.check_exists('id', 1886745457):
                print('[plug-conv] Amped to VST2: CompressorMini > Airwindows PurestSquish:',pluginid)
                plugtransform.transform('./data_plugts/amped_vst2.pltr', 'vst2_compressormini', convproj_obj, plugin_obj, pluginid, dv_config)
                plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1886745457, 'chunk', struct.pack('<ffff', plugtransform.get_storedval('squash'), 0, 1, 1), 0)
            else: errorprint.printerr('ext_notfound', ['VST2', 'PurestSquish [Airwindows]'])

        else: return False
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import data_bytes
from functions import xtramath
from functions import note_data
from objects_params import fx_delay

import math

delaytab = [[32, 1, ''], [28, 1, ''], [24, 1, ''], [20, 1, ''], [16, 1, ''], [12, 1, ''], [10, 1, ''], [8, 1, ''], [6, 1, ''], [5, 1, ''], [4, 1, ''], [3, 1, ''], [2, 1, ''], [1, 1, ''], [1, 1, 'd'], [1, 1, ''], [1, 1, 't'], [1, 2, 'd'], [1, 2, ''], [1, 2, 't'], [1, 4, 'd'], [1, 4, ''], [1, 4, 't'], [1, 8, 'd'], [1, 8, ''], [1, 8, 't'], [1, 16, 'd'], [1, 16, ''], [1, 16, 't'], [1, 32, 'd'], [1, 32, ''], [1, 32, 't'], [1, 64, 'd'], [1, 64, ''], [1, 64, 't']]

def djeq_calc_gain(lvl): return math.log2((lvl*2)**13.8) if lvl else -100 

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-tracktion', None, 'waveform_edit'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == '1bandEq':
            print('[plug-conv] Waveform to Universal: 1bandEq > Filter:',pluginid)
            band_freq = plugin_obj.params.get('freq', 30).value
            band_shape = plugin_obj.params.get('shape', 0).value
            band_q = plugin_obj.params.get('q', 0).value
            band_gain = plugin_obj.params.get('gain', 0).value
            band_slope = plugin_obj.params.get('slope', 0).value

            if band_shape == 0: band_shape = 'high_pass'
            if band_shape == 1: band_shape = 'low_shelf'
            if band_shape == 2: band_shape = 'peak'
            if band_shape == 5: band_shape = 'high_shelf'
            if band_shape == 6: band_shape = 'low_pass'

            plugin_obj.replace('universal', 'filter')
            plugin_obj.filter.on = True
            plugin_obj.filter.type = band_shape
            plugin_obj.filter.freq = note_data.note_to_freq(band_freq-72)
            plugin_obj.filter.q = band_q
            plugin_obj.filter.gain = band_gain
            plugin_obj.filter.slope = band_slope
            return 1

        if plugin_obj.plugin_subtype == '3bandEq':
            print('[plug-conv] Waveform to Universal: 3bandEq > EQ Bands:',pluginid)
            freq1 = plugin_obj.params.get('freq1', 43.34996032714844).value
            freq2 = plugin_obj.params.get('freq2', 90.23263549804688).value
            freq3 = plugin_obj.params.get('freq3', 119.2130889892578).value
            gain1 = plugin_obj.params.get('gain1', 0).value
            gain2 = plugin_obj.params.get('gain2', 0).value
            gain3 = plugin_obj.params.get('gain3', 0).value

            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'low_shelf'
            filter_obj.freq = note_data.note_to_freq(freq1-72)
            filter_obj.gain = gain1

            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'peak'
            filter_obj.freq = note_data.note_to_freq(freq2-72)
            filter_obj.gain = gain2

            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'high_shelf'
            filter_obj.freq = note_data.note_to_freq(freq3-72)
            filter_obj.gain = gain3
            plugin_obj.replace('universal', 'eq-bands')

        if plugin_obj.plugin_subtype == '8bandEq':
            print('[plug-conv] Waveform to Universal: 8bandEq > EQ Bands:',pluginid)
            eq_bands = []
            for num in range(8):
                eqnumtxt = str(num+1)
                eq_part = []
                for typenum in range(2):
                    typename = ['lm', 'rs'][typenum]
                    band_enable = int(plugin_obj.params.get("enable"+eqnumtxt+typename, 0).value)
                    band_freq = plugin_obj.params.get("freq"+eqnumtxt+typename, 25).value
                    band_gain = plugin_obj.params.get("gain"+eqnumtxt+typename, 0).value
                    band_q = plugin_obj.params.get("q"+eqnumtxt+typename, 1).value
                    band_shape = plugin_obj.params.get("shape"+eqnumtxt+typename, 1).value
                    band_slope = plugin_obj.params.get("slope"+eqnumtxt+typename, 12).value

                    if band_shape == 0: band_shape = 'low_pass'
                    if band_shape == 1: band_shape = 'low_shelf'
                    if band_shape == 2: band_shape = 'peak'
                    if band_shape == 3: band_shape = 'band_pass'
                    if band_shape == 4: band_shape = 'band_stop'
                    if band_shape == 5: band_shape = 'high_shelf'
                    if band_shape == 6: band_shape = 'high_pass'

                    if not typenum: filter_obj = plugin_obj.eq_add()
                    else: filter_obj = plugin_obj.named_eq_add('alt')

                    filter_obj.on = bool(band_enable)
                    filter_obj.freq = band_freq
                    filter_obj.gain = band_gain
                    filter_obj.q = band_q
                    filter_obj.type = band_shape
                    filter_obj.slope = band_slope

            eq_mode = plugin_obj.params.get("mode", 0).value
            cvpj_eq_mode = ['normal', 'l_r', 'm_s'][eq_mode]

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.datavals.add('mode', cvpj_eq_mode)
            return 1

        if plugin_obj.plugin_subtype == 'comp':
            print("[plug-conv] Waveform to Universal: Compressor:",pluginid)
            plugtransform.transform('./data_plugts/waveform_univ.pltr', 'comp', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'gate':
            print("[plug-conv] Waveform to Universal: Gate:",pluginid)
            plugtransform.transform('./data_plugts/waveform_univ.pltr', 'gate', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'limiter':
            print("[plug-conv] Waveform to Universal: Limiter:",pluginid)
            plugtransform.transform('./data_plugts/waveform_univ.pltr', 'limiter', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1
            
        if plugin_obj.plugin_subtype == 'djeq':
            print('[plug-conv] Waveform to Universal: DJ EQ > 3 Band EQ:',pluginid)
            freq1 = plugin_obj.params.get('freq1', 59.213096618652344).value
            freq2 = plugin_obj.params.get('freq2', 99.07624816894531).value
            bass = plugin_obj.params.get('bass', 1).value/1.5
            mid = plugin_obj.params.get('mid', 1).value/1.5
            treble = plugin_obj.params.get('treble', 1).value/1.5

            plugin_obj.replace('universal', 'eq-3band')
            plugin_obj.params.add('low_gain', djeq_calc_gain(bass), 'float')
            plugin_obj.params.add('mid_gain', djeq_calc_gain(mid), 'float')
            plugin_obj.params.add('high_gain', djeq_calc_gain(treble), 'float')
            plugin_obj.params.add('lowmid_freq', note_data.note_to_freq(freq1-72), 'float')
            plugin_obj.params.add('midhigh_freq', note_data.note_to_freq(freq2-72), 'float')
            return 1

        if plugin_obj.plugin_subtype == 'pitchShifter':
            print("[plug-conv] Waveform to Universal: Pitch Shifter:",pluginid)
            pitchmod = plugin_obj.params.get('semitonesUp', 0).value
            plugin_obj.replace('universal', 'pitchshift')
            plugin_obj.params.add('pitch', pitchmod, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'stereoDelay':
            print("[plug-conv] Waveform to Universal: Stereo Delay > Delay:",pluginid)
            crossL = plugin_obj.params.get('crossL', 0).value
            crossR = plugin_obj.params.get('crossR', 0).value
            delaySyncOffL = plugin_obj.params.get('delaySyncOffL', 0).value
            delaySyncOffR = plugin_obj.params.get('delaySyncOffR', 0).value
            delaySyncOnL = plugin_obj.params.get('delaySyncOnL', 0).value
            delaySyncOnR = plugin_obj.params.get('delaySyncOnR', 0).value
            feedbackL = plugin_obj.params.get('feedbackL', 0).value
            feedbackR = plugin_obj.params.get('feedbackR', 0).value
            highcut = plugin_obj.params.get('highcut', 0).value
            lowcut = plugin_obj.params.get('lowcut', 0).value
            mix = plugin_obj.params.get('mix', 0).value
            mixLock = plugin_obj.params.get('mixLock', 0).value
            panL = plugin_obj.params.get('panL', 0).value
            panR = plugin_obj.params.get('panR', 0).value
            volL = plugin_obj.params.get('volL', 0).value
            volR = plugin_obj.params.get('volR', 0).value
            plugin_obj.params.debugtxt()

            sync = int(plugin_obj.params.get('sync', 0).value)

            delay_obj = fx_delay.fx_delay()

            time_m = []
            time_m.append(delay_obj.timing_add(0))
            time_m.append(delay_obj.timing_add(1))
            if not sync:
                time_m[0].set_seconds(delaySyncOffL/1000)
                time_m[1].set_seconds(delaySyncOffR/1000)
            else:
                for n, x in enumerate([delaySyncOnL, delaySyncOnR]):
                    if x < 35: 
                        num, denum, stxt = delaytab[x]
                        time_m[n].set_frac(num, denum, stxt, convproj_obj)

            delay_obj.feedback_pan[0] = panL
            delay_obj.feedback_pan[1] = panR
            delay_obj.feedback[0] = feedbackL/100
            delay_obj.feedback[0] = feedbackR/100
            delay_obj.feedback_cross[0] = crossL/100
            delay_obj.feedback_cross[0] = crossR/100
            delay_obj.cut_low = lowcut
            delay_obj.cut_high = highcut
            plugin_obj.fxdata_add(None, mix)

        return 2
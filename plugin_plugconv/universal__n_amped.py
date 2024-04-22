# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath
from objects_params import fx_delay

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        
        if plugin_obj.plugin_subtype == 'Delay':
            print('[plug-conv] Amped to Universal: Delay > Delay:',pluginid)
            p_time = plugin_obj.params.get('time', 0).value
            p_fb = plugin_obj.params.get('fb', 0).value
            p_mix = plugin_obj.params.get('mix', 0.5).value
            p_offset = plugin_obj.params.get('offset', 0).value

            delay_obj = fx_delay.fx_delay()
            delay_obj.feedback_first = False
            timing_obj = delay_obj.timing_add(0)
            timing_obj.set_seconds(p_time)
            delay_obj.feedback[0] = p_fb
            delay_obj.stereo_offset = p_offset
            plugin_obj = delay_obj.to_cvpj(convproj_obj, pluginid)
            plugin_obj.params_slot.add('wet', p_mix, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'Vibrato':
            print('[plug-conv] Amped to Universal: Vibrato > Vibrato:',pluginid)
            p_delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0).value
            p_delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0).value
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_vibrato', convproj_obj, plugin_obj, pluginid, dv_config)
            lfo_obj = plugin_obj.lfo_add('amount')
            lfo_obj.time.set_hz(p_delayLfoRateHz)
            lfo_obj.amount = p_delayLfoDepth
            return 1

        if plugin_obj.plugin_subtype == 'Tremolo':
            print('[plug-conv] Amped to Universal: Tremolo > AutoPan:',pluginid)
            p_lfoARateHz = plugin_obj.params.get('lfoARateHz', 0).value
            p_lfoADepth = plugin_obj.params.get('lfoADepth', 0).value
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_autopan', convproj_obj, plugin_obj, pluginid, dv_config)
            lfo_obj = plugin_obj.lfo_add('amount')
            lfo_obj.time.set_hz(p_lfoARateHz)
            lfo_obj.amount = p_lfoADepth
            return 1

        if plugin_obj.plugin_subtype == 'BitCrusher':
            print('[plug-conv] Amped to Universal: BitCrusher > BitCrusher:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_bitcrush', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Phaser':
            print('[plug-conv] Amped to Universal: Phaser > Phaser:',pluginid)
            p_rate = plugin_obj.params.get('rate', 0).value
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_phaser', convproj_obj, plugin_obj, pluginid, dv_config)
            lfo_obj = plugin_obj.lfo_add('phaser')
            lfo_obj.time.set_hz(p_rate)
            return 1

        if plugin_obj.plugin_subtype == 'LimiterMini':
            print('[plug-conv] Amped to Universal: LimiterMini > Limiter:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_limitermini', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Limiter':
            print('[plug-conv] Amped to Universal: LimiterMini > Limiter:',pluginid)
            plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
            plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
            plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
            plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
            filter_mode = plugin_obj.params.get('filterMode', 0).value
            convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])
            if filter_mode == 0: plugin_obj.filter.type = 'low_pass'
            if filter_mode == 1: plugin_obj.filter.type = 'high_pass'
            if filter_mode == 2: plugin_obj.filter.type = 'band_pass'
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_limiter', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Gate':
            print('[plug-conv] Amped to Universal: Gate > Gate:',pluginid)
            plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
            plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
            plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
            plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
            filter_mode = plugin_obj.params.get('filterMode', 0).value
            convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])
            if filter_mode == 0: plugin_obj.filter.type = 'low_pass'
            if filter_mode == 1: plugin_obj.filter.type = 'high_pass'
            if filter_mode == 2: plugin_obj.filter.type = 'band_pass'
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_gate', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype in ['Compressor', 'Expander']:
            comp_detect_mode = plugin_obj.params.get('detectMode', 0).value
            comp_circuit_mode = plugin_obj.params.get('circuitMode', 0).value

            plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
            plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
            plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
            plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
            filter_mode = plugin_obj.params.get('filterMode', 0).value
            convproj_obj.automation.move(['plugin', pluginid, 'filterGainDB'], ['filter', pluginid, 'gain'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterFrequency'], ['filter', pluginid, 'freq'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterQ'], ['filter', pluginid, 'q'])
            convproj_obj.automation.move(['plugin', pluginid, 'filterActive'], ['filter', pluginid, 'on'])
            if filter_mode == 0: plugin_obj.filter.type = 'low_pass'
            if filter_mode == 1: plugin_obj.filter.type = 'high_pass'
            if filter_mode == 2: plugin_obj.filter.type = 'band_pass'

            if plugin_obj.plugin_subtype == 'Compressor':
                print('[plug-conv] Amped to Universal: Compressor > Compressor:',pluginid)
                plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_compressor', convproj_obj, plugin_obj, pluginid, dv_config)

            if plugin_obj.plugin_subtype == 'Expander':
                print('[plug-conv] Amped to Universal: Expander > Expander:',pluginid)
                plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_expander', convproj_obj, plugin_obj, pluginid, dv_config)

        if plugin_obj.plugin_subtype == 'Flanger':
            print('[plug-conv] Amped to Universal: Flanger > Flanger:',pluginid)
            p_delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0).value
            p_delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0).value
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_flanger', convproj_obj, plugin_obj, pluginid, dv_config)
            lfo_obj = plugin_obj.lfo_add('flanger')
            lfo_obj.time.set_hz(p_delayLfoRateHz)
            lfo_obj.amount = p_delayLfoDepth

        if plugin_obj.plugin_subtype == 'Equalizer':
            print('[plug-conv] Amped to Universal: Equalizer > EQ Bands:',pluginid)
            filter_obj, filter_id = plugin_obj.eq_add()
            filter_obj.type = 'high_pass'
            filter_obj.freq = plugin_obj.params.get("hpfreq", 20).value
            convproj_obj.automation.move(['plugin', pluginid, "hpfreq"], ['n_filter', pluginid, filter_id, 'freq'])

            filter_obj, filter_id = plugin_obj.eq_add()
            filter_obj.type = 'peak'
            filter_obj.freq = plugin_obj.params.get("peakfreq", 2000).value
            filter_obj.gain = plugin_obj.params.get("peakgain", 0).value
            filter_obj.q = plugin_obj.params.get("peakq", 1).value
            convproj_obj.automation.move(['plugin', pluginid, "peakfreq"], ['n_filter', pluginid, filter_id, 'freq'])
            convproj_obj.automation.move(['plugin', pluginid, "peakgain"], ['n_filter', pluginid, filter_id, 'gain'])
            convproj_obj.automation.move(['plugin', pluginid, "peakq"], ['n_filter', pluginid, filter_id, 'q'])

            filter_obj, filter_id = plugin_obj.eq_add()
            filter_obj.type = 'low_pass'
            filter_obj.freq = plugin_obj.params.get("lpfreq", 10000).value
            convproj_obj.automation.move(['plugin', pluginid, "lpfreq"], ['n_filter', pluginid, filter_id, 'freq'])

            plugin_obj.replace('universal', 'eq-bands')

        if plugin_obj.plugin_subtype == 'EqualizerPro':
            print('[plug-conv] Amped to Universal: EqualizerPro > EQ Bands:',pluginid)
            master_gain = plugin_obj.params.get("postGain", 0).value

            for band_num in range(8):
                str_band_num = str(band_num+1)
                starttxt = 'filter/'+str_band_num+'/'
                cvpj_band_txt = 'main/'+str_band_num+'/'

                filter_obj, filter_id = plugin_obj.eq_add()
                filter_obj.on = int(plugin_obj.params.get(starttxt+"active", 0).value)
                filter_obj.freq = plugin_obj.params.get(starttxt+"freq", 20).value
                filter_obj.q = plugin_obj.params.get(starttxt+"q", 0.5).value
                filter_obj.gain = plugin_obj.params.get(starttxt+"gain", 0).value

                band_type = plugin_obj.params.get(starttxt+"type", 0).value
                if band_type == 0: filter_obj.type = 'peak'
                if band_type == 2: filter_obj.type = 'low_pass'
                if band_type == 1: filter_obj.type = 'high_pass'
                if band_type == 3: filter_obj.type = 'low_shelf'
                if band_type == 4: filter_obj.type = 'high_shelf'

                convproj_obj.automation.move(['plugin', pluginid, starttxt+"active"], ['n_filter', pluginid, filter_id, 'on'])
                convproj_obj.automation.move(['plugin', pluginid, starttxt+"freq"], ['n_filter', pluginid, filter_id, 'freq'])
                convproj_obj.automation.move(['plugin', pluginid, starttxt+"gain"], ['n_filter', pluginid, filter_id, 'gain'])
                convproj_obj.automation.move(['plugin', pluginid, starttxt+"q"], ['n_filter', pluginid, filter_id, 'q'])

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.params.add('gain_out', master_gain, 'float')
            return 1

        return 2
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

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

            plugin_obj.replace('universal', 'delay')
            plugin_obj.datavals.add('traits', [])
            timing_obj = plugin_obj.timing_add('center')
            timing_obj.set_seconds(p_time)
            plugin_obj.datavals.add('c_fb', p_fb)
            plugin_obj.datavals.add('stereo_offset', p_offset)
            plugin_obj.params_slot.add('wet', p_mix, 'float')
            return 1

        if plugin_obj.plugin_subtype == 'Vibrato':
            print('[plug-conv] Amped to Universal: Vibrato > Vibrato:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_vibrato', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Tremolo':
            print('[plug-conv] Amped to Universal: Tremolo > AutoPan:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_autopan', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'BitCrusher':
            print('[plug-conv] Amped to Universal: BitCrusher > BitCrusher:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_bitcrush', convproj_obj, plugin_obj, pluginid, dv_config)
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
            if filter_mode == 0: plugin_obj.filter.type = 'low_pass'
            if filter_mode == 1: plugin_obj.filter.type = 'high_pass'
            if filter_mode == 2: plugin_obj.filter.type = 'band_pass'
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_gate', convproj_obj, plugin_obj, pluginid, dv_config)
            return 1

        if plugin_obj.plugin_subtype == 'Flanger':
            print('[plug-conv] Amped to Universal: Flanger > Flanger:',pluginid)
            plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_flanger', convproj_obj, plugin_obj, pluginid, dv_config)

        if plugin_obj.plugin_subtype in ['Compressor', 'Expander']:
            comp_detect_mode = plugin_obj.params.get('detectMode', 0).value
            comp_circuit_mode = plugin_obj.params.get('circuitMode', 0).value

            plugin_obj.filter.gain = plugin_obj.params.get('filterGainDB', 0).value
            plugin_obj.filter.freq = plugin_obj.params.get('filterFrequency', 44100).value
            plugin_obj.filter.q = plugin_obj.params.get('filterQ', 0).value
            plugin_obj.filter.on = plugin_obj.params.get('filterActive', False).value
            filter_mode = plugin_obj.params.get('filterMode', 0).value
            if filter_mode == 0: plugin_obj.filter.type = 'low_pass'
            if filter_mode == 1: plugin_obj.filter.type = 'high_pass'
            if filter_mode == 2: plugin_obj.filter.type = 'band_pass'

            if plugin_obj.plugin_subtype == 'Compressor':
                print('[plug-conv] Amped to Universal: Compressor > Compressor:',pluginid)
                plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_compressor', convproj_obj, plugin_obj, pluginid, dv_config)

            if plugin_obj.plugin_subtype == 'Expander':
                print('[plug-conv] Amped to Universal: Expander > Expander:',pluginid)
                plugtransform.transform('./data_plugts/amped_univ.pltr', 'univ_expander', convproj_obj, plugin_obj, pluginid, dv_config)

        if plugin_obj.plugin_subtype == 'Equalizer':
            print('[plug-conv] Amped to Universal: Equalizer > EQ Bands:',pluginid)
            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'high_pass'
            filter_obj.freq = plugin_obj.params.get("hpfreq", 20).value
            convproj_obj.automation.move_group(['plugin', pluginid], "hpfreq", "main/0/freq")

            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'peak'
            filter_obj.freq = plugin_obj.params.get("peakfreq", 2000).value
            filter_obj.gain = plugin_obj.params.get("peakgain", 0).value
            filter_obj.q = plugin_obj.params.get("peakq", 1).value
            convproj_obj.automation.move_group(['plugin', pluginid], "peakgain", "main/1/gain")
            convproj_obj.automation.move_group(['plugin', pluginid], "peakfreq", "main/1/freq")
            convproj_obj.automation.move_group(['plugin', pluginid], "peakq", "main/1/q")

            filter_obj = plugin_obj.eq_add()
            filter_obj.type = 'low_pass'
            filter_obj.freq = plugin_obj.params.get("lpfreq", 10000).value
            convproj_obj.automation.move_group(['plugin', pluginid], "lpfreq", "main/2/freq")

            plugin_obj.replace('universal', 'eq-bands')

        if plugin_obj.plugin_subtype == 'EqualizerPro':
            print('[plug-conv] Amped to Universal: EqualizerPro > EQ Bands:',pluginid)
            master_gain = plugin_obj.params.get("postGain", 0).value

            for band_num in range(8):
                str_band_num = str(band_num+1)
                starttxt = 'filter/'+str_band_num+'/'
                cvpj_band_txt = 'main/'+str_band_num+'/'

                filter_obj = plugin_obj.eq_add()
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

                convproj_obj.automation.move_group(['plugin', pluginid], starttxt+"active", cvpj_band_txt+"on")
                convproj_obj.automation.move_group(['plugin', pluginid], starttxt+"freq", cvpj_band_txt+"freq")
                convproj_obj.automation.move_group(['plugin', pluginid], starttxt+"gain", cvpj_band_txt+"gain")
                convproj_obj.automation.move_group(['plugin', pluginid], starttxt+"q", cvpj_band_txt+"q")

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.params.add('gain_out', master_gain, 'float')
            return 1

        return 2
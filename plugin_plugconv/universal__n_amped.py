# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import plugins
from functions import xtramath
from functions_tracks import auto_data

def bitcrush_freq(i_val):
    return 100*(2**(i_val*10))

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['universal', None, None], False, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        if plugintype[1] == 'Vibrato':
            delayLfoRateHz = cvpj_plugindata.param_get('delayLfoRateHz', 0)[0]
            delayLfoDepth = cvpj_plugindata.param_get('delayLfoDepth', 0)[0]
            cvpj_plugindata.replace('universal', 'vibrato')
            cvpj_plugindata.param_add('freq', delayLfoRateHz, 'float', 'freq')
            cvpj_plugindata.param_add('depth', delayLfoDepth, 'float', 'depth')

            auto_data.rename_plugparam(cvpj_l, pluginid, 'delayLfoRateHz', 'freq')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'delayLfoDepth', 'depth')
            return True

        if plugintype[1] == 'Tremolo':
            lfoARateHz = cvpj_plugindata.param_get('lfoARateHz', 0)[0]
            lfoADepth = cvpj_plugindata.param_get('lfoADepth', 0)[0]
            cvpj_plugindata.replace('universal', 'tremolo')
            cvpj_plugindata.param_add('freq', lfoARateHz, 'float', 'freq')
            cvpj_plugindata.param_add('depth', lfoADepth, 'float', 'depth')

            auto_data.rename_plugparam(cvpj_l, pluginid, 'lfoARateHz', 'freq')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'lfoADepth', 'depth')
            return True

        if plugintype[1] == 'BitCrusher':
            bitcrush_bits = cvpj_plugindata.param_get('bits', 0)[0]
            bitcrush_down = cvpj_plugindata.param_get('down', 0)[0]
            bitcrush_mix = cvpj_plugindata.param_get('mix', 0)[0]
            cvpj_plugindata.fxdata_add(None, bitcrush_mix)
            cvpj_plugindata.replace('universal', 'bitcrush')
            cvpj_plugindata.param_add('bits', bitcrush_bits, 'float', 'bits')
            cvpj_plugindata.param_add('freq', bitcrush_freq(bitcrush_down), 'float', 'freq')

            auto_data.move(cvpj_l, ['plugin', pluginid, 'mix'], ['slot', pluginid, 'wet'])
            auto_data.rename_plugparam(cvpj_l, pluginid, 'bits', 'bits')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'down', 'freq')
            auto_data.function_value(cvpj_l, ['plugin', pluginid, 'freq'], bitcrush_freq)
            return True

        if plugintype[1] in ['Compressor', 'Expander']:
            comp_pregain = cvpj_plugindata.param_get('preGainDB', 0)[0]
            comp_ratio = cvpj_plugindata.param_get('ratio', 0)[0]
            comp_threshold = cvpj_plugindata.param_get('thresholdDB', 0)[0]
            comp_attack = cvpj_plugindata.param_get('attackTimeMS', 0)[0]
            comp_release = cvpj_plugindata.param_get('releaseTimeMS', 0)[0]
            comp_postgain = cvpj_plugindata.param_get('postGainDB', 0)[0]
            comp_lookahead = cvpj_plugindata.param_get('lookaheadTimeMS', 0)[0]
            comp_knee = cvpj_plugindata.param_get('softKneeWidth', 0)[0]

            comp_detect_mode = cvpj_plugindata.param_get('detectMode', 0)[0]
            comp_circuit_mode = cvpj_plugindata.param_get('circuitMode', 0)[0]

            filter_gain = cvpj_plugindata.param_get('filterGainDB', 0)[0]
            filter_cutoff = cvpj_plugindata.param_get('filterFrequency', 44100)[0]
            filter_reso = cvpj_plugindata.param_get('filterQ', 0)[0]
            filter_enabled = cvpj_plugindata.param_get('filterActive', False)[0]
            filter_mode = cvpj_plugindata.param_get('filterMode', 0)[0]

            cvpj_filter_type = 'lowpass'
            if cvpj_filter_type == 'filterMode':
                if cvpj_filter_type == 0: filter_mode = 'lowpass'
                if cvpj_filter_type == 1: filter_mode = 'highpass'
                if cvpj_filter_type == 2: filter_mode = 'bandpass'

            cvpj_plugindata.filter_add(filter_enabled, filter_cutoff, filter_reso, cvpj_filter_type, None)

            if plugintype[1] == 'Compressor': cvpj_plugindata.replace('universal', 'compressor')
            if plugintype[1] == 'Expander': cvpj_plugindata.replace('universal', 'expander')

            cvpj_plugindata.param_add('pregain', comp_pregain, 'float', 'pregain')
            cvpj_plugindata.param_add('ratio', comp_ratio, 'float', 'ratio')
            cvpj_plugindata.param_add('threshold', comp_threshold, 'float', 'threshold')
            cvpj_plugindata.param_add('attack', comp_attack/1000, 'float', 'attack')
            cvpj_plugindata.param_add('release', comp_release/1000, 'float', 'release')
            cvpj_plugindata.param_add('postgain', comp_postgain, 'float', 'postgain')
            cvpj_plugindata.param_add('lookahead', comp_lookahead/1000, 'float', 'lookahead')
            cvpj_plugindata.param_add('knee', comp_knee*6, 'float', 'knee')

            auto_data.rename_plugparam(cvpj_l, pluginid, 'preGainDB', 'pregain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'ratio', 'ratio')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'thresholdDB', 'threshold')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'attackTimeMS', 'attack')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'releaseTimeMS', 'release')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'postGainDB', 'postgain')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'lookaheadTimeMS', 'lookahead')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'softKneeWidth', 'knee')

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'lookahead'], 0, 0.001)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'knee'], 0, 6)
            return True

        if plugintype[1] == 'EqualizerPro':
            master_gain = cvpj_plugindata.param_get("postGain", 0)[0]

            for band_num in range(8):
                str_band_num = str(band_num+1)
                starttxt = 'filter/'+str_band_num+'/'
                cvpj_band_txt = 'main/'+str_band_num+'/'

                band_active = int(cvpj_plugindata.param_get(starttxt+"active", 0)[0])
                band_freq = cvpj_plugindata.param_get(starttxt+"freq", 20)[0]
                band_gain = cvpj_plugindata.param_get(starttxt+"gain", 0)[0]
                band_q = cvpj_plugindata.param_get(starttxt+"q", 0.5)[0]
                band_type = cvpj_plugindata.param_get(starttxt+"type", 0)[0]

                if band_type == 0: cvpj_bandtype = 'peak'
                if band_type == 2: cvpj_bandtype = 'low_pass'
                if band_type == 1: cvpj_bandtype = 'high_pass'
                if band_type == 3: cvpj_bandtype = 'low_shelf'
                if band_type == 4: cvpj_bandtype = 'high_shelf'

                auto_data.rename_plugparam(cvpj_l, pluginid, starttxt+"active", cvpj_band_txt+"on")
                auto_data.rename_plugparam(cvpj_l, pluginid, starttxt+"freq", cvpj_band_txt+"freq")
                auto_data.rename_plugparam(cvpj_l, pluginid, starttxt+"gain", cvpj_band_txt+"gain")
                auto_data.rename_plugparam(cvpj_l, pluginid, starttxt+"q", cvpj_band_txt+"q")

                cvpj_plugindata.eqband_add(band_active, band_freq, cvpj_bandtype, None)
                cvpj_plugindata.eqband_add_param('gain', band_gain, None)
                cvpj_plugindata.eqband_add_param('q', band_q, None)

            cvpj_plugindata.replace('universal', 'eq-bands')
            cvpj_plugindata.param_add('gain_out', master_gain, 'float', 'Out Gain')
            return True


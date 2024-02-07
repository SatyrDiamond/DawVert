# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import math
from functions import xtramath

def bitcrush_freq(i_val):
    return 100*(2**(i_val*10))

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-amped', None, 'amped'], ['universal', None, None], False, False
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        if plugin_obj.plugin_subtype[1] == 'Vibrato':
            delayLfoRateHz = plugin_obj.params.get('delayLfoRateHz', 0).value
            delayLfoDepth = plugin_obj.params.get('delayLfoDepth', 0).value
            plugin_obj.replace('universal', 'vibrato')
            plugin_obj.params.add('freq', delayLfoRateHz, 'float')
            plugin_obj.params.add('depth', delayLfoDepth, 'float')
            convproj_obj.moveg_automation(['plugin', pluginid], 'delayLfoRateHz', 'freq')
            convproj_obj.moveg_automation(['plugin', pluginid], 'delayLfoDepth', 'depth')
            return 1

        if plugin_obj.plugin_subtype[1] == 'Tremolo':
            lfoARateHz = plugin_obj.params.get('lfoARateHz', 0).value
            lfoADepth = plugin_obj.params.get('lfoADepth', 0).value
            plugin_obj.replace('universal', 'tremolo')
            plugin_obj.params.add('freq', lfoARateHz, 'float')
            plugin_obj.params.add('depth', lfoADepth, 'float')
            convproj_obj.moveg_automation(['plugin', pluginid], 'lfoARateHz', 'freq')
            convproj_obj.moveg_automation(['plugin', pluginid], 'lfoADepth', 'depth')
            return 1

        if plugin_obj.plugin_subtype[1] == 'BitCrusher':
            bitcrush_bits = plugin_obj.params.get('bits', 0).value
            bitcrush_down = plugin_obj.params.get('down', 0).value
            bitcrush_mix = plugin_obj.params.get('mix', 0).value
            cvpj_plugindata.fxdata_add(None, bitcrush_mix)
            auto_data.move(cvpj_l, ['plugin', pluginid, 'mix'], ['slot', pluginid, 'wet'])
            plugin_obj.replace('universal', 'bitcrush')
            plugin_obj.params.add('bits', bitcrush_bits, 'float', 'bits')
            plugin_obj.params.add('freq', bitcrush_freq(bitcrush_down), 'float', 'freq')
            convproj_obj.moveg_automation(['plugin', pluginid], 'down', 'freq')
            convproj_obj.funcval_automation(['plugin', pluginid, 'freq'], bitcrush_freq)
            return 1

        if plugin_obj.plugin_subtype[1] in ['Compressor', 'Expander']:
            comp_pregain = plugin_obj.params.get('preGainDB', 0).value
            comp_ratio = plugin_obj.params.get('ratio', 0).value
            comp_threshold = plugin_obj.params.get('thresholdDB', 0).value
            comp_attack = plugin_obj.params.get('attackTimeMS', 0).value
            comp_release = plugin_obj.params.get('releaseTimeMS', 0).value
            comp_postgain = plugin_obj.params.get('postGainDB', 0).value
            comp_lookahead = plugin_obj.params.get('lookaheadTimeMS', 0).value
            comp_knee = plugin_obj.params.get('softKneeWidth', 0).value

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

            if plugin_obj.plugin_subtype[1] == 'Compressor': plugin_obj.replace('universal', 'compressor')
            if plugin_obj.plugin_subtype[1] == 'Expander': plugin_obj.replace('universal', 'expander')

            plugin_obj.params.add('pregain', comp_pregain, 'float', 'pregain')
            plugin_obj.params.add('ratio', comp_ratio, 'float', 'ratio')
            plugin_obj.params.add('threshold', comp_threshold, 'float', 'threshold')
            plugin_obj.params.add('attack', comp_attack/1000, 'float', 'attack')
            plugin_obj.params.add('release', comp_release/1000, 'float', 'release')
            plugin_obj.params.add('postgain', comp_postgain, 'float', 'postgain')
            plugin_obj.params.add('lookahead', comp_lookahead/1000, 'float', 'lookahead')
            plugin_obj.params.add('knee', comp_knee*6, 'float', 'knee')

            convproj_obj.moveg_automation(['plugin', pluginid], 'preGainDB', 'pregain')
            convproj_obj.moveg_automation(['plugin', pluginid], 'ratio', 'ratio')
            convproj_obj.moveg_automation(['plugin', pluginid], 'thresholdDB', 'threshold')
            convproj_obj.moveg_automation(['plugin', pluginid], 'attackTimeMS', 'attack')
            convproj_obj.moveg_automation(['plugin', pluginid], 'releaseTimeMS', 'release')
            convproj_obj.moveg_automation(['plugin', pluginid], 'postGainDB', 'postgain')
            convproj_obj.moveg_automation(['plugin', pluginid], 'lookaheadTimeMS', 'lookahead')
            convproj_obj.moveg_automation(['plugin', pluginid], 'softKneeWidth', 'knee')

            convproj_obj.addmul_automation(['plugin', pluginid, 'attack'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'release'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'lookahead'], 0, 0.001)
            convproj_obj.addmul_automation(['plugin', pluginid, 'knee'], 0, 6)
            return 1

        if plugin_obj.plugin_subtype[1] == 'EqualizerPro':
            master_gain = plugin_obj.params.get("postGain", 0).value

            for band_num in range(8):
                str_band_num = str(band_num+1)
                starttxt = 'filter/'+str_band_num+'/'
                cvpj_band_txt = 'main/'+str_band_num+'/'

                band_active = int(plugin_obj.params.get(starttxt+"active", 0).value)
                band_freq = plugin_obj.params.get(starttxt+"freq", 20).value
                band_gain = plugin_obj.params.get(starttxt+"gain", 0).value
                band_q = plugin_obj.params.get(starttxt+"q", 0.5).value
                band_type = plugin_obj.params.get(starttxt+"type", 0).value

                if band_type == 0: cvpj_bandtype = 'peak'
                if band_type == 2: cvpj_bandtype = 'low_pass'
                if band_type == 1: cvpj_bandtype = 'high_pass'
                if band_type == 3: cvpj_bandtype = 'low_shelf'
                if band_type == 4: cvpj_bandtype = 'high_shelf'

                convproj_obj.moveg_automation(['plugin', pluginid], starttxt+"active", cvpj_band_txt+"on")
                convproj_obj.moveg_automation(['plugin', pluginid], starttxt+"freq", cvpj_band_txt+"freq")
                convproj_obj.moveg_automation(['plugin', pluginid], starttxt+"gain", cvpj_band_txt+"gain")
                convproj_obj.moveg_automation(['plugin', pluginid], starttxt+"q", cvpj_band_txt+"q")

                cvpj_plugindata.eqband_add(band_active, band_freq, cvpj_bandtype, None)
                cvpj_plugindata.eqband_add_param('gain', band_gain, None)
                cvpj_plugindata.eqband_add_param('q', band_q, None)

            plugin_obj.replace('universal', 'eq-bands')
            plugin_obj.params.add('gain_out', master_gain, 'float', 'Out Gain')
            return 1

        return 2

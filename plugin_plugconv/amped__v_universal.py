# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from functions_tracks import auto_data
import math
import plugin_plugconv

def bitcrush_freq(i_val):
    return (math.log(i_val / 100) / math.log(2))/10


class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-amped', None, 'amped'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()

        fx_on, fx_wet = cvpj_plugindata.fxdata_get()

        if plugintype[1] == 'vibrato':
            delayLfoRateHz = cvpj_plugindata.param_get('freq', 0)[0]
            delayLfoDepth = cvpj_plugindata.param_get('depth', 0)[0]

            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'delayLfoRateHz')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'depth', 'delayLfoDepth')

            cvpj_plugindata.replace('native-amped', 'Vibrato')
            cvpj_plugindata.param_add('delayLfoRateHz', delayLfoRateHz, 'float', '')
            cvpj_plugindata.param_add('delayLfoDepth', delayLfoDepth, 'float', '')
            return True

        if plugintype[1] == 'tremolo':
            lfoARateHz = cvpj_plugindata.param_get('freq', 0)[0]
            lfoADepth = cvpj_plugindata.param_get('depth', 0)[0]

            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'lfoARateHz')
            auto_data.rename_plugparam(cvpj_l, pluginid, 'depth', 'lfoADepth')

            cvpj_plugindata.replace('native-amped', 'Tremolo')
            cvpj_plugindata.param_add('lfoARateHz', lfoARateHz, 'float', '')
            cvpj_plugindata.param_add('lfoADepth', lfoADepth, 'float', '')
            return True

        if plugintype[1] == 'bitcrush':
            bitcrush_bits = cvpj_plugindata.param_get('bits', 0)[0]
            bitcrush_down = cvpj_plugindata.param_get('freq', 0)[0]

            cvpj_plugindata.fxdata_add(None, 1)

            auto_data.move(cvpj_l, ['slot', pluginid, 'wet'], ['plugin', pluginid, 'mix'])
            auto_data.rename_plugparam(cvpj_l, pluginid, 'freq', 'down')
            auto_data.function_value(cvpj_l, ['plugin', pluginid, 'down'], bitcrush_freq)

            cvpj_plugindata.replace('native-amped', 'BitCrusher')
            cvpj_plugindata.param_add_minmax('bits', bitcrush_bits, 'float', '', [2,16])
            cvpj_plugindata.param_add_minmax('down', bitcrush_freq(bitcrush_down), 'float', '', [0,1])
            cvpj_plugindata.param_add_minmax('mix', fx_wet, 'float', '', [0,1])

            return True

        if plugintype[1] in ['compressor', 'expander']:
            preGainDB = cvpj_plugindata.param_get('pregain', 0)[0]
            ratio = cvpj_plugindata.param_get('ratio', 0)[0]
            thresholdDB = cvpj_plugindata.param_get('threshold', 0)[0]
            attackTimeMS = cvpj_plugindata.param_get('attack', 0)[0]*1000
            releaseTimeMS = cvpj_plugindata.param_get('release', 0)[0]*1000
            postGainDB = cvpj_plugindata.param_get('postgain', 0)[0]
            lookaheadTimeMS = cvpj_plugindata.param_get('lookahead', 0)[0]*1000
            softKneeWidth = cvpj_plugindata.param_get('knee', 0)[0]/6

            detect_mode = cvpj_plugindata.dataval_get('detect_mode', 'rms')
            circuit_mode = cvpj_plugindata.dataval_get('circuit_mode', 'digital')

            detectMode = 1 if detect_mode == 'peak' else 0
            circuitMode = 1 if circuit_mode == 'analog' else 0

            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'attack'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'release'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'lookahead'], 0, 1000)
            auto_data.multiply(cvpj_l, ['plugin', pluginid, 'knee'], 0, 1/6)

            if plugintype[1] == 'compressor': 
                cvpj_plugindata.replace('native-amped', 'Compressor')
            if plugintype[1] == 'expander': 
                cvpj_plugindata.replace('native-amped', 'Expander')

            filt_enabled, filt_cutoff, filt_reso, filt_type, filt_subtype = cvpj_plugindata.filter_get()

            filterMode = 0
            if filt_type == 'lowpass': filterMode = 0
            if filt_type == 'highpass': filterMode = 1
            if filt_type == 'bandpass': filterMode = 2

            filterFrequency = filt_cutoff
            filterQ = filt_reso
            filterGainDB = cvpj_plugindata.dataval_get('filter_gain', 0)
            filterActive = int(filt_enabled)
            filterAudition = 0

            cvpj_plugindata.param_add('preGainDB', preGainDB, 'float', 'depth')
            cvpj_plugindata.param_add('ratio', ratio, 'float', 'depth')
            cvpj_plugindata.param_add('thresholdDB', thresholdDB, 'float', 'depth')
            cvpj_plugindata.param_add('attackTimeMS', attackTimeMS, 'float', 'depth')
            cvpj_plugindata.param_add('releaseTimeMS', releaseTimeMS, 'float', 'depth')
            cvpj_plugindata.param_add('postGainDB', postGainDB, 'float', 'depth')
            cvpj_plugindata.param_add('lookaheadTimeMS', lookaheadTimeMS, 'float', 'depth')
            cvpj_plugindata.param_add('softKneeWidth', softKneeWidth, 'float', 'depth')
            cvpj_plugindata.param_add('detectMode', detectMode, 'float', 'depth')
            cvpj_plugindata.param_add('circuitMode', circuitMode, 'float', 'depth')
            cvpj_plugindata.param_add('filterMode', filterMode, 'float', 'depth')
            cvpj_plugindata.param_add('filterFrequency', filterFrequency, 'float', 'depth')
            cvpj_plugindata.param_add('filterQ', filterQ, 'float', 'depth')
            cvpj_plugindata.param_add('filterGainDB', filterGainDB, 'float', 'depth')
            cvpj_plugindata.param_add('filterActive', filterActive, 'float', 'depth')
            cvpj_plugindata.param_add('filterAudition', filterAudition, 'float', 'depth')
            return True

        if plugintype[1] == 'eq-bands':
            master_gain = cvpj_plugindata.param_get("gain_out", 0)[0]

            cvpj_plugindata.replace('native-amped', 'EqualizerPro')

            cvpj_bands, reorder = cvpj_plugindata.eqband_get_limitnum(None, 8)
            for band_num in range(8):
                eqnumtxt = str(band_num+1)
                cvpj_band_txt = 'main/'+str(band_num)+'/'

                s_band = cvpj_bands[band_num]

                if s_band != None:
                    band_type = s_band['type']
                    band_on = float(s_band['on'])
                    band_freq = s_band['freq']
                    band_gain = s_band['gain'] if 'gain' in s_band else 0
                    band_res = s_band['q']

                    filtername = "filter/"+eqnumtxt+"/"

                    eq_bandtype = 0
                    if band_type == 'peak': eq_bandtype = 0
                    if band_type == 'low_pass': eq_bandtype = 2
                    if band_type == 'high_pass': eq_bandtype = 1
                    if band_type == 'low_shelf': eq_bandtype = 3
                    if band_type == 'high_shelf': eq_bandtype = 4

                    cvpj_plugindata.param_add(filtername+'active', band_on, 'float', '')
                    cvpj_plugindata.param_add(filtername+'freq', band_freq, 'float', '')
                    cvpj_plugindata.param_add(filtername+'gain', band_gain, 'float', '')
                    cvpj_plugindata.param_add(filtername+'type', eq_bandtype, 'float', '')
                    cvpj_plugindata.param_add(filtername+'q', band_res, 'float', '')

                    #auto_data.rename_plugparam(cvpj_l, pluginid, cvpj_band_txt+"on", filtername+"active")
                    #auto_data.rename_plugparam(cvpj_l, pluginid, cvpj_band_txt+"freq", filtername+"freq")
                    #auto_data.rename_plugparam(cvpj_l, pluginid, cvpj_band_txt+"gain", filtername+"gain")
                    #auto_data.rename_plugparam(cvpj_l, pluginid, cvpj_band_txt+"q", filtername+"q")

            cvpj_plugindata.param_add('postGain', master_gain, 'float', '')
            return True
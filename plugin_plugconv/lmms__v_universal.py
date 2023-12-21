# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import plugins
from functions import data_bytes
from functions import xtramath
from functions_tracks import auto_data

def getslope(band_data):
    outval = 0
    if 'slope' in band_data:
        i_val = band_data['slope']
        if i_val > 24: outval = 1
        if i_val > 48: outval = 2
    return outval

def getq(band_data):
    return band_data['q'] if 'q' in band_data else 1

def getgain(band_data):
    return band_data['gain'] if 'gain' in band_data else 0

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-lmms', None, 'lmms'], True, True
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()
        #print(plugintype[1])

        if plugintype[1] == 'eq-bands':
            cvpj_plugindata.replace('native-lmms', 'eq')

            data_LP, data_LS, data_Peaks, data_HS, data_HP, data_reorder = cvpj_plugindata.eqband_get_limited(None)

            if data_HP != None:
                cvpj_plugindata.param_add('HPactive', int(data_HP['on']), 'float', 'HPactive')
                cvpj_plugindata.param_add('HPfreq', data_HP['freq'], 'float', 'HPfreq')
                cvpj_plugindata.param_add('HPres', getq(data_HP), 'float', 'HPres')
                cvpj_plugindata.param_add('HP', getslope(data_HP), 'float', 'HP')
                
            if data_LS != None:
                cvpj_plugindata.param_add('Lowshelfactive', int(data_LS['on']), 'float', 'Lowshelfactive')
                cvpj_plugindata.param_add('LowShelffreq', data_LS['freq'], 'float', 'LowShelffreq')
                cvpj_plugindata.param_add('Lowshelfgain', getgain(data_LS), 'float', 'Lowshelfgain')
                cvpj_plugindata.param_add('LowShelfres', getq(data_LS), 'float', 'LowShelfres')
                
            for peak_num in range(4):
                if data_Peaks[peak_num] != None:
                    peak_txt = 'Peak'+str(peak_num+1)
                    data_peak = data_Peaks[peak_num]
                    qdata = getq(data_peak)

                    if qdata == 0: qdata = 1

                    cvpj_plugindata.param_add(peak_txt+'active', int(data_peak['on']), 'float', peak_txt+'active')
                    cvpj_plugindata.param_add(peak_txt+'freq', data_peak['freq'], 'float', peak_txt+'freq')
                    cvpj_plugindata.param_add(peak_txt+'gain', getgain(data_peak), 'float', peak_txt+'gain')
                    cvpj_plugindata.param_add(peak_txt+'bw', xtramath.logpowmul(qdata, -1), 'float', peak_txt+'res')

            if data_HS != None:
                cvpj_plugindata.param_add('Highshelfactive', int(data_HS['on']), 'float', 'Highshelfactive')
                cvpj_plugindata.param_add('Highshelffreq', data_HS['freq'], 'float', 'Highshelffreq')
                cvpj_plugindata.param_add('HighShelfgain', getgain(data_HS), 'float', 'HighShelfgain')
                cvpj_plugindata.param_add('HighShelfres', getq(data_HS), 'float', 'HighShelfres')
                
            if data_LP != None:
                cvpj_plugindata.param_add('LPactive', int(data_LP['on']), 'float', 'LPactive')
                cvpj_plugindata.param_add('LPfreq', data_LP['freq'], 'float', 'LPfreq')
                cvpj_plugindata.param_add('LPres', getq(data_LP), 'float', 'LPres')
                cvpj_plugindata.param_add('LP', getslope(data_LP), 'float', 'LP')
            return 0

        return 2
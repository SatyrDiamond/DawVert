# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import data_bytes
from functions import xtramath
import os

def getslope(slopeval):
    outval = 0
    if slopeval > 24: outval = 1
    if slopeval > 48: outval = 2
    return outval

def getq(band_data):
    return band_data['q'] if 'q' in band_data else 1

def getgain(band_data):
    return band_data['gain'] if 'gain' in band_data else 0

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['universal', None, None], ['native-lmms', None, 'lmms'], True, True
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json):
        #plugintype = cvpj_plugindata.type_get()

        if plugin_obj.plugin_subtype == 'synth-osc':
            samplefolder = extra_json['samplefolder']
            if plugin_obj.oscs:
                osc_obj = plugin_obj.oscs[0]
                if osc_obj.shape in ['square', 'triangle', 'triangle', 'pulse', 'saw', 'sine', 'custom_wave']:

                    plugin_obj.replace('native-lmms', 'tripleoscillator')
                    plugin_obj.params.add('coarse0', -12, 'int')
                    plugin_obj.params.add('finel0', 0, 'int')
                    plugin_obj.params.add('finer0', 0, 'int')
                    plugin_obj.params.add('pan0', 0, 'int')
                    plugin_obj.params.add('phoffset0', 0, 'int')
                    plugin_obj.params.add('stphdetun0', 0, 'int')
                    plugin_obj.params.add('vol0', 33, 'int')
                    plugin_obj.params.add('vol1', 0, 'int')
                    plugin_obj.params.add('vol2', 0, 'int')
                    plugin_obj.params.add('wavetype0', 0, 'int')
                    if osc_obj.shape == 'sine': plugin_obj.params.add('wavetype0', 0, 'int')
                    if osc_obj.shape == 'pulse': plugin_obj.params.add('wavetype0', 3, 'int')
                    if osc_obj.shape == 'square': plugin_obj.params.add('wavetype0', 3, 'int')
                    if osc_obj.shape == 'triangle': plugin_obj.params.add('wavetype0', 1, 'int')
                    if osc_obj.shape == 'saw': plugin_obj.params.add('wavetype0', 2, 'int')
                    if osc_obj.shape == 'custom_wave': 
                        plugin_obj.params.add('wavetype0', 7, 'int')
                        wave_path = os.path.join(samplefolder, pluginid+'_wave.wav')
                        wave_obj = plugin_obj.wave_get(osc_obj.name_id)
                        wave_obj.to_audio(wave_path)
                        convproj_obj.add_sampleref(pluginid+'_wave', wave_path)
                        plugin_obj.samplerefs['userwavefile0'] = pluginid+'_wave'
                    return 0

        return 2
        #    data_LP, data_LS, data_Peaks, data_HS, data_HP, data_reorder = cvpj_plugindata.eqband_get_limited(None)

        #    if data_HP != None:
        #        plugin_obj.params.add('HPactive', int(data_HP['on']), 'float', 'HPactive')
        #        plugin_obj.params.add('HPfreq', data_HP['freq'], 'float', 'HPfreq')
        #        plugin_obj.params.add('HPres', getq(data_HP), 'float', 'HPres')
        #        plugin_obj.params.add('HP', getslope(data_HP), 'float', 'HP')
        #    
        #    if data_LS != None:
        #        plugin_obj.params.add('Lowshelfactive', int(data_LS['on']), 'float', 'Lowshelfactive')
        #        plugin_obj.params.add('LowShelffreq', data_LS['freq'], 'float', 'LowShelffreq')
        #        plugin_obj.params.add('Lowshelfgain', getgain(data_LS), 'float', 'Lowshelfgain')
        #        plugin_obj.params.add('LowShelfres', getq(data_LS), 'float', 'LowShelfres')
        #
        #    for peak_num in range(4):
        #        if data_Peaks[peak_num] != None:
        #            peak_txt = 'Peak'+str(peak_num+1)
        #            data_peak = data_Peaks[peak_num]
        #            qdata = getq(data_peak)

        #            if qdata == 0: qdata = 1

        #            plugin_obj.params.add(peak_txt+'active', int(data_peak['on']), 'float', peak_txt+'active')
        #            plugin_obj.params.add(peak_txt+'freq', data_peak['freq'], 'float', peak_txt+'freq')
        #            plugin_obj.params.add(peak_txt+'gain', getgain(data_peak), 'float', peak_txt+'gain')
        #            plugin_obj.params.add(peak_txt+'bw', xtramath.logpowmul(qdata, -1), 'float', peak_txt+'res')

        #    if data_HS != None:
        #        plugin_obj.params.add('Highshelfactive', int(data_HS['on']), 'float', 'Highshelfactive')
        #        plugin_obj.params.add('Highshelffreq', data_HS['freq'], 'float', 'Highshelffreq')
        #        plugin_obj.params.add('HighShelfgain', getgain(data_HS), 'float', 'HighShelfgain')
        #        plugin_obj.params.add('HighShelfres', getq(data_HS), 'float', 'HighShelfres')
        #    
        #    if data_LP != None:
        #        plugin_obj.params.add('LPactive', int(data_LP['on']), 'float', 'LPactive')
        #        plugin_obj.params.add('LPfreq', data_LP['freq'], 'float', 'LPfreq')
        #        plugin_obj.params.add('LPres', getq(data_LP), 'float', 'LPres')
        #        plugin_obj.params.add('LP', getslope(data_LP), 'float', 'LP')
        #    return 0

        #return 2
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
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        #plugintype = cvpj_plugindata.type_get()

        if plugin_obj.plugin_subtype == 'synth-osc':
            samplefolder = dv_config.path_samples_generated

            if len(plugin_obj.oscs) == 1 and not plugin_obj.env_blocks_get_exists('vol')[0]:
                osc_obj = plugin_obj.oscs[0]

                if osc_obj.shape == 'square' and 'pulse_width' in osc_obj.params:
                    plugin_obj.replace('native-lmms', 'monstro')
                    plugin_obj.params.add('o1vol', 50, 'int')
                    plugin_obj.params.add('o2vol', 0, 'int')
                    plugin_obj.params.add('o3vol', 0, 'int')
                    plugin_obj.params.add('o1crs', -12, 'int')
                    plugin_obj.params.add('o1pw', osc_obj.params['pulse_width']*100, 'int')

                elif osc_obj.shape in ['triangle', 'pulse', 'saw', 'sine', 'custom_wave']:
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

        if plugin_obj.plugin_subtype == 'bitcrush':
            plugtransform.transform('./data_plugts/univ_lmms.pltr', 'bitcrush', convproj_obj, plugin_obj, pluginid, dv_config)
            return 0

        if plugin_obj.plugin_subtype == 'eq-8limited':
            fil_hp = plugin_obj.named_filter_get('high_pass')
            fil_ls = plugin_obj.named_filter_get('low_shelf')
            fil_p1 = plugin_obj.named_filter_get('peak_1')
            fil_p2 = plugin_obj.named_filter_get('peak_2')
            fil_p3 = plugin_obj.named_filter_get('peak_3')
            fil_p4 = plugin_obj.named_filter_get('peak_4')
            fil_hs = plugin_obj.named_filter_get('high_shelf')
            fil_lp = plugin_obj.named_filter_get('low_pass')

            plugin_obj.params.add('HPactive', int(fil_hp.on), 'float')
            plugin_obj.params.add('HPfreq', fil_hp.freq, 'float')
            plugin_obj.params.add('HPres', fil_hp.q, 'float')
            plugin_obj.params.add('HP', getslope(fil_hp.slope), 'float')

            plugin_obj.params.add('Lowshelfactive', int(fil_ls.on), 'float')
            plugin_obj.params.add('LowShelffreq', fil_ls.freq, 'float')
            plugin_obj.params.add('Lowshelfgain', fil_ls.gain, 'float')
            plugin_obj.params.add('LowShelfres', fil_ls.q, 'float')

            for peak_num in range(4):
                fil_p = plugin_obj.named_filter_get('peak_'+str(peak_num+1))
                peak_txt = 'peak'+str(peak_num+1)
                plugin_obj.params.add(peak_txt+'active', int(fil_p.on), 'float')
                plugin_obj.params.add(peak_txt+'freq', fil_p.freq, 'float')
                plugin_obj.params.add(peak_txt+'gain', fil_p.gain, 'float')
                plugin_obj.params.add(peak_txt+'res', fil_p.q**0.5, 'float')

            plugin_obj.params.add('Highshelfactive', int(fil_hs.on), 'float')
            plugin_obj.params.add('Highshelffreq', fil_hs.freq, 'float')
            plugin_obj.params.add('HighShelfgain', fil_hs.gain, 'float')
            plugin_obj.params.add('HighShelfres', fil_hs.q, 'float')

            plugin_obj.params.add('LPactive', int(fil_lp.on), 'float')
            plugin_obj.params.add('LPfreq', fil_lp.freq, 'float')
            plugin_obj.params.add('LPres', fil_lp.q, 'float')
            plugin_obj.params.add('LP', getslope(fil_lp.slope), 'float')
            return 0

        return 2

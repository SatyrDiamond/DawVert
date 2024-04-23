# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import os
import math
import bisect

from objects_convproj import wave

fl_voc_bandnums = [4,8,16,32,64,128]
als_voc_bandnums = [4,8,12,16,20,24,28,32,36,40]

def fl_to_freq(value): 
    preval = (math.log(value/10) / math.log(1000))
    return int((preval**2)*32768)

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-ableton', None, 'ableton'], ['native-flstudio', None, 'flp'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):
        
        if plugin_obj.plugin_subtype == 'Vocoder':  
            print('[plug-conv] Ableton to FL Studio: Vocoder > Fruity Vocoder:',pluginid)

            EnvelopeRate = plugin_obj.params.get('EnvelopeRate', 0).value
            EnvelopeRelease = plugin_obj.params.get('EnvelopeRelease', 0).value
            FormantShift = plugin_obj.params.get('FormantShift', 0).value
            FilterBandWidth = plugin_obj.params.get('FilterBandWidth', 0).value

            als_BandCount = als_voc_bandnums[int(plugin_obj.datavals.get('FilterBank/BandCount', 4))]
            band_lvls = [plugin_obj.datavals.get('FilterBank/BandLevel.'+str(n), 1) for n in range(als_BandCount)]
            fl_BandCount = fl_voc_bandnums[bisect.bisect_left(fl_voc_bandnums, als_BandCount)]

            if als_BandCount != fl_BandCount: band_lvls = wave.resizewave(band_lvls, fl_BandCount, True)

            plugin_obj.replace('native-flstudio', 'fruity vocoder')
            plugin_obj.datavals.add('bands', band_lvls)
            plugin_obj.params.add('env_att', int(EnvelopeRate), 'int')
            plugin_obj.params.add('env_rel', int(EnvelopeRelease), 'int')
            plugin_obj.params.add('freq_bandwidth', int(FilterBandWidth*200), 'int')
            plugin_obj.params.add('freq_formant', int(FormantShift*100), 'int')
            return 0

        return 2


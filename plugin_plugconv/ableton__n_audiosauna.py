# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import xtramath

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-audiosauna', None, 'audiosauna'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, plugtransform):

        if plugin_obj.plugin_subtype == 'fm':
            opdata = []
            for opnum in range(4):
                endtxt = str(opnum+1)
                adsr_obj = plugin_obj.env_asdr_get('op'+endtxt)
                frq = plugin_obj.params.get('frq'+endtxt, 0).value
                fine = plugin_obj.params.get('fine'+endtxt, 0).value
                opAmp = plugin_obj.params.get('opAmp'+endtxt, 0).value
                if env_decay == 0: env_decay = 30
                opdata.append([adsr_obj, frq, fine, opAmp])

            fmAlgorithm = plugin_obj.params.get('fmAlgorithm', 0).value+1
            plugin_obj.replace('native-ableton', 'Operator')
            oporder = [1,2,3,4]

            als_alg = 1
            if fmAlgorithm == 1: als_alg = 1
            if fmAlgorithm == 2: als_alg = 2
            if fmAlgorithm == 3: als_alg = 3
            if fmAlgorithm == 4: 
                als_alg = 3
                oporder = [1,4,2,3]
            if fmAlgorithm == 5: als_alg = 7
            if fmAlgorithm == 6: als_alg = 8
            if fmAlgorithm == 7: als_alg = 9
            if fmAlgorithm == 8: als_alg = 10

            plugin_obj.params.add('Globals/Algorithm', als_alg-1, 'float')

            for opnum in oporder:
                s_opdata = opdata[opnum-1]
                als_stxt = 'Operator.'+str(opnum-1)+'/'
                plugin_obj.params.add(als_stxt+'Envelope/AttackTime', s_opdata[0].attack*1000, 'float')
                plugin_obj.params.add(als_stxt+'Envelope/DecayTime', s_opdata[0].decay*1000, 'float')
                plugin_obj.params.add(als_stxt+'Envelope/SustainLevel', s_opdata[0].sustain, 'float')
                plugin_obj.params.add(als_stxt+'Volume', s_opdata[3]/100, 'float')
                plugin_obj.params.add(als_stxt+'IsOn', True, 'bool')

                outpitch = (s_opdata[1]+s_opdata[2])*12
                plugin_obj.params.add(als_stxt+'Tune/Coarse', int(outpitch)/12, 'float')
                #plugin_obj.params.add(als_stxt+'Tune/Fine', ((outpitch % 12)/12)*1000, 'float')
                plugin_obj.params.add(als_stxt+'Envelope/DecaySlope', 0, 'float')
                plugin_obj.params.add(als_stxt+'Envelope/ReleaseSlope', 0, 'float')

            return 0
        return 2
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

from functions import xtramath
from functions_tracks import auto_data

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-audiosauna', None, 'audiosauna'], ['native-ableton', None, 'ableton'], True, False
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json):
        plugintype = cvpj_plugindata.type_get()
        #print(plugintype[1])

        if plugintype[1] == 'fm':
            opdata = []
            for opnum in range(4):
                endtxt = str(opnum+1)
                env_predelay, env_attack, env_hold, env_decay, env_sustain, env_release, env_amount = cvpj_plugindata.asdr_env_get('op'+endtxt)
                frq = cvpj_plugindata.param_get('frq'+endtxt, 0)[0]
                fine = cvpj_plugindata.param_get('fine'+endtxt, 0)[0]
                opAmp = cvpj_plugindata.param_get('opAmp'+endtxt, 0)[0]
                if env_decay == 0: env_decay = 30
                opdata.append([env_attack, env_decay, env_sustain, frq, fine, opAmp])

            volume_env = cvpj_plugindata.asdr_env_get('volume')[0]
            fmAlgorithm = cvpj_plugindata.param_get('fmAlgorithm', 0)[0]+1

            cvpj_plugindata.replace('native-ableton', 'Operator')

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

            cvpj_plugindata.param_add('Globals/Algorithm', als_alg-1, 'float', "")

            for opnum in oporder:
                s_opdata = opdata[opnum-1]
                als_stxt = 'Operator.'+str(opnum-1)+'/'
                cvpj_plugindata.param_add(als_stxt+'Envelope/AttackTime', s_opdata[0]*1000, 'float', "")
                cvpj_plugindata.param_add(als_stxt+'Envelope/DecayTime', s_opdata[1]*1000, 'float', "")
                cvpj_plugindata.param_add(als_stxt+'Envelope/SustainLevel', s_opdata[2], 'float', "")
                cvpj_plugindata.param_add(als_stxt+'Volume', s_opdata[5]/100, 'float', "")
                cvpj_plugindata.param_add(als_stxt+'IsOn', True, 'bool', "")

                outpitch = (s_opdata[3]+s_opdata[4])*12

                cvpj_plugindata.param_add(als_stxt+'Tune/Coarse', int(outpitch)/12, 'float', "")
                #cvpj_plugindata.param_add(als_stxt+'Tune/Fine', ((outpitch % 12)/12)*1000, 'float', "")

                cvpj_plugindata.param_add(als_stxt+'Envelope/DecaySlope', 0, 'float', "")
                cvpj_plugindata.param_add(als_stxt+'Envelope/ReleaseSlope', 0, 'float', "")

            return 0

        return 2
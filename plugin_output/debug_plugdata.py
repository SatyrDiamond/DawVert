# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
from functions import plugins

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'debug_plugdata'
    def getshortname(self): return 'debug_plugdata'
    def gettype(self): return 'debug'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': 'debug',
        'track_lanes': 'debug',
        'placement_cut': 'debug',
        'placement_loop': 'debug',
        'track_nopl': 'debug',
        'auto_nopl': 'debug',
        'placement_audio_events': 'debug',
        'placement_audio_stretch': ['warp', 'rate']
        }
    def getsupportedplugformats(self): return ['vst2', 'vst3', 'clap', 'ladspa']
    def getsupportedplugins(self): return ['sampler:single', 'sampler:multi', 'sampler:slicer', 'soundfont2']
    def getfileextension(self): return 'nothing'
    def parse(self, convproj_json, output_file):
        cvpj_l = json.loads(convproj_json)

        if 'plugins' in cvpj_l:
            for pluginid in cvpj_l['plugins']:
                cvpj_plugindata = plugins.cvpj_plugin('cvpj', cvpj_l, pluginid)

                plugintype = cvpj_plugindata.type_get()
                print()
                print(pluginid,'-------------------------------',':'.join([str(x) for x in plugintype]))


                i_enabled, i_wet = cvpj_plugindata.fxdata_get()
                if i_enabled != True or i_wet != 1: print('\t\t FX Data:',i_enabled, i_wet)


                param_list = cvpj_plugindata.param_list()
                if param_list: 
                    print('\t\t Params:',', '.join(param_list))
                    for pid in param_list:
                        param_mm = cvpj_plugindata.param_get_minmax(pid, None)
                        #print(param_mm)
                        if param_mm[3] != None: 
                            if param_mm[0] < param_mm[3]: 
                                print(pid+': '+str(param_mm[0])+" is lower then "+str(param_mm[3]))
                        if param_mm[4] != None: 
                            if param_mm[0] > param_mm[4]: 
                                print(pid+': '+str(param_mm[0])+" is higher then "+str(param_mm[4]))


                dataval_list = cvpj_plugindata.dataval_list()
                if dataval_list: print('\t\t DataVals:',', '.join(dataval_list))


                asdr_env_list = cvpj_plugindata.asdr_env_list()
                if asdr_env_list: print('\t\t Env ASDR:',', '.join(asdr_env_list))


                env_points_list = cvpj_plugindata.env_points_list()
                if env_points_list: print('\t\t Env Points:',', '.join(env_points_list))


                env_blocks_list = cvpj_plugindata.env_blocks_list()
                if env_blocks_list: print('\t\t Env Blocks:',', '.join(env_blocks_list))


                plug_filter = cvpj_plugindata.filter_get()
                if plug_filter != (0, 44100, 0, None, None): print('\t\t Filter:',plug_filter)


                lfo_list = cvpj_plugindata.lfo_list()
                if lfo_list: print('\t\t LFOs:',', '.join(lfo_list))


                eqbands = cvpj_plugindata.eqband_get(None)
                if eqbands: print('\t\t EQ Bands:',len(eqbands))


                harmonics = cvpj_plugindata.harmonics_list()
                if harmonics: print('\t\t Harmonics:',len(harmonics))


                wavedata = cvpj_plugindata.wave_list()
                if wavedata: print('\t\t Waves:',len(wavedata))


                waveable = cvpj_plugindata.wavetable_list()
                if waveable: print('\t\t Wavetable:',len(waveable))




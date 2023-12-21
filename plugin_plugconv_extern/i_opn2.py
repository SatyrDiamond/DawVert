# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugdata import plugin_adlplug

def getparam(paramname):
    global cvpj_plugindata_g
    return cvpj_plugindata_g.param_get(paramname, 0)[0]

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['fm', 'opn2'], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        global cvpj_plugindata_g   
        cvpj_plugindata_g = cvpj_plugindata

        if extplugtype == 'vst2':
            print('[plug-conv] Converting OPN2 > OPNPlug:',pluginid)
            adlplug_data = plugin_adlplug.adlplug_data(cvpj_plugindata)
  
            adlplug_data.set_param("blank" ,0)    
            adlplug_data.set_param("note_offset" ,0)  
            adlplug_data.set_param("feedback" ,getparam('feedback'))  
            adlplug_data.set_param("algorithm" ,getparam('algorithm'))    
            adlplug_data.set_param("ams" ,getparam('ams'))    
            adlplug_data.set_param("fms" ,getparam('fms'))    
            adlplug_data.set_param("midi_velocity_offset" ,0) 
            adlplug_data.set_param("percussion_key_number" ,0)
    
            for opnum in range(4):  
                optxt = "op"+str(opnum+1)   
                adlplug_data.set_param(optxt+"detune" ,getparam(optxt+"_detune")) 
                adlplug_data.set_param(optxt+"fmul" ,getparam(optxt+"_freqmul"))  
                adlplug_data.set_param(optxt+"level" ,getparam(optxt+"_level"))   
                adlplug_data.set_param(optxt+"ratescale" ,getparam(optxt+"_ratescale"))   
                adlplug_data.set_param(optxt+"attack" ,getparam(optxt+"_env_attack")) 
                adlplug_data.set_param(optxt+"am" ,getparam(optxt+"_am")) 
                adlplug_data.set_param(optxt+"decay1" ,getparam(optxt+"_env_decay"))  
                adlplug_data.set_param(optxt+"decay2" ,getparam(optxt+"_env_decay2")) 
                adlplug_data.set_param(optxt+"sustain" ,getparam(optxt+"_env_sustain"))   
                adlplug_data.set_param(optxt+"release" ,getparam(optxt+"_env_release"))   
                adlplug_data.set_param(optxt+"ssgenable" ,getparam(optxt+"_ssg_enable"))  
                adlplug_data.set_param(optxt+"ssgwave" ,getparam(optxt+"_ssg_mode"))
    
            adlplug_data.set_param("delay_off_ms" ,120)   
            adlplug_data.set_param("delay_on_ms" ,486)    
            adlplug_data.set_param("bank" ,0) 
            adlplug_data.set_param("program" ,0)  
            adlplug_data.set_param("name" ,'DawVert')

            adlplug_data.add_selection(0, 0, 0)
            adlplug_data.opnplug_chip(0, 1, 0)
            adlplug_data.opnplug_global(0, getparam("lfo_enable"), getparam("lfo_frequency"))

            adlplug_data.add_common('DawVert', 0, 12.0)

            adlplug_data.opnplug_to_cvpj_vst2()
            return True
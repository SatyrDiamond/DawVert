# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugdata import plugin_adlplug

def getparam(paramname):
    global cvpj_plugindata_g
    return cvpj_plugindata_g.param_get(paramname, 0)[0]

opadltxt = ['m1', 'c1', 'm2', 'c2']

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['fm', 'opl2'], ['vst2'], None
    def convert(self, cvpj_l, pluginid, cvpj_plugindata, extra_json, extplugtype):
        global cvpj_plugindata_g   
        cvpj_plugindata_g = cvpj_plugindata

        if extplugtype == 'vst2':
            print('[plug-conv] Converting OPL2 to ADLplug:',pluginid)
            adlplug_data = plugin_adlplug.adlplug_data(cvpj_plugindata)

            adlplug_data.set_param("four_op" ,0)  
            adlplug_data.set_param("pseudo_four_op" ,0)   
            adlplug_data.set_param("blank" ,0)    
            adlplug_data.set_param("con12" ,getparam('fm'))
            adlplug_data.set_param("con34" ,0)    
            adlplug_data.set_param("note_offset1" ,0)
            adlplug_data.set_param("note_offset2" ,0)
            adlplug_data.set_param("fb12" ,getparam("feedback"))  
            adlplug_data.set_param("fb34" ,0) 
            adlplug_data.set_param("midi_velocity_offset" ,0) 
            adlplug_data.set_param("second_voice_detune" ,0)  
            adlplug_data.set_param("percussion_key_number" ,0)
    
            for opnplugopname, cvpjopname in [['m1', 'op1'], ['c1', 'op2'], ['m2', ''], ['c2', '']]:  
                adlplug_data.set_param(opnplugopname+"attack" ,(getparam(cvpjopname+"_env_attack")*-1)+15)    
                adlplug_data.set_param(opnplugopname+"decay" ,(getparam(cvpjopname+"_env_decay")*-1)+15)  
                adlplug_data.set_param(opnplugopname+"sustain" ,(getparam(cvpjopname+"_env_sustain")*-1)+15)
                adlplug_data.set_param(opnplugopname+"release" ,(getparam(cvpjopname+"_env_release")*-1)+15)  
                adlplug_data.set_param(opnplugopname+"level" ,(getparam(cvpjopname+"_level")*-1)+63)  
                adlplug_data.set_param(opnplugopname+"ksl" ,getparam(cvpjopname+"_ksl"))
                adlplug_data.set_param(opnplugopname+"fmul" ,getparam(cvpjopname+"_freqmul")) 
                adlplug_data.set_param(opnplugopname+"trem" ,getparam(cvpjopname+"_tremolo")) 
                adlplug_data.set_param(opnplugopname+"vib" ,getparam(cvpjopname+"_vibrato"))  
                adlplug_data.set_param(opnplugopname+"sus" ,getparam(cvpjopname+"_sustained"))
                adlplug_data.set_param(opnplugopname+"env" ,getparam(cvpjopname+"_ksr"))
                adlplug_data.set_param(opnplugopname+"wave" ,getparam(cvpjopname+"_waveform"))
    
            adlplug_data.set_param("delay_off_ms" ,160)   
            adlplug_data.set_param("delay_on_ms" ,386)    
            adlplug_data.set_param("bank" ,0) 
            adlplug_data.set_param("program" ,0)  
            adlplug_data.set_param("name" ,'')
    
            adlplug_data.add_selection(0, 0, 0)
            adlplug_data.adlplug_chip(2, 2, 0)
            adlplug_data.adlplug_global(0, getparam("tremolo_depth"), getparam("vibrato_depth"))
    
            adlplug_data.add_common('DawVert', 0, 1.0)
    
            adlplug_data.adlplug_to_cvpj_vst2()
            return True
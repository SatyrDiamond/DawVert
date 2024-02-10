# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugin_ext import params_os_adlplug

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['fm', 'opn2'], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):

        if extplugtype == 'vst2':
            print('[plug-conv] Converting OPN2 > OPNPlug:',pluginid)
            adlplug_data = params_os_adlplug.adlplug_data()
  
            opn_feedback = plugin_obj.params.get('feedback', 0).value
            opn_algorithm = plugin_obj.params.get('algorithm', 0).value
            opn_ams = plugin_obj.params.get('ams', 0).value
            opn_fms = plugin_obj.params.get('fms', 0).value

            adlplug_data.set_param("blank" ,0)    
            adlplug_data.set_param("note_offset" ,0)  
            adlplug_data.set_param("feedback" ,opn_feedback)  
            adlplug_data.set_param("algorithm" ,opn_algorithm)    
            adlplug_data.set_param("ams" ,opn_ams)    
            adlplug_data.set_param("fms" ,opn_fms)    
            adlplug_data.set_param("midi_velocity_offset" ,0) 
            adlplug_data.set_param("percussion_key_number" ,0)
    
            for opnum in range(4):  
                optxt = "op"+str(opnum+1)   
                opn_op_detune = plugin_obj.params.get(optxt+"_detune", 0).value
                opn_op_freqmul = plugin_obj.params.get(optxt+"_freqmul", 0).value
                opn_op_level = plugin_obj.params.get(optxt+"_level", 0).value
                opn_op_ratescale = plugin_obj.params.get(optxt+"_ratescale", 0).value
                opn_op_env_attack = plugin_obj.params.get(optxt+"_env_attack", 0).value
                opn_op_am = plugin_obj.params.get(optxt+"_am", 0).value
                opn_op_env_decay = plugin_obj.params.get(optxt+"_env_decay", 0).value
                opn_op_env_decay2 = plugin_obj.params.get(optxt+"_env_decay2", 0).value
                opn_op_env_sustain = plugin_obj.params.get(optxt+"_env_sustain", 0).value
                opn_op_env_release = plugin_obj.params.get(optxt+"_env_release", 0).value
                opn_op_ssg_enable = plugin_obj.params.get(optxt+"_ssg_enable", 0).value
                opn_op_ssg_mode = plugin_obj.params.get(optxt+"_ssg_mode", 0).value

                adlplug_data.set_param(optxt+"detune" ,opn_op_detune) 
                adlplug_data.set_param(optxt+"fmul" ,opn_op_freqmul)  
                adlplug_data.set_param(optxt+"level" ,opn_op_level)   
                adlplug_data.set_param(optxt+"ratescale" ,opn_op_ratescale)   
                adlplug_data.set_param(optxt+"attack" ,opn_op_env_attack) 
                adlplug_data.set_param(optxt+"am" ,opn_op_am) 
                adlplug_data.set_param(optxt+"decay1" ,opn_op_env_decay)  
                adlplug_data.set_param(optxt+"decay2" ,opn_op_env_decay2) 
                adlplug_data.set_param(optxt+"sustain" ,opn_op_env_sustain)   
                adlplug_data.set_param(optxt+"release" ,opn_op_env_release)   
                adlplug_data.set_param(optxt+"ssgenable" ,opn_op_ssg_enable)  
                adlplug_data.set_param(optxt+"ssgwave" ,opn_op_ssg_mode)
    
            adlplug_data.set_param("delay_off_ms" ,120)   
            adlplug_data.set_param("delay_on_ms" ,486)    
            adlplug_data.set_param("bank" ,0) 
            adlplug_data.set_param("program" ,0)  
            adlplug_data.set_param("name" ,'DawVert')

            opn_lfo_enable = plugin_obj.params.get('lfo_enable', 0).value
            opn_lfo_frequency = plugin_obj.params.get('lfo_frequency', 0).value

            adlplug_data.add_selection(0, 0, 0)
            adlplug_data.opnplug_chip(0, 1, 0)
            adlplug_data.opnplug_global(0, opn_lfo_enable, opn_lfo_frequency)

            adlplug_data.add_common('DawVert', 0, 12.0)

            adlplug_data.opnplug_to_cvpj_vst2(convproj_obj, plugin_obj)
            return True
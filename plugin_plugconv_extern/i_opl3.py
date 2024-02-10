# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv_extern
from functions_plugin_ext import params_os_adlplug

opadltxt = ['m1', 'c1', 'm2', 'c2']

class plugconv(plugin_plugconv_extern.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv_ext'
    def getplugconvinfo(self): return ['fm', 'opl3'], ['vst2'], None
    def convert(self, convproj_obj, plugin_obj, pluginid, extra_json, extplugtype):

        if extplugtype == 'vst2':
            print('[plug-conv] Converting OPL3 to ADLplug:',pluginid)
            adlplug_data = params_os_adlplug.adlplug_data()

            opl_con_12 = plugin_obj.params.get('con_12', 0).value
            opl_con_34 = plugin_obj.params.get('con_34', 0).value
            opl_feedback_12 = plugin_obj.params.get('feedback_12', 0).value
            opl_feedback_34 = plugin_obj.params.get('feedback_34', 0).value

            adlplug_data.set_param("four_op" ,1)  
            adlplug_data.set_param("pseudo_four_op" ,0)   
            adlplug_data.set_param("blank" ,0)    
            adlplug_data.set_param("con12" ,opl_con_12)
            adlplug_data.set_param("con34" ,opl_con_34)
            adlplug_data.set_param("note_offset1" ,0) 
            adlplug_data.set_param("note_offset2" ,0) 
            adlplug_data.set_param("fb12" ,opl_feedback_12)
            adlplug_data.set_param("fb34" ,opl_feedback_34)
            adlplug_data.set_param("midi_velocity_offset" ,0) 
            adlplug_data.set_param("second_voice_detune" ,0)  
            adlplug_data.set_param("percussion_key_number" ,0)
    
            for opnplugopname, cvpjopname in [['m1', 'op1'], ['c1', 'op2'], ['m2', 'op3'], ['c2', 'op4']]:
                opl_op_attack = plugin_obj.params.get(cvpjopname+"_env_attack", 0).value
                opl_op_decay = plugin_obj.params.get(cvpjopname+"_env_decay", 0).value
                opl_op_sustain = plugin_obj.params.get(cvpjopname+"_env_sustain", 0).value
                opl_op_release = plugin_obj.params.get(cvpjopname+"_env_release", 0).value
                opl_op_level = plugin_obj.params.get(cvpjopname+"_level", 0).value
                opl_op_ksl = plugin_obj.params.get(cvpjopname+"_ksl", 0).value
                opl_op_fmul = plugin_obj.params.get(cvpjopname+"_freqmul", 0).value
                opl_op_trem = plugin_obj.params.get(cvpjopname+"_tremolo", 0).value
                opl_op_vib = plugin_obj.params.get(cvpjopname+"_vibrato", 0).value
                opl_op_sus = plugin_obj.params.get(cvpjopname+"_sustained", 0).value
                opl_op_env = plugin_obj.params.get(cvpjopname+"_ksr", 0).value
                opl_op_wave = plugin_obj.params.get(cvpjopname+"_waveform", 0).value

                adlplug_data.set_param(opnplugopname+"attack" ,(opl_op_attack*-1)+15)    
                adlplug_data.set_param(opnplugopname+"decay" ,(opl_op_decay*-1)+15)  
                adlplug_data.set_param(opnplugopname+"sustain" ,(opl_op_sustain*-1)+15)
                adlplug_data.set_param(opnplugopname+"release" ,(opl_op_release*-1)+15)  
                adlplug_data.set_param(opnplugopname+"level" ,(opl_op_level*-1)+63)  
                adlplug_data.set_param(opnplugopname+"ksl" ,opl_op_ksl)
                adlplug_data.set_param(opnplugopname+"fmul" ,opl_op_fmul) 
                adlplug_data.set_param(opnplugopname+"trem" ,opl_op_trem) 
                adlplug_data.set_param(opnplugopname+"vib" ,opl_op_vib)  
                adlplug_data.set_param(opnplugopname+"sus" ,opl_op_sus)
                adlplug_data.set_param(opnplugopname+"env" ,opl_op_env)
                adlplug_data.set_param(opnplugopname+"wave" ,opl_op_wave)
    
            adlplug_data.set_param("delay_off_ms" ,160)   
            adlplug_data.set_param("delay_on_ms" ,386)    
            adlplug_data.set_param("bank" ,0) 
            adlplug_data.set_param("program" ,0)  
            adlplug_data.set_param("name" ,'')
    
            opl_tremolo_depth = plugin_obj.params.get('tremolo_depth', 0).value
            opl_vibrato_depth = plugin_obj.params.get('vibrato_depth', 0).value

            adlplug_data.add_selection(0, 0, 0)
            adlplug_data.adlplug_chip(2, 2, 1)
            adlplug_data.adlplug_global(0, opl_tremolo_depth, opl_vibrato_depth)
    
            adlplug_data.add_common('DawVert', 0, 1.0)

            adlplug_data.adlplug_to_cvpj_vst2(convproj_obj, plugin_obj)
            return True
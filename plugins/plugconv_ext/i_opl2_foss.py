# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import extpluglog
from functions_plugin_ext import plugin_vst2

opadltxt = ['m1', 'c1', 'm2', 'c2']

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv_ext'
	def get_prop(self, in_dict): 
		in_dict['in_plugin'] = ['chip', 'fm', 'opl2']
		in_dict['ext_formats'] = ['vst2']
		in_dict['plugincat'] = ['foss']
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config, extplugtype):
		from functions_plugin_ext import params_os_adlplug

		if 'vst2' in extplugtype:
			extpluglog.extpluglist.add('FOSS', 'VST2', 'ADLplug', '')
			if plugin_vst2.check_exists('id', 1094995021):
				extpluglog.extpluglist.success('FM', 'OPL2')
				adlplug_data = params_os_adlplug.adlplug_data()
	
				adlplug_data.set_param("four_op" ,0)  
				adlplug_data.set_param("pseudo_four_op" ,0)   
				adlplug_data.set_param("blank" ,0)	
				adlplug_data.set_param("con12" ,int(plugin_obj.params.get('fm_1', 0).value))
				adlplug_data.set_param("con34" ,int(plugin_obj.params.get('fm_2', 0).value))	
				adlplug_data.set_param("note_offset1" ,0)
				adlplug_data.set_param("note_offset2" ,0)
				adlplug_data.set_param("fb12" ,int(plugin_obj.params.get('feedback_1', 0).value))  
				adlplug_data.set_param("fb34" ,int(plugin_obj.params.get('feedback_2', 0).value)) 
				adlplug_data.set_param("midi_velocity_offset" ,0) 
				adlplug_data.set_param("second_voice_detune" ,0)  
				adlplug_data.set_param("percussion_key_number" ,0)
		
				for opnplugopname, cvpjopname in [['m1', 'op0'], ['c1', 'op1'], ['m2', ''], ['c2', '']]:
					opl_op_attack = int(plugin_obj.params.get(cvpjopname+"/env_attack", 0).value)
					opl_op_decay = int(plugin_obj.params.get(cvpjopname+"/env_decay", 0).value)
					opl_op_sustain = int(plugin_obj.params.get(cvpjopname+"/env_sustain", 0).value)
					opl_op_release = int(plugin_obj.params.get(cvpjopname+"/env_release", 0).value)
					opl_op_level = int(plugin_obj.params.get(cvpjopname+"/level", 0).value)
					opl_op_ksl = int(plugin_obj.params.get(cvpjopname+"/ksl", 0).value)
					opl_op_fmul = int(plugin_obj.params.get(cvpjopname+"/freqmul", 0).value)
					opl_op_trem = int(plugin_obj.params.get(cvpjopname+"/tremolo", 0).value)
					opl_op_vib = int(plugin_obj.params.get(cvpjopname+"/vibrato", 0).value)
					opl_op_sus = int(plugin_obj.params.get(cvpjopname+"/sustained", 0).value)
					opl_op_env = int(plugin_obj.params.get(cvpjopname+"/ksr", 0).value)
					opl_op_wave = int(plugin_obj.params.get(cvpjopname+"/waveform", 0).value)
	
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
		
				adlplug_data.set_param("delay_off_ms" ,0)   
				adlplug_data.set_param("delay_on_ms" ,0)	
				adlplug_data.set_param("bank" ,0) 
				adlplug_data.set_param("program" ,0)  
				adlplug_data.set_param("name" ,'')
		
				opl_tremolo_depth = int(plugin_obj.params.get('tremolo_depth', 0).value)
				opl_vibrato_depth = int(plugin_obj.params.get('vibrato_depth', 0).value)
				
				adlplug_data.add_selection(0, 0, 0)
				adlplug_data.adlplug_chip(2, 2, 0)
				adlplug_data.adlplug_global(0, opl_tremolo_depth, opl_vibrato_depth)
		
				adlplug_data.add_common('DawVert', 0, 1.0)
		
				adlplug_data.adlplug_to_cvpj_vst2(convproj_obj, plugin_obj)
				return True	
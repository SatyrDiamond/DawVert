# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import plugin_vst2
from functions import plugins
from functions_plugparams import data_vc2xml
import math
import struct
import xml.etree.ElementTree as ET

def getparam(paramname):
	global pluginid_g
	global cvpj_l_g
	paramval = plugins.get_plug_param(cvpj_l_g, pluginid_g, paramname, 0)
	return paramval[0]

def opnplug_addvalue(opnplug_params, name, value):
	temp_xml = ET.SubElement(opnplug_params, 'VALUE')
	temp_xml.set('name', str(name))
	temp_xml.set('val', str(value))

def opnplug_addbank(opnplug_params, num, name):
	bank_xml = ET.SubElement(opnplug_params, 'bank')
	opnplug_addvalue(bank_xml, 'bank', num)
	opnplug_addvalue(bank_xml, 'name', name)

def convert(cvpj_l, pluginid, plugintype):
	global pluginid_g
	global cvpj_l_g
	pluginid_g = pluginid
	cvpj_l_g = cvpj_l

	opnplug_root = ET.Element("ADLMIDI-state")
	opnplug_addbank(opnplug_root, 1, 'DawVert')
	opnplug_params = ET.SubElement(opnplug_root, 'instrument')
	opnplug_addvalue(opnplug_params, "blank" ,0)
	opnplug_addvalue(opnplug_params, "note_offset" ,0)
	opnplug_addvalue(opnplug_params, "feedback" ,getparam('feedback'))
	opnplug_addvalue(opnplug_params, "algorithm" ,getparam('algorithm'))
	opnplug_addvalue(opnplug_params, "ams" ,getparam('ams'))
	opnplug_addvalue(opnplug_params, "fms" ,getparam('fms'))
	opnplug_addvalue(opnplug_params, "midi_velocity_offset" ,0)
	opnplug_addvalue(opnplug_params, "percussion_key_number" ,0)

	for opnum in range(4):
		optxt = "op"+str(opnum+1)
		opnplug_addvalue(opnplug_params, optxt+"detune" ,getparam(optxt+"_detune"))
		opnplug_addvalue(opnplug_params, optxt+"fmul" ,getparam(optxt+"_freqmul"))
		opnplug_addvalue(opnplug_params, optxt+"level" ,getparam(optxt+"_level"))
		opnplug_addvalue(opnplug_params, optxt+"ratescale" ,getparam(optxt+"_ratescale"))
		opnplug_addvalue(opnplug_params, optxt+"attack" ,getparam(optxt+"_env_attack"))
		opnplug_addvalue(opnplug_params, optxt+"am" ,getparam(optxt+"_am"))
		opnplug_addvalue(opnplug_params, optxt+"decay1" ,getparam(optxt+"_env_decay"))
		opnplug_addvalue(opnplug_params, optxt+"decay2" ,getparam(optxt+"_env_decay2"))
		opnplug_addvalue(opnplug_params, optxt+"sustain" ,getparam(optxt+"_env_sustain"))
		opnplug_addvalue(opnplug_params, optxt+"release" ,getparam(optxt+"_env_release"))
		opnplug_addvalue(opnplug_params, optxt+"ssgenable" ,getparam(optxt+"_ssg_enable"))
		opnplug_addvalue(opnplug_params, optxt+"ssgwave" ,getparam(optxt+"_ssg_mode"))

	opnplug_addvalue(opnplug_params, "delay_off_ms" ,120)
	opnplug_addvalue(opnplug_params, "delay_on_ms" ,486)
	opnplug_addvalue(opnplug_params, "bank" ,0)
	opnplug_addvalue(opnplug_params, "program" ,0)
	opnplug_addvalue(opnplug_params, "name" ,'DawVert')

	opnplug_selection = ET.SubElement(opnplug_root, 'selection')
	opnplug_addvalue(opnplug_selection, "part" ,0)
	opnplug_addvalue(opnplug_selection, "bank" ,0)
	opnplug_addvalue(opnplug_selection, "program" ,0)

	opnplug_chip = ET.SubElement(opnplug_root, 'chip')
	opnplug_addvalue(opnplug_chip, "emulator" ,0)
	opnplug_addvalue(opnplug_chip, "chip_count" ,1)
	opnplug_addvalue(opnplug_chip, "chip_type" ,0)

	opnplug_global = ET.SubElement(opnplug_root, 'global')
	opnplug_addvalue(opnplug_global, "volume_model" ,0)
	opnplug_addvalue(opnplug_global, "lfo_enable" ,getparam("lfo_enable"))
	opnplug_addvalue(opnplug_global, "lfo_frequency" ,getparam("lfo_frequency"))

	opnplug_common = ET.SubElement(opnplug_root, 'common')
	opnplug_addvalue(opnplug_common, "bank_title" ,'DawVert')
	opnplug_addvalue(opnplug_common, "part" ,0)
	opnplug_addvalue(opnplug_common, "master_volume" ,12.0)

	plugin_vst2.replace_data(cvpj_l, pluginid, 'any', 'OPNplug', 'chunk', data_vc2xml.make(opnplug_root), None)
	return True
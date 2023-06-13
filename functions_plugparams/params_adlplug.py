# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def opnplug_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, 'VALUE')
	temp_xml.set('name', str(name))
	temp_xml.set('val', str(value))

def opnplug_addbank(xmltag, num, name):
	bank_xml = ET.SubElement(xmltag, 'bank')
	opnplug_addvalue(bank_xml, 'bank', num)
	opnplug_addvalue(bank_xml, 'name', name)

def opnplug_op_params(xmltag, opnum, plugindata):
	opdata = plugindata["op"+str(opnum)]
	opnplug_addvalue(xmltag, "op"+str(opnum)+"detune" ,opdata["detune"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"fmul" ,opdata["freqmul"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"level" ,opdata["level"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ratescale" ,opdata["ratescale"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"attack" ,opdata["env_attack"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"am" ,opdata["am"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"decay1" ,opdata["env_decay"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"decay2" ,opdata["env_decay2"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"sustain" ,opdata["env_sustain"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"release" ,opdata["env_release"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ssgenable" ,opdata["ssg_enable"])
	opnplug_addvalue(xmltag, "op"+str(opnum)+"ssgwave" ,opdata["ssg_mode"])

def opnplug_convert(plugindata):
	opnplug_root = ET.Element("ADLMIDI-state")
	opnplug_addbank(opnplug_root, 1, 'DawVert')
	opnplug_params = ET.SubElement(opnplug_root, 'instrument')
	opnplug_addvalue(opnplug_params, "blank" ,0)
	opnplug_addvalue(opnplug_params, "note_offset" ,0)
	opnplug_addvalue(opnplug_params, "feedback" ,plugindata["feedback"])
	opnplug_addvalue(opnplug_params, "algorithm" ,plugindata["algorithm"])
	opnplug_addvalue(opnplug_params, "ams" ,plugindata["ams"])
	opnplug_addvalue(opnplug_params, "fms" ,plugindata["fms"])
	opnplug_addvalue(opnplug_params, "midi_velocity_offset" ,0)
	opnplug_addvalue(opnplug_params, "percussion_key_number" ,0)
	for opnum in range(4):
		opnplug_op_params(opnplug_params, opnum+1, plugindata)

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
	opnplug_addvalue(opnplug_global, "lfo_enable" ,plugindata["lfo_enable"])
	opnplug_addvalue(opnplug_global, "lfo_frequency" ,plugindata["lfo_frequency"])

	opnplug_common = ET.SubElement(opnplug_root, 'common')
	opnplug_addvalue(opnplug_common, "bank_title" ,'DawVert')
	opnplug_addvalue(opnplug_common, "part" ,0)
	opnplug_addvalue(opnplug_common, "master_volume" ,12.0)

	return opnplug_root

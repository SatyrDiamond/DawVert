# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import lxml.etree as ET
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import data_vc2xml

class m8bp_data:
	def __init__(self):
		self.m8bp_params_env = {}
		self.m8bp_params_env["duty"] = None
		self.m8bp_params_env["pitch"] = None
		self.m8bp_params_env["volume"] = None

		self.m8bp_params = {}
		self.m8bp_params["arpeggioDirection"] = 0.0
		self.m8bp_params["arpeggioTime"] = 0.02999999932944775
		self.m8bp_params["attack"] = 0.0
		self.m8bp_params["bendRange"] = 12.0
		self.m8bp_params["colorScheme"] = 1.0
		self.m8bp_params["decay"] = 0.0
		self.m8bp_params["duty"] = 0.0
		self.m8bp_params["gain"] = 0.5
		self.m8bp_params["isAdvancedPanelOpen_raw"] = 1.0
		self.m8bp_params["isArpeggioEnabled_raw"] = 0.0
		self.m8bp_params["isPitchSequenceEnabled_raw"] = 0.0
		self.m8bp_params["isDutySequenceEnabled_raw"] = 0.0
		self.m8bp_params["isVolumeSequenceEnabled_raw"] = 0.0
		self.m8bp_params["maxPoly"] = 8.0
		self.m8bp_params["noiseAlgorithm_raw"] = 0.0
		self.m8bp_params["osc"] = 0.0
		self.m8bp_params["duty"] = 2.0
		self.m8bp_params["pitchSequenceMode_raw"] = 0.0
		self.m8bp_params["release"] = 0.0
		self.m8bp_params["restrictsToNESFrequency_raw"] = 0.0
		self.m8bp_params["suslevel"] = 1.0
		self.m8bp_params["sweepInitialPitch"] = 0.0
		self.m8bp_params["sweepTime"] = 0.1000000014901161
		self.m8bp_params["vibratoDelay"] = 0.2999999821186066
		self.m8bp_params["vibratoDepth"] = 0.0
		self.m8bp_params["vibratoIgnoresWheel_raw"] = 1.0
		self.m8bp_params["vibratoRate"] = 0.1500000059604645

	def set_param(self, name, value):
		self.m8bp_params[name] = value

	def set_env(self, name, value):
		self.m8bp_params_env[name] = value

	def out_xml(self):
		xml_m8p_root = ET.Element("root")
		xml_m8p_params = ET.SubElement(xml_m8p_root, "Params")
		for m8bp_param in self.m8bp_params:

			temp_xml = ET.SubElement(xml_m8p_params, 'PARAM')
			temp_xml.set('id', str(m8bp_param))
			temp_xml.set('value', str(self.m8bp_params[m8bp_param]))

		xml_m8p_dutyEnv = ET.SubElement(xml_m8p_root, "dutyEnv")
		xml_m8p_pitchEnv = ET.SubElement(xml_m8p_root, "pitchEnv")
		xml_m8p_volumeEnv = ET.SubElement(xml_m8p_root, "volumeEnv")

		if self.m8bp_params_env["duty"] != None: 
			xml_m8p_dutyEnv.text = ','.join(str(item) for item in self.m8bp_params_env["duty"])
		if self.m8bp_params_env["pitch"] != None: 
			xml_m8p_pitchEnv.text = ','.join(str(item) for item in self.m8bp_params_env["pitch"])
		if self.m8bp_params_env["volume"] != None: 
			xml_m8p_volumeEnv.text = ','.join(str(item) for item in self.m8bp_params_env["volume"])

		return xml_m8p_root

	def to_cvpj_vst2(self, plugin_obj):
		plugin_vst2.replace_data(plugin_obj, 'name','any', 'Magical 8bit Plug 2', 'chunk', data_vc2xml.make(self.out_xml()), None)
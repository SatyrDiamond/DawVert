# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions_plugin_ext import plugin_vst2
import xml.etree.ElementTree as ET

class spaceship_delay_data:
	def __init__(self):
		self.params = {}
		self.params['INPUT'] = 0
		self.params['OUTPUT'] = 0.5
		self.params['MIX'] = 5
		self.params['DELAYMODE'] = 0
		self.params['DELAYL'] = 0
		self.params['DELAYR'] = 0
		self.params['DELAYSYNCL'] = 22
		self.params['DELAYSYNCR'] = 22
		self.params['DELAYVT'] = 0
		self.params['DELAYBPM'] = 0.35714286565780639648
		self.params['FEEDBACK'] = 0
		self.params['CFEEDBACK'] = 0
		self.params['DELAYSLEW'] = 0.5
		self.params['DLYTYPE'] = 2
		self.params['FREEZE'] = 0
		self.params['REVERB'] = 0
		self.params['ATTACK'] = 0
		self.params['MODAMOUNT'] = 0
		self.params['MODRATE'] = 0.5
		self.params['MODFILTAMOUNT'] = 0
		self.params['MODFILTRATE'] = 0.5
		self.params['MODENVAMOUNT'] = 0.5
		self.params['FILTALGO'] = 1
		self.params['FILTPRM1'] = 0
		self.params['FILTPRM2'] = 1
		self.params['FILTPRM3'] = 0.75
		self.params['FILTPRM4'] = 0
		self.params['FILTLOC'] = 0
		self.params['FXALGO'] = 0
		self.params['FXPRM1'] = 0
		self.params['FXPRM2'] = 0
		self.params['FXPRM3'] = 0
		self.params['FXPRM4'] = 0
		self.params['FXPRM5'] = 0
		self.params['EFFLOC'] = 1
		self.params['NLALGO'] = 1
		self.params['NLPRM1'] = 0
		self.params['NLPRM2'] = 0
		self.params['NLPRM3'] = 0
		self.params['NLPRM4'] = 0

	def set_param(self, name, value):
		self.params[name] = value
	
	def to_cvpj_vst3(self, convproj_obj, plugin_obj):
        xmldata = ET.Element("SPSHIPDELAY1.0.5")  
        for key, value in self.params.iteritems(): xmldata.set(key) = value
		plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'any', 1181644592, 'chunk', data_vc2xml.make(xmldata), None)
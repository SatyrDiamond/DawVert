# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from io import StringIO
from functions import data_values
from functions_plugin_ext import plugin_vst2
import json

def parse_value_to_data(i_value, tabnum, stringdata, use_newline):
	if isinstance(i_value, float): stringdata.write(str(i_value))
	elif isinstance(i_value, int): stringdata.write(str(i_value))
	elif isinstance(i_value, str): 
		i_value = i_value.replace('\\', '\\\\')
		i_value = i_value.replace('\"', '\\\"')
		stringdata.write('"'+str(i_value)+'"')
	elif isinstance(i_value, dict): 
		parse_dict_to_data(i_value, tabnum+1, stringdata, use_newline)
	elif isinstance(i_value, list): 
		stringdata.write('{')
		for num in range(len(i_value)):
			part = i_value[num]
			parse_value_to_data(part, tabnum, stringdata, use_newline)
			if num < len(i_value)-1: stringdata.write(',')
		stringdata.write('}')

def parse_dict_to_data(i_list, tabnum, stringdata, use_newline):
	stringdata.write('{')
	if use_newline: stringdata.write('\n')
	for key in i_list:
		if use_newline: stringdata.write('\t'*(tabnum+1))
		stringdata.write(key)
		value = i_list[key]
		stringdata.write(' = ')
		parse_value_to_data(value, tabnum, stringdata, use_newline)
		stringdata.write(',')
		if use_newline: stringdata.write('\n')
	if use_newline: stringdata.write('\t'*tabnum)
	stringdata.write('}')

def parse_value_to_text(i_value):
	stringdata = StringIO()
	outstring = parse_value_to_data(i_value, 0, stringdata, False)
	return stringdata.getvalue()


class aas_vs3_data: #String Studio VS-3
	def __init__(self):
		self.vsthree_data = {}
		self.vsthree_data['lastUse'] = 1702012753
		self.vsthree_data['bankSource'] = "Factory"
		self.vsthree_data['index'] = 1
		self.vsthree_data['bankName'] = "Factory Library"
		self.vsthree_data['bankPath'] = "C:\\Program Files\\Applied Acoustics Systems\\String Studio VS-3\\Factory Library\\Factory Library.VS-3 Pack"
		self.vsthree_data['loadedDomains'] = {}
		self.vsthree_data['mdate'] = "2018-11-15T11:57:46Z"
		self.vsthree_data['parameters'] = {}
		self.vsthree_data['parameters']['version'] = parse_value_to_text([5,"String Studio VS-3","3.2.3"])
		self.vsthree_data['bankController'] = {}
		self.vsthree_data['bankController']['sortOptions'] = {'typeForNone': 3, 'directionForNone': 1, 'directionForCategory': 1, 'typeForCategory': 1}
		self.vsthree_data['bankController']['mode'] = 2
		self.vsthree_data['version'] = 1
		self.vsthree_data['layerLabels'] = {}
		self.vsthree_data['programName'] = "DawVert"
		self.vsthree_data['extensions'] = {}
		self.vsthree_data['base'] = '1IN48FL'
		self.vsthree_data['tuning'] = {'type': "built-in", 'name': "Equal Temperament", 'referenceNote': 69}

		try:
			with open("./data_json/aas_vs3.json") as f: 
				self.outputvals = json.load(f)
		except:
			self.outputvals = {}

	def set_param(self, group, name, value):
		if group in self.outputvals: self.outputvals[group][name] = value

	def outputval(self):
		outvals = data_values.dict__get_all_keys(self.outputvals, [])
		self.out_schema = []
		self.out_values = []
		groupname = None
		for outval in outvals:
			if outval[0][0] != groupname: 
				groupname = outval[0][0]
				self.out_schema.append([groupname])
			self.out_schema.append(outval[0][-1])
			self.out_values.append(outval[1])
		self.vsthree_data['parameters']['schema'] = parse_value_to_text(self.out_schema)
		self.vsthree_data['parameters']['values'] = parse_value_to_text(self.out_values)
		stringdata = StringIO()
		parse_dict_to_data(self.vsthree_data, 0, stringdata, True)
		return stringdata.getvalue()

	def to_cvpj_vst2(self, cvpj_plugindata):
		plugin_vst2.replace_data(convproj_obj, cvpj_plugindata, 'id', 'win', 1213417780, 'chunk', self.outputval().encode(), None)
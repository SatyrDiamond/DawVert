# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import chardet
from objects.valobjs import triplestr
import xml.etree.ElementTree as ET

def fixvalue(v, t):
	if t == 'float': return float(v)
	elif t == 'int': return int(v)
	elif t == 'bool': return bool(int(v))

class pltr_pipe:
	def __init__(self):
		self.type = None
		self.v_from = None
		self.v_to = None
		self.value = 0
		self.valuetype = ''
		self.name = None

	def read_xml(self, xml_data, isout):
		self.type = xml_data.tag
		self.valuetype = xml_data.get('type')
		if self.type == 'param':
			if not isout:
				self.v_from = xml_data.get('to')
				self.v_to = xml_data.get('from')
				if not self.v_from: self.v_from = self.v_to
			else:
				self.v_to = xml_data.get('to')
				self.v_from = xml_data.get('from')
				if not self.v_from: self.v_from = self.v_to
		if self.type == 'wet':
			if not isout:
				self.v_to = xml_data.get('from')
			else:
				self.v_to = xml_data.get('from')
		if xml_data.text: self.value = fixvalue(xml_data.text, self.valuetype)
		name = xml_data.get('name')
		if name: self.name = name

	def write_xml(self, xml_data, isout):
		transform_xml = ET.SubElement(xml_data, self.type)
		if self.type == 'param':
			if not isout:
				if self.v_from != self.v_to: transform_xml.set('to', str(self.v_from))
				transform_xml.set('from', str(self.v_to))
			else:
				transform_xml.set('to', str(self.v_to))
				if self.v_from != self.v_to: transform_xml.set('from', str(self.v_from))
		if self.type == 'wet':
			if not isout:
				transform_xml.set('from', str(self.v_to))
			else:
				transform_xml.set('from', str(self.v_to)) 
		transform_xml.set('type', str(self.valuetype))
		if self.value == False: transform_xml.text = str(0)
		elif self.value == True: transform_xml.text = str(1)
		else: transform_xml.text = str(self.value)
		if self.name: transform_xml.set('name', str(self.name))

class pltr_ts:
	def __init__(self):
		self.in_type = triplestr()
		self.out_type = triplestr()
		self.in_data = {}
		self.out_data = {}
		self.proc = []

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'input':
				self.in_type.set_str(x_part.get('plugtype'))
				for x_inpart in x_part:
					pipe_obj = pltr_pipe()
					pipe_obj.read_xml(x_inpart, False)
					self.in_data[pipe_obj.v_from] = pipe_obj
				
			if x_part.tag == 'proc':
				for x_inpart in x_part:
					if x_inpart.tag == 'calc':
						name = x_inpart.get('name')
						calctype = x_inpart.get('type')
						self.proc.append(['calc', name, calctype]+[(float(x) if '.' in x else int(x)) for x in x_inpart.text.split(';')])
						
			if x_part.tag == 'output':
				self.out_type.set_str(x_part.get('plugtype'))
				for x_inpart in x_part:
					pipe_obj = pltr_pipe()
					pipe_obj.read_xml(x_inpart, True)
					self.out_data[pipe_obj.v_from] = pipe_obj

	def write_xml(self, xml_data, name):
		transform_xml = ET.SubElement(xml_data, "transform")
		transform_xml.set('name', name)

		input_xml = ET.SubElement(transform_xml, "input")
		input_xml.set('plugtype', str(self.in_type))
		for k, v in self.in_data.items():
			v.write_xml(input_xml, False)

		proc_xml = ET.SubElement(transform_xml, "proc")
		for v in self.proc:
			if v[0]=='calc':
				calc_xml = ET.SubElement(proc_xml, "calc")
				calc_xml.set('name', v[1])
				calc_xml.set('type', v[2])
				calc_xml.text = ';'.join([str(x) for x in v[3:]])

		output_xml = ET.SubElement(transform_xml, "output")
		output_xml.set('plugtype', str(self.out_type))
		for k, v in self.out_data.items():
			v.write_xml(output_xml, True)


class plugts:
	def __init__(self, filename):
		self.transforms = {}
		if filename: self.load_xml(filename)

	def load_xml(self, filename):
		parser = ET.XMLParser(encoding='utf-8')
		xml_data = ET.parse(filename, parser)
		xml_plugts = xml_data.getroot()
		for x_part in xml_plugts:
			if x_part.tag == 'transform':
				ts_obj = pltr_ts()
				ts_obj.read_xml(x_part)
				self.transforms[x_part.get('name')] = ts_obj

	def load_legacy(self, filename):
		if os.path.exists(filename):
			with open(filename, 'r') as ptsfile:
				inside_group = None
				for n, line in enumerate(ptsfile.readlines()):
					line = line.lstrip().strip()
					if line:
						if line[0] == '[' and line[-1] == ']':
							inside_group = line[1:]
							cur_ts_name = line[1:-1]
							cur_ts_obj = self.transforms[cur_ts_name] = pltr_ts()
						elif line[0] == '>': inside_group = line[1:]
						elif line[0] == '<': inside_group = None
						else: 
							linesplit = line.split('|')
							if linesplit[0] == 'type':
								#print(inside_group, linesplit)
								if inside_group == 'input': cur_ts_obj.in_type.set_str(linesplit[1])
								if inside_group == 'output': cur_ts_obj.out_type.set_str(linesplit[1])

							elif linesplit[0] in ['param', 'wet']:
								pipe_obj = pltr_pipe()

								path1 = linesplit[1]
								opdir = False
								if '>' in path1: 
									path1, path2 = path1.split('>')
								elif '<' in path1: 
									opdir = True
									path1, path2 = path1.split('<')
								else:
									path2 = path1

								pipe_obj.type = linesplit[0]
								pipe_obj.valuetype = 'float'
								pipe_obj.value = 0 if pipe_obj.type != 'wet' else 1
								if '#' in path1: 
									path1, valueval = path1.split('#')
									pipe_obj.value = int(valueval)
									pipe_obj.valuetype = 'int'
								if '%' in path1: 
									path1, valueval = path1.split('%')
									pipe_obj.value = float(valueval)
									pipe_obj.valuetype = 'float'
								if '&' in path1: 
									path1, valueval = path1.split('&')
									pipe_obj.value = valueval=='True'
									pipe_obj.valuetype = 'bool'

								if '#' in path1: path1 = path1.split('#')[0]
								if '%' in path1: path1 = path1.split('%')[0]
								if '&' in path1: path1 = path1.split('&')[0]
								
								if '#' in path2: path2 = path2.split('#')[0]
								if '%' in path2: path2 = path2.split('%')[0]
								if '&' in path2: path2 = path2.split('&')[0]

								if not opdir:
									pipe_obj.v_from = path1 if pipe_obj.type != 'wet' else 'wet'
									pipe_obj.v_to = path2
								else:
									pipe_obj.v_from = path2 if pipe_obj.type != 'wet' else 'wet'
									pipe_obj.v_to = path1

								if inside_group == 'input': cur_ts_obj.in_data[path1] = pipe_obj
								if inside_group == 'output': cur_ts_obj.out_data[path1] = pipe_obj

							elif linesplit[0] == 'name':
								pipe_obj.name = linesplit[1]
							elif inside_group == 'proc':
								cur_ts_obj.proc.append(linesplit)
							else:
								print('unknown cmd:', linesplit[0])

							#print(inside_group, linesplit)

	def save_xml(self, filename):
		xml_proj = ET.Element("plugtransform")

		for name, transform in self.transforms.items():
			transform.write_xml(xml_proj, name)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space="    ", level=0)
		outfile.write(filename)
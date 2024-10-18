# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import chardet
from objects.valobjs import triplestr

class pltr_pipe:
	def __init__(self):
		self.type = None
		self.v_from = None
		self.v_to = None
		self.value = 0
		self.valuetype = ''
		self.name = None

class pltr_ts:
	def __init__(self):
		self.in_type = triplestr()
		self.out_type = triplestr()
		self.in_data = {}
		self.out_data = {}
		self.proc = []

class plugts:
	def __init__(self, filename):
		self.transforms = {}

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
									pipe_obj.value = int(valueval)!=0
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


		#for x,v in self.transforms.items():
		#	print(x, v.in_type, v.out_type)

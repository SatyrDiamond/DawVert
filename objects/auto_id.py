# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from objects.convproj import placements_autopoints
from objects.convproj import automation
from objects import counter

class convproj2autoid:
	def __init__(self, time_ppq, time_float):
		self.in_data = {}
		self.time_ppq = time_ppq
		self.time_float = time_float

	def define(self, i_id, i_loc, i_type, i_addmul):
		#print('[auto id] Define - '+str(i_id)+' - '+i_loc)
		if i_id not in self.in_data: 
			self.in_data[i_id] = [i_loc, i_type, i_addmul]
		else:
			self.in_data[i_id][0] = i_loc
			self.in_data[i_id][1] = i_type
			self.in_data[i_id][2] = i_addmul

	def output(self, convproj_obj):
		for i, v in self.in_data.items():
			convproj_obj.automation.move(['id', str(i)], v[0])
			if v[2] != None: 
				convproj_obj.automation.calc(v[0], 'addmul', v[2][0], v[2][1], 0, 0)

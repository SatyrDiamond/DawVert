# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

class auto_multidata:
	def __init__(self): 
		self.autodata = {}

	def __iter__(self): 
		for x in self.autodata.items():
			yield x

	def add_point(self, position, value):
		if position not in self.autodata: self.autodata[position] = [value]
		else: self.autodata[position].append(value)

	def sort(self):
		self.autodata = dict(sorted(self.autodata.items()))

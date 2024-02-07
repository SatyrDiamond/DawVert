# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class findrepeats:
	def __init__(self):
		self.repeat_founds = []
		self.repeat_num = []
		self.timesigs = []
		self.poses = []
		self.tsnum = []

	def do_find(self, nls_obj, timesigposs, ppq):
		temp_tsp = timesigposs[0:-1]
		self.poses = [x[0] for x in temp_tsp]
		self.tsnum = [(x[1]/ppq)*4 for x in temp_tsp]

		self.repeat_founds = []
		self.repeat_num = []
		for x in nls_obj.splnl:
			if x[0] in self.poses: self.repeat_num.append([])
			obj = [x[1]-x[0], x[2]]
			if x[2]:
				if obj not in self.repeat_founds: self.repeat_founds.append(obj)
				self.repeat_num[-1].append(self.repeat_founds.index(obj))
			else: 
				self.repeat_num[-1].append(-1)

		return self.repeat_num

	def debugview(self):
		print('SPLIT   ', end='')
		for x in self.repeat_num:
			f = False
			for p in x: 
				print('|' if f else '|__|', end='')
				print(str(p).rjust(4) if p != -1 else '    ', end='')
				f = True
		print('')


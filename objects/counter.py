# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

class counter:
	def __init__(self, starting_num, start_txt):
		self.current = starting_num
		self.start_txt = start_txt

	def get(self):
		self.current += 1
		return self.current

	def get_str(self):
		self.current += 1
		return str(self.current)

	def get_str_txt(self):
		self.current += 1
		return self.start_txt+str(self.current)

	def next(self):
		return self.current+1

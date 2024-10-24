# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
from objects import globalstore

class colorset:
	def __init__(self, colorset):
		self.colorset = colorset
		self.colorlen = len(self.colorset) if self.colorset != None else 0
		self.num = 0

	@classmethod
	def from_dataset(cls, d_id, d_cat, d_item):
		dset = globalstore.dataset.get_cat(d_id, d_cat)
		if dset:
			colors = dset.colorset.get(d_item)
			return cls(colors.value) if colors else None
		else:
			return cls(None)

	def getcolor(self):
		if self.colorset:
			out_color = self.colorset[self.num % self.colorlen]
			self.num += 1
			return out_color
		else:
			return None

	def getcolornum(self, colornum):
		if self.colorset:
			out_color = self.colorset[colornum % self.colorlen]
			return out_color
		else:
			return None
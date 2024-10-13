# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import numpy as np
from functions import xtramath
from objects import globalstore
from dataclasses import dataclass
from dataclasses import field

def hsv_to_rgb(h, s, v) -> tuple:
	h -= h.__ceil__()-1
	if s:
		if h == 1.0: h = 0.0
		i = int(h*6.0); f = h*6.0 - i
		w = v * (1.0 - s)
		q = v * (1.0 - s * f)
		t = v * (1.0 - s * (1.0 - f))
		if i==0: return (v, t, w)
		if i==1: return (q, v, w)
		if i==2: return (w, v, t)
		if i==3: return (w, q, v)
		if i==4: return (t, w, v)
		if i==5: return (v, w, q)
	else: return (v, v, v)

# fx
def moregray(rgb_float): return [(rgb_float[0]/2)+0.25,(rgb_float[1]/2)+0.25,(rgb_float[2]/2)+0.25]
def darker(rgb_float, minus): 
	return [xtramath.clamp(rgb_float[0]-minus, 0, 1),xtramath.clamp(rgb_float[1]-minus, 0, 1),xtramath.clamp(rgb_float[2]-minus, 0, 1)]

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
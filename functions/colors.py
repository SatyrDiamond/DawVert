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

@dataclass
class cvpj_color:
	r_i: int = 0
	g_i: int = 0
	b_i: int = 0
	r_f: float = 0
	g_f: float = 0
	b_f: float = 0
	used: bool = False
	fx_allowed: bool = False

	@classmethod
	def from_float(self, indata):
		color_obj = cvpj_color()
		color_obj.set_float(indata)
		return color_obj

	@classmethod
	def from_int(self, indata):
		color_obj = cvpj_color()
		color_obj.set_int(indata)
		return color_obj

	@classmethod
	def from_hex(self, indata):
		color_obj = cvpj_color()
		color_obj.set_hex(indata)
		return color_obj

	def __add__(self, valuein):
		obj_copy = copy.copy(self)
		if obj_copy.used:
			if isinstance(valuein, cvpj_color):
				obj_copy.r_f += valuein.r_f
				obj_copy.g_f += valuein.g_f
				obj_copy.b_f += valuein.b_f
			else:
				obj_copy.r_f += valuein
				obj_copy.g_f += valuein
				obj_copy.b_f += valuein
			obj_copy.internal_clamp()
			obj_copy.internal_toint()
		return obj_copy

	def __iadd__(self, valuein):
		if self.used:
			if isinstance(valuein, cvpj_color):
				self.r_f += valuein.r_f
				self.g_f += valuein.g_f
				self.b_f += valuein.b_f
			else:
				self.r_f += valuein
				self.g_f += valuein
				self.b_f += valuein
			self.internal_clamp()
			self.internal_toint()
		return self

	def __sub__(self, valuein):
		obj_copy = copy.copy(self)
		if obj_copy.used:
			if isinstance(valuein, cvpj_color):
				obj_copy.r_f -= valuein.r_f
				obj_copy.g_f -= valuein.g_f
				obj_copy.b_f -= valuein.b_f
			else:
				obj_copy.r_f -= valuein
				obj_copy.g_f -= valuein
				obj_copy.b_f -= valuein
			obj_copy.internal_clamp()
			obj_copy.internal_toint()
		return obj_copy

	def __isub__(self, valuein):
		if self.used:
			if isinstance(valuein, cvpj_color):
				self.r_f -= valuein.r_f
				self.g_f -= valuein.g_f
				self.b_f -= valuein.b_f
			else:
				self.r_f -= valuein
				self.g_f -= valuein
				self.b_f -= valuein
			self.internal_clamp()
			self.internal_toint()
		return self

	def __mul__(self, valuein):
		obj_copy = copy.copy(self)
		if obj_copy.used:
			if isinstance(valuein, cvpj_color):
				obj_copy.r_f *= valuein.r_f
				obj_copy.g_f *= valuein.g_f
				obj_copy.b_f *= valuein.b_f
			else:
				obj_copy.r_f *= valuein
				obj_copy.g_f *= valuein
				obj_copy.b_f *= valuein
			obj_copy.internal_clamp()
			obj_copy.internal_toint()
		return obj_copy

	def __imul__(self, valuein):
		if self.used:
			if isinstance(valuein, cvpj_color):
				self.r_f *= valuein.r_f
				self.g_f *= valuein.g_f
				self.b_f *= valuein.b_f
			else:
				self.r_f *= valuein
				self.g_f *= valuein
				self.b_f *= valuein
			self.internal_clamp()
			self.internal_toint()
		return self

	def __rtruediv__(self, valuein):
		obj_copy = copy.copy(self)
		if obj_copy.used:
			if isinstance(valuein, cvpj_color):
				obj_copy.r_f /= valuein.r_f
				obj_copy.g_f /= valuein.g_f
				obj_copy.b_f /= valuein.b_f
			else:
				obj_copy.r_f /= valuein
				obj_copy.g_f /= valuein
				obj_copy.b_f /= valuein
			obj_copy.internal_clamp()
			obj_copy.internal_toint()
		return obj_copy

	def __itruediv__(self, valuein):
		if self.used:
			if isinstance(valuein, cvpj_color):
				self.r_f /= valuein.r_f
				self.g_f /= valuein.g_f
				self.b_f /= valuein.b_f
			else:
				self.r_f /= valuein
				self.g_f /= valuein
				self.b_f /= valuein
			self.internal_clamp()
			self.internal_toint()
		return self

	def __bool__(self):
		return self.used

	def get_int(self):
		return [self.r_i, self.g_i, self.b_i] if self.used else None

	def get_float(self):
		return [self.r_f, self.g_f, self.b_f] if self.used else None

	def get_hex(rgb_int): 
		return ('%02x%02x%02x' % [self.r_i, self.g_i, self.b_i]) if self.used else None

	def internal_clamp(self):
		self.r_f = xtramath.clamp(self.r_f, 0, 1)
		self.g_f = xtramath.clamp(self.g_f, 0, 1)
		self.b_f = xtramath.clamp(self.b_f, 0, 1)

	def internal_tofloat(self):
		self.r_f = self.r_i/255
		self.g_f = self.g_i/255
		self.b_f = self.b_i/255

	def internal_toint(self):
		self.r_i = int(self.r_f*255)
		self.g_i = int(self.g_f*255)
		self.b_i = int(self.b_f*255)

	def set_int(self, indata):
		if indata:
			self.r_i = int(indata[0])
			self.g_i = int(indata[1])
			self.b_i = int(indata[2])
			self.used = True
			self.internal_tofloat()

	def set_float(self, indata):
		if indata:
			self.r_f = indata[0]
			self.g_f = indata[1]
			self.b_f = indata[2]
			self.used = True
			self.internal_toint()

	def set_hex(self, hexcode):
		if indata:
			nonumsign = hexcode.lstrip('#')
			self.r_i, self.g_i, self.b_i = tuple(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))
			self.used = True
			self.internal_tofloat()

	def closest_color_index(colorset_obj, fallbacknum):
		if colorset_obj:
			if colorset_obj.colorset and self.used:
				colors = np.array(colorset_obj.colorset)
				color = np.array([self.r_f, self.g_f, self.b_f])
				distances = np.sqrt(np.sum((colors-color)**2,axis=1))
				index_of_smallest = np.where(distances==np.amin(distances))
				return index_of_smallest[0][0]
		return fallbacknum

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
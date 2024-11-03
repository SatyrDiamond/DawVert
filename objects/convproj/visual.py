# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from objects import globalstore
import numpy as np
import copy

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
	priority: int = 0

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

	@classmethod
	def from_hsv(self, h, s, v):
		color_obj = cvpj_color()
		color_obj.set_hsv(h, s, v)
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

	def remove(self):
		self.used = False

	def copy(self):
		return copy.copy(self)

	def get_int(self):
		return [self.r_i, self.g_i, self.b_i] if self.used else None

	def get_float(self):
		return [self.r_f, self.g_f, self.b_f] if self.used else None

	def get_hex(self): 
		return ('%02x%02x%02x' % (self.r_i, self.g_i, self.b_i)) if self.used else None

	def getbgr_int(self):
		return [self.b_i, self.g_i, self.r_i] if self.used else None

	def getbgr_float(self):
		return [self.b_f, self.g_f, self.r_f] if self.used else None

	def getbgr_hex(self): 
		return ('%02x%02x%02x' % [self.b_i, self.g_i, self.r_i]) if self.used else None

	def get_hex_fb(self, r, g, b): 
		outcolor = [self.r_i, self.g_i, self.b_i] if self.used else [r, g, b]
		return ('%02x%02x%02x' % (outcolor[0],outcolor[1],outcolor[2]))

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
		if hexcode:
			nonumsign = hexcode.lstrip('#')
			self.r_i, self.g_i, self.b_i = tuple(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))
			self.used = True
			self.internal_tofloat()

	def set_hsv(self, h, s, v):
		self.r_f, self.g_f, self.b_f = hsv_to_rgb(h, s, v)
		self.used = True
		self.internal_toint()

	def from_colorset(self, colorset_obj):
		if colorset_obj:
			self.set_float(colorset_obj.getcolor())

	def from_colorset_num(self, colorset_obj, num):
		if colorset_obj:
			self.set_float(colorset_obj.getcolornum(num))

	def closest_color_index(self, colorset_obj, fallbacknum):
		if colorset_obj:
			if colorset_obj.colorset and self.used:
				colors = np.array(colorset_obj.colorset)
				color = np.array([self.r_f, self.g_f, self.b_f])
				distances = np.sqrt(np.sum((colors-color)**2,axis=1))
				index_of_smallest = np.where(distances==np.amin(distances))
				return index_of_smallest[0][0]
		return fallbacknum

	def copy_to_self(self, other_color):
		self.r_i = other_color.r_i
		self.g_i = other_color.g_i
		self.b_i = other_color.b_i
		self.r_f = other_color.r_f
		self.g_f = other_color.g_f
		self.b_f = other_color.b_f
		self.used = other_color.used
		self.fx_allowed = other_color.fx_allowed
		self.priority = other_color.priority

	def merge(self, other_color):
		if other_color: 
			if not self: self.copy_to_self(other_color)
			elif other_color.priority > self.priority and other_color: self.copy_to_self(other_color)

class cvpj_visual_ui:
	def __init__(self):
		self.height = 1
		self.other = {}

	def __bool__(self):
		return bool(self.other) and self.height!=1

class cvpj_visual:
	__slots__ = ['name','color','comment']
	def __init__(self):
		self.name = None
		self.color = cvpj_color()
		self.comment = None

	def __bool__(self):
		return bool(self.name) and bool(self.color)

	def __eq__(self, visual_obj):
		s_name = self.name == visual_obj.name
		s_color = self.color == visual_obj.color
		return s_name and s_color

	def add(self, v_name, v_color):
		if v_name != None: self.name = v_name
		if v_color != None: self.color.set_float(v_color)

	def add_opt(self, v_name, v_color):
		if v_name != None and self.name == None: self.name = v_name
		if v_color != None and not self.color: self.color.set_float(v_color)

	def merge(self, other_visual_obj):
		if other_visual_obj.name != None and self.name == None: self.name = other_visual_obj.name
		self.merge_color(other_visual_obj)

	def from_dset(self, d_id, d_cat, d_item, overwrite):
		d = globalstore.dataset.get_obj(d_id, d_cat, d_item)
		if d: 
			if overwrite or (not self.name): self.name = d.visual.name
			if overwrite or (not self.color): self.color.set_float(d.visual.color)

	def from_dset_midi(self, m_bank_hi, m_bank, m_inst, m_drum, m_dev, overwrite):
		midi_dev = m_dev if m_dev else 'gm'
		startcat = midi_dev+'_inst' if not m_drum else midi_dev+'_drums'
		dset_inst = str(m_bank_hi)+'_'+str(m_bank)+'_'+str(m_inst)
		dset_fb = '0_0_'+str(m_inst)
		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')
		self.from_dset('midi', startcat, dset_inst, overwrite)
		self.from_dset('midi', startcat, dset_fb, overwrite)

class cvpj_metadata:
	def __init__(self):
		self.name = ''
		self.author = ''
		self.original_author = ''
		self.comment_text = ''
		self.comment_datatype = 'text'
		self.url = ''
		self.genre = ''
		self.t_seconds = -1
		self.t_minutes = -1
		self.t_hours = -1
		self.t_day = -1
		self.t_month = -1
		self.t_year = -1
		self.email = ''
		self.album = ''
		self.songwriter = ''
		self.producer = ''
		self.copyright = ''

class cvpj_window_data:
	__slots__ = ['pos_x','pos_y','size_x','size_y','open','detatched','maximized','minimized']
	def __init__(self):
		self.pos_x = -1
		self.pos_y = -1
		self.size_x = -1
		self.size_y = -1
		self.open = -1
		self.maximized = -1
		self.minimized = -1
		self.detatched = -1

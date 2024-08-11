# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass
from dataclasses import field

@dataclass
class cvpj_visual_ui:
	height: float = 0
	other: dict = field(default_factory=dict)

@dataclass
class cvpj_color:
	used: bool = False
	r: float = 0
	g: float = 0
	b: float = 0
	is_float: bool = False
	is_named: bool = False
	name: str = ''

	def from_hex(self, hexcode):
		nonumsign = hexcode.lstrip('#')
		rgb = tuple(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))
		self.used = True
		self.is_float = False
		self.r = rgb[0]
		self.g = rgb[1]
		self.b = rgb[2]

	def from_int(self, i_int):
		self.used = True
		self.is_float = False
		self.r = i_int[0]
		self.g = i_int[1]
		self.b = i_int[2]

	def from_float(self, i_float):
		self.used = True
		self.is_float = True
		self.r = i_float[0]
		self.g = i_float[1]
		self.b = i_float[2]

	def to_float(self):
		if self.used:
			if not is_named: r,g,b = self.r, self.g, self.b
			return ([r, g, b] if self.is_float else [r/255, g/255, b/255])

	def to_int(self):
		if self.used:
			if not is_named: r,g,b = self.r, self.g, self.b
			return ([int(r*255),int(g*255),int(b*255)] if self.is_float else [int(r), int(g), int(b)])

	def to_hex(self):
		intd = to_int()
		return ('%02x%02x%02x' % intd) if intd else None




@dataclass
class cvpj_visual:
	name: float = 0
	color: cvpj_color = field(default_factory=cvpj_color)


class cvpj_visual:
	__slots__ = ['name','color']
	def __init__(self):
		self.name = None
		self.color = None

	def __eq__(self, visual_obj):
		s_name = self.name == visual_obj.name
		s_color = self.color == visual_obj.color
		return s_name and s_color

	def add(self, v_name, v_color):
		if v_name != None: self.name = v_name
		if v_color != None: self.color = v_color

	def add_opt(self, v_name, v_color):
		if v_name != None and self.name == None: self.name = v_name
		if v_color != None and self.color == None: self.color = v_color

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

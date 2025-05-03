# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class dualstr:
	def __init__(self):
		self.type = None
		self.subtype = None

	@classmethod
	def from_type(cls, i_type, i_subtype):
		outobj = cls()
		outobj.set(i_type, i_subtype)
		return outobj

	@classmethod
	def from_str(cls, in_str):
		outobj = cls()
		outobj.set_str(in_str)
		return outobj

	def __str__(self):
		if self.type != None and self.subtype != None: return self.type+':'+self.subtype
		elif self.type != None and self.subtype == None: return self.type
		elif self.type == None and self.subtype == None: return ''

	def get_list(self):
		return [self.type, self.subtype]

	def __eq__(self, in_obj):
		return self.type==in_obj.type and self.subtype==in_obj.subtype

	def obj_wildmatch(self, in_obj):
		return self.check_wildmatch(in_obj.type, in_obj.subtype)

	def set(self, i_type, i_subtype):
		self.type = i_type
		self.subtype = i_subtype

	def set_str(self, in_str):
		self.set_list(in_str.split(':', 1))

	def set_list(self, in_list):
		self.type = None
		self.subtype = None
		if len(in_list)>0: self.type = in_list[0]
		if len(in_list)>1: self.subtype = in_list[1]

	def check_match(self, i_type, i_subtype):
		return self.type==i_type and self.subtype==i_subtype

	def check_matchmulti(self, i_type, i_subtypes):
		return self.type==i_type and (self.subtype in i_subtypes)

	def check_wildmatch(self, i_type, i_subtype):
		if self.type==i_type:
			if self.subtype==i_subtype: return True
			elif i_subtype == None: return True
			else: return False
		else: return False

class triplestr:
	def __init__(self):
		self.category = None
		self.type = None
		self.subtype = None

	@classmethod
	def from_type(cls, i_category, i_type, i_subtype):
		outobj = cls()
		outobj.set(i_category, i_type, i_subtype)
		return outobj

	@classmethod
	def from_str(cls, in_str):
		outobj = cls()
		outobj.set_str(in_str)
		return outobj

	def __str__(self):
		if self.category != None and self.type != None and self.subtype != None: return self.category+':'+self.type+':'+self.subtype
		elif self.category != None and self.type != None and self.subtype == None: return self.category+':'+self.type
		elif self.category != None and self.type == None and self.subtype == None: return self.category
		elif self.category == None and self.type == None and self.subtype == None: return ''

	def get_list(self):
		return [self.category, self.type, self.subtype]

	def __eq__(self, in_obj):
		return self.type==in_obj.type and self.subtype==in_obj.subtype and self.category==in_obj.category

	def obj_wildmatch(self, in_obj):
		return self.check_wildmatch(in_obj.category, in_obj.type, in_obj.subtype)

	def set(self, i_category, i_type, i_subtype):
		self.category = i_category
		self.type = i_type
		self.subtype = i_subtype

	def set_str(self, in_str):
		self.set_list(in_str.split(':', 3))

	def set_list(self, in_list):
		self.category = None
		self.type = None
		self.subtype = None
		if len(in_list)>0: self.category = in_list[0]
		if len(in_list)>1: self.type = in_list[1]
		if len(in_list)>2: self.subtype = in_list[2]

	def check_match(self, i_category, i_type, i_subtype):
		return self.type==i_type and self.subtype==i_subtype and self.category==i_category

	def check_matchmulti(self, i_category, i_type, i_subtypes):
		return self.type==i_type and self.category==i_category and (self.subtype in i_subtypes)

	def check_wildmatch(self, i_category, i_type, i_subtype):
		eq_cat = self.category==i_category if i_category else True
		eq_type = self.type==i_type if i_type else True
		eq_subtype = self.subtype==i_subtype if i_subtype else True
		return False not in (eq_cat, eq_type, eq_subtype)

class indexed_value:
	def __init__(self):
		self.data = []

	def __contains__(self, v):
		return v in self.data

	def items(self):
		for n, x in enumerate(self.data):
			if x is not None:
				yield (n, x)

	def get(self, n):
		if None in self.data: self.data[self.data.index(None)] = v
		else: return None

	def add(self, v):
		if v is not None:
			if v not in self.data: 
				if None in self.data: self.data[self.data.index(None)] = v
				else: self.data.append(v)
			return self.data.index(v)+1
		else:
			return 0

	def remove(self, v):
		if v is not None:
			if v in self.data: 
				indexv = self.data.index(v)
				self.data[indexv] = None
				return indexv+1
		return 0

	def merge_other(self, other):
		out = {}
		for n, x in other.items():
			out[n+1] = self.add(x)
		return out
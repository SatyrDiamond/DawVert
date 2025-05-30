# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects.valobjs import dualstr
import lxml.etree as ET

def fixval(v, vtype):
	if v:
		if vtype == 'float': return float(v)
		elif vtype == 'int': return int(float(v))
		elif vtype == 'bool': return bool(float(v))
		else: return v
	else: return 0

# --------------------------------------------------------- ACTIONS ---------------------------------------------------------

class action__in__param:
	def __init__(self):
		self.in_name = None
		self.storename = None
		self.value = 0
		self.valtype = None

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.in_name = v_from
			self.storename = v_from
		elif not v_from and v_to: 
			self.in_name = v_to
			self.storename = v_to
		elif v_from and v_to:
			self.in_name = v_from
			self.storename = v_to
		self.valtype = xmldata.get('type')
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		manu_obj.in__param(self.storename, self.in_name, self.value)

class action__in__dataval:
	def __init__(self):
		self.in_name = None
		self.storename = None
		self.value = 0
		self.valtype = None

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.in_name = v_from
			self.storename = v_from
		elif not v_from and v_to: 
			self.in_name = v_to
			self.storename = v_to
		elif v_from and v_to:
			self.in_name = v_from
			self.storename = v_to
		self.valtype = xmldata.get('type')
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		manu_obj.in__dataval(self.storename, self.in_name, self.value)

class action__in__wet:
	def __init__(self):
		self.storename = None
		self.value = 1

	def from_xml(self, xmldata):
		self.storename = xmldata.get('from')
		self.value = float(xmldata.text) if xmldata.text else None

	def do_action(self, manu_obj):
		manu_obj.in__wet(self.storename, self.value)

class action__in__value:
	def __init__(self):
		self.storename = None
		self.value = 1

	def from_xml(self, xmldata):
		self.storename = xmldata.get('to')
		self.value = float(xmldata.text)

	def do_action(self, manu_obj):
		manu_obj.in__value(self.storename, self.value)

class action__in__filter_param:
	def __init__(self):
		self.in_name = None
		self.storename = None
		self.valtype = None

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.in_name = v_from
			self.storename = v_from
		elif not v_from and v_to: 
			self.in_name = v_to
			self.storename = v_to
		elif v_from and v_to:
			self.in_name = v_from
			self.storename = v_to
		self.valtype = xmldata.get('type')

	def do_action(self, manu_obj):
		manu_obj.in__filter_param(self.storename, self.in_name)

class action__replace:
	def __init__(self):
		self.plugtype = []

	def from_xml(self, xmldata):
		plugtype = xmldata.get('plugtype')
		if plugtype: self.plugtype = plugtype.split(':')

	def do_action(self, manu_obj):
		i_category, i_type, i_subtype = [(self.plugtype[n] if len(self.plugtype)>n else None) for n in range(3)]
		manu_obj.plugin_obj.replace(i_category, i_type, i_subtype)

class action__replace_hard:
	def __init__(self):
		self.plugtype = []

	def from_xml(self, xmldata):
		plugtype = xmldata.get('plugtype')
		if plugtype: self.plugtype = plugtype.split(':')

	def do_action(self, manu_obj):
		i_category, i_type, i_subtype = [(self.plugtype[n] if len(self.plugtype)>n else None) for n in range(3)]
		manu_obj.plugin_obj.replace_hard(i_category, i_type, i_subtype)

class action__calc:
	def __init__(self):
		self.storename = None
		self.calc_type = None
		self.values = []

	def from_xml(self, xmldata):
		self.storename = xmldata.get('name')
		self.calc_type = xmldata.get('type')
		self.values = [float(x) for x in xmldata.text.split(';')] if xmldata.text else []

	def do_action(self, manu_obj):
		val1, val2, val3, val4 = [(self.values[n] if len(self.values)>n else 0) for n in range(4)]
		try:
			manu_obj.calc(self.storename, self.calc_type, val1, val2, val3, val4)
		except:
			pass

class action__cond__single:
	def __init__(self):
		self.actions_true = []
		self.actions_false = []
		self.storename = None
		self.expr = None

	def from_xml(self, xmldata):
		self.storename = xmldata.get('in')
		self.expr = xmldata.get('data')
		for i in xmldata:
			if i.tag == 'cond__true': self.actions_true = [get_action(x) for x in i]
			elif i.tag == 'cond__false': self.actions_false = [get_action(x) for x in i]
			else: self.actions_true.append(get_action(i))

	def do_action(self, manu_obj):
		if self.storename in manu_obj.cur_params:
			valpack = manu_obj.cur_params[self.storename]
			condval = eval(self.expr, None, {'x': valpack.value})
			if condval: 
				for action in self.actions_true: action.do_action(manu_obj)
			else: 
				for action in self.actions_false: action.do_action(manu_obj)

class action__out__param:
	def __init__(self):
		self.storename = None
		self.out_name = None
		self.value = 0
		self.valtype = None
		self.only_value = False

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.storename = v_from
			self.out_name = v_from
		elif not v_from and v_to: 
			self.storename = v_to
			self.out_name = v_to
		elif v_from and v_to:
			self.storename = v_from
			self.out_name = v_to

		only_value = xmldata.get('only_value')
		if only_value: self.only_value = bool(int(only_value))
		self.valtype = xmldata.get('type')
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		if not self.only_value:
			manu_obj.out__param(self.storename, self.value, self.out_name, None)
		else:
			manu_obj.out__param_val(self.storename, self.value)

class action__out__dataval:
	def __init__(self):
		self.storename = None
		self.out_name = None
		self.value = 0
		self.valtype = None
		self.only_value = False

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.storename = v_from
			self.out_name = v_from
		elif not v_from and v_to: 
			self.storename = v_to
			self.out_name = v_to
		elif v_from and v_to:
			self.storename = v_from
			self.out_name = v_to

		only_value = xmldata.get('only_value')
		if only_value: self.only_value = bool(int(only_value))
		self.valtype = xmldata.get('type')
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		if not self.only_value:
			manu_obj.out__dataval(self.storename, self.value, self.out_name)

class action__out__wet:
	def __init__(self):
		self.storename = None
		self.value = 0

	def from_xml(self, xmldata):
		self.storename = xmldata.get('from')
		self.value = float(xmldata.text) if xmldata.text else None

	def do_action(self, manu_obj):
		manu_obj.out__wet(self.storename, self.value)

class action__tobool:
	def __init__(self):
		self.storename = None
		self.cond = None

	def from_xml(self, xmldata):
		self.storename = xmldata.get('name')
		self.cond = xmldata.get('cond')

	def do_action(self, manu_obj):
		if self.storename in manu_obj.cur_params:
			valpack = manu_obj.cur_params[self.storename]
			valpack.value = eval(self.cond, None, {'x': valpack.value})
			valpack.automation = None
			valpack.valuetype = 'bool'

class action__toint:
	def __init__(self):
		self.storename = None
		self.cond = None

	def from_xml(self, xmldata):
		self.storename = xmldata.get('name')
		self.cond = xmldata.get('cond')

	def do_action(self, manu_obj):
		if self.storename in manu_obj.cur_params:
			valpack = manu_obj.cur_params[self.storename]
			valpack.value = int(valpack.value)
			valpack.automation = None
			valpack.valuetype = 'numeric'

class action__define_remap:
	def __init__(self):
		self.name = None
		self.in_type = 'int'
		self.out_type = 'int'
		self.vals = {}
		self.fallback = None

	def from_xml(self, xmldata):
		self.name = xmldata.get('name')
		self.in_type = xmldata.get('in_type')
		self.out_type = xmldata.get('out_type')
		for x in xmldata:
			in_val = fixval(x.get('in_val'), self.in_type)
			out_val = fixval(x.get('out_val'), self.out_type)
			if x.tag == 'val': 
				self.vals[in_val] = out_val
			if x.tag == 'fallback': 
				self.fallback = out_val

	def do_action(self, manu_obj):
		manu_obj.def_remap(self.name, self.fallback, self.in_type, self.out_type)
		for k, v in self.vals.items():
			manu_obj.def_remap_add_val(self.name,k, v)

class action__remap:
	def __init__(self):
		self.storename = None
		self.remapname = None

	def from_xml(self, xmldata):
		self.storename = xmldata.get('name')
		self.remapname = xmldata.get('remapdef')

	def do_action(self, manu_obj):
		manu_obj.remap(self.storename, self.remapname)

class action__out__filter_param:
	def __init__(self):
		self.in_name = None
		self.storename = None
		self.valtype = None
		self.value = 0
		self.only_value = False

	def from_xml(self, xmldata):
		v_from = xmldata.get('from')
		v_to = xmldata.get('to')
		if v_from and not v_to: 
			self.storename = v_from
			self.out_name = v_from
		elif not v_from and v_to: 
			self.storename = v_to
			self.out_name = v_to
		elif v_from and v_to:
			self.storename = v_from
			self.out_name = v_to
		self.valtype = xmldata.get('type')
		only_value = xmldata.get('only_value')
		if only_value: self.only_value = bool(int(only_value))
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		manu_obj.out__filter_param(self.storename, self.value, self.out_name)

class action__out__dataval_val:
	def __init__(self):
		self.out_name = None
		self.valtype = None
		self.value = 0

	def from_xml(self, xmldata):
		self.out_name = xmldata.get('to')
		self.valtype = xmldata.get('type')
		self.value = fixval(xmldata.text, self.valtype) if xmldata.text else None

	def do_action(self, manu_obj):
		if self.out_name and self.value is not None:
			manu_obj.out__dataval_val(self.out_name, self.value)

class debug__storeview:
	def from_xml(self, xmldata):
		pass

	def do_action(self, manu_obj):
		print(manu_obj.cur_params)

class debug__paramview:
	def from_xml(self, xmldata):
		pass

	def do_action(self, manu_obj):
		print(manu_obj.plugin_obj.params.list())

# --------------------------------------------------------- MAIN ---------------------------------------------------------

actionclasses = {}
actionclasses['in__param'] = action__in__param
actionclasses['in__wet'] = action__in__wet
actionclasses['in__filterparam'] = action__in__filter_param
actionclasses['in__value'] = action__in__value
actionclasses['in__dataval'] = action__in__dataval
actionclasses['out__param'] = action__out__param
actionclasses['out__wet'] = action__out__wet
actionclasses['out__filterparam'] = action__out__filter_param
actionclasses['out__dataval'] = action__out__dataval
actionclasses['out__dataval_val'] = action__out__dataval_val
actionclasses['cond__single'] = action__cond__single
actionclasses['calc'] = action__calc
actionclasses['remap'] = action__remap
actionclasses['replace'] = action__replace
actionclasses['replace_hard'] = action__replace_hard
actionclasses['toint'] = action__toint
actionclasses['tobool'] = action__tobool
actionclasses['define_remap'] = action__define_remap
actionclasses['debug__storeview'] = debug__storeview
actionclasses['debug__paramview'] = debug__paramview

def get_action(xmldata):
	actionname = xmldata.tag
	if actionname in actionclasses:
		action_obj = actionclasses[actionname]()
		action_obj.from_xml(xmldata)
		return action_obj
	else:
		print('ERROR: NOT SUPPORTED', actionname)

class plugstatets_current_state:
	def __init__(self):
		self.actions = []

class plugstatets:
	def __init__(self):
		self.actions = []
		self.priority = None
		self.daw_in = None
		self.daw_out = None
		self.plugtype = None
		self.state = plugstatets_current_state()

	def load_from_file(self, filepath):
		parser = ET.XMLParser(remove_comments=True)
		xml_data = ET.parse(filepath, parser)
		xml_proj = xml_data.getroot()

		self.__init__()

		priority = xml_proj.get('priority')
		if priority: self.priority = int(hpriority)
		daw_in = xml_proj.get('daw_in')
		if daw_in: self.daw_in = daw_in.split(';')
		daw_out = xml_proj.get('daw_out')
		if daw_out: self.daw_out = daw_out.split(';')
		plugtype = xml_proj.get('plugtype')
		if plugtype: self.plugtype = plugtype.split(':')

		for x in xml_proj:
			self.actions.append(get_action(x))

	def do_actions(self, manu_obj):
		for action in self.actions:
			if action: 
				action.do_action(manu_obj)
			else:
				print('ERROR: NOT SUPPORTED', action)

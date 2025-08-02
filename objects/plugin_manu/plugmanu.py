# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import globalstore
from objects.convproj import automation
from objects.convproj import project as convproj
from objects.valobjs import dualstr
import logging

DEBUG__TXT = False

logger_plugconv = logging.getLogger('plugconv')

def fixval(v, vtype):
	if v:
		if vtype == 'float': return float(v)
		elif vtype == 'int': return int(float(v))
		elif vtype == 'bool': return bool(float(v))
		elif vtype == 'filter_type': return dualstr.from_str(v)
		else: return v
	else: return 0

class valuepack:
	def __init__(self, value, autodata, valuetype):
		self.value = value
		self.automation = autodata
		self.valuetype = valuetype

	def __repr__(self): return '<'+self.value.__repr__()+', ['+str(self.automation)+'], '+str(self.valuetype)+'>'

	def __int__(self): return int(self.value)

	def __float__(self): return float(self.value)

	def __bool__(self): return bool(self.value)

	def __str__(self): return str(self.value)

	def __iadd__(self, valuein):
		self.calc('add', valuein, 0, 0, 0)
		return self

	def __isub__(self, valuein):
		self.calc('add', -valuein, 0, 0, 0)
		return self

	def __imul__(self, valuein):
		self.calc('mul', valuein, 0, 0, 0)
		return self

	def __itruediv__(self, valuein):
		self.calc('div', valuein, 0, 0, 0)
		return self

	def calc(self, mathtype, val1, val2, val3, val4):
		self.value = xtramath.do_math(self.value, mathtype, val1, val2, val3, val4)
		if self.automation: self.automation.calc(mathtype, val1, val2, val3, val4)

	def calc_clamp(self, i_min, i_max):
		self.value = xtramath.clamp(self.value, i_min, i_max)

def get_storename(paramnum, extid):
	return 'param'+str(paramnum) if paramnum > -1 else extid

def valtype_from_ptype(ptype):
	if ptype in ['int', 'float']: valtype = 'numeric'
	elif ptype == 'bool': valtype = 'bool'
	else: valtype = ptype
	return valtype

def valtype_from_obj(value):
	if type(value) in [int, float]: valtype = 'numeric'
	elif type(value) == bool: valtype = 'bool'
	elif type(value) == str: valtype = 'string'
	elif type(value) == dualstr: valtype = 'filter_type'
	else: valtype = 'other'
	return valtype

class remap_def:
	def __init__(self):
		self.name = None
		self.in_type = 'int'
		self.out_type = 'int'
		self.vals = {}
		self.fallback = None

class plug_manu:
	def __init__(self, plugin_obj, convproj_obj, pluginid):
		self.plugin_obj = plugin_obj
		self.convproj_obj = convproj_obj
		self.pluginid = pluginid
		self.cur_params = {}
		self.remaps = {}
		self.cur_eq = None
		self.cur_eq_name = None

# --------------------------------------------------------- INPUT ---------------------------------------------------------

	def in__wet(self, storename, fb):
		if DEBUG__TXT: print('DEBUG: in__wet:', storename.__repr__(), fb.__repr__())
		auto_obj = self.convproj_obj.automation.pop_f(['slot', self.pluginid, 'wet'])
		if 'wet' in self.plugin_obj.params_slot or fb is not None:
			if not storename: storename = 'wet'
			param_obj = self.plugin_obj.params_slot.pop('wet',fb)
			self.cur_params[storename] = valuepack(float(param_obj.value), auto_obj, 'numeric')
			return self.cur_params[storename]

	def in__param(self, storename, paramname, fb):
		if DEBUG__TXT: print('DEBUG: in__param:', storename.__repr__(), paramname.__repr__(), fb.__repr__())
		auto_obj = self.convproj_obj.automation.pop_f(['plugin', self.pluginid, paramname])
		if paramname in self.plugin_obj.params or fb is not None:
			param_obj = self.plugin_obj.params.pop(paramname,fb)
			self.cur_params[storename] = valuepack(param_obj.value, auto_obj, valtype_from_ptype(param_obj.type))
			return self.cur_params[storename]

	def in__dataval(self, storename, paramname, fb):
		if DEBUG__TXT: print('DEBUG: in__dataval:', storename.__repr__(), paramname.__repr__(), fb.__repr__())
		value = self.plugin_obj.datavals.pop(paramname,fb)
		self.cur_params[storename] = valuepack(value, None, valtype_from_obj(value))
		return self.cur_params[storename]

	def in__value(self, storename, value):
		if DEBUG__TXT: print('DEBUG: in__value:', storename.__repr__(), value.__repr__())
		self.cur_params[storename] = valuepack(value, None, valtype_from_obj(value))
		return self.cur_params[storename]

	def internal__in__filter_param(self, storename, filterparam, autolocstart, filter_obj):
		auto_obj = self.convproj_obj.automation.pop_f(autolocstart+[filterparam])
		outv = None
		if filterparam == 'on': outv = valuepack(filter_obj.on, auto_obj, 'bool')
		if filterparam == 'freq': outv = valuepack(filter_obj.freq, auto_obj, 'numeric')
		if filterparam == 'q': outv = valuepack(filter_obj.q, auto_obj, 'numeric')
		if filterparam == 'gain': outv = valuepack(filter_obj.gain, auto_obj, 'numeric')
		if filterparam == 'slope': outv = valuepack(filter_obj.slope, auto_obj, 'numeric')
		if filterparam == 'type': outv = valuepack(filter_obj.type, auto_obj, 'filter_type')
		if outv is not None: 
			self.cur_params[storename] = outv
			return self.cur_params[storename]

	def in__filter_param(self, storename, filterparam):
		if DEBUG__TXT: print('DEBUG: in__filter_param:', storename.__repr__(), filterparam.__repr__())
		self.internal__in__filter_param(storename, filterparam, ['filter', self.pluginid], self.plugin_obj.filter)

	def in__named_filter_name(self, filt_name):
		if DEBUG__TXT: print('DEBUG: in__named_filter_name:', filt_name)
		self.cur_eq_name = filt_name

	def in__named_filter_param(self, storename, filterparam, filt_name):
		if DEBUG__TXT: print('DEBUG: in__named_filter_name:', storename, filterparam, filt_name)
		filterid = filt_name if filt_name else self.cur_eq_name
		if filterid:
			f_exists, f_obj = self.plugin_obj.named_filter_get_exists(filterid)
			if f_exists:
				self.internal__in__filter_param(storename, filterparam, ['n_filter', self.pluginid, filterid], f_obj)

# --------------------------------------------------------- OUTPUT ---------------------------------------------------------

	def out__param_val(self, valuename, value):
		self.plugin_obj.params.add(valuename, value, 'float')

	def out__param(self, storename, fallbackval, paramname, valuename):
		if DEBUG__TXT: print('DEBUG: out__param:', storename.__repr__(), fallbackval.__repr__(), paramname.__repr__(), valuename.__repr__())
		#if DEBUG__TXT: print('	> param  |'+paramname+'<'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			if valstored.valuetype in ['numeric', 'bool']:
				valauto = valstored.automation
				if valauto: 
					autopath = automation.cvpj_autoloc(['plugin', self.pluginid, paramname])
					self.convproj_obj.automation.data[autopath] = valauto
				if valstored.valuetype == 'numeric':
					param_obj = self.plugin_obj.params.add(paramname, valstored.value, 'float')
				if valstored.valuetype == 'bool':
					param_obj = self.plugin_obj.params.add(paramname, valstored.value, 'bool')
				param_obj.visual.name = valuename
				return param_obj
			else:
				logger_plugconv.warning('plugmanu: "%s" is not compatable for param, "%s"' % (valstored.valuetype, storename))
		else:
			logger_plugconv.warning('plugmanu: val "%s" is not found for OUT_PARAM' % storename)

	def out__dataval_val(self, valuename, value):
		self.plugin_obj.datavals.add(valuename, value)

	def out__dataval(self, storename, fallbackval, paramname):
		if DEBUG__TXT: print('DEBUG: out__dataval:', storename.__repr__(), fallbackval.__repr__(), paramname.__repr__(), valuename.__repr__())
		#if DEBUG__TXT: print('	> param  |'+paramname+'<'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			if valstored.valuetype == 'numeric':
				self.plugin_obj.datavals.add(paramname, valstored.value)
			if valstored.valuetype == 'bool':
				self.plugin_obj.datavals.add(paramname, valstored.value)
			if valstored.valuetype == 'string':
				self.plugin_obj.datavals.add(paramname, valstored.value)
			return True
		else:
			logger_plugconv.warning('plugmanu: val "%s" is not found for OUT_DATAVAL' % storename)
		return False

	def out__wet(self, storename, fallbackval):
		if DEBUG__TXT: print('DEBUG: out__wet:', storename.__repr__(), fallbackval.__repr__())
		#if DEBUG__TXT: print('	> wet    |'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valauto = valstored.automation
			if valauto: 
				autopath = automation.cvpj_autoloc(['slot', self.pluginid, 'wet'])
				self.convproj_obj.automation.data[autopath] = valauto
			param_obj = self.plugin_obj.params_slot.add('wet', float(valstored.value), 'float')
			param_obj.visual.name = 'Wet'
		elif fallbackval is not None:
			self.plugin_obj.params_slot.add('wet', fallbackval, 'float')

	def out__eq_add(self):
		if DEBUG__TXT: print('DEBUG: out__eq_add')
		self.cur_eq, self.cur_eq_name = self.plugin_obj.eq_add()

	def out__filter_param(self, storename, fallbackval, filterparam):
		if DEBUG__TXT: print('DEBUG: out__filter_param:', storename.__repr__(), fallbackval.__repr__(), filterparam.__repr__())
		self.internal__out__filter_param(storename, fallbackval, filterparam, self.plugin_obj.filter, ['filter', self.pluginid])

	def out__named_filter_add(self, filt_name):
		if DEBUG__TXT: print('DEBUG: out__named_filter_add:', filt_name)
		self.plugin_obj.named_filter_add(filt_name)
		self.cur_eq_name = filt_name

	def out__named_filter_param(self, storename, fallbackval, filterparam, filt_name):
		if DEBUG__TXT: print('DEBUG: out__named_filter_param:', storename.__repr__(), fallbackval.__repr__(), filterparam.__repr__(), name)
		filterid = filt_name if filt_name else self.cur_eq_name
		if filterid:
			f_exists, f_obj = self.plugin_obj.named_filter_get_exists(filterid)
			if f_exists: self.internal__out__filter_param(storename, fallbackval, filterparam, f_obj, ['n_filter', self.pluginid, filterid])
		else:
			logger_plugconv.warning('plugmanu: named_filter name not defined')

	def internal__out__filter_param(self, storename, fallbackval, filterparam, filter_obj, autolocstart):
		#if DEBUG__TXT: print('	> filter |'+paramid+'%'+str(value))

		plugin_obj = self.plugin_obj

		val = None

		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valauto = valstored.automation
			val = valstored.value
			valuetype = valstored.valuetype

			if valauto and (valuetype in ['numeric', 'bool']): 
				autoloc = autolocstart+[filterparam]
				autopath = automation.cvpj_autoloc(autoloc)
				self.convproj_obj.automation.data[autopath] = valauto

		elif fallbackval is not None: 
			val = fallbackval
			valuetype = valtype_from_obj(val)

		if val is not None:
			if filterparam == 'on': 
				if valuetype == 'numeric': filter_obj.on = float(val)
				elif valuetype == 'bool': filter_obj.on = bool(val)
				else:
					logger_plugconv.warning('plugmanu: filter_param "on" type mismatch. should be "numeric" or "bool". not "%s".' % (valuetype))
			if filterparam in ["freq", "q", "gain", "slope"]: 
				if valuetype == 'numeric':
					if filterparam == 'freq': filter_obj.freq = float(val)
					if filterparam == 'q': filter_obj.q = float(val)
					if filterparam == 'gain': filter_obj.gain = float(val)
					if filterparam == 'slope': filter_obj.slope = float(val)
				else:
					logger_plugconv.warning('plugmanu: filter_param "%s" type mismatch. should be "numeric". not "%s".' % (filterparam, valuetype))
	
			if filterparam == 'type': 
				if valuetype == 'filter_type':
					filter_obj.type = val
				elif valuetype == 'string':
					filter_obj.type.set_str(val)
				else:
					logger_plugconv.warning('plugmanu: filter_param "type" type mismatch. should be "filter_type". not "%s".' % (valuetype))

# --------------------------------------------------------- MANU ---------------------------------------------------------

	def def_remap(self, name, fallback, in_type, out_type):
		if DEBUG__TXT: print('DEBUG: def_remap:', name.__repr__(), fallback.__repr__(), in_type.__repr__(), out_type.__repr__())
		remap_obj = remap_def()
		remap_obj.in_type = in_type
		remap_obj.out_type = out_type
		remap_obj.fallback = fallback
		out_type = valtype_from_ptype(remap_obj.out_type)
		remap_obj.fallback = fixval(fallback, remap_obj.out_type)
		self.remaps[name] = remap_obj

	def def_remap_add_val(self, name, key, value):
		if DEBUG__TXT: print('DEBUG: def_remap_add_val:', name.__repr__(), key.__repr__(), value.__repr__(), end=' > ')
		if name in self.remaps:
			remap_obj = self.remaps[name]
			remap_obj.vals[key] = fixval(value, remap_obj.out_type)
			if DEBUG__TXT: print(remap_obj.vals[key].__repr__())
		else:
			if DEBUG__TXT: print()

	def remap(self, storename, remapname):
		if DEBUG__TXT: print('DEBUG: remap:', storename.__repr__(), remapname.__repr__())
		if storename not in self.cur_params:
			logger_plugconv.warning('plugmanu: stored value "%s" is not found for REMAP' % storename)
		elif remapname not in self.remaps:
			logger_plugconv.warning('plugmanu: stored remap "%s" is not found for REMAP' % storename)
		else: 
			storeval = self.cur_params[storename]
			remap_obj = self.remaps[remapname]

			ptypei = valtype_from_ptype(remap_obj.in_type)
			ptypeo = valtype_from_ptype(remap_obj.out_type)

			cond_n_b = (ptypei=='numeric' and storeval.valuetype=='bool')

			if ptypei==storeval.valuetype or cond_n_b:
				if ptypei == 'filter_type' and ptypeo != 'filter_type':
					val = storeval.value
					is_found = False
					for k, v in remap_obj.vals.items():
						if val.obj_wildmatch(dualstr.from_str(k)):
							storeval.value = v
							storeval.valuetype = ptypeo
							is_found = True
							break
					if not is_found:
						storeval.value = remap_obj.fallback
						storeval.valuetype = ptypeo
				else:
					svald = storeval.value
					if cond_n_b: svald = int(svald)
					if svald in remap_obj.vals: 
						storeval.value = remap_obj.vals[svald]
						storeval.valuetype = ptypeo
					else: 
						storeval.value = remap_obj.fallback
						storeval.valuetype = ptypeo
				storeval.automation = None
			else:
				logger_plugconv.warning('plugmanu: remap type mismatch "%s" is defined not "%s"' % (ptypei, storeval.valuetype))


			#if remap_obj.in_type == 'filter_type' and remap_obj.out_type != 'filter_type':
			#	val = storeval.value
			#	if type(val) == dualstr:
			#		is_found = False
			#		for k, v in remap_obj.vals.items():
			#			if val.obj_wildmatch(dualstr.from_str(k)):
			#				storeval.value = fixval(v, remap_obj.out_type)
			#				storeval.isbool = type(v)==bool
			#				storeval.automation = None
			#				is_found = True
			#				break
			#		if not is_found:
			#			storeval.value = fixval(remap_obj.fallback, remap_obj.out_type)
			#			storeval.isbool = type(remap_obj.fallback)==bool
			#			storeval.automation = None

	def calc(self, storename, mathtype, val1, val2, val3, val4):
		if DEBUG__TXT: print('DEBUG: calc:', storename, mathtype, val1, val2, val3, val4)
		#if DEBUG__TXT: print('	calc     |'+'|'.join([str(x) for x in [storename, mathtype, val1, val2, val3, val4]]))
		if storename in self.cur_params: 
			storeval = self.cur_params[storename]
			if type(storeval.value) in [int, float, bool]:
				storeval.calc(mathtype, val1, val2, val3, val4)
		else:
			logger_plugconv.warning('plugmanu: stored value "%s" is not found for CALC' % storename)

	def calc_clamp(self, storename, i_min, i_max):
		if DEBUG__TXT: print('DEBUG: calc_clamp:', storename, i_min, i_max)
		if storename in self.cur_params: 
			storeval = self.cur_params[storename]
			if type(storeval.value) in [int, float, bool]:
				storeval.calc_clamp(i_min, i_max)
		else:
			logger_plugconv.warning('plugmanu: stored value "%s" is not found for CLAMP' % storename)

	# --------------------------- scripts ---------------------------

	def do_plugstatets(self, plugstatets_obj):
		plugstatets_obj.do_actions(self)
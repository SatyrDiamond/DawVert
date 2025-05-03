# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import globalstore
from objects.convproj import automation
from objects.convproj import project as convproj
from objects.valobjs import dualstr
import logging

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

DEBUG__TXT = False

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

# --------------------------------------------------------- INPUT ---------------------------------------------------------

	def in__wet(self, storename, fb):
		if DEBUG__TXT: print('DEBUG: in__wet:', storename.__repr__(), fb.__repr__())
		auto_obj = self.convproj_obj.automation.pop_f(['slot', self.pluginid, 'wet'])
		param_obj = self.plugin_obj.params_slot.pop('wet',fb)
		self.cur_params[storename] = valuepack(float(param_obj.value), auto_obj, 'numeric')
		return self.cur_params[storename]

	def in__param(self, storename, paramname, fb):
		if DEBUG__TXT: print('DEBUG: in__param:', storename.__repr__(), paramname.__repr__(), fb.__repr__())
		auto_obj = self.convproj_obj.automation.pop_f(['plugin', self.pluginid, paramname])
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

	def in__filter_param(self, storename, filterparam):
		if DEBUG__TXT: print('DEBUG: in__filter_param:', storename.__repr__(), filterparam.__repr__())
		auto_obj = self.convproj_obj.automation.pop_f(['filter', self.pluginid, filterparam])
		outv = None
		plugin_obj = self.plugin_obj
		if filterparam == 'on': outv = valuepack(plugin_obj.filter.on, auto_obj, 'bool')
		if filterparam == 'freq': outv = valuepack(plugin_obj.filter.freq, auto_obj, 'numeric')
		if filterparam == 'q': outv = valuepack(plugin_obj.filter.q, auto_obj, 'numeric')
		if filterparam == 'gain': outv = valuepack(plugin_obj.filter.gain, auto_obj, 'numeric')
		if filterparam == 'slope': outv = valuepack(plugin_obj.filter.slope, auto_obj, 'numeric')
		if filterparam == 'type': outv = valuepack(plugin_obj.filter.type, auto_obj, 'filter_type')
		if outv is not None: 
			self.cur_params[storename] = outv
			return self.cur_params[storename]

# --------------------------------------------------------- OUTPUT ---------------------------------------------------------

	def out__param(self, storename, fallbackval, paramname, valuename):
		if DEBUG__TXT: print('DEBUG: out__param:', storename.__repr__(), fallbackval.__repr__(), paramname.__repr__(), valuename.__repr__())
		#if DEBUG__TXT: print('	> param  |'+paramname+'<'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valtype = type(valstored.value)
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
				return True
			else:
				logger_plugconv.warning('plugmanu: "%s" is not compatable for param, "%s"' % (valstored.valuetype, storename))
			return False
		else:
			logger_plugconv.warning('plugmanu: val "%s" is not found for OUT_PARAM' % storename)
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

	def out__filter_param(self, storename, fallbackval, filterparam):
		if DEBUG__TXT: print('DEBUG: out__filter_param:', storename.__repr__(), fallbackval.__repr__(), filterparam.__repr__())
		#if DEBUG__TXT: print('	> filter |'+paramid+'%'+str(value))

		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valauto = valstored.automation
			val = valstored.value
			valuetype = valstored.valuetype

			if valauto and (valuetype in ['numeric', 'bool']): 
				autoloc = ['filter', self.pluginid, filterparam]
				autopath = automation.cvpj_autoloc(autoloc)
				self.convproj_obj.automation.data[autopath] = valauto

		else: 
			val = fallbackval
			valuetype = valtype_from_obj(val)

		plugin_obj = self.plugin_obj

		if filterparam == 'on': 
			if valuetype == 'numeric': plugin_obj.filter.on = float(val)
			if valuetype == 'bool': plugin_obj.filter.on = bool(val)
			else:
				logger_plugconv.warning('plugmanu: filter_param "on" type mismatch. should be "numeric" or "bool". not "%s".' % (valuetype))

		if valuetype == 'numeric':
			if filterparam == 'freq': plugin_obj.filter.freq = float(val)
			if filterparam == 'q': plugin_obj.filter.q = float(val)
			if filterparam == 'gain': plugin_obj.filter.gain = float(val)
			if filterparam == 'slope': plugin_obj.filter.slope = float(val)
		else:
			logger_plugconv.warning('plugmanu: filter_param "type" type mismatch. should be "numeric". not "%s".' % (valuetype))

		if valuetype == 'filter_type':
			if filterparam == 'type': plugin_obj.filter.type = val
		else:
			logger_plugconv.warning('plugmanu: filter_param "type" type mismatch. should be "filter_type". not "%s".' % (valuetype))

# --------------------------------------------------------- MANU ---------------------------------------------------------

	def def_remap(self, name, vals, fallback, in_type, out_type):
		if DEBUG__TXT: print('DEBUG: def_remap:', name.__repr__(), vals.__repr__(), fallback.__repr__(), in_type.__repr__(), out_type.__repr__())
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

			if ptypei==storeval.valuetype:
				pass
				if ptypei == 'filter_type' and ptypeo != 'filter_type':
					val = storeval.value
					is_found = False
					for k, v in remap_obj.vals.items():
						if val.obj_wildmatch(dualstr.from_str(k)):
							storeval.value = v
							storeval.valuetype = ptypeo
							storeval.automation = None
							is_found = True
							break
					if not is_found:
						storeval.value = remap_obj.fallback
						storeval.valuetype = ptypeo
						storeval.automation = None
				else:
					if storeval.value in remap_obj.vals: 
						storeval.value = remap_obj.vals[storeval.value]
						storeval.valuetype = ptypeo
					else: 
						storeval.value = remap_obj.fallback
						storeval.valuetype = ptypeo

				pass
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
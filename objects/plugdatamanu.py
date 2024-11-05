# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath
from objects import globalstore
from objects.convproj import automation
from objects.convproj import project as convproj

class valuepack:
	def __init__(self, value, autodata, isbool):
		self.value = value
		self.automation = autodata
		self.isbool = isbool

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

TOPLTR_DEBUG = False

class plug_manu:
	def __init__(self, plugin_obj, convproj_obj, pluginid):
		self.plugin_obj = plugin_obj
		self.convproj_obj = convproj_obj
		self.pluginid = pluginid
		self.cur_params = {}

	def from_wet(self, storename, fb):
		if TOPLTR_DEBUG: print('	wet|'+storename)
		self.cur_params[storename] = valuepack(
			self.plugin_obj.params_slot.pop('wet',fb).value, 
			self.convproj_obj.automation.pop_f(['slot', self.pluginid, 'wet']),
			False)
		return self.cur_params[storename]

	def from_param(self, storename, paramname, fb):
		if TOPLTR_DEBUG: print('	param|'+storename)
		self.cur_params[storename] = valuepack(
			self.plugin_obj.params.pop(paramname,fb).value, 
			self.convproj_obj.automation.pop_f(['plugin', self.pluginid, paramname]), False)
		return self.cur_params[storename]

	def from_dataval(self, storename, paramname, fb):
		self.cur_params[storename] = valuepack(
			self.plugin_obj.datavals.pop(paramname,fb), None, False)
		return self.cur_params[storename]

	def from_value(self, storename, paramname, value):
		self.cur_params[storename] = valuepack(value, None, False)
		return self.cur_params[storename]

	def to_param(self, storename, paramname, valuename):
		if TOPLTR_DEBUG: print('	param|'+paramname+'<'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valauto = valstored.automation
			if valauto: 
				autopath = automation.cvpj_autoloc(['plugin', self.pluginid, paramname])
				self.convproj_obj.automation.data[autopath] = valauto
			param_obj = self.plugin_obj.params.add(paramname, valstored.value, 'float' if not valstored.isbool else 'bool')
			param_obj.visual.name = valuename
			return True
		return False

	def to_wet(self, storename):
		if TOPLTR_DEBUG: print('	wet|'+storename)
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			valauto = valstored.automation
			if valauto: 
				autopath = automation.cvpj_autoloc(['slot', self.pluginid, 'wet'])
				self.convproj_obj.automation.data[autopath] = valauto
			param_obj = self.plugin_obj.params_slot.add('wet', float(valstored.value), 'float')
			param_obj.visual.name = 'Wet'

	def to_value(self, value, paramid, valuename, valtype):
		if TOPLTR_DEBUG: print('	param|'+paramid+'%'+str(value))
		param_obj = self.plugin_obj.params.add(paramid, value, valtype)
		if valuename: param_obj.visual.name = valuename

	def calc(self, storename, mathtype, val1, val2, val3, val4):
		if TOPLTR_DEBUG: print('	calc|'+'|'.join([str(x) for x in [storename, mathtype, val1, val2, val3, val4]]))
		if storename in self.cur_params: 
			self.cur_params[storename].calc(mathtype, val1, val2, val3, val4)

	def calc_clamp(self, storename, i_min, i_max):
		if storename in self.cur_params: 
			self.cur_params[storename].calc_clamp(i_min, i_max)

	def remap_ext_to_cvpj__pre__one(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				storename = 'param'+str(paramnum) if paramnum > -1 else p_cvpj['extid']
				vp = self.from_param(storename, 'ext_param_'+str(paramnum), p_cvpj['def_one'])
				yield vp, p_cvpj['extid'], paramnum
				if p_cvpj['mathtype'] == 'exp': vp.calc('pow', p_cvpj['mathval'], 0, 0, 0)
				vp.calc('from_one', p_cvpj['min'], p_cvpj['max'], 0, 0)
		self.plugin_obj.params.clear()

	def remap_ext_to_cvpj__pre(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				storename = 'param'+str(paramnum) if paramnum > -1 else p_cvpj['extid']
				vp = self.from_param(storename, 'ext_param_'+str(paramnum), p_cvpj['def_one'])
				if p_cvpj['mathtype'] == 'exp': vp.calc('pow', p_cvpj['mathval'], 0, 0, 0)
				vp.calc('from_one', p_cvpj['min'], p_cvpj['max'], 0, 0)
				yield vp, p_cvpj['extid'], paramnum
		self.plugin_obj.params.clear()

	def remap_ext_to_cvpj__post(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				storename = 'param'+str(paramnum) if paramnum > -1 else p_cvpj['extid']
				self.to_param(storename, p_cvpj['paramid'], p_cvpj['visname'])

	def remap_cvpj_to_ext__pre__one(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				storename = 'param'+str(paramnum) if paramnum > -1 else p_cvpj['extid']
				vp = self.from_param(storename, p_cvpj['paramid'], p_cvpj['def'])
				vp.calc_clamp(p_cvpj['min'], p_cvpj['max'])
				vp.calc('to_one', p_cvpj['min'], p_cvpj['max'], 0, 0)
				if p_cvpj['mathtype'] == 'exp': vp.calc('pow', 1/p_cvpj['mathval'], 0, 0, 0)
				yield vp, p_cvpj['extid'], paramnum

	def remap_cvpj_to_ext__pre(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				storename = 'param'+str(paramnum) if paramnum > -1 else p_cvpj['extid']
				vp = self.from_param(storename, p_cvpj['paramid'], p_cvpj['def'])
				yield vp, p_cvpj['extid'], paramnum
				vp.calc_clamp(p_cvpj['min'], p_cvpj['max'])
				vp.calc('to_one', p_cvpj['min'], p_cvpj['max'], 0, 0)
				if p_cvpj['mathtype'] == 'exp': vp.calc('pow', 1/p_cvpj['mathval'], 0, 0, 0)

			self.plugin_obj.params.clear()

	def remap_cvpj_to_ext__post(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				if paramnum > -1:
					self.to_param('param'+str(paramnum), 'ext_param_'+str(paramnum), p_ext['visname'])

	def remap_cvpj_to_ext_opt(self, remapname, ext_type):
		prm = globalstore.paramremap.get(remapname)
		foundparams = self.plugin_obj.params.list()
		auto_obj = self.convproj_obj.automation
		if prm:
			for p_cvpj, p_ext in prm.iter_cvpj_ext(ext_type):
				paramnum = p_ext['paramnum']
				if paramnum > -1:
					if self.plugin_obj.params not in foundparams:
						orgid = ['plugin',self.pluginid,p_cvpj['paramid']]
						auto_obj.calc(orgid, 'to_one', p_cvpj['min'], p_cvpj['max'], 0, 0)
						auto_obj.move(orgid, ['plugin',self.pluginid,'ext_param_'+str(paramnum)])
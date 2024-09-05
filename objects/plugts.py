# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import xtramath
from objects.convproj import automation
from objects.convproj import project as convproj
import math

class valuepack:
	def __init__(self, value, autodata, isbool):
		self.value = value
		self.automation = autodata
		self.isbool = isbool

	def calc(self, mathtype, val1, val2, val3, val4):
		self.value = xtramath.do_math(self.value, mathtype, val1, val2, val3, val4)
		if self.automation: self.automation.calc(mathtype, val1, val2, val3, val4)

	def calc_clamp(self, i_min, i_max):
		self.value = xtramath.clamp(self.value, i_min, i_max)

class transform_store:
	def __init__(self):
		self.cmds = []

		self.in_type = ''
		self.in_subtype = ''
		self.out_type = ''
		self.out_subtype = ''

		self.in_data = {}

		self.out_param = {}
		self.out_dataval = {}

		self.store_data = {}
		self.cur_params = {}

def txt_to_val(inputval):
	if inputval in ['false', 'False']: return False, True
	elif inputval in ['true', 'True']: return True, True
	else: return float(inputval), False

class plugtransform:
	def __init__(self):
		self.transforms = {}
		self.cur_params = {}
		self.store_data = {}
		self.filtername = ''

	def load_file(self, filepath):
		try:
			if filepath:
				f = open(filepath, "r")
				ddlines = [x.strip().split('#')[0].split('|') for x in f.readlines()]

				ts_active = False

				for ddline in ddlines:

					if ddline == ['']: ddline = []

					if ddline:
						if ddline[0] == 'new':
							ts_active = True
							ts_store_obj = self.transforms[ddline[1]] = transform_store()

						if ts_active: 
							if ddline[0] == 'in_param':
								paramname = ddline[2] if len(ddline) == 3 else ddline[1]
								defualtval, isbool = txt_to_val(ddline[3]) if len(ddline) == 4 else (0, False)
								ts_store_obj.in_data[ddline[1]] = [paramname, False, defualtval, isbool]
							elif ddline[0] == 'in_dataval': 
								paramname = ddline[2] if len(ddline) == 3 else ddline[1]
								defualtval, isbool = txt_to_val(ddline[3]) if len(ddline) == 4 else (0, False)
								ts_store_obj.in_data[ddline[1]] = [paramname, True, defualtval, isbool]
							elif ddline[0] == 'in_type': 
								if ddline[1]: ts_store_obj.in_type = ddline[1]
							elif ddline[0] == 'in_subtype': 
								if ddline[1]: ts_store_obj.in_subtype = ddline[1]
							elif ddline[0] == 'out_type': 
								if ddline[1]: ts_store_obj.out_type = ddline[1]
							elif ddline[0] == 'out_subtype': 
								if ddline[1]: ts_store_obj.out_subtype = ddline[1]

							#elif ddline[0] == 'out_param': ts_store_obj.out_param[ddline[1]] = [True, ddline[2], ddline[3] if len(ddline) == 4 else ddline[2]]
							#elif ddline[0] == 'out_v_param': ts_store_obj.out_param[ddline[1]] = [False, float(ddline[2]), ddline[3] if len(ddline) == 4 else ddline[2]]
							
							#elif ddline[0] == 'out_dataval': ts_store_obj.out_dataval[ddline[1]] = [True, ddline[2], ddline[3]]
							#elif ddline[0] == 'out_v_dataval': ts_store_obj.out_dataval[ddline[1]] = [False, float(ddline[2]), ddline[3]]
							elif ddline[0] != 'new': ts_store_obj.cmds.append(ddline)
							#print(ddline)


				print('[plugtransform] Loaded '+filepath)
		except:
			pass

	def set_filtername(self, val):
		self.filtername = val

	def store_wet(self, plugin_obj, convproj_obj, storename, pluginid):
		autopath = cvpj_autoloc(['slot', pluginid, 'wet'])
		d_value = plugin_obj.params_slot.get('wet', 1).value
		plugin_obj.params_slot.remove('wet')
		self.cur_params[storename] = valuepack(d_value, convproj_obj.automation.data[autopath] if autopath in convproj_obj.automation.data else None, False)

	def store_param(self, plugin_obj, convproj_obj, paramid, storename, pluginid, defualtval, isbool):
		autopath = cvpj_autoloc(['plugin', pluginid, paramid])
		p_value = plugin_obj.params.get(paramid, defualtval)
		d_value = p_value.value
		plugin_obj.params.remove(paramid)
		self.cur_params[storename] = valuepack(d_value, convproj_obj.automation.data[autopath] if autopath in convproj_obj.automation.data else None, p_value.type == 'bool')

	def store_dataval(self, plugin_obj, paramid, storename, defualtval, isbool):
		d_value = plugin_obj.datavals.get(paramid, defualtval)
		plugin_obj.datavals.remove(paramid)
		self.cur_params[storename] = valuepack(d_value, None, isbool)

	def calc(self, storename, mathtype, val1, val2, val3, val4):
		if storename in self.cur_params: self.cur_params[storename].calc(mathtype, val1, val2, val3, val4)

	def calc_clamp(self, storename, i_min, i_max):
		if storename in self.cur_params: self.cur_params[storename].calc_clamp(i_min, i_max)

	def to_store(self, storename, outname):
		self.store_data[outname] = self.cur_params[storename].value

	def out_auto(self, convproj_obj, pluginid, storename, paramid):
		if storename in self.cur_params: 
			if self.cur_params[storename].automation: 
				autopath = cvpj_autoloc(['plugin', pluginid, paramid])
				convproj_obj.automation.data[autopath] = self.cur_params[storename].automation

	def out(self, convproj_obj, plugin_obj, pluginid, storename, paramid, valuename):
		if storename in self.cur_params: 
			valstored = self.cur_params[storename]
			if valstored.automation: 
				autopath = cvpj_autoloc(['plugin', pluginid, paramid])
				convproj_obj.automation.data[autopath] = valstored.automation
			param_obj = plugin_obj.params.add(paramid, valstored.value, 'float' if not valstored.isbool else 'bool')
			param_obj.visual.name = valuename

	def out_wet(self, convproj_obj, plugin_obj, pluginid, storename):
		if storename in self.cur_params: 
			if self.cur_params[storename].automation: 
				autopath = cvpj_autoloc(['slot', pluginid, 'wet'])
				convproj_obj.automation.data[autopath] = self.cur_params[storename].automation
			param_obj = plugin_obj.params_slot.add('wet', self.cur_params[storename].value, 'float')
			param_obj.visual.name = 'Wet'


	def transform(self, tsname, convproj_obj, plugin_obj, pluginid, extra_json):
		self.store_data = {}
		self.cur_params = {}

		if tsname in self.transforms:
			cur_ts = self.transforms[tsname]

			#print('[plugtransform] Transforming',cur_ts.in_type+':'+cur_ts.in_subtype,'to',cur_ts.out_type+':'+cur_ts.out_subtype)

			for in_name, in_data in cur_ts.in_data.items():
				paramname, isdata, defualtval, isbool = in_data
				if not isdata: 
					self.store_param(plugin_obj, convproj_obj, paramname, in_name, pluginid, defualtval, isbool)
				else: 
					self.store_dataval(plugin_obj, paramname, in_name, defualtval, isbool)

			plugin_obj.params.clear()
			plugin_obj.type_set(cur_ts.out_type, cur_ts.out_subtype)

			filtername = ''
			for cmd in cur_ts.cmds:
				if cmd[0] == 'filter': filtername = cmd[1]
				elif not filtername or (filtername == self.filtername):
					if cmd[0] == 'in_wet': self.store_wet(plugin_obj, convproj_obj, pluginid, cmd[1])
					elif cmd[0] == 'calc':
						if cmd[2] == 'clamp': 
							self.calc_clamp(cmd[1], float(cmd[3]), float(cmd[4]))
						else:
							val1 = float(cmd[3]) if len(cmd) > 3 else 0
							val2 = float(cmd[4]) if len(cmd) > 4 else 0
							val3 = float(cmd[5]) if len(cmd) > 5 else 0
							val4 = float(cmd[6]) if len(cmd) > 6 else 0
							self.calc(cmd[1], cmd[2], val1, val2, val3, val4)

					elif cmd[0] == 'out_store': self.to_store(cmd[2], cmd[1])
					elif cmd[0] == 'out_auto': self.out_auto(convproj_obj, pluginid, cmd[2], cmd[1])
					elif cmd[0] == 'out_wet': self.out_wet(convproj_obj, plugin_obj, pluginid, cmd[1])
					elif cmd[0] == 'out_param': self.out(convproj_obj, plugin_obj, pluginid, cmd[2], cmd[1], cmd[3] if len(cmd) == 4 else cmd[2])
					elif cmd[0] == 'out_v_param': 
						param_obj = plugin_obj.params.add(cmd[1], float(cmd[2]), 'float')
						param_obj.visual.name = cmd[3] if len(cmd) == 4 else cmd[2]
					else:
						print(cmd)

			for paramid, paramdata in cur_ts.out_param.items():
				if paramdata[0]:
					self.out(convproj_obj, plugin_obj, pluginid, paramdata[1], paramid, paramdata[2])
				else:
					param_obj = plugin_obj.params.add(paramid, paramdata[1], 'float')
					param_obj.visual.name = paramdata[2]

			#for datavald in cur_ts.out_dataval.items():
			#	print(datavald)

		else:
			print('[plugtransform] '+tsname+' not defined')

	def get_storedval(self, name):
		return self.store_data[name] if name in self.store_data else 0

class storedtransform:
	storedts = {}

	def transform(self, filepath, ts_name, convproj_obj, plugin_obj, pluginid, extra_json):
		if filepath not in storedtransform.storedts: 
			storedtransform.storedts[filepath] = plugtransform()
			storedtransform.storedts[filepath].load_file(filepath)
		self.current_ts = storedtransform.storedts[filepath]
		self.current_ts.transform(ts_name, convproj_obj, plugin_obj, pluginid, extra_json)

	def get_storedval(self, name):
		return self.current_ts.get_storedval(name)
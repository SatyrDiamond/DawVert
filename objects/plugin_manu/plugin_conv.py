
from objects.plugin_manu import plugstatets
import json
import logging
import copy
from objects.valobjs import triplestr

logger_plugconv = logging.getLogger('plugconv')

logger_plugconv.setLevel(logging.DEBUG)

class plugconv_mapping:
	def __init__(self):
		self.daw_in = []
		self.daw_out = []
		self.priority = 0
		self.finish = False
		self.plugtype_in = triplestr()
		self.plugtype_out = []
		self.type = None
		self.file_pstr = None
		self.loaded_pstr = None
		self.plug_class = None

	def load(self):
		if self.type == 'pstr':
			if not self.loaded_pstr:
				plugstatets_obj = plugstatets.plugstatets()
				plugstatets_obj.load_from_file(self.file_pstr)
				self.loaded_pstr = plugstatets_obj
			return True

	def convert_plugin(self, convproj_obj, plugin_obj, pluginid, plugin_conv_obj, dawvert_intent):
		cond_match = plugin_obj.type.obj_wildmatch(self.plugtype_in)
		cond_inmat = plugin_conv_obj.current_daw_out not in self.daw_in

		if cond_match and cond_inmat:
			self.load()

			if self.type == 'pstr':
				if self.loaded_pstr:
					manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
					manu_obj.do_plugstatets(self.loaded_pstr)
					return True

			if self.type == 'plug':
				plug_class = self.plug_class
				return plug_class.convert(convproj_obj, plugin_obj, pluginid, dawvert_intent)


class convproj_plug_conv:
	def __init__(self):
		self.storage = {}
		self.active_queue = {}
		self.finish_ids = []
		self.current_daw_in = None
		self.current_daw_out = None
		self.supported_plugins_in = []
		self.supported_plugins_out = []

	def add_supported_plugin_in(self, plugstr):
		self.supported_plugins_in.append(triplestr.from_str(plugstr))

	def add_supported_plugin_out(self, plugstr):
		self.supported_plugins_out.append(triplestr.from_str(plugstr))

	def storage_clear(self):
		self.storage = {}
		self.active_queue = {}
		self.finish_ids = []
		self.supported_plugins_in = []
		self.supported_plugins_out = []

	def storage_pstr(self, filename):
		f = open(filename, 'r')
		pstrindex = json.load(f)
		for k, v in pstrindex.items():
			mappdata = plugconv_mapping()
			mappdata.type = 'pstr'
			if 'file' in v: mappdata.file_pstr = v['file']
			if 'daw_in' in v: mappdata.daw_in = v['daw_in']
			if 'daw_out' in v: mappdata.daw_out = v['daw_out']
			if 'plugtype_in' in v: mappdata.plugtype_in = triplestr.from_str(v['plugtype_in'])
			if 'plugtype_out' in v: mappdata.plugtype_out = [triplestr.from_str(x) for x in v['plugtype_out']]
			if 'priority' in v: mappdata.priority = v['priority']
			self.storage[k] = mappdata

	def storage_plugs(self):
		from plugins import base as dv_plugins
		dv_plugins.load_plugindir('plugconv', '')

		for shortname, plugdata in dv_plugins.iter_list('plugconv'):
			prop_obj = plugdata.prop_obj

			mappdata = plugconv_mapping()
			mappdata.type = 'plug'
			mappdata.daw_in = prop_obj.in_daws
			mappdata.daw_out = prop_obj.out_daws
			mappdata.plugtype_in = triplestr.from_str(prop_obj.in_plugin) 
			mappdata.plugtype_out = [triplestr.from_str(x) for x in prop_obj.out_plugins]
			mappdata.plug_class = plugdata.plug_obj

			self.storage[shortname] = mappdata

	def set_active(self):
		self.active_queue = {}
		self.finish_ids = []

		for k, mappdata in self.storage.items():
			priority = mappdata.priority

			cond_daw_in = (self.current_daw_in in mappdata.daw_in) if mappdata.daw_in else False
			cond_daw_out = (self.current_daw_out in mappdata.daw_out) if mappdata.daw_out else False

			if cond_daw_in:
				priority = -1000
			elif cond_daw_out:
				self.finish_ids.append(k)

			if mappdata.daw_out or mappdata.daw_in:
				if self.current_daw_in != self.current_daw_out: 
					cond_daw_out_a = (self.current_daw_out in mappdata.daw_out) if mappdata.daw_out else True
					if cond_daw_out_a:
						if priority not in self.active_queue: self.active_queue[priority] = []
						self.active_queue[priority].append([k, mappdata])
			#else:
			#	print(mappdata.plugtype_in, mappdata.plugtype_out)

		self.active_queue = dict(sorted(self.active_queue.items(), key=lambda item: item[0]))

	def convert_plugin(self, convproj_obj, plugin_obj, pluginid, dawvert_intent):
		#print(plugin_obj.type)
		#plugin_obj.params.debugtxt()

		if self.current_daw_in != self.current_daw_out:
			for num, i in self.active_queue.items():
				for k, mappdata in i:

					old_type = copy.copy(plugin_obj.type)
					is_converted = mappdata.convert_plugin(convproj_obj, plugin_obj, pluginid, self, dawvert_intent)
					if is_converted:
						#print(plugin_obj.type)
						#plugin_obj.params.debugtxt()
						#plugin_obj.filter.debugtxt()
						logger_plugconv.info('INT    | "%s" > "%s"' % (str(old_type), str(plugin_obj.type)))
						if k in self.finish_ids: 
							return 1
			#print('       | No equivalent to "%s" found or not supported' % (str(plugin_obj.type)))
			return 0
		else:
			return -1
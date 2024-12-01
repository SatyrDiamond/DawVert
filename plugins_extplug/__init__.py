import os
import traceback
import glob
import logging
from importlib import util

logger_plugins = logging.getLogger('plugins')

class info_bincodec:
	def __init__(self):
		self.datatype = None

	def from_dict(self, indict):
		if 'datatype' in indict: self.datatype = indict['datatype']

class info_plugparams:
	def __init__(self):
		self.supported_arch = [32, 64]
		self.supported_os = ['win', 'unix']
		self.supported_types = []
		self.bincodec = None
		self.cvpj_type = None
		self.cvpj_subtype = None
		self.id_vst2 = None
		self.id_vst3 = None
		self.id_clap = None

	def from_dict(self, indict):
		if 'supported_arch' in indict: self.supported_arch = indict['supported_arch']
		if 'supported_os' in indict: self.supported_os = indict['supported_os']
		if 'supported_types' in indict: self.supported_types = indict['supported_types']
		if 'bincodec' in indict: self.bincodec = indict['bincodec']
		if 'cvpj_type' in indict: self.cvpj_type = indict['cvpj_type']
		if 'cvpj_subtype' in indict: self.cvpj_subtype = indict['cvpj_subtype']
		if 'id_vst2' in indict: self.id_vst2 = indict['id_vst2']
		if 'id_vst3' in indict: self.id_vst3 = indict['id_vst3']
		if 'id_clap' in indict: self.id_clap = indict['id_clap']
		







class dv_extplugin:
	def __init__(self):
		self.name = ""
		self.shortname = ""
		self.type = ""
		self.prop = {}
		self.prop_obj = None
		self.plug_obj = None
		self.supported_autodetect = False
		self.priority = 100
		self.usable = True
		self.usable_meg = ''

	def propproc(self):
		if self.type == 'bincodec':
			propobj = info_bincodec()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'plugparams':
			propobj = info_plugparams()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

class plugin_selector:
	def __init__(self, plugintype, loaded_plugins):
		self.selected_shortname = None
		self.selected_plugin = None
		self.plugintype = plugintype
		self.pluginlist = loaded_plugins

	def unset(self):
		if self.selected_plugin:
			self.selected_shortname = None
			self.selected_plugin = None
			logger_plugins.info('Unset '+self.plugintype+' plugin')

	def set(self, dvplugsn):
		if self.plugintype in self.pluginlist:
			if self.selected_shortname != dvplugsn:
				if dvplugsn in self.pluginlist[self.plugintype]:
					self.selected_shortname = dvplugsn
					self.selected_plugin = self.pluginlist[self.plugintype][dvplugsn]
					logger_plugins.info('Set '+self.plugintype+' plugin: '+self.selected_shortname+' ('+ self.selected_plugin.name+')')
					return dvplugsn
			else:
				return dvplugsn

	def set_auto(self, indata):
		if self.plugintype in self.pluginlist:
			for shortname, dvplugin in self.pluginlist[self.plugintype].items():
				if dvplugin.supported_autodetect:
					funclist = dir(dvplugin.plug_obj)
					if 'detect' in funclist:
						try:
							detected_format = dvplugin.plug_obj.detect(indata)
							if detected_format:
								self.selected_shortname = shortname
								self.selected_plugin = self.pluginlist[self.plugintype][shortname]
								logger_plugins.info('Auto-Set '+self.plugintype+' plugin: '+self.selected_shortname+' ('+ self.selected_plugin.name+')')
								return shortname
						except PermissionError:
							pass
		self.unset()

	def set_auto_keepset(self, indata):
		if self.plugintype in self.pluginlist:
			for shortname, dvplugin in self.pluginlist[self.plugintype].items():
				if dvplugin.supported_autodetect:
					funclist = dir(dvplugin.plug_obj)
					if 'detect' in funclist:
						try:
							detected_format = dvplugin.plug_obj.detect(indata)
							if detected_format:
								self.selected_shortname = shortname
								self.selected_plugin = self.pluginlist[self.plugintype][shortname]
								logger_plugins.info('Auto-Set '+self.plugintype+' plugin: '+self.selected_shortname+' ('+ self.selected_plugin.name+')')
								return shortname
						except PermissionError:
							pass

	def get_prop_obj(self):
		return self.selected_plugin.prop_obj if self.selected_plugin else None

	def iter(self):
		plugqueue = []

		if self.plugintype in self.pluginlist:
			for shortname, dvplugin in self.pluginlist[self.plugintype].items():
				plugqueue.append((dvplugin.priority, shortname, dvplugin))

		plugqueue.sort()

		for priority, shortname, dvplugin in plugqueue: 
			yield shortname, dvplugin.plug_obj, dvplugin.prop_obj

	def iter_noorder(self):
		if self.plugintype in self.pluginlist:
			for shortname, dvplugin in self.pluginlist[self.plugintype].items():
				yield shortname, dvplugin.plug_obj, dvplugin.prop_obj

	def iter_dvp(self):
		if self.plugintype in self.pluginlist:
			for shortname, dvplugin in self.pluginlist[self.plugintype].items():
				yield shortname, dvplugin


class base:
	loaded_plugins = {}

	noname_num = 0

	def __init_subclass__(plcv_obj, **kwargs):
		super().__init_subclass__(**kwargs)
		in_object = plcv_obj()
		plugintype = in_object.is_dawvert_plugin()

		try:
			if plugintype not in base.loaded_plugins: base.loaded_plugins[plugintype] = {}
			dvplug_obj = dv_extplugin()
			if 'get_shortname' in dir(in_object): 
				dvplug_obj.shortname = in_object.get_shortname()
			else: 
				dvplug_obj.shortname = 'noname_'+str(base.noname_num)
				base.noname_num += 1

			if 'usable' in dir(in_object): 
				dvplug_obj.usable, dvplug_obj.usable_meg = in_object.usable()

			if dvplug_obj.shortname not in base.loaded_plugins:
				dvplug_obj.type = plugintype
				dvplug_obj.plug_obj = in_object
				if 'supported_autodetect' in dir(in_object): dvplug_obj.supported_autodetect = in_object.supported_autodetect()
				if 'get_priority' in dir(in_object): dvplug_obj.priority = in_object.get_priority()
				if 'get_name' in dir(in_object): dvplug_obj.name = in_object.get_name()
				in_object.get_prop(dvplug_obj.prop)
				dvplug_obj.propproc()
				base.loaded_plugins[plugintype][dvplug_obj.shortname] = dvplug_obj

		except Exception: 
			pass

	def create_selector(plug_type):
		selector_obj = plugin_selector(plug_type, base.loaded_plugins)
		return selector_obj

	def get_list(plug_type):
		return list(base.loaded_plugins[plug_type]) if plug_type in base.loaded_plugins else []

	def get_list_names(plug_type):
		return [n.name for _, n in base.loaded_plugins[plug_type].items()] if plug_type in base.loaded_plugins else []

	def get_list_prop_obj(plug_type):
		return [n.prop_obj for _, n in base.loaded_plugins[plug_type].items()] if plug_type in base.loaded_plugins else []

	def load_plugindir(plug_type, plugsetname):
		if plug_type in base.loaded_plugins: del base.loaded_plugins[plug_type]
		plugfolder = plug_type + ('_'+plugsetname if plugsetname else '')
		plugincount = 0
		for filename in glob.iglob(dirpath + '**/'+plugfolder+'/*.py', recursive=True):
			if not filename.startswith('.') and \
				not filename.endswith('__init__.py') and filename.endswith('.py'):
				try: 
					load_module(os.path.join(dirpath, filename))
					plugincount += 1
				except Exception: traceback.print_exc()
		if plug_type in base.loaded_plugins: 
			base.loaded_plugins[plug_type] = dict(sorted(base.loaded_plugins[plug_type].items()))
		logger_plugins.info('Loaded '+str(plugincount)+' '+plug_type+' Plugins.')

	def extplug_exists(pluginname, exttypes, subname):
		if 'extplugin' in base.loaded_plugins:
			if pluginname in base.loaded_plugins['extplugin']:
				plugd = base.loaded_plugins['extplugin'][pluginname]
				plugsup = plugd.plug_obj.check_exists(subname)
				for exttype in exttypes:
					if exttype in plugsup: return exttype
		return None

def load_module(path):
	name = os.path.split(path)[-1]
	spec = util.spec_from_file_location(name, path)
	module = util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


# Get current path
path = os.path.abspath(__file__)
dirpath = os.path.dirname(path)

import os
import traceback
import glob
import logging
from importlib import util

logger_plugins = logging.getLogger('plugins')

class info_daw:
	def __init__(self):
		self.name = ""
		self.shortname = ""
		self.object = None
		self.file_ext = ''
		self.plugin_arch = [32, 64]
		self.plugin_ext = []
		self.plugin_included = []

		self.audio_filetypes = []

		self.track_lanes = False
		self.track_nopl = False
		self.track_hybrid = False
		self.placement_cut = False
		self.placement_loop = []
		self.audio_nested = False
		self.audio_stretch = []
		self.fxrack = False
		self.fxrack_params = ['vol','enabled']
		self.auto_types = []
		self.fxchain_mixer = False
		self.fxtype = 'groupreturn'

		self.time_seconds = False

class info_plugconv:
	def __init__(self):
		self.object = None
		self.priority = 100
		self.in_plugins = []
		self.in_daws = []
		self.out_plugins = []
		self.out_daws = []

class info_plugconv_ext:
	def __init__(self):
		self.object = None
		self.priority = 100
		self.in_plugin = []
		self.ext_formats = []
		self.direction = 'to'
		self.plugincat = []

class info_extplug:
	def __init__(self):
		self.classfunc = None
		self.priority = 100
		self.ext_formats = []
		self.supported_bits = ['amd64']
		self.type = None
		self.subtype = None

class info_audiofileplug:
	def __init__(self):
		self.object = None
		self.priority = 100
		self.file_formats = []

class info_audioconvplug:
	def __init__(self):
		self.object = None
		self.priority = 100
		self.in_file_formats = []
		self.out_file_formats = []

class info_audiocodec:
	def __init__(self):
		self.name = ""

		self.encode_supported = False
		self.decode_supported = False

class base:
	plugins = []
	plugins_input = {}
	plugins_output = {}
	plugins_extplug = {}

	plugins_plugconv = []
	plugins_plugconv_ext = []

	plugins_input_auto = {}
	plugins_audio_file = {}
	plugins_audio_codec = {}
	plugins_audio_convert = {}

	plugselector_input = None
	plugselector_output = None

	def __init_subclass__(plcv_obj, **kwargs):
		super().__init_subclass__(**kwargs)
		in_object = plcv_obj()
		plugintype = in_object.is_dawvert_plugin()

		if plugintype == 'input': 
			dawinfo_obj = info_daw()
			dawinfo_obj.object = in_object
			in_object.getdawinfo(dawinfo_obj)
			shortname = in_object.getshortname()
			base.plugins_input[shortname] = dawinfo_obj
			dawinfo_obj.shortname = shortname
			if in_object.supported_autodetect(): 
				base.plugins_input_auto[shortname] = base.plugins_input[shortname]

		if plugintype == 'output': 
			dawinfo_obj = info_daw()
			dawinfo_obj.object = in_object
			in_object.getdawinfo(dawinfo_obj)
			shortname = in_object.getshortname()
			dawinfo_obj.shortname = shortname
			base.plugins_output[in_object.getshortname()] = dawinfo_obj

		if plugintype == 'plugconv': 
			plugconv_obj = info_plugconv()
			plugconv_obj.object = in_object
			in_object.getplugconvinfo(plugconv_obj)
			base.plugins_plugconv.append(plugconv_obj)

		if plugintype == 'plugconv_ext': 
			plugconv_ext_obj = info_plugconv_ext()
			plugconv_ext_obj.object = in_object
			in_object.getplugconvinfo(plugconv_ext_obj)
			base.plugins_plugconv_ext.append(plugconv_ext_obj)

		if plugintype == 'extplugin':
			extplug_obj = info_extplug()
			extplug_obj.classfunc = plcv_obj
			temp_obj = extplug_obj.classfunc()
			temp_obj.getextpluginfo(extplug_obj)
			shortname = temp_obj.getshortname()
			base.plugins_extplug[shortname] = extplug_obj

		if plugintype == 'audiofile':
			extplug_obj = info_audiofileplug()
			extplug_obj.object = plcv_obj()
			extplug_obj.object.getaudiofileinfo(extplug_obj)
			shortname = extplug_obj.object.getshortname()
			base.plugins_audio_file[shortname] = extplug_obj

		if plugintype == 'audiocodec':
			extplug_obj = info_audiocodec()
			extplug_obj.object = plcv_obj()
			extplug_obj.object.getaudiocodecinfo(extplug_obj)
			shortname = extplug_obj.object.getshortname()
			base.plugins_audio_codec[shortname] = extplug_obj

		if plugintype == 'audioconv':
			extplug_obj = info_audioconvplug()
			extplug_obj.object = plcv_obj()
			extplug_obj.object.getaudioconvinfo(extplug_obj)
			shortname = extplug_obj.object.getshortname()
			base.plugins_audio_convert[shortname] = extplug_obj

	def load_plugindir(plug_type):
		plugincount = 0
		for filename in glob.iglob(dirpath + '**/'+plug_type+'/*.py', recursive=True):
			if not filename.startswith('.') and \
			   not filename.endswith('__init__.py') and filename.endswith('.py'):
				try: 
					load_module(os.path.join(dirpath, filename))
					plugincount += 1
				except Exception: traceback.print_exc()
		logger_plugins.info('Loaded '+str(plugincount)+' '+plug_type+' Plugins.')

	def iter_extplug():
		for name, extplugitem in base.plugins_extplug.items(): 
			yield name, extplugitem

	def iter_plugconv():
		plugqueue = []
		for num, plugin in enumerate(base.plugins_plugconv): 
			plugqueue.append((plugin.priority, num))
		plugqueue.sort()
		for priority, num in plugqueue: 
			yield base.plugins_plugconv[num]

	def iter_plugconv_ext():
		plugqueue = []
		for num, plugin in enumerate(base.plugins_plugconv_ext): 
			plugqueue.append((plugin.priority, num))
		plugqueue.sort()
		for priority, num in plugqueue: 
			yield base.plugins_plugconv_ext[num]

	def extplug_exists(pluginname, exttypes, subname):
		if pluginname in base.plugins_extplug:
			plugsup = base.plugins_extplug[pluginname].classfunc.check_exists(subname)
			for exttype in exttypes:
				if exttype in plugsup: return exttype
		return None

			


	def detect_plugin(plugin_obj, ext_formats):
		for shortname, extplug_obj in base.plugins_extplug.items():
			is_supported = True in [(x in extplug_obj.ext_formats) for x in ext_formats]
			if is_supported:
				extplug_obj = extplug_obj.classfunc()
				is_match = extplug_obj.check(plugin_obj)
				if is_match: return True, extplug_obj
		return False, None


	def print_pluginfo():
		extended = False
		if not extended:
			logger_plugins.info('Inputs:',len(base.plugins_input))
			logger_plugins.info('Outputs:',len(base.plugins_output))
			logger_plugins.info('PlugConv (Internal):',len(base.plugins_plugconv))
			logger_plugins.info('PlugConv (External):',len(base.plugins_plugconv_ext))
		else:
			outtxt = ''
			for x, plug_obj in base.plugins_input.items():
				outtxt += x+('[a] ' if plug_obj.supported_autodetect(plug_obj) else ' ')
			logger_plugins.info('Input: '+outtxt)

			outtxt = ''
			for x, plug_obj in base.plugins_input.items(): outtxt += x+' '
			logger_plugins.info('Output: '+outtxt)


def load_module(path):
	name = os.path.split(path)[-1]
	spec = util.spec_from_file_location(name, path)
	module = util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


# Get current path
path = os.path.abspath(__file__)
dirpath = os.path.dirname(path)

base.load_plugindir('input')
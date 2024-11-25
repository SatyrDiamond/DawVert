import os
import traceback
import glob
import logging
from importlib import util
from objects.data_bytes import bytereader

logger_plugins = logging.getLogger('plugins')

class info_daw:
	def __init__(self):
		self.file_ext = []
		self.file_ext_detect = True
		self.plugin_ext_arch = [32, 64]
		self.plugin_ext_platforms = ['win', 'unix']
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
		self.fxtype = 'none'
		self.time_seconds = False
		self.projtype = '?'

	def from_dict(self, indict):
		if 'file_ext' in indict: self.file_ext = indict['file_ext']
		if 'file_ext_detect' in indict: self.file_ext_detect = indict['file_ext_detect']
		if 'plugin_ext_arch' in indict: self.plugin_ext_arch = indict['plugin_ext_arch']
		if 'plugin_ext_platforms' in indict: self.plugin_ext_platforms = indict['plugin_ext_platforms']
		if 'plugin_ext' in indict: self.plugin_ext = indict['plugin_ext']
		if 'plugin_included' in indict: self.plugin_included = indict['plugin_included']
		if 'audio_filetypes' in indict: self.audio_filetypes = indict['audio_filetypes']
		if 'track_lanes' in indict: self.track_lanes = indict['track_lanes']
		if 'track_nopl' in indict: self.track_nopl = indict['track_nopl']
		if 'track_hybrid' in indict: self.track_hybrid = indict['track_hybrid']
		if 'placement_cut' in indict: self.placement_cut = indict['placement_cut']
		if 'placement_loop' in indict: self.placement_loop = indict['placement_loop']
		if 'audio_nested' in indict: self.audio_nested = indict['audio_nested']
		if 'audio_stretch' in indict: self.audio_stretch = indict['audio_stretch']
		if 'fxrack' in indict: self.fxrack = indict['fxrack']
		if 'fxrack_params' in indict: self.fxrack_params = indict['fxrack_params']
		if 'auto_types' in indict: self.auto_types = indict['auto_types']
		if 'fxchain_mixer' in indict: self.fxchain_mixer = indict['fxchain_mixer']
		if 'fxtype' in indict: self.fxtype = indict['fxtype']
		if 'time_seconds' in indict: self.time_seconds = indict['time_seconds']
		if 'projtype' in indict: self.projtype = indict['projtype']

class info_plugconv:
	def __init__(self):
		self.in_plugins = []
		self.in_daws = []
		self.out_plugins = []
		self.out_daws = []

	def from_dict(self, indict):
		if 'in_plugins' in indict: self.in_plugins = indict['in_plugins']
		if 'in_daws' in indict: self.in_daws = indict['in_daws']
		if 'out_plugins' in indict: self.out_plugins = indict['out_plugins']
		if 'out_daws' in indict: self.out_daws = indict['out_daws']

class info_plugconv_ext:
	def __init__(self):
		self.in_plugin = []
		self.ext_formats = []
		self.direction = 'to'
		self.plugincat = []

	def from_dict(self, indict):
		if 'in_plugin' in indict: self.in_plugin = indict['in_plugin']
		if 'ext_formats' in indict: self.ext_formats = indict['ext_formats']
		if 'direction' in indict: self.direction = indict['direction']
		if 'plugincat' in indict: self.plugincat = indict['plugincat']

class info_extplug:
	def __init__(self):
		self.ext_formats = []
		self.supported_bits = ['amd64']
		self.type = None
		self.subtype = None

	def from_dict(self, indict):
		if 'ext_formats' in indict: self.ext_formats = indict['ext_formats']
		if 'supported_bits' in indict: self.supported_bits = indict['supported_bits']
		if 'type' in indict: self.type = indict['type']
		if 'subtype' in indict: self.subtype = indict['subtype']

class info_audiofileplug:
	def __init__(self):
		self.file_formats = []

	def from_dict(self, indict):
		if 'file_formats' in indict: self.file_formats = indict['file_formats']

class info_audioconvplug:
	def __init__(self):
		self.in_file_formats = []
		self.out_file_formats = []

	def from_dict(self, indict):
		if 'in_file_formats' in indict: self.in_file_formats = indict['in_file_formats']
		if 'out_file_formats' in indict: self.out_file_formats = indict['out_file_formats']

class info_audiocodec:
	def __init__(self):
		self.encode_supported = False
		self.decode_supported = False

	def from_dict(self, indict):
		if 'encode_supported' in indict: self.encode_supported = indict['encode_supported']
		if 'decode_supported' in indict: self.decode_supported = indict['decode_supported']

class info_externalsearch:
	def __init__(self):
		self.supported_os = False

	def from_dict(self, indict):
		if 'supported_os' in indict: self.supported_os = indict['supported_os']
		
class dv_plugin_bindetect:
	def __init__(self):
		self.used = False
		self.type = 'bytes'
		self.headers = []
		self.containers = []
		self.container_only = False

	def detect_container__file(self, inpath):
		if os.path.exists(inpath):
			byw_reader = bytereader.bytereader()
			byw_reader.load_file(inpath)
			for containerd in self.containers:

				if containerd[0] == 'gzip':
					bytepos = containerd[1] if len(containerd)>1 else 0
					byw_reader.seek(bytepos)
					if byw_reader.raw(3) == b'\x1f\x8b\x08':
						import gzip
						if self.type == 'bytes':
							try:
								d = open(inpath, 'rb')
								d.seek(bytepos)
								f = gzip.GzipFile(fileobj=d)
								return self.detect_headers__data(f.read(512))
							except:
								return False
						else:
							return False

				if containerd[0] == 'zlib':
					bytepos = containerd[1] if len(containerd)>1 else 0
					byw_reader.seek(bytepos)
					if byw_reader.raw(2) in [b'\x78\x08', b'\x78\x5E', b'\x78\x9C', b'\x78\xDA']:
						import zlib
						byw_reader.seek(bytepos)
						if self.type == 'bytes':
							try:
								decomp_obj = zlib.decompressobj(wbits=zlib.MAX_WBITS)
								data = decomp_obj.decompress(byw_reader.raw(1024), max_length=512)
								return self.detect_headers__data(data)
							except:
								return False
						else:
							return False

				if containerd[0] == 'zip':
					byw_reader.seek(0)
					if byw_reader.raw(4) == b'PK\x03\x04':
						import zipfile
						import fnmatch
						try:
							zip_data = zipfile.ZipFile(inpath, 'r')
							validnames = [x for x in zip_data.namelist() if fnmatch.fnmatch(x, containerd[1])]
							if validnames: return True
							else: return False
						except:
							return False
						return False
			return False
		else:
			return False

	def detect_headers__data(self, indata):
		if self.type == 'bytes':
			byw_reader = bytereader.bytereader(indata)
			outseries = []
			for x in self.headers:
				if byw_reader.end>x[0]+len(x[1]):
					byw_reader.seek(x[0])
					outseries.append(byw_reader.raw(len(x[1]))==x[1])
				else: outseries.append(False)
			return all(outseries) if outseries else False
		if self.type == 'xml':
			import xml.etree.ElementTree as ET
			try: 
				tree = ET.fromstring(indata)
				root = tree.getroot()
				for x in self.headers:
					if root.tag == x[0]: return True
				return False
			except:
				return False

	def detect_headers__file(self, inpath):
		if os.path.exists(inpath):
			if self.type == 'bytes':
				byw_reader = bytereader.bytereader()
				byw_reader.load_file(inpath)
				outseries = []
				for x in self.headers:
					if byw_reader.end>x[0]+len(x[1]):
						byw_reader.seek(x[0])
						outseries.append(byw_reader.raw(len(x[1]))==x[1])
					else: outseries.append(False)
				return all(outseries) if outseries else False
			if self.type == 'xml':
				import xml.etree.ElementTree as ET
				try: 
					tree = ET.parse(inpath)
					root = tree.getroot()
					for x in self.headers:
						if root.tag == x[0]: return True
					return False
				except:
					return False



class dv_plugin:
	def __init__(self):
		self.name = ""
		self.shortname = ""
		self.type = ""
		self.prop = {}
		self.prop_obj = None
		self.plug_obj = None
		self.priority = 100
		self.usable = True
		self.usable_meg = ''
		self.detectdef = dv_plugin_bindetect()

	def propproc(self):
		if self.type in ['input','output']:
			propobj = info_daw()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'plugconv':
			propobj = info_plugconv()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'plugconv_ext':
			propobj = info_plugconv_ext()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'extplugin':
			propobj = info_extplug()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'audiofile':
			propobj = info_audiofileplug()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'audiocodec':
			propobj = info_audiocodec()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'audioconv':
			propobj = info_audioconvplug()
			propobj.from_dict(self.prop)
			self.prop_obj = propobj

		if self.type == 'externalsearch':
			propobj = info_externalsearch()
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
		outname = self.set_auto_keepset(indata)
		if not outname: self.unset()
		return outname

	def set_auto_keepset(self, inpath):
		if self.plugintype in self.pluginlist:

			d_containers = {}
			d_non_containers = []

			outd = [(shortname, dvplugin.detectdef) for shortname, dvplugin in self.pluginlist[self.plugintype].items() if dvplugin.detectdef.used]

			outname = None

			for shortname, detectdef_obj in outd:
				detectf = detectdef_obj.detect_container__file(inpath)
				if detectf: outname = shortname
				elif not detectdef_obj.container_only:
					ddd = detectdef_obj.detect_headers__file(inpath)
					if ddd: 
						outname = shortname

			if outname:
				self.selected_shortname = outname
				self.selected_plugin = self.pluginlist[self.plugintype][outname]
				logger_plugins.info('Auto-Set '+self.plugintype+' plugin: '+self.selected_shortname+' ('+ self.selected_plugin.name+')')
				return outname

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
			dvplug_obj = dv_plugin()
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

				if 'get_priority' in dir(in_object): dvplug_obj.priority = in_object.get_priority()
				if 'get_name' in dir(in_object): dvplug_obj.name = in_object.get_name()
				if 'get_detect_info' in dir(in_object): 
					dvplug_obj.detectdef.used = True
					in_object.get_detect_info(dvplug_obj.detectdef)
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

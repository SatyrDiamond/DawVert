
#datadef = dv_datadef.datadef('./data_main/datadef/openmpt.ddef')
#dataset = dv_dataset.dataset('./data_main/dataset/openmpt.dset')
from functions_plugin_ext import plugin_vst2

class openmpt_plugin:
	def __init__(self):
		self.type = None
		self.id = None
		self.route = None
		self.mix = None
		self.gain = None
		self.output_routing = None
		self.name = None
		self.libname = None
		self.data = None
		self.params = None

	def read(self, song_file):
		self.type = song_file.raw(4)
		self.id = song_file.uint32()
		self.route = song_file.uint8()
		self.mix = song_file.uint8()
		self.gain = song_file.uint8()
		song_file.skip(1)
		self.output_routing = song_file.uint32()
		song_file.skip(16)
		self.name = song_file.string(32, encoding="windows-1252")
		self.libname = song_file.string(64, encoding="windows-1252")

		datalen = song_file.uint32()
		if self.type == b'DBM0':
			song_file.skip(4)
			self.params = song_file.l_uint8(datalen-4)
		elif self.type == b'SymM':
			song_file.skip(4)
			self.params = song_file.l_uint8(datalen-4)
		else:
			self.data = song_file.raw(datalen)

	def to_cvpj(self, fxnum, convproj_obj):
		pluginid = 'FX'+str(fxnum)
		if self.type == b'OMXD':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'directx', self.libname)
			plugin_obj.from_bytes(self.data, 'directx', 'directx', 'plugin', self.libname.lower(), None)
		elif self.type == b'PtsV':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'external', 'vst2', None)
			plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', 'win', self.id, 'chunk', self.data, 0)
		elif self.type == b'DBM0':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'digibooster', 'pro_echo')
			plugin_obj.params.add('delay', self.params[0], 'int')
			plugin_obj.params.add('fb', self.params[1], 'int')
			plugin_obj.params.add('wet', self.params[2], 'int')
			plugin_obj.params.add('cross_echo', self.params[3], 'int')
		elif self.type == b'SymM':
			plugin_obj = convproj_obj.plugin__add(pluginid, 'native', 'symmod', 'echo')
			plugin_obj.params.add('type', self.params[0], 'int')
			plugin_obj.params.add('delay', self.params[1], 'int')
			plugin_obj.params.add('fb', self.params[2], 'int')
		if plugin_obj and self.name:
			if self.name: plugin_obj.visual.name = self.name

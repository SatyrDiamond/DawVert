
from plugin_extsearch import base as base_extsearch
import platform
import os
import dawdreamer
import time

class scanstate:
	def __init__(self):
		pluginnum = 0
		maxplugs = 0

class paramdata:
	def __init__(self):
		self.uniqueid = None
		self.plugtype = None
		self.audio_num_inputs = None
		self.audio_num_outputs = None
		self.num_params = None
		self.params = {}


def probe_vst2(platformtxt, pluginfo_obj, scanstate_obj, paramdata_obj):
	engine = dawdreamer.RenderEngine(44100, 128)
	vstarch, vstpath = pluginfo_obj.find_locpath([32, 64])

	try:
		if vstpath:
			#print(str(scanstate_obj.pluginnum)+'/'+str(scanstate_obj.maxplugs)+' | Probing '+pluginfo_obj.name+'...')
			synth = engine.make_plugin_processor("testplug", vstpath)

			paramdata = synth.get_parameters_description()
			paramdata_obj.audio_num_inputs = synth.get_num_input_channels()
			paramdata_obj.audio_num_outputs = synth.get_num_output_channels()
			paramdata_obj.num_params = len(paramdata)

			paramdata_obj.plugtype = 'vst2'
			paramdata_obj.uniqueid = str(pluginfo_obj.id)
			for param in paramdata:
				p_index = 'ext_param_'+str(param['index'])
				p_name = param['name']
				p_min = param['min']
				p_max = param['max']
				p_def = param['defaultValue']
				paramdata_obj.params[p_index] = [False, 'float', float(p_def), float(p_min), float(p_max), p_name]

			engine.remove_processor("testplug")
	except:
		pass



if __name__ == "__main__":
	from objects import manager_extplug

	plugsearch_classes = base_extsearch
	
	validplugs = []
	
	platform_architecture = platform.architecture()
	if platform_architecture[1] == 'WindowsPE': platformtxt = 'win'
	else: platformtxt = 'lin'
	
	for plugconvplugin in plugsearch_classes.plugins:
		plco_class_data = plugconvplugin()
		try:
			if plco_class_data.is_dawvert_plugin() == 'externalsearch' and plco_class_data.issupported(platformtxt): 
				validplugs.append(plco_class_data)
		except: pass
	
	homepath = os.path.expanduser("~")
	
	for plugsearchclass in validplugs:
		plugsearchclass.import_plugins(platformtxt, homepath)
	
	manager_extplug.write_db()
	
	useprobe = 1

	useprobe = 0
	if useprobe == 0:
		answer = input("Probe Plugins for Info? [y/n]")
		if answer.lower() == "y": useprobe = 1
	
	if useprobe == 1:
		pluginfo_objs = manager_extplug.vst2_getall()
		numplugs = len(pluginfo_objs)

		scanstate_obj = scanstate()
		scanstate_obj.maxplugs = numplugs
		scanstate_obj.pluginnum = 0

		while scanstate_obj.pluginnum != scanstate_obj.maxplugs:
			pluginfo_obj = pluginfo_objs[scanstate_obj.pluginnum]
			paramdata_obj = paramdata()

			is_exists = manager_extplug.extplug_dataset.params_exists('vst2', str(pluginfo_obj.id))

			if pluginfo_obj.id and not is_exists:
				idstr = str(pluginfo_obj.id)
				probe_vst2(platformtxt, pluginfo_obj, scanstate_obj, paramdata_obj)
				manager_extplug.extplug_dataset.object_add('vst2', idstr)
				manager_extplug.extplug_dataset.params_create(paramdata_obj.plugtype, idstr)
				for n, v in paramdata_obj.params.items():
					manager_extplug.extplug_dataset.params_i_add(paramdata_obj.plugtype, idstr, n)
					manager_extplug.extplug_dataset.params_i_set(paramdata_obj.plugtype, idstr, n, v)
				pluginfo_obj.audio_num_inputs = paramdata_obj.audio_num_inputs
				pluginfo_obj.audio_num_outputs = paramdata_obj.audio_num_outputs
				pluginfo_obj.num_params = paramdata_obj.num_params
				manager_extplug.vst2_add(pluginfo_obj, platformtxt)
				manager_extplug.write_db()
			scanstate_obj.pluginnum += 1


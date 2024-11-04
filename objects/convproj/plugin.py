# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath
from objects import globalstore
from objects.valobjs import triplestr
from plugins import base as dv_plugins
import wave as audio_wav
import base64
import struct
import copy
import logging

from objects.convproj import sample_entry
from objects.convproj import params
from objects.convproj import visual
from objects.convproj import eqfilter
from objects.convproj import autopoints
from objects.convproj import envelope
from objects.convproj import wave
from objects.convproj import harmonics
from objects.convproj import time
from objects.convproj import chord
from objects.convproj import plugstate
from objects.convproj import midi_inst
from objects import plugdatamanu

logger_plugins = logging.getLogger('plugins')
logger_plugconv = logging.getLogger('plugconv')

class cvpj_audioports:
	def __init__(self):
		self.num_inputs = 2
		self.num_outputs = 2
		self.ports = [[0],[1]]

	def __getitem__(self, index):
		return self.ports[index]

	def append(self, val):
		self.ports.append(val)

	def setnums_auto(self, i_in, i_out):
		self.num_inputs = i_in if i_in != None else 2
		self.num_outputs = i_out if i_out != None else 2
		self.ports = []
		for x in range(max(self.num_inputs, self.num_outputs)):
			self.ports.append([x])

class cvpj_plugin:

	extplug_selector = dv_plugins.create_selector('extplugin')

	def __init__(self):
		self.type = triplestr()
		self.visual = visual.cvpj_visual()
		self.params_slot = params.cvpj_paramset()
		self.filerefs_global = {}
		self.datavals_global = params.cvpj_datavals()
		self.datavals_cvpj = params.cvpj_datavals()
		self.visual_custom = {}
		self.programs = {0: plugstate.cvpj_plugin_state()}
		self.audioports = cvpj_audioports()
		self.role = 'fx'
		self.midi = midi_inst.cvpj_midi_inst()
		self.current_program = 0
		self.program_used = False
		self.set_program(0)

	def set_program(self, prenum):
		if prenum not in self.programs: 
			self.programs[prenum] = plugstate.cvpj_plugin_state()
			self.program_used = True

		self.current_program = prenum
		self.state = self.programs[prenum]

		self.params = self.state.params
		self.datavals = self.state.datavals
		self.poly = self.state.poly
		self.bytesdata = self.state.bytesdata
		self.regions = self.state.regions
		self.sampleregions = self.state.sampleregions
		self.env_adsr = self.state.env_adsr
		self.env_points = self.state.env_points
		self.env_points_vars = self.state.env_points_vars
		self.env_blocks = self.state.env_blocks
		self.filter = self.state.filter
		self.named_filter = self.state.named_filter
		self.eq = self.state.eq
		self.named_eq = self.state.named_eq
		self.lfos = self.state.lfos
		self.waves = self.state.waves
		self.harmonics = self.state.harmonics
		self.wavetables = self.state.wavetables
		self.filerefs = self.state.filerefs
		self.sampleparts = self.state.sampleparts
		self.oscs = self.state.oscs
		self.timing = self.state.timing
		self.chord = self.state.chord
		self.arrays = self.state.arrays
		self.midi = self.state.midi
		self.preset = self.state.preset
		self.audios = self.state.audios
		self.modulations = self.state.modulations

	def clear_prog_keep(self, prenum):
		old_poly = self.poly
		old_bytesdata = self.bytesdata
		old_regions = self.regions
		old_sampleregions = self.sampleregions
		old_env_adsr = self.env_adsr
		old_env_points = self.env_points
		old_env_points_vars = self.env_points_vars
		old_env_blocks = self.env_blocks
		old_filter = self.filter
		old_named_filter = self.named_filter
		old_eq = self.eq
		old_named_eq = self.named_eq
		old_lfos = self.lfos
		old_waves = self.waves
		old_harmonics = self.harmonics
		old_wavetables = self.wavetables
		old_filerefs = self.filerefs
		old_sampleparts = self.sampleparts
		old_oscs = self.oscs
		old_timing = self.timing
		old_chord = self.chord
		old_arrays = self.arrays
		old_midi = self.midi
		old_preset = self.preset
		old_audios = self.audios
		old_modulations = self.modulations

		self.current_program = prenum
		self.programs = {prenum: plugstate.cvpj_plugin_state()}
		self.state = self.programs[prenum]

		self.params = self.state.params
		self.datavals = self.state.datavals
		self.poly = self.state.poly = old_poly
		self.bytesdata = self.state.bytesdata = old_bytesdata
		self.regions = self.state.regions = old_regions
		self.sampleregions = self.state.sampleregions = old_sampleregions
		self.env_adsr = self.state.env_adsr = old_env_adsr
		self.env_points = self.state.env_points = old_env_points
		self.env_points_vars = self.state.env_points_vars = old_env_points_vars
		self.env_blocks = self.state.env_blocks = old_env_blocks
		self.filter = self.state.filter = old_filter
		self.named_filter = self.state.named_filter = old_named_filter
		self.eq = self.state.eq = old_eq
		self.named_eq = self.state.named_eq = old_named_eq
		self.lfos = self.state.lfos = old_lfos
		self.waves = self.state.waves = old_waves
		self.audios = self.state.audios = old_audios
		self.harmonics = self.state.harmonics = old_harmonics
		self.wavetables = self.state.wavetables = old_wavetables
		self.filerefs = self.state.filerefs = old_filerefs
		self.sampleparts = self.state.sampleparts = old_sampleparts
		self.oscs = self.state.oscs = old_oscs
		self.timing = self.state.timing = old_timing
		self.chord = self.state.chord = old_chord
		self.arrays = self.state.arrays = old_arrays
		self.midi = self.state.midi = old_midi
		self.preset = self.state.preset = old_preset
		self.modulations = self.state.modulations = old_modulations

	def move_prog(self, prenum):
		self.programs[prenum] = self.state = self.programs.pop(self.current_program)
		self.current_program = prenum

	def type_set(self, i_category, i_type, i_subtype):
		self.type.set(i_category, i_type, i_subtype)

	def type_get(self):
		return self.type.get_list()

	def get_type_visual(self):
		return str(self.type)

	def replace_hard(self, i_category, i_type, i_subtype):
		self.type.set(i_category, i_type, i_subtype)
		self.programs = {0: plugstate.cvpj_plugin_state()}
		self.set_program(0)
		self.program_used = False
		self.data = {}

	def replace_keepprog(self, i_category, i_type, i_subtype):
		self.type.set(i_category, i_type, i_subtype)
		self.programs = {self.current_program: plugstate.cvpj_plugin_state()}
		self.clear_prog_keep(self.current_program)
		self.program_used = False
		self.data = {}

	def replace(self, i_category, i_type, i_subtype):
		self.type.set(i_category, i_type, i_subtype)
		self.programs = {0: plugstate.cvpj_plugin_state()}
		self.clear_prog_keep(0)
		self.program_used = False
		self.data = {}

	def check_match(self, i_category, i_type, i_subtype):
		return self.type.check_match(i_category, i_type, i_subtype)

	def check_matchmulti(self, i_category, i_type, i_subtypes):
		return self.type.check_matchmulti(i_category, i_type, i_subtypes)

	def check_wildmatch(self, i_category, i_type, i_subtype):
		return self.type.check_wildmatch(i_category, i_type, i_subtype)

	def check_str_multi(self, strlist):
		return True in [self.check_wildmatch(x[0], x[1], x[2]) for x in strlist]

	# -------------------------------------------------- fxdata
	def fxdata_add(self, i_enabled, i_wet):
		if i_enabled != None: self.params_slot.add('enabled', i_enabled, 'bool')
		if i_wet != None: self.params_slot.add('wet', i_wet, 'float')

	def fxdata_get(self):
		i_enabled = self.params_slot.get('enabled', 1).value
		i_wet = self.params_slot.get('wet', 1).value
		return i_enabled, i_wet

	# -------------------------------------------------- visual_custom
	def viscustom_add(self, name, value):
		self.visual_custom[name] = value

	def viscustom_get(self, name, fallback):
		return self.visual_custom[name] if name in self.visual_custom else fallback

	# -------------------------------------------------- dataset
	def from_bytes(self, in_bytes, ds_name, df_name, cat_name, obj_name, structname): 
		return self.state.from_bytes(in_bytes, ds_name, df_name, cat_name, obj_name, structname)

	def to_bytes(self, ds_name, df_name, cat_name, obj_name, structname):
		return self.state.to_bytes(ds_name, df_name, cat_name, obj_name, structname)

	def dset_param__add(self, p_id, p_value, dset_param):
		return self.state.dset_param__add(p_id, p_value, dset_param)

	def add_from_dset(self, p_id, p_value, dset, ds_cat, ds_group): 
		return self.state.add_from_dset(p_id, p_value, dset, ds_cat, ds_group)

	def dset_obj__add_param(self, dataset_obj, i_dict):
		return self.state.dset_obj__add_param(dataset_obj, i_dict)

	def param_dict_dataset_set(self, ds_name, catname, pluginname):
		return self.state.param_dict_dataset_set(ds_name, catname, pluginname)

	# -------------------------------------------------- rawdata
	def rawdata_add(self, i_name, i_databytes): return self.state.rawdata_add(i_name, i_databytes)
	def rawdata_add_b64(self, i_name, i_databytes): return self.state.rawdata_add_b64(i_name, i_databytes)
	def rawdata_get(self, i_name): return self.state.rawdata_get(i_name)
	def rawdata_get_b64(self, i_name): return self.state.rawdata_get_b64(i_name)

	# -------------------------------------------------- sampleregions
	def sampleregion_add(self, i_min, i_max, i_middle, i_data, **kwargs):
		return self.state.sampleregion_add(i_min, i_max, i_middle, i_data, **kwargs)

	# -------------------------------------------------- regions
	def region_add(self, i_name, i_min, i_max, i_value):
		return self.state.region_add(i_name, i_min, i_max, i_value)

	def regions_get(self, i_name):
		return self.state.regions_get(i_name)

	# -------------------------------------------------- asdr_env
	def env_asdr_add(self, a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount): return self.state.env_asdr_add(a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount)
	def env_asdr_tension_add(self, a_type, t_attack, t_decay, t_release): return self.state.env_asdr_tension_add(a_type, t_attack, t_decay, t_release)
	def env_asdr_get(self, a_type): return self.state.env_asdr_get(a_type)
	def env_asdr_get_exists(self, a_type): return self.state.env_asdr_get_exists(a_type)
	def env_asdr_list(self): return self.state.env_asdr_list()
	def env_asdr_copy(self, o_type, n_type): return self.state.env_asdr_copy(o_type, n_type)

	# -------------------------------------------------- env_blocks
	def env_blocks_add(self, a_type, a_vals, a_time, a_max, a_loop, a_release): return self.state.env_blocks_add(a_type, a_vals, a_time, a_max, a_loop, a_release)
	def env_blocks_get(self, a_type): return self.state.env_blocks_get(a_type)
	def env_blocks_get_exists(self, a_type): return self.state.env_blocks_get_exists(a_type)
	def env_blocks_list(self): return self.state.env_blocks_list()

	# -------------------------------------------------- env_points
	def env_points_add(self, a_type, time_ppq, time_float, val_type): return self.state.env_points_add(a_type, time_ppq, time_float, val_type)
	def env_points_get(self, a_type): return self.state.env_points_get(a_type)
	def env_points_get_exists(self, a_type): return self.state.env_points_get_exists(a_type)
	def env_points_addvar(self, a_type, p_name, p_value): return self.state.env_points_addvar(a_type, p_name, p_value)
	def env_points_copy(self, o_type, n_type): return self.state.env_points_copy(o_type, n_type)

	def env_points_from_blocks(self, a_type): return self.state.env_points_from_blocks(a_type)
	def env_asdr_from_points(self, a_type): return self.state.env_asdr_from_points(a_type)
	def env_points_list(self): return self.state.env_points_list()

	# -------------------------------------------------- lfo
	def lfo_add(self, a_type): return self.state.lfo_add(a_type)
	def lfo_get(self, a_type): return self.state.lfo_get(a_type)
	def lfo_get_exists(self, a_type): return self.state.lfo_get_exists(a_type)
	def lfo_list(self): return self.state.lfo_list()
	def lfo_copy(self, o_type, n_type): return self.state.lfo_copy(o_type, n_type)

	# -------------------------------------------------- osc
	def osc_add(self): return self.state.osc_add()
	def osc_get(self, i_num): return self.state.osc_get(i_num)

	# -------------------------------------------------- wave
	def wave_add(self, i_name): return self.state.wave_add(i_name)
	def wave_get(self, i_name): return self.state.wave_get(i_name)
	def wave_get_exists(self, i_name): return self.state.wave_get_exists(i_name)
	def wave_list(self): return self.state.wave_list()
	def wave_copy(self, o_type, n_type): return self.state.wave_get(o_type, n_type)

	# -------------------------------------------------- audio
	def audio_add(self, i_name): return self.state.audio_add(i_name)
	def audio_get(self, i_name): return self.state.audio_get(i_name)
	def audio_get_exists(self, i_name): return self.state.audio_get_exists(i_name)
	def audio_list(self): return self.state.audio_list()

	# -------------------------------------------------- timing
	def timing_add(self, i_name): return self.state.timing_add(i_name)
	def timing_get(self, i_name): return self.state.timing_get(i_name)
	def timing_list(self): return self.state.timing_list()

	# -------------------------------------------------- chord
	def chord_add(self, i_name): return self.state.chord_add(i_name)
	def chord_get(self, i_name): return self.state.chord_get(i_name)
	def chord_list(self):  return self.state.chord_list()

	# -------------------------------------------------- harmonics
	def harmonics_add(self, i_name): return self.state.harmonics_add(i_name)
	def harmonics_get(self, i_name): return self.state.harmonics_get(i_name)
	def harmonics_list(self): return self.state.harmonics_list()

	# -------------------------------------------------- wave
	def wavetable_add(self, i_name): return self.state.wavetable_add(i_name)
	def wavetable_get(self, i_name): return self.state.wavetable_get(i_name)
	def wavetable_get_exists(self, i_name): return self.state.wavetable_get_exists(i_name)
	def wavetable_list(self): return self.state.wavetable_list()

	# -------------------------------------------------- modulations
	def modulation_add(self): return self.state.modulation_add()
	def modulation_add_native(self, modfrom, modto): return self.state.modulation_add_native(modfrom, modto)
	def modulation_iter(self): return self.state.modulation_iter()
			
	# -------------------------------------------------- fileref_global

	def get_fileref_global(self, fileref_name, convproj_obj): 
		if fileref_name in self.filerefs_global:
			fileref_id = self.filerefs_global[fileref_name]
			return convproj_obj.get_fileref(fileref_id)
		return False, None

	def getpath_fileref_global(self, convproj_obj, refname, os_type, nofile): 
		ref_found, fileref_obj = self.get_fileref_global(refname, convproj_obj)
		return fileref_obj.get_path(os_type, nofile) if ref_found else ''

	# -------------------------------------------------- fileref
	def get_fileref(self, fileref_name, convproj_obj): 
		return self.state.get_fileref(fileref_name, convproj_obj)

	def getpath_fileref(self, convproj_obj, refname, os_type, nofile): 
		return self.state.getpath_fileref(convproj_obj, refname, os_type, nofile)

	# -------------------------------------------------- samplepart

	def samplepart_add(self, i_name): return self.state.samplepart_add(i_name)
	def samplepart_copy(self, o_name, i_name): return self.state.samplepart_copy(o_name, i_name)
	def samplepart_move(self, o_name, i_name): return self.state.samplepart_move(o_name, i_name)
	def samplepart_remove(self, i_name): return self.state.samplepart_remove(i_name)
	def samplepart_get(self, i_name):  return self.state.samplepart_get(i_name)

	# -------------------------------------------------- eq
	def eq_add(self): return self.state.eq_add()
	def eq_to_8limited(self, convproj_obj, pluginid): return self.state.eq.to_8limited(convproj_obj, pluginid)

	# -------------------------------------------------- named_eq
	def named_eq_add(self, eq_name): return self.state.named_eq_add(eq_name)

	# -------------------------------------------------- named_filter
	def named_filter_add(self, filt_name):  return self.state.named_filter_add(filt_name)
	def named_filter_get(self, filt_name): return self.state.named_filter_get(filt_name)
	def named_filter_get_exists(self, filt_name): return self.state.named_filter_get_exists(filt_name)
	def named_filter_rename(self, filt_name, new_name): return self.state.named_filter_rename(filt_name, new_name)

	# -------------------------------------------------- array
	def array_add(self, arr_name, values): return self.state.array_add(arr_name, values)
	def array_get(self, arr_name, missingnum): return self.state.array_get(arr_name, missingnum)
	def array_get_vl(self, arr_name): return self.state.array_get_vl(arr_name)
	def array_resize(self, arr_name, newsize): return self.state.array_resize(arr_name, newsize)
	def array_rename(self, arr_name, new_name): return self.state.array_rename(arr_name, new_name)

	# -------------------------------------------------- manu

	def create_manu_obj(self, convproj_obj, pluginid):
		return plugdatamanu.plug_manu(self, convproj_obj, pluginid)

	def plugts_transform(self, plugts_path, plugts_tr, convproj_obj, pluginid):
		globalstore.plugts.load(plugts_path, plugts_path)
		plugts_obj = globalstore.plugts.get(plugts_path)

		if plugts_obj:
			if plugts_tr in plugts_obj.transforms:
				trobj = plugts_obj.transforms[plugts_tr]

				if self.type.obj_wildmatch(trobj.in_type):
					manu_obj = self.create_manu_obj(convproj_obj, pluginid)
					for paramid, pltrpipe_obj in trobj.in_data.items():
						if pltrpipe_obj.type == 'param':
							manu_obj.from_param(pltrpipe_obj.v_to, pltrpipe_obj.v_from, pltrpipe_obj.value)
						if pltrpipe_obj.type == 'wet':
							manu_obj.from_wet(paramid, pltrpipe_obj.value)

					for procdata in trobj.proc:
						if procdata[0] == 'calc':
							calcvals = [0,0,0,0]
							for n,x in enumerate(procdata[3:]): calcvals[n] = float(x)
							manu_obj.calc(procdata[1], procdata[2], calcvals[0], calcvals[1], calcvals[2], calcvals[3])

					self.replace(trobj.out_type.category, trobj.out_type.type, trobj.out_type.subtype)

					for paramid, pltrpipe_obj in trobj.out_data.items():
						if pltrpipe_obj.type == 'param':
							iffound = manu_obj.to_param(pltrpipe_obj.v_from, pltrpipe_obj.v_to, pltrpipe_obj.name)
							if not iffound: manu_obj.to_value(pltrpipe_obj.value, pltrpipe_obj.v_to, pltrpipe_obj.name, pltrpipe_obj.valuetype)
					#print(trobj.proc)
					
	# -------------------------------------------------- convert

	def convert_internal(self, convproj_obj, pluginid, target_daw, dv_config):
		plugconv_int_selector = dv_plugins.create_selector('plugconv')
		converted_val = 2
		for shortname, dvplug_obj, prop_obj in plugconv_int_selector.iter():
			ismatch = self.check_str_multi(prop_obj.in_plugins)
			correctdaw = (target_daw in prop_obj.out_daws) if prop_obj.out_daws else True
			if ismatch and correctdaw:
				converted_val_p = dvplug_obj.convert(convproj_obj, self, pluginid, dv_config)
				if converted_val_p < converted_val: converted_val = converted_val_p
				if converted_val == 0: break
		return converted_val

	def convert_external(self, convproj_obj, pluginid, target_extplugs, dv_config):
		from functions import extpluglog
		plugconv_ext_selector = dv_plugins.create_selector('plugconv_ext')
		extpluglog.extpluglist.clear()
		ext_conv_val = False
		for shortname, dvplug_obj, prop_obj in plugconv_ext_selector.iter():
			ismatch = self.check_wildmatch(prop_obj.in_plugin[0], prop_obj.in_plugin[1], prop_obj.in_plugin[2])
			extmatch = True in [(x in target_extplugs) for x in prop_obj.ext_formats]
			catmatch = data_values.list__only_values(prop_obj.plugincat, dv_config.extplug_cat)
	
			if ismatch and extmatch and catmatch:
				ext_conv_val = dvplug_obj.convert(convproj_obj, self, pluginid, dv_config, target_extplugs)
				if ext_conv_val: break
		return ext_conv_val

	# -------------------------------------------------- ext

	def external_make_compat(self, convproj_obj, ext_daw_out):
		if self.check_wildmatch('external', None, None):
			in_exttype = self.type.type
			if not in_exttype in ext_daw_out:
				for shortname, dvplug_obj, prop_obj in cvpj_plugin.extplug_selector.iter():
					plugcheck = dvplug_obj.check_plug(self)
					if plugcheck:
						funclist = dir(dvplug_obj)
						if 'decode_data' in funclist and 'encode_data' in funclist:
							try:
								of_ext_compat = None
								for x in prop_obj.ext_formats:
									if x in ext_daw_out: 
										of_ext_compat = x
										break

								if of_ext_compat:
									chunkdata = self.rawdata_get('chunk')
									success = dvplug_obj.decode_data(plugcheck, self)
									if success:
										dvplug_obj.encode_data(of_ext_compat, convproj_obj, self, None)
										logger_plugins.info(shortname+': Converted from '+in_exttype+' to '+of_ext_compat)
										return True
							except:
								return False
		return False

	def external_to_user(self, convproj_obj, pluginid, exttype):
		for shortname, dvplug_obj, prop_obj in cvpj_plugin.extplug_selector.iter():
			if exttype in prop_obj.ext_formats:
				funclist = dir(dvplug_obj)
				if 'check_plug' in funclist and 'decode_data' in funclist and 'params_from_plugin' in funclist:
					if dvplug_obj.check_plug(self):
						dvplug_obj.decode_data(exttype, self)
						dvplug_obj.params_from_plugin(convproj_obj, self, pluginid, exttype)

	def user_to_external(self, convproj_obj, pluginid, exttype, extplat):
		for shortname, dvplug_obj, prop_obj in cvpj_plugin.extplug_selector.iter():
			if self.check_wildmatch('user', prop_obj.type, prop_obj.subtype):
				funclist = dir(dvplug_obj)
				if 'params_to_plugin' in funclist and 'encode_data' in funclist:
					dvplug_obj.params_to_plugin(convproj_obj, self, pluginid, exttype)
					dvplug_obj.encode_data(exttype, convproj_obj, self, extplat)

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugins import base as dv_plugins
from functions import xtramath
from functions import data_values
from objects import globalstore
import wave as audio_wav
import base64
import struct
import copy

from objects.convproj import sample_entry
from objects.convproj import params
from objects.convproj import eqfilter
from objects.convproj import autopoints
from objects.convproj import envelope
from objects.convproj import wave
from objects.convproj import oscillator
from objects.convproj import harmonics
from objects.convproj import time
from objects.convproj import chord
from objects.convproj import midi_inst
from objects import plugdatamanu
from objects import audio_data

class cvpj_regions:
	def __init__(self):
		self.data = []

	def add(self, i_min, i_max, i_data):
		self.data.append([i_min, i_max, i_data])

	def __iter__(self):
		for x in self.data:
			yield x

class cvpj_sampleregions:
	def __init__(self):
		self.data = []

	def add(self, i_min, i_max, i_mid, i_id, i_data):
		self.data.append([i_min, i_max, i_mid, i_id, i_data])

	def __iter__(self):
		for x in self.data:
			yield x

class cvpj_modulation:
	def __init__(self):
		self.source = []
		self.destination = []
		self.amount = 0
		self.power = 0

		self.env_points = ''

		self.bipolar = False
		self.bypass = False
		self.stereo = False

class cvpj_preset:
	def __init__(self):
		self.name = 'DawVert'
		self.program = 0

class cvpj_poly:
	def __init__(self):
		self.limited = False
		self.mono = False
		self.max = 32
		self.porta = False
		self.porta_time = time.cvpj_time()
		self.slide_always = False
		self.porta_octive_scale = False
		self.slide_slope = 0
		self.defined = False

class cvpj_plugin_state:
	def __init__(self):
		self.params = params.cvpj_paramset()
		self.datavals = params.cvpj_datavals()
		self.poly = cvpj_poly()
		self.bytesdata = {}
		self.regions = cvpj_regions()
		self.sampleregions = cvpj_sampleregions()
		self.env_adsr = {}
		self.env_points = {}
		self.env_points_vars = {}
		self.env_blocks = {}
		self.filter = eqfilter.cvpj_filter()
		self.named_filter = {}
		self.eq = eqfilter.cvpj_eq(self, 'main')
		self.named_eq = {}
		self.lfos = {}
		self.waves = {}
		self.audios = {}
		self.harmonics = {}
		self.wavetables = {}
		self.filerefs = {}
		self.sampleparts = {}
		self.oscs = []
		self.timing = {}
		self.chord = {}
		self.arrays = {}
		self.modulations = []
		self.midi = midi_inst.cvpj_midi_inst()
		self.preset = cvpj_preset()

	def create_manu_obj(self, convproj_obj, pluginid):
		return plugdatamanu.plug_manu(self, convproj_obj, pluginid)

	def type_set(self, i_type, i_subtype):
		self.type.set(i_type, i_subtype)

	def type_get(self):
		return self.type.get_list()

	def get_type_visual(self):
		return str(self.type)

	# -------------------------------------------------- dataset
	def from_bytes(self, in_bytes, ds_name, df_name, cat_name, obj_name, structname): 
		fldso = globalstore.dataset.get_obj(ds_name, 'plugin', obj_name)
		fldf = globalstore.datadef.get(df_name)

		try:
			if fldso and fldf:
				if fldso.datadef.struct: dfdict = fldf.parse(fldso.datadef.struct, in_bytes)
				elif structname: dfdict = fldf.parse(structname, in_bytes)

				self.dset_obj__add_param(fldso, dfdict)
				return dfdict
			return {}
		except:
			return {}

	def from_bytes_debug(self, in_bytes, df_name, structname): 
		fldf = globalstore.datadef.get(df_name)

		try:
			if fldf:
				dfdict = fldf.parse(structname, in_bytes)
				for x, d in dfdict.items():
					print(x, d)
		except:
			pass

	def to_bytes(self, ds_name, df_name, cat_name, obj_name, structname): 
		fldf = globalstore.datadef.get(df_name)
		fldso = globalstore.dataset.get_obj(ds_name, 'plugin', obj_name)

		if fldf and fldso:
			dsetdict = self.param_dict_dataset_set(ds_name, 'plugin', obj_name)
			outbytes = fldf.create(fldso.datadef.struct if fldso.datadef.struct else structname, dsetdict)
			return outbytes
		else:
			return b''
			
	def dset_param__add(self, p_id, p_value, dset_param):
		if p_value is None: p_value = dset_param.defv
		if dset_param.type != 'list': 
			if not dset_param.noauto:
				param_obj = self.params.add(p_id, p_value, dset_param.type)
				param_obj.min = dset_param.min
				param_obj.max = dset_param.max
				param_obj.visual.name = dset_param.name
			else: self.datavals.add(p_id, p_value)
		else: 
			self.array_add(p_id, p_value)





	def add_from_dset(self, p_id, p_value, dset, ds_cat, ds_group): 
		defparams = dset.params_i_get(ds_cat, ds_group, p_id)
		if defparams != None:
			if p_value == None: p_value = defparams[2]
			if defparams[0] == False:
				param_obj = self.params.add(p_id, p_value, defparams[1])
				param_obj.min = defparams[3]
				param_obj.max = defparams[4]
				param_obj.visual.name = defparams[5]
			else:
				self.datavals.add(p_id, p_value)
		else:
			if p_value == None: p_value = 0
			self.params.add(p_id, p_value, 'float')

	def dset_obj__add_param(self, dataset_obj, i_dict):
		if dataset_obj:
			for param_id, dset_param in dataset_obj.params.iter():
				outval = data_values.dict__nested_get_value(i_dict, param_id.split('/'))
				self.dset_param__add(param_id, outval, dset_param)

	def param_dict_dataset_set(self, ds_name, catname, pluginname):
		fldso = globalstore.dataset.get_obj(ds_name, 'plugin', pluginname)
		outdict = {}
		if fldso:
			for param_id, dset_param in fldso.params.iter():
				if dset_param.type != 'list': 
					if not dset_param.noauto: outdata = self.params.get(param_id, dset_param.defv).value
					else: outdata = self.datavals.get(param_id, dset_param.defv)
				else:
					outdata = array_get(param_id, len(dset_param.defv))
				data_values.dict__nested_add_value(outdict, param_id.split('/'), outdata)
		return outdict

	# -------------------------------------------------- rawdata
	def rawdata_add(self, i_name, i_databytes):
		self.bytesdata[i_name] = i_databytes

	def rawdata_add_b64(self, i_name, i_databytes):
		self.bytesdata[i_name] = base64.b64decode(i_databytes)

	def rawdata_get(self, i_name):
		return self.bytesdata[i_name] if i_name in self.bytesdata else b''

	def rawdata_get_b64(self, i_name):
		return base64.b64encode(self.bytesdata[i_name] if i_name in self.bytesdata else b'').decode('ascii')

	# -------------------------------------------------- sampleregions
	def sampleregion_add(self, i_min, i_max, i_middle, i_data, **kwargs):
		samplepartid = kwargs['samplepartid'] if 'samplepartid' in kwargs else 'multi_'+str(i_min)+'_'+str(i_max)
		samplepart_obj = self.samplepart_add(samplepartid)
		self.sampleregions.add(i_min, i_max, i_middle, samplepartid, i_data)
		return samplepart_obj

	# -------------------------------------------------- regions
	def region_add(self, i_name, i_min, i_max, i_value):
		if i_name not in self.regions: self.regions[i_name] = cvpj_regions()
		self.regions[i_name].add(i_min, i_max, i_value)

	def regions_get(self, i_name):
		return self.regions[i_name] if i_name in self.regions else cvpj_regions()

	# -------------------------------------------------- asdr_env
	def env_asdr_add(self, a_type, a_predelay, a_attack, a_hold, a_decay, a_sustain, a_release, a_amount):
		adsr_obj = envelope.cvpj_envelope_adsr()
		adsr_obj.predelay = a_predelay
		adsr_obj.attack = a_attack
		adsr_obj.hold = a_hold
		adsr_obj.decay = a_decay
		adsr_obj.sustain = a_sustain
		adsr_obj.release = a_release
		adsr_obj.amount = a_amount
		if a_type not in self.env_adsr: self.env_adsr[a_type] = {}
		self.env_adsr[a_type] = adsr_obj
		return adsr_obj

	def env_asdr_tension_add(self, a_type, t_attack, t_decay, t_release):
		if a_type in self.env_adsr: 
			self.env_adsr[a_type].attack_tension = t_attack
			self.env_adsr[a_type].decay_tension = t_decay
			self.env_adsr[a_type].release_tension = t_release

	def env_asdr_get(self, a_type):
		if a_type in self.env_adsr: return self.env_adsr[a_type]
		return envelope.cvpj_envelope_adsr()

	def env_asdr_get_exists(self, a_type): 
		if a_type in self.env_adsr: return True, self.env_adsr[a_type]
		return False, envelope.cvpj_envelope_adsr()

	def env_asdr_copy(self, o_type, n_type):
		if o_type in self.env_adsr: 
			self.env_adsr[n_type] = copy.deepcopy(self.env_adsr[o_type])

	def env_asdr_list(self): 
		return [x for x in self.env_adsr]

	# -------------------------------------------------- env_blocks
	def env_blocks_add(self, a_type, a_vals, a_time, a_max, a_loop, a_release):
		blocks_obj = envelope.cvpj_envelope_blocks()
		blocks_obj.values = a_vals
		blocks_obj.time = a_time
		blocks_obj.max = a_max
		blocks_obj.loop = a_loop
		blocks_obj.release = a_release
		if a_type not in self.env_blocks: self.env_blocks[a_type] = {}
		self.env_blocks[a_type] = blocks_obj

	def env_blocks_get(self, a_type): 
		if a_type in self.env_blocks: return self.env_blocks[a_type]
		return envelope.cvpj_envelope_blocks()

	def env_blocks_get_exists(self, a_type): 
		if a_type in self.env_blocks: return True, self.env_blocks[a_type]
		return False, envelope.cvpj_envelope_blocks()

	def env_blocks_list(self): 
		return [x for x in self.env_blocks]

	# -------------------------------------------------- env_points
	def env_points_add(self, a_type, time_ppq, time_float, val_type):
		self.env_points[a_type] = autopoints.cvpj_autopoints(time_ppq, time_float, val_type)
		return self.env_points[a_type]

	def env_points_get(self, a_type): 
		if a_type in self.env_points: return self.env_points[a_type]
		return autopoints.cvpj_autopoints(1, True, 'float')

	def env_points_get_exists(self, a_type): 
		if a_type in self.env_points: return True, self.env_points[a_type]
		return False, autopoints.cvpj_autopoints(1, True, 'float')

	def env_points_addvar(self, a_type, p_name, p_value):
		if a_type in self.env_points_vars: self.env_points_vars[a_type] = {}
		self.env_points_vars[a_type][p_name] = p_value

	def env_points_copy(self, o_type, n_type):
		if o_type in self.env_points: 
			self.env_points[n_type] = copy.deepcopy(self.env_points[o_type])

	def env_points_from_blocks(self, a_type):
		blocks_obj = self.env_blocks_get(a_type)
		points_obj = self.env_points_add(a_type, 4, True, 'float')
		points_obj.from_blocks_obj(blocks_obj)

	def env_asdr_from_points(self, a_type):
		env_pointsdata = self.env_points_get(a_type)
		env_pointsdata.change_timings(1, True)
		adsr_obj = self.env_asdr_add(a_type, 0, 0, 0, 0, 1, 0, 1)
		adsr_obj.from_envpoints(env_pointsdata, a_type, self)

	def env_points_list(self): 
		return [x for x in self.env_points]

	# -------------------------------------------------- lfo
	def lfo_add(self, a_type): 
		lfo_obj = oscillator.cvpj_lfo()
		self.lfos[a_type] = lfo_obj
		return lfo_obj

	def lfo_get(self, a_type): return self.lfos[a_type] if a_type in self.lfos else oscillator.cvpj_lfo()
	def lfo_get_exists(self, a_type): return (True, self.lfos[a_type]) if a_type in self.lfos else (False, oscillator.cvpj_lfo())
	def lfo_list(self): return [x for x in self.lfos]
	def lfo_copy(self, o_type, n_type):
		if o_type in self.lfos: self.lfos[n_type] = copy.deepcopy(self.lfos[o_type])

	# -------------------------------------------------- osc
	def osc_add(self): 
		osc_obj = oscillator.cvpj_osc()
		self.oscs.append(osc_obj)
		return osc_obj
	def osc_get(self, i_num): return self.oscs[i_num] if i_num<len(self.oscs) else None

	# -------------------------------------------------- wave
	def wave_add(self, i_name): 
		self.waves[i_name] = wave.cvpj_wave()
		return self.waves[i_name]
	def wave_get(self, i_name): return self.waves[i_name] if i_name in self.waves else wave.cvpj_wave()
	def wave_get_exists(self, i_name): return (True, self.waves[i_name]) if i_name in self.waves else (False, wave.cvpj_wave())
	def wave_list(self): return [x for x in self.waves]
	def wave_copy(self, o_type, n_type):
		if o_type in self.waves: self.waves[n_type] = copy.deepcopy(self.waves[o_type])

	# -------------------------------------------------- audio
	def audio_add(self, i_name): 
		self.audios[i_name] = audio_data.audio_obj()
		return self.audios[i_name]
	def audio_get(self, i_name): return self.audios[i_name] if i_name in self.audios else audio_data.audio_obj()
	def audio_get_exists(self, i_name): return (True, self.audios[i_name]) if i_name in self.audios else (False, audio_data.audio_obj())
	def audio_list(self):  return [x for x in self.audios]

	# -------------------------------------------------- timing
	def timing_add(self, i_name): 
		self.timing[i_name] = time.cvpj_time()
		return self.timing[i_name]
	def timing_get(self, i_name): return self.timing[i_name] if i_name in self.timing else time.cvpj_time()
	def timing_list(self):  return [x for x in self.timing]

	# -------------------------------------------------- chord
	def chord_add(self, i_name): 
		self.chord[i_name] = chord.cvpj_chord()
		return self.chord[i_name]
	def chord_get(self, i_name): return self.chord[i_name] if i_name in self.chord else chord.cvpj_chord()
	def chord_list(self):  return [x for x in self.chord]

	# -------------------------------------------------- harmonics
	def harmonics_add(self, i_name): 
		self.harmonics[i_name] = harmonics.cvpj_harmonics()
		return self.harmonics[i_name]
	def harmonics_get(self, i_name): return self.harmonics[i_name] if i_name in self.harmonics else harmonics.cvpj_harmonics()
	def harmonics_list(self): return [x for x in self.harmonics]

	# -------------------------------------------------- wave
	def wavetable_add(self, i_name): 
		wavetable_obj = oscillator.cvpj_wavetable()
		self.wavetables[i_name] = wavetable_obj
		return wavetable_obj
	def wavetable_get(self, i_name): return self.wavetables[i_name] if i_name in self.wavetables else oscillator.cvpj_wavetable()
	def wavetable_get_exists(self, i_name): return (True, self.wavetables[i_name]) if i_name in self.wavetables else (False, oscillator.cvpj_wavetable())
	def wavetable_list(self): return [x for x in self.wavetables]

	# -------------------------------------------------- modulations
	def modulation_add(self): 
		mod_obj = cvpj_modulation()
		self.modulations.append(mod_obj)
		return mod_obj

	def modulation_add_native(self, modfrom, modto): 
		mod_obj = cvpj_modulation()
		mod_obj.source = ['native', modfrom]
		mod_obj.destination = ['native', modto]
		self.modulations.append(mod_obj)
		return mod_obj

	def modulation_iter(self): 
		for x in self.modulations:
			yield x
			
	# -------------------------------------------------- fileref

	def get_fileref(self, fileref_name, convproj_obj): 
		if fileref_name in self.filerefs:
			fileref_id = self.filerefs[fileref_name]
			return convproj_obj.get_fileref(fileref_id)
		return False, None

	def getpath_fileref(self, convproj_obj, refname, os_type, relative): 
		ref_found, fileref_obj = self.get_fileref(refname, convproj_obj)
		return fileref_obj.get_path(os_type, relative) if ref_found else ''

	# -------------------------------------------------- samplepart

	def samplepart_add(self, i_name):
		self.sampleparts[i_name] = sample_entry.cvpj_sample_entry()
		return self.sampleparts[i_name]

	def samplepart_copy(self, o_name, i_name):
		if i_name in self.sampleparts:
			self.sampleparts[o_name] = copy.deepcopy(self.sampleparts[i_name])

	def samplepart_move(self, o_name, i_name):
		if i_name in self.sampleparts:
			self.sampleparts[o_name] = self.sampleparts[i_name]
			del sampleparts[i_name]

	def samplepart_remove(self, i_name):
		if i_name in self.sampleparts: del self.sampleparts[i_name]

	def samplepart_get(self, i_name): return self.sampleparts[i_name] if i_name in self.sampleparts else sample_entry.cvpj_sample_entry()

	# -------------------------------------------------- eq
	def eq_add(self): 
		return self.eq.add()

	# -------------------------------------------------- named_eq
	def named_eq_add(self, eq_name): 
		if eq_name not in self.named_eq: self.named_eq[eq_name] = eqfilter.cvpj_eq(self, eq_name)
		return self.named_eq[eq_name].add()

	# -------------------------------------------------- named_filter
	def named_filter_add(self, filt_name): 
		if filt_name not in self.named_filter: 
			self.named_filter[filt_name] = eqfilter.cvpj_filter()
			self.named_filter[filt_name].on = True
		return self.named_filter[filt_name]

	def named_filter_get(self, filt_name):
		if filt_name in self.named_filter: return self.named_filter[filt_name]
		else: return eqfilter.cvpj_filter()

	def named_filter_get_exists(self, filt_name): 
		if filt_name in self.named_filter: return True, self.named_filter[filt_name]
		return False, eqfilter.cvpj_filter()

	def named_filter_rename(self, filt_name, new_name):
		if filt_name in self.named_filter: 
			self.named_filter[new_name] = self.named_filter.pop(filt_name)

	# -------------------------------------------------- array
	def array_add(self, arr_name, values): 
		if arr_name not in self.arrays: self.arrays[arr_name] = list(values)

	def array_get(self, arr_name, missingnum):
		if arr_name in self.arrays: return self.arrays[arr_name]
		else: return [0 for _ in range(missingnum)]

	def array_get_vl(self, arr_name):
		if arr_name in self.arrays: return self.arrays[arr_name]
		else: return []

	def array_resize(self, arr_name, newsize):
		if arr_name in self.arrays:
			self.arrays[arr_name] = wave.resizewave(self.arrays[arr_name], newsize, True)

	def array_rename(self, arr_name, new_name):
		if arr_name in self.arrays: 
			self.arrays[new_name] = self.arrays.pop(arr_name)

	# -------------------------------------------------- ext

	def external_to_user(self, convproj_obj, pluginid, exttype):
		for name, info_extplug in dv_plugins.iter_extplug():
			if exttype in info_extplug.ext_formats:
				exttsobj = info_extplug.classfunc()
				if info_extplug.classfunc.check_plug(self):
					exttsobj.decode_data(exttype, self)
					exttsobj.params_from_plugin(convproj_obj, self, pluginid, exttype)

	def user_to_external(self, convproj_obj, pluginid, exttype, extplat):
		for name, info_extplug in dv_plugins.iter_extplug():
			if self.check_wildmatch(info_extplug.type, info_extplug.subtype):
				exttsobj = info_extplug.classfunc()
				exttsobj.params_to_plugin(convproj_obj, self, pluginid, exttype)
				exttsobj.encode_data(exttype, convproj_obj, self, extplat)
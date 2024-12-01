# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from functions import data_xml
from functions import note_data
from functions import xtramath
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
from functions_plugin_ext import plugin_clap
from functions_plugin_ext import data_vstw
from objects import globalstore
from objects.convproj import wave
from objects.file import preset_vst2
import json
import math
import numpy as np
import base64
import copy

list_fade_style = ['file_blend',None,'time','spectral']
list_phase_style = [None,'clear','vocode']

tempo_frac = [[0,0],[32,1],[16,1],[8,1],[4,1],[2,1],[1,1],[1,2],[1,4],[1,8],[1,16],[1,32],[1,64]]

DATASETPATH = './data_ext/dataset/vital.dset'
DATASETNAME = 'vital'

def calc_filter_freq_from(value):
	return note_data.note_to_freq(value-72)

def calc_filter_freq_to(value):
	filterfreq = note_data.freq_to_note(value)+72 if value else -52
	return xtramath.clamp(filterfreq, -52, 76)

def calc_filter_q_from(value):
	return (value+1)*6

def calc_filter_q_to(value):
	return (value/6)-1

def do_filter(plugin_obj, filter_obj, starttxt, vs):
	vs[starttxt+'_resonance'] = calc_filter_q_to(filter_obj.q)
	vs[starttxt+'_cutoff'] = calc_filter_freq_to(filter_obj.freq)
	vs[starttxt+'_on'] = int(filter_obj.on)
	if filter_obj.type.type == 'low_pass': vs[starttxt+'_blend'] = 0
	if filter_obj.type.type == 'high_pass': vs[starttxt+'_blend'] = 2
	if filter_obj.type.type == 'band_pass': vs[starttxt+'_blend'] = 1
	if filter_obj.type.type == 'notch':
		vs[starttxt+'_blend'] = 1
		vs[starttxt+'_style'] = 2
	if filter_obj.type.type == 'moog': vs[starttxt+'_blend'] = 0
	if filter_obj.type.type == 'formant': vs[starttxt+'_model'] = 5

def add_free_auto(vm, modfrom, modto):
	free_mods = []
	for n, x in enumerate(vm):
		if (x['destination']=='' and x['source']==''): free_mods.append(n)

	if free_mods:
		firstfree = free_mods[0]
		vm[firstfree]['destination'] = modto
		vm[firstfree]['source'] = modfrom
		return firstfree+1

def get_free_lfo(vm):
	free_mods = []
	for n in range(8):
		starttxt = 'lfo_'+str(n+1)+'_'

		def_delay_time = vm[starttxt+'delay_time'] == 0
		def_fade_time = vm[starttxt+'fade_time'] == 0
		def_frequency = vm[starttxt+'frequency'] == 1
		def_keytrack_transpose = vm[starttxt+'keytrack_transpose'] == -12
		def_keytrack_tune = vm[starttxt+'keytrack_tune'] == 0
		def_phase = vm[starttxt+'phase'] == 0
		def_smooth_mode = vm[starttxt+'smooth_mode'] == 1
		def_smooth_time = vm[starttxt+'smooth_time'] == -7.5
		def_stereo = vm[starttxt+'stereo'] == 0
		def_sync = vm[starttxt+'sync'] == 1
		def_sync_type = vm[starttxt+'sync_type'] == 0
		def_tempo = vm[starttxt+'tempo'] == 7
		def_env = vm['lfos'][n] == {"name": "Triangle","num_points": 3,"points":[0.0,1.0,0.5,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth": False}

		alldef = def_delay_time and def_fade_time and def_frequency and def_env and def_keytrack_transpose and def_keytrack_tune and def_phase and def_smooth_mode and def_smooth_time and def_stereo and def_sync and def_sync_type and def_tempo
		if alldef: return n

def get_free_random(vm):
	free_mods = []
	for n in range(4):
		starttxt = 'random_'+str(n+1)+'_'

		def_frequency = vm[starttxt+'frequency'] == 1
		def_keytrack_transpose = vm[starttxt+'keytrack_transpose'] == -12
		def_keytrack_tune = vm[starttxt+'keytrack_tune'] == 0
		def_stereo = vm[starttxt+'stereo'] == 0
		def_style = vm[starttxt+'style'] == 0
		def_sync = vm[starttxt+'sync'] == 1
		def_sync_type = vm[starttxt+'sync_type'] == 0
		def_tempo = vm[starttxt+'tempo'] == 8

		alldef = def_frequency and def_keytrack_transpose and def_keytrack_tune and def_stereo and def_style and def_sync and def_sync_type and def_tempo
		if alldef: return n

def add_random(vs, n, lfo_obj):
	starttxt = 'random_'+str(n+1)+'_'
	time_to(lfo_obj.time, starttxt, vs)
	vs[starttxt+'stereo'] = lfo_obj.stereo
	lfo_style = 1
	if lfo_obj.prop.random_type == 'perlin': lfo_style == 0
	if lfo_obj.prop.random_type == 'sine': lfo_style == 2
	if lfo_obj.prop.random_type == 'lorenz': lfo_style == 3
	vs[starttxt+'style'] = lfo_style


def add_lfo(vs, n, plugin_obj, lfo_obj):
	starttxt = 'lfo_'+str(n+1)+'_'

	vl = vs['lfos']
	smooth_time = lfo_obj.data['smooth_time'] if 'smooth_time' in lfo_obj.data else 0.00001

	vs[starttxt+'delay_time'] = lfo_obj.predelay
	vs[starttxt+'smooth_time'] = -math.log2(smooth_time)
	vs[starttxt+'smooth_mode'] = int(smooth_time == 0)
	vs[starttxt+'fade_time'] = lfo_obj.attack
	vs[starttxt+'phase'] = lfo_obj.phase
	vs[starttxt+'stereo'] = lfo_obj.stereo

	time_to(lfo_obj.time, starttxt, vs)

	lfo_sync_type = 0
	if not lfo_obj.loop_on:
		if lfo_obj.sustained: lfo_sync_type = 3
		else: lfo_sync_type = 2
	if lfo_obj.mode == 'trigger': lfo_sync_type = 0 
	if lfo_obj.mode == 'sync': lfo_sync_type = 1 
	if lfo_obj.mode == 'loop_point': lfo_sync_type = 4 
	if lfo_obj.mode == 'loop_old': lfo_sync_type = 5 
	if lfo_obj.mode == 'env_point_cycle': lfo_sync_type = 6 

	vs[starttxt+'sync_type'] = lfo_sync_type

	if lfo_obj.prop.type == 'env': create_points(plugin_obj, lfo_obj.prop.nameid, vl[n])
	if lfo_obj.prop.type == 'shape': 
		if lfo_obj.prop.shape == 'sine': vl[n] = {"name":"Sin","num_points":3,"points":[0.0,1.0,0.5,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth":True}
		if lfo_obj.prop.shape == 'square': vl[n] = {"name":"Square","num_points":5,"points":[0.0,1.0,0.0,0.0,0.5,0.0,0.5,1.0,1.0,1.0],"powers":[0.0,0.0,0.0,0.0,0.0],"smooth":False}
		if lfo_obj.prop.shape == 'triangle': vl[n] = {"name":"Triangle","num_points":3,"points":[0.0,1.0,0.5,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth":False}
		if lfo_obj.prop.shape == 'saw': vl[n] = {"name":"Saw","num_points":3,"points":[0.0,1.0,1.0,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth":False}

def rev_time(value):
	return pow(value, 2)**2

def do_time(value):
	return math.sqrt(pow(value, 0.5))

def to_env(plugin_obj, asdrtype, envnum, vs):
	vitals = 'env_'+str(envnum+1)+'_'
	asdrdata_obj = plugin_obj.env_asdr_get(asdrtype)
	vs[vitals+'delay'] = do_time(asdrdata_obj.predelay)
	vs[vitals+'attack'] = do_time(asdrdata_obj.attack)
	vs[vitals+'hold'] = do_time(asdrdata_obj.hold)
	vs[vitals+'decay'] = do_time(asdrdata_obj.decay)
	vs[vitals+'sustain'] = asdrdata_obj.sustain
	vs[vitals+'release'] = do_time(asdrdata_obj.release)
	vs[vitals+'attack_power'] = asdrdata_obj.attack_tension
	vs[vitals+'decay_power'] = asdrdata_obj.decay_tension
	vs[vitals+'release_power'] = asdrdata_obj.release_tension

def cvpj_wave_to_wavetable(plugin_obj, s_osc, wt_json):
	wtg = wt_json["groups"]
	wtgs = {'components': [{}]}
	wtc = wtgs['components']
	wtcs = wtc[0]

	wave_obj = wave.cvpj_wave()
	wave_obj.set_numpoints(2048)

	if s_osc.type == 'shape':
		if s_osc.shape == 'sine': wave_obj.add_wave('sine', 0, 1, 1)
		if s_osc.shape == 'square': wave_obj.add_wave('square', (s_osc.pulse_width*2)-1, 1, 1)
		if s_osc.shape == 'pulse': wave_obj.add_wave('square', (s_osc.pulse_width*2)-1, 1, 1)
		if s_osc.shape == 'triangle': wave_obj.add_wave('triangle', 0, 1, 1)
		if s_osc.shape == 'saw': wave_obj.add_wave('saw', 0, 1, 1)
	if s_osc.type == 'wave': 
		wave_obj = copy.deepcopy(plugin_obj.wave_get(s_osc.nameid))
		wave_obj.resize(2048)

	wtcs['interpolation'] = 1
	wtcs['interpolation_style'] = 0
	wtcs['type'] = 'Wave Source'
	wtkfs = wtcs['keyframes'] = []
	keyframe = {}
	keyframe['position'] = 0
	keyframe['wave_data'] = base64.b64encode(np.asarray(wave_obj.points, dtype=np.float32)).decode()
	wtkfs.append(keyframe)
	wtg.append(wtgs)

def cvpj_wt_to_wavetable(plugin_obj, wtid, wt_json, vs, vm, oscnum):
	ifexists, wavetable_obj = plugin_obj.wavetable_get_exists(wtid)
	if ifexists:
		wt_json["author"] = wavetable_obj.author
		wt_json["full_normalize"] = wavetable_obj.full_normalize
		wtg = wt_json["groups"]
		wt_json["name"] = wavetable_obj.name
		wt_json["remove_all_dc"] = wavetable_obj.remove_all_dc
		for wavetabsource_obj in wavetable_obj.sources:
			wtgs = {'components': [{}]}
			wtc = wtgs['components']
			wtcs = wtc[0]

			wtcs['interpolation_style'] = (2 if wavetabsource_obj.blend_smooth else 1) if wavetabsource_obj.blend_on else 0

			if wavetabsource_obj.type == 'retro':
				wtcs['interpolation'] = 1 if wavetabsource_obj.blend_mode == 'spectral' else 0
				wtcs['type'] = 'Wave Source'
				wtkfs = wtcs['keyframes'] = []
				wave_obj = copy.deepcopy(plugin_obj.wave_get(wavetabsource_obj.retro_id))
				wavsplit = wave_obj.split(wavetabsource_obj.retro_size)
				for pos, wt_part in enumerate(wavsplit):
					keyframe = {}
					keyframe['position'] = int((pos/wavetabsource_obj.retro_count)*256)
					wt_part = copy.deepcopy(wt_part)
					wt_part.smooth = False
					wt_part.resize(2048)
					wt_part.balance()
					keyframe['wave_data'] = base64.b64encode(np.asarray(wt_part.points, dtype=np.float32)).decode()
					wtkfs.append(keyframe)
				free_lfo = get_free_lfo(vs)
				endtxt = 'lfo_'+str(free_lfo+1)
				vs[endtxt+'_frequency'] = -math.log2(wavetabsource_obj.retro_time)
				vs[endtxt+'_sync_type'] = 4.0
				vs[endtxt+'_sync'] = 0.0
				vs[endtxt+'_phase'] = wavetabsource_obj.retro_loop/wave_obj.numpoints

				vl = vs['lfos']
				vl[free_lfo] = {"name":"Saw","num_points":3,"points":[0.0,1.0,1.0,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth":False}

				wave_frame_txt = 'osc_'+str(oscnum+1)+'_wave_frame'
				vs[wave_frame_txt] = 0.0

				modnum = add_free_auto(vm, endtxt, wave_frame_txt)
				if modnum: vs['modulation_'+str(modnum)+'_amount'] = 1

			if wavetabsource_obj.type == 'audio':
				wtcs['audio_file'] = ''
				wtcs['audio_sample_rate'] = 44100
				wtcs['fade_style'] = list_fade_style.index(wavetabsource_obj.fade_style) if wavetabsource_obj.fade_style in list_fade_style else 0
				wtcs['phase_style'] = list_phase_style.index(wavetabsource_obj.phase_style) if wavetabsource_obj.phase_style in list_phase_style else 0
				wtcs['normalize_gain'] = wavetabsource_obj.audio_normalize_gain
				wtcs['normalize_mult'] = wavetabsource_obj.audio_normalize_mult
				wtcs['type'] = 'Audio File Source'
				wtcs['random_seed'] = 0
				wtcs['window_size'] = wavetabsource_obj.audio_window_size
				isexists, audio_obj = plugin_obj.audio_get_exists(wavetabsource_obj.audio_id)
				if isexists:
					audio_obj = copy.deepcopy(audio_obj)
					audio_obj.pcm_changecodec('float')
					wtcs['audio_file'] = base64.b64encode(audio_obj.to_raw()).decode()
					wtcs['audio_sample_rate'] = audio_obj.rate
				wtkfs = wtcs['keyframes'] = []
				for pos, wt_part in wavetabsource_obj.parts.items():
					keyframe = {}
					keyframe['position'] = int(pos*256)
					keyframe['start_position'] = wt_part.audio_pos
					keyframe['window_fade'] = wt_part.audio_window_fade
					keyframe['window_size'] = wt_part.audio_window_size
					wtkfs.append(keyframe)

			if wavetabsource_obj.type == 'wave':
				wtcs['interpolation'] = 1 if wavetabsource_obj.blend_mode == 'spectral' else 0
				wtcs['type'] = 'Wave Source'
				wtkfs = wtcs['keyframes'] = []
				for pos, wt_part in wavetabsource_obj.parts.items():
					keyframe = {}
					keyframe['position'] = int(pos*256)
					wave_obj = copy.deepcopy(plugin_obj.wave_get(wt_part.wave_id))
					wave_obj.resize(2048)
					keyframe['wave_data'] = base64.b64encode(np.asarray(wave_obj.points, dtype=np.float32)).decode()
					wtkfs.append(keyframe)

			if wavetabsource_obj.type == 'line':
				numpoints = 0
				wtkfs = wtcs['keyframes'] = []
				for pos, wt_part in wavetabsource_obj.parts.items():
					keyframe = {}
					keyframe['position'] = int(pos*256)
					keyframe['line'] = {}
					numpoints = max(create_points(plugin_obj, wt_part.line_envid, keyframe['line']), numpoints)
					keyframe['pull_power'] = wt_part.data['pull_power'] if 'pull_power' in wt_part.data else 0.0
					wtkfs.append(keyframe)
				wtcs['num_points'] = numpoints
				wtcs['type'] = 'Line Source'

			wtg.append(wtgs)

def parse_points(plugin_obj, envname, lfodict, islfo):
	autopoints_obj = plugin_obj.env_points_add(envname, 1, True, 'float')
	lfo_name = lfodict['name'] if 'name' in lfodict else ''
	lfo_num_points = lfodict['num_points'] if 'num_points' in lfodict else (3 if islfo else 2)
	lfo_points = lfodict['points'] if 'points' in lfodict else ([0.0, 1.0, 0.5, 0.0, 1.0, 1.0] if islfo else [0.5, 1.0, 0.5, 0.0])
	lfo_powers = lfodict['powers'] if 'powers' in lfodict else ([0.0, 0.0, 0.0] if islfo else [0.0, 0.0])
	lfo_smooth = lfodict['smooth'] if 'smooth' in lfodict else False 
	autopoints_obj.data['smooth'] = lfo_smooth
	autopoints_obj.name = lfo_name
	cvpj_points = [autopoints_obj.add_point() for _ in range(lfo_num_points)]
	pointsdif = []
	for pn, pv in enumerate(lfo_points):
		cvpj_point = cvpj_points[pn//2]
		if pn%2: 
			cvpj_point.value = 1-pv
			pointsdif.append(cvpj_point.value)
		else: cvpj_point.pos = pv
	for pn, pv in enumerate(lfo_powers[:-1]):
		valdel = pointsdif[pn]-pointsdif[pn+1]
		cvpj_points[pn].tension = pv/10 if valdel>=0 else pv/-10

def create_points(plugin_obj, envname, lfopoints):
	isexist, autopoints_obj = plugin_obj.env_points_get_exists(envname)
	if isexist:
		lfo_points = []
		lfo_pud = []
		prevval = 1
		for ap in autopoints_obj: 
			lfo_points += [ap.pos, 1-ap.value]
			lfo_pud.append((prevval-ap.value)>=0)
			prevval = ap.value
		lfo_powers = [ap.tension*10 for ap in autopoints_obj]
		for n, p in enumerate(lfo_pud[1:]):
			if not p: lfo_powers[n] *= -1
		lfopoints['num_points'] = autopoints_obj.count()
		lfopoints['points'] = lfo_points
		lfopoints['powers'] = lfo_powers
		lfopoints['smooth'] = autopoints_obj.data['smooth'] if 'smooth' in autopoints_obj.data else False
		lfopoints['name'] = autopoints_obj.name
		return lfopoints['num_points']
	return 0

def time_from(convproj_obj, time_obj, lfo_tempo, lfo_frequency, lfo_sync, lfo_keytrack_transpose, lfo_keytrack_tune):
	lfo_frequency = math.pow(2, lfo_frequency)
	frac_num, frac_denom = tempo_frac[lfo_tempo]

	if lfo_sync == 0: time_obj.set_hz(lfo_frequency)
	if lfo_sync == 1: time_obj.set_frac(frac_num, frac_denom, '', convproj_obj)
	if lfo_sync == 2: time_obj.set_frac(frac_num, frac_denom, 'd', convproj_obj)
	if lfo_sync == 3: time_obj.set_frac(frac_num, frac_denom, 't', convproj_obj)
	if lfo_sync == 4: time_obj.set_keytrack(lfo_keytrack_transpose, lfo_keytrack_tune)

def time_to(time_obj, starttxt, vs):
	if time_obj.type == 'steps':
		if not time_obj.frozen:
			frac_num, frac_denom, letter = time_obj.get_frac_letter_mul()
			sfrac = [frac_num, frac_denom]
			if sfrac in tempo_frac: lfo_tempo = tempo_frac.index(sfrac)
			else: lfo_tempo = 6

			if letter == 'd': lfo_sync = 2
			elif letter == 't': lfo_sync = 3
			else: lfo_sync = 1
		else: 
			lfo_tempo = 0
			lfo_sync = 1
	elif time_obj.type == 'keytrack': 
		lfo_sync = 4
		lfo_tempo = 0
	else: 
		lfo_sync = 0
		lfo_tempo = 0

	vs[starttxt+'tempo'] = lfo_tempo
	vs[starttxt+'sync'] = lfo_sync
	vs[starttxt+'frequency'] = math.log2(1/time_obj.speed_seconds) 
	vs[starttxt+'keytrack_transpose'] = time_obj.keytrack_transpose
	vs[starttxt+'keytrack_tune'] = time_obj.keytrack_tune

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def get_shortname(self): return 'vital'
	def get_name(self): return 'Vital'
	def get_prop(self, in_dict): 
		in_dict['ext_formats'] = ['vst2', 'vst3', 'clap']
		in_dict['type'] = 'matt_tytel'
		in_dict['subtype'] = 'vital'

	def check_exists(self, inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 1449751649): outlist.append('vst2')
		if plugin_vst3.check_exists('id', '56535456697461766974616C00000000'): outlist.append('vst3')
		return outlist

	def check_plug(self, plugin_obj): 
		if plugin_obj.check_wildmatch('external', 'vst2', None):
			if plugin_obj.datavals_global.match('fourid', 1449751649): return 'vst2'
		if plugin_obj.check_wildmatch('external', 'vst3', None):
			if plugin_obj.datavals_global.match('id', '56535456697461766974616C00000000'): return 'vst3'
		if plugin_obj.check_wildmatch('external', 'clap', None):
			if plugin_obj.datavals_global.match('id', 'audio.vital.synth'): return 'clap'
		return None

	def decode_data(self, plugintype, plugin_obj):
		chunkdata = None
		if plugintype in ['vst2', 'clap']:
			chunkdata = plugin_obj.rawdata_get('chunk').decode().strip()
		if plugintype in ['vst3']:
			chunkdata = plugin_obj.rawdata_get('chunk')
			vstw_d = data_vstw.get(chunkdata)
			if vstw_d: 
				chunkdata = data_vc2xml.get(vstw_d)
				chunkdata = chunkdata[4:int.from_bytes(chunkdata[0:4])+8]
				chunkdata = chunkdata.split(b'\x00')[0].decode().strip()+'\x00'
				self.plugin_type = plugintype
				return True

		if chunkdata:
			try:
				self.plugin_type = plugintype
				self.plugin_data = chunkdata
				self.plugin_data = json.loads(self.plugin_data[0:-1])
				return True
			except:
				pass

	#def extract_params(self):
	#	if not (self.plugin_data is None):
	#		for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre(DATASETNAME, 'plugin', 'main', plugintype):

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if not (self.plugin_data is None):
			jsonout = json.dumps(self.plugin_data).encode()
			if plugintype == 'vst2':
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 1449751649, 'chunk', jsonout, None)
			if plugintype == 'vst3':
				plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, '56535456697461766974616C00000000', jsonout)
			if plugintype == 'clap':
				plugin_clap.replace_data(convproj_obj, plugin_obj, 'id', None, 'audio.vital.synth', jsonout)

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)

		if not (self.plugin_data is None):
			vd =  self.plugin_data
			v_author = vd['author'] if 'author' in vd else ''
			v_comments = vd['comments'] if 'comments' in vd else ''
			v_macro1 = vd['macro1'] if 'macro1' in vd else 'MACRO 1'
			v_macro2 = vd['macro2'] if 'macro2' in vd else 'MACRO 2'
			v_macro3 = vd['macro3'] if 'macro3' in vd else 'MACRO 3'
			v_macro4 = vd['macro4'] if 'macro4' in vd else 'MACRO 4'
			v_preset_name = vd['preset_name'] if 'preset_name' in vd else ''
			v_preset_style = vd['preset_style'] if 'preset_style' in vd else ''
			v_synth_version = vd['synth_version'] if 'synth_version' in vd else ''
			v_settings = vd['settings'] if 'settings' in vd else {}

			for valuepack, extparamid, paramnum in manu_obj.dset_remap_ext_to_cvpj__pre(DATASETNAME, 'plugin', 'main', plugintype):
				if extparamid in v_settings: valuepack.value = v_settings[extparamid]
				else: v_settings[extparamid] = valuepack.value

			plugin_obj.replace('user', 'matt_tytel', 'vital')

			filter_objs = [plugin_obj.filter, plugin_obj.named_filter_add('filter_1'), plugin_obj.named_filter_add('filter_2')]

			for n, x in enumerate(['fx', '1', '2']):
				starttxt = 'filter_'+x+'_'
				filter_obj = filter_objs[n]
				filter_obj.on = bool(v_settings[starttxt+'on'])
				filter_obj.freq = calc_filter_freq_from(v_settings[starttxt+'cutoff'])
				filter_obj.q = calc_filter_q_from(v_settings[starttxt+'resonance'])
				filter_model = int(v_settings[starttxt+'model'])
				filter_style = int(v_settings[starttxt+'style'])
				filter_obj.type.set('custom', None)

			if 'modulations' in v_settings:
				for n, t in enumerate(v_settings['modulations']):
					starttxt = 'modulation_'+str(n+1)+'_'
					if 'source' in t: plugin_obj.datavals.add(starttxt+'source', t['source'])
					if 'destination' in t: plugin_obj.datavals.add(starttxt+'destination', t['destination'])

			plugin_obj.datavals.add('modulation_imported', True)
			for modnum in range(64):
				starttxt = 'modulation_'+str(modnum+1)+'_'
				mod_source = plugin_obj.datavals.get(starttxt+'source', '')
				mod_destination = plugin_obj.datavals.get(starttxt+'destination', '')
				if mod_source and mod_destination:
					modulation_obj = plugin_obj.modulation_add()
					modulation_obj.source = ['native', mod_source]
					modulation_obj.destination = ['native', mod_destination]
					modulation_obj.amount = v_settings[starttxt+'amount']
					modulation_obj.bipolar = v_settings[starttxt+'bipolar']
					modulation_obj.bypass = v_settings[starttxt+'bypass']
					modulation_obj.power = v_settings[starttxt+'power']
					modulation_obj.stereo = v_settings[starttxt+'stereo']

			if 'sample' in v_settings:
				v_sample = v_settings['sample']
				if 'name' in v_sample: plugin_obj.datavals.add('sample_name', v_sample['name'])
				if 'samples' in v_sample: 
					audio_obj = plugin_obj.audio_add('vital_sample')
					audio_obj.set_codec('float')
					audio_obj.pcm_from_bytes(base64.b64decode(v_sample['samples']))
					if 'sample_rate' in v_sample: audio_obj.rate = v_sample['sample_rate']

			for n in range(6):
				asdrtype = 'vital_env_'+str(n+1)
				vitals = 'env_'+str(n+1)+'_'
				env_attack = rev_time(v_settings[vitals+'attack'])
				env_attack_power = v_settings[vitals+'attack_power']
				env_decay = rev_time(v_settings[vitals+'decay'])
				env_decay_power = v_settings[vitals+'decay_power']
				env_delay = rev_time(v_settings[vitals+'delay'])
				env_hold = rev_time(v_settings[vitals+'hold'])
				env_release = rev_time(v_settings[vitals+'release'])
				env_release_power = v_settings[vitals+'release_power']
				env_sustain = v_settings[vitals+'sustain']
				asdrdata_obj = plugin_obj.env_asdr_add(asdrtype, env_delay, env_attack, env_hold, env_decay, env_sustain, env_release, 1)
				asdrdata_obj.attack_tension = env_attack_power
				asdrdata_obj.decay_tension = env_decay_power
				asdrdata_obj.release_tension = env_release_power

			for n in range(4):
				lfoname = 'vital_random_'+str(n+1)
				starttxt = 'random_'+str(n+1)+'_'

				lfo_frequency = v_settings[starttxt+'frequency']
				lfo_keytrack_transpose = v_settings[starttxt+'keytrack_transpose']
				lfo_keytrack_tune = v_settings[starttxt+'keytrack_tune']
				lfo_sync = int(v_settings[starttxt+'sync'])
				lfo_sync_type = v_settings[starttxt+'sync_type']
				lfo_tempo = int(v_settings[starttxt+'tempo'])

				lfo_stereo = v_settings[starttxt+'stereo']
				lfo_style = int(v_settings[starttxt+'style'])

				lfo_obj = plugin_obj.lfo_add(lfoname)
				time_from(convproj_obj, lfo_obj.time, lfo_tempo, lfo_frequency, lfo_sync, lfo_keytrack_transpose, lfo_keytrack_tune)
				lfo_obj.stereo = lfo_stereo
				lfo_obj.prop.shape = 'random'

				if lfo_style == 0: lfo_obj.prop.random_type = 'perlin'
				if lfo_style == 2: lfo_obj.prop.random_type = 'sine'
				if lfo_style == 3: lfo_obj.prop.random_type = 'lorenz'

			if 'lfos' in v_settings:
				for n, lfodict in enumerate(v_settings['lfos']):
					starttxt = 'lfo_'+str(n+1)+'_'
					lfo_delay_time = v_settings[starttxt+'delay_time']
					lfo_fade_time = v_settings[starttxt+'fade_time']
					lfo_frequency = v_settings[starttxt+'frequency']
					lfo_keytrack_transpose = v_settings[starttxt+'keytrack_transpose']
					lfo_keytrack_tune = v_settings[starttxt+'keytrack_tune']
					lfo_phase = v_settings[starttxt+'phase']
					lfo_smooth_mode = v_settings[starttxt+'smooth_mode']
					lfo_smooth_time = v_settings[starttxt+'smooth_time']
					lfo_stereo = v_settings[starttxt+'stereo']
					lfo_sync = int(v_settings[starttxt+'sync'])
					lfo_sync_type = v_settings[starttxt+'sync_type']
					lfo_tempo = int(v_settings[starttxt+'tempo'])

					lfo_smooth_time = pow(2, lfo_smooth_time)

					starttxt = 'vital_lfo_'+str(n+1)

					lfo_obj = plugin_obj.lfo_add(starttxt)

					lfo_obj.prop.type = 'env'
					lfo_obj.prop.nameid = starttxt

					lfo_obj.predelay = lfo_delay_time
					if not lfo_smooth_mode: lfo_obj.attack = lfo_fade_time
					else: lfo_obj.data['smooth_time'] = lfo_smooth_time
					lfo_obj.phase = lfo_phase
					lfo_obj.stereo = lfo_stereo

					time_from(convproj_obj, lfo_obj.time, lfo_tempo, lfo_frequency, lfo_sync, lfo_keytrack_transpose, lfo_keytrack_tune)

					if lfo_sync_type == 0: lfo_obj.mode = 'trigger'
					if lfo_sync_type == 1: lfo_obj.mode = 'sync'
					if lfo_sync_type == 2: lfo_obj.loop_on = False
					if lfo_sync_type == 3: 
						lfo_obj.loop_on = False
						lfo_obj.sustained = True
					if lfo_sync_type == 4: lfo_obj.mode = 'loop_point'
					if lfo_sync_type == 5: lfo_obj.mode = 'loop_old'
					if lfo_sync_type == 6: lfo_obj.mode = 'env_point_cycle'

					parse_points(plugin_obj, starttxt, lfodict, True)

			if 'wavetables' in v_settings:
				for wn, wtdict in enumerate(v_settings['wavetables']):
					wt_id = 'vital_wt_'+str(wn+1)

					osc_obj = plugin_obj.osc_add()
					osc_obj.prop.type = 'wavetable'
					osc_obj.prop.nameid = wt_id

					wavetable_obj = plugin_obj.wavetable_add(wt_id)
					wavetable_obj.full_normalize = wtdict['full_normalize'] if 'full_normalize' in wtdict else True
					wavetable_obj.remove_all_dc = wtdict['remove_all_dc'] if 'remove_all_dc' in wtdict else True
					wavetable_obj.author = wtdict['author'] if 'author' in wtdict else ''
					wavetable_obj.name = wtdict['name'] if 'name' in wtdict else ''

					if 'groups' in wtdict:
						for gn, wtgroup in enumerate(wtdict['groups']):
							v_wt_g_components = wtgroup['components']
							v_wt_source = v_wt_g_components[0]
							v_wt_modifiers = v_wt_g_components[1:]

							sourcetype = v_wt_source['type']
							wr_src_obj = wavetable_obj.add_source()

							interpolation_style = v_wt_source['interpolation_style']
							wr_src_obj.blend_smooth = interpolation_style == 2
							wr_src_obj.blend_on = interpolation_style != 0

							if sourcetype == 'Wave Source':
								interpolation = v_wt_source['interpolation']
								keyframes = v_wt_source['keyframes']
								
								wr_src_obj.type = 'wave'
								wr_src_obj.blend_mode = ['normal','spectral'][interpolation]
								for pn, keyframe in enumerate(keyframes):
									wave_data = list(np.frombuffer(base64.b64decode(keyframe['wave_data']), dtype=np.float32))
									wave_id = 'vital_wave_'+'_'.join([str(wn), str(gn), str(pn)])
									wt_part = wr_src_obj.parts.add_pos(keyframe['position']/256)
									wt_part.wave_id = wave_id
									wave_obj = plugin_obj.wave_add(wave_id)
									wave_obj.set_all_range(wave_data, -1, 1)

							if sourcetype == 'Audio File Source':
								audio_file = v_wt_source['audio_file']
								audio_sample_rate = v_wt_source['audio_sample_rate']

								audio_id = 'vital_audio_'+'_'.join([str(wn), str(gn)])
								wr_src_obj.type = 'audio'
								wr_src_obj.audio_id = audio_id
								if 'fade_style' in v_wt_source: wr_src_obj.fade_style = list_fade_style[v_wt_source['fade_style']]
								if 'phase_style' in v_wt_source: wr_src_obj.phase_style = list_phase_style[v_wt_source['phase_style']]
								if 'window_size' in v_wt_source: wr_src_obj.audio_window_size = v_wt_source['window_size']
								if 'normalize_gain' in v_wt_source: wr_src_obj.audio_normalize_gain = v_wt_source['normalize_gain']
								if 'normalize_mult' in v_wt_source: wr_src_obj.audio_normalize_mult = v_wt_source['normalize_mult']
								audio_obj = plugin_obj.audio_add(audio_id)
								audio_obj.set_codec('float')
								audio_obj.pcm_from_bytes(base64.b64decode(audio_file))
								audio_obj.rate = audio_sample_rate
								keyframes = v_wt_source['keyframes']
								for pn, keyframe in enumerate(keyframes):
									wt_part = wr_src_obj.parts.add_pos(keyframe['position']/256)
									wt_part.audio_pos = keyframe['start_position']
									wt_part.audio_window_fade = keyframe['window_fade']
									wt_part.audio_window_size = keyframe['window_size']

							if sourcetype == 'Line Source':
								wr_src_obj.type = 'line'
								keyframes = v_wt_source['keyframes']
								for pn, keyframe in enumerate(keyframes):
									wt_part = wr_src_obj.parts.add_pos(keyframe['position']/256)
									if 'line' in keyframe:
										env_id = 'vital_line_'+'_'.join([str(wn), str(gn), str(pn)])
										parse_points(plugin_obj, env_id, keyframe['line'], False)
										if 'pull_power' in v_wt_source: wt_part.data['pull_power'] = v_wt_source['pull_power']
										wt_part.line_envid = env_id

			time = v_settings['portamento_time']

			poly_obj = plugin_obj.poly
			poly_obj.limited = True
			poly_obj.max = v_settings['polyphony']
			poly_obj.slide_always = v_settings['portamento_force']
			poly_obj.porta_octive_scale = v_settings['portamento_scale']
			poly_obj.slide_slope = v_settings['portamento_slope']
			poly_obj.porta_time.set_seconds(2**time)

			plugin_obj.datavals.add('macro1', v_macro1)
			plugin_obj.datavals.add('macro2', v_macro2)
			plugin_obj.datavals.add('macro3', v_macro3)
			plugin_obj.datavals.add('macro4', v_macro4)
			plugin_obj.datavals.add('author', v_author)
			plugin_obj.datavals.add('comments', v_comments)
			plugin_obj.datavals.add('preset_name', v_preset_name)
			plugin_obj.datavals.add('preset_style', v_preset_style)
			manu_obj.dset_remap_ext_to_cvpj__post(DATASETNAME, 'plugin', 'main', plugintype)
			return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.dataset.load(DATASETNAME, DATASETPATH)
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		vd = {}
		vd['author'] = plugin_obj.datavals.get('author', '')
		vd['comments'] = plugin_obj.datavals.get('comments', '')
		vd['macro1'] = plugin_obj.datavals.get('macro1', 'MACRO 1')
		vd['macro2'] = plugin_obj.datavals.get('macro2', 'MACRO 2')
		vd['macro3'] = plugin_obj.datavals.get('macro3', 'MACRO 3')
		vd['macro4'] = plugin_obj.datavals.get('macro4', 'MACRO 4')
		vd['preset_name'] = plugin_obj.datavals.get('preset_name', '')
		vd['preset_style'] = plugin_obj.datavals.get('preset_style', '')
		vs = vd['settings'] = {}
		vd['synth_version'] = '1.0.6'

		sample_generate_noise = plugin_obj.datavals.get('sample_generate_noise', False)

		vm = vs['modulations'] = [{'destination': '', 'source': ''} for x in range(64)]
		vl = vs['lfos'] = [{"name": "Triangle","num_points": 3,"points":[0.0,1.0,0.5,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth": False} for x in range(8)]
		vwt = vs['wavetables'] = [{"author": '', 'full_normalize': True, 'groups': [], "name": '', "remove_all_dc": True, "version": "1.0.6"} for _ in range(3)]

		for valuepack, extparamid, paramnum in manu_obj.dset_remap_cvpj_to_ext__pre(DATASETNAME, 'plugin', 'main', plugintype): 
			vs[extparamid] = valuepack.value

		modulation_imported = plugin_obj.datavals.get('modulation_imported', False)

		if modulation_imported:
			for n in range(64):
				starttxt = 'modulation_'+str(n+1)+'_'
				vm[n]['source'] = plugin_obj.datavals.get(starttxt+'source', '')
				vm[n]['destination'] = plugin_obj.datavals.get(starttxt+'destination', '')

		va = vs['sample'] = {}
		va['length'] = 0
		va['name'] = plugin_obj.datavals.get('sample_name', '')
		va['sample_rate'] = 44100
		va['samples'] = ''
		isexists, audio_obj = plugin_obj.audio_get_exists('vital_sample')
		if isexists:
			audio_obj = copy.deepcopy(audio_obj)
			audio_obj.pcm_changecodec('float')
			va['samples'] = base64.b64encode(audio_obj.to_raw()).decode()
			va['sample_rate'] = audio_obj.rate
			va['length'] = len(audio_obj)*2

		for n in range(6): 
			to_env(plugin_obj, 'vital_env_'+str(n+1), n, vs)

		for n in range(4): 
			ifexists, lfo_obj = plugin_obj.lfo_get_exists('vital_random_'+str(n+1))
			if ifexists: add_random(vs, n, lfo_obj)

		for n in range(8): 
			ifexists, lfo_obj = plugin_obj.lfo_get_exists('vital_lfo_'+str(n+1))
			if ifexists: add_lfo(vs, n, plugin_obj, lfo_obj)

		for n in range(3): 
			osc_obj = plugin_obj.osc_get(n)
			if osc_obj:
				if osc_obj.prop.type == 'wavetable': 
					cvpj_wt_to_wavetable(plugin_obj, osc_obj.prop.nameid, vwt[n], vs, vm, n)
				else: 
					cvpj_wave_to_wavetable(plugin_obj, osc_obj.prop, vwt[n])
					if osc_obj.prop.shape == 'random':
						sample_generate_noise = True
						vs['sample_on'] = 1

		do_filter(plugin_obj, plugin_obj.filter, 'filter_fx', vs)
		namedfilt_exists, namedfilt_obj = plugin_obj.named_filter_get_exists('filter_1')
		if namedfilt_exists: do_filter(plugin_obj, namedfilt_obj, 'filter_1', vs)
		namedfilt_exists, namedfilt_obj = plugin_obj.named_filter_get_exists('filter_2')
		if namedfilt_exists: do_filter(plugin_obj, namedfilt_obj, 'filter_2', vs)

		if sample_generate_noise:
			floatrandoms = np.random.random(100000).astype(np.float32)
			va['length'] = 100000
			va['samples'] = base64.b64encode(floatrandoms).decode()

		filter_objs = [plugin_obj.filter, plugin_obj.named_filter_get('filter_1'), plugin_obj.named_filter_get('filter_2')]

		for pointsid in plugin_obj.env_points_list():
			if pointsid.startswith('vital_import_'):
				endtxt = pointsid.split('vital_import_')[1]
				autopoints_obj = plugin_obj.env_points_get(pointsid)
				duration = autopoints_obj.get_dur()

				if duration:
					envname, envnum = endtxt.split('_')
					autopoints_obj.time_ppq = duration
					autopoints_obj.time_float = True
					autopoints_obj.change_timings(1, True)
					vs[endtxt+'_frequency'] = -math.log2(duration)
					vs[endtxt+'_sync_type'] = 2.0
					vs[endtxt+'_sync'] = 0.0
					create_points(plugin_obj, pointsid, vl[int(envnum)-1])

					modnum = add_free_auto(vm, endtxt, 'osc_1_level')
					if modnum: 
						vs['modulation_'+str(modnum)+'_amount'] = 1
						vs['osc_1_level'] = 0
					modnum = add_free_auto(vm, endtxt, 'osc_2_level')
					if modnum: 
						vs['modulation_'+str(modnum)+'_amount'] = 1
						vs['osc_2_level'] = 0
					modnum = add_free_auto(vm, endtxt, 'osc_3_level')
					if modnum: 
						vs['modulation_'+str(modnum)+'_amount'] = 1
						vs['osc_3_level'] = 0

		if not modulation_imported:
			usedlfos = {}
			for n, x in enumerate(plugin_obj.modulation_iter()):
				#print(x.source, x.destination)
				if x.source[0] == 'native' and x.destination[0] == 'native':
					modnum = add_free_auto(vm, x.source[1], x.destination[1])
					if modnum:
						starttxt = 'modulation_'+str(modnum)+'_'
						vs[starttxt+'amount'] = x.amount
						vs[starttxt+'bipolar'] = float(x.bipolar)
						vs[starttxt+'bypass'] = float(x.bypass)
						vs[starttxt+'power'] = x.power
						vs[starttxt+'stereo'] = float(x.stereo)
				if x.source[0] == 'lfo' and x.destination[0] == 'native':
					lfo_id = x.source[1]
					lfo_obj = plugin_obj.lfo_get(lfo_id)

					if x.source[1] not in usedlfos: 
						if lfo_obj.prop.shape != 'random':
							usedlfos[lfo_id] = ['lfo', get_free_lfo(vs)]
						else:
							usedlfos[lfo_id] = ['random', get_free_random(vs)]

					if usedlfos[lfo_id][1] != None:
						lfotype, lfonum = usedlfos[lfo_id]
						if lfotype == 'lfo':
							add_lfo(vs, lfonum, plugin_obj, lfo_obj)
							modnum = add_free_auto(vm, 'lfo_'+str(lfonum+1), x.destination[1])
							if modnum:
								lstarttxt = 'modulation_'+str(modnum)+'_'
								vs[lstarttxt+'amount'] = x.amount
								vs[lstarttxt+'bipolar'] = float(x.bipolar)
								vs[lstarttxt+'bypass'] = float(x.bypass)
								vs[lstarttxt+'power'] = x.power
								vs[lstarttxt+'stereo'] = float(x.stereo)
						if lfotype == 'random':
							add_random(vs, lfonum, lfo_obj)
							modnum = add_free_auto(vm, 'random_'+str(lfonum+1), x.destination[1])
							if modnum:
								lstarttxt = 'modulation_'+str(modnum)+'_'
								vs[lstarttxt+'amount'] = x.amount
								vs[lstarttxt+'bipolar'] = float(x.bipolar)
								vs[lstarttxt+'bypass'] = float(x.bypass)
								vs[lstarttxt+'power'] = x.power
								vs[lstarttxt+'stereo'] = float(x.stereo)

		poly_obj = plugin_obj.poly
		if poly_obj.defined:
			vs['polyphony'] = poly_obj.max if poly_obj.limited else 32
			if poly_obj.porta: 
				vs['portamento_force'] = int(poly_obj.slide_always)
				vs['portamento_scale'] = poly_obj.porta_octive_scale
				vs['portamento_slope'] = poly_obj.slide_slope
				vs['portamento_time'] = math.sqrt(poly_obj.porta_time.speed_seconds**2)

		manu_obj.dset_remap_cvpj_to_ext__post(DATASETNAME, 'plugin', 'main', plugintype)

		self.plugin_data = dict(sorted(vd.items()))

		return True
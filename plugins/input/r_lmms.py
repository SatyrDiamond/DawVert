# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import math
import plugins
import os
import struct
import zlib
import copy
import xml.etree.ElementTree as ET
from objects import counter
from objects import globalstore
from objects import auto_id
from objects.convproj import placements_notes
from objects.convproj import placements_audio
from objects.inst_params import fx_delay
from objects.inst_params import fm_opl
from objects.inst_params import chip_sid

def get_sample(i_value):
	if i_value:
		ifsampfac = i_value.startswith('factorysample:')
		if not os.path.exists(i_value) or ifsampfac:
			if ifsampfac: i_value = i_value[14:]
			for t in [
			'/usr/share/lmms/samples/', 
			'C:\\Program Files\\LMMS\\data\\samples\\'
			]:
				if os.path.exists(t+i_value): return t+i_value
			return i_value
		else:
			return i_value
	else:
		return ''

lfoshape = ['sine', 'tri', 'saw_down', 'square', 'custom', 'random']
arpdirection = ['up', 'down', 'updown', 'downup', 'random']

chordids = ["major","majb5","minor","minb5","sus2","sus4","aug","augsus4","tri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add11","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","harmonic_minor","melodic_minor","whole_tone","diminished","major_pentatonic","minor_pentatonic","jap_in_sen","major_bebop","dominant_bebop","blues","arabic","enigmatic","neopolitan","neopolitan_minor","hungarian_minor","dorian","phrygian","lydian","mixolydian","aeolian","locrian","full_minor","chromatic","half-whole_diminished","5","phrygian_dominant","persian"]

filtertype = [
['low_pass', None], ['high_pass', None], ['band_pass','csg'], 
['band_pass','czpg'], ['notch', None], ['all_pass', None], 
['moog', None], ['low_pass','double'], ['low_pass','rc12'], 
['band_pass','rc12'], ['high_pass','rc12'], ['low_pass','rc24'], 
['band_pass','rc24'], ['high_pass','rc24'], ['formant', None], 
['moog','double'], ['low_pass','sv'], ['band_pass','sv'], 
['high_pass','sv'], ['notch','sv'], ['formant','fast'], ['tripole', None]
]

chord = [[0], [0, 4, 7], [0, 4, 6], [0, 3, 7], [0, 3, 6], [0, 2, 7], [0, 5, 7], [0, 4, 8], [0, 5, 8], [0, 3, 6, 9], [0, 4, 7, 9], [0, 5, 7, 9], [0, 4, 7, 9, 14], [0, 3, 7, 9], [0, 3, 7, 9, 14], [0, 4, 7, 10], [0, 5, 7, 10], [0, 4, 8, 10], [0, 4, 6, 10], [0, 4, 7, 10, 15], [0, 4, 7, 10, 13], [0, 4, 8, 10, 15], [0, 4, 8, 10, 13], [0, 4, 6, 10, 13], [0, 4, 7, 10, 17], [0, 4, 7, 10, 21], [0, 4, 7, 10, 18], [0, 4, 7, 11], [0, 4, 6, 11], [0, 4, 8, 11], [0, 4, 7, 11, 18], [0, 4, 7, 11, 21], [0, 3, 7, 10], [0, 3, 6, 10], [0, 3, 7, 10, 13], [0, 3, 7, 10, 17], [0, 3, 7, 10, 21], [0, 3, 7, 11], [0, 3, 7, 11, 17], [0, 3, 7, 11, 21], [0, 4, 7, 10, 14], [0, 5, 7, 10, 14], [0, 4, 7, 14], [0, 4, 8, 10, 14], [0, 4, 6, 10, 14], [0, 4, 7, 10, 14, 18], [0, 4, 7, 10, 14, 20], [0, 4, 7, 11, 14], [0, 5, 7, 11, 15], [0, 4, 8, 11, 14], [0, 4, 7, 11, 14, 18], [0, 3, 7, 10, 14], [0, 3, 7, 14], [0, 3, 6, 10, 14], [0, 3, 7, 11, 14], [0, 4, 7, 10, 14, 17], [0, 4, 7, 10, 13, 17], [0, 4, 7, 11, 14, 17], [0, 3, 7, 10, 14, 17], [0, 3, 7, 11, 14, 17], [0, 4, 7, 10, 14, 21], [0, 4, 7, 10, 15, 21], [0, 4, 7, 10, 13, 21], [0, 4, 6, 10, 13, 21], [0, 4, 7, 11, 14, 21], [0, 3, 7, 10, 14, 21], [0, 3, 7, 11, 14, 21], [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 11], [0, 2, 3, 5, 7, 9, 11], [0, 2, 4, 6, 8, 10], [0, 2, 3, 5, 6, 8, 9, 11], [0, 2, 4, 7, 9], [0, 3, 5, 7, 10], [0, 1, 5, 7, 10], [0, 2, 4, 5, 7, 8, 9, 11], [0, 2, 4, 5, 7, 9, 10, 11], [0, 3, 5, 6, 7, 10], [0, 1, 4, 5, 7, 8, 11], [0, 1, 4, 6, 8, 10, 11], [0, 1, 3, 5, 7, 9, 11], [0, 1, 3, 5, 7, 8, 11], [0, 2, 3, 6, 7, 8, 11], [0, 2, 3, 5, 7, 9, 10], [0, 1, 3, 5, 7, 8, 10], [0, 2, 4, 6, 7, 9, 11], [0, 2, 4, 5, 7, 9, 10], [0, 2, 3, 5, 7, 8, 10], [0, 1, 3, 5, 6, 8, 10], [0, 2, 3, 5, 7, 8, 10], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [0, 1, 3, 4, 6, 7, 9, 10], [0, 7], [0, 1, 4, 5, 7, 8, 10], [0, 1, 4, 5, 6, 8, 11]]

# ------- functions -------

def get_timedata(lmms_param):
	steps = None
	if lmms_param.sync_mode == '1': steps = 16*8
	elif lmms_param.sync_mode == '2': steps = 16
	elif lmms_param.sync_mode == '3': steps = 8
	elif lmms_param.sync_mode == '4': steps = 4
	elif lmms_param.sync_mode == '5': steps = 2
	elif lmms_param.sync_mode == '6': steps = 1
	elif lmms_param.sync_mode == '7': steps = 0.5
	elif lmms_param.sync_mode == '8': 
		if lmms_param.sync_denominator and lmms_param.sync_numerator: 
			steps = (int(lmms_param.sync_numerator)/int(lmms_param.sync_denominator))*4

	return (steps != None), steps

send_auto_id_counter = counter.counter(1000, 'send_')

def get_wavestr(lmms_plugin, x_name):
	sampleshape = str(lmms_plugin.get_param(x_name, ''))
	if sampleshape:
		sampleshape = base64.b64decode(sampleshape.encode('ascii'))
		sampleshape_size = len(sampleshape)//4
		return struct.unpack('f'*sampleshape_size, sampleshape)
	else:
		return ()

def add_window_data(lwd_obj, convproj_obj, w_group, w_name):
	windata_obj = convproj_obj.viswindow__add([w_group,w_name])

	if lwd_obj.x != -1 and lwd_obj.y != -1: 
		windata_obj.pos_x = lwd_obj.x
		windata_obj.pos_y = lwd_obj.y
	if lwd_obj.width != -1 and lwd_obj.height != -1: 
		windata_obj.size_x = int(lwd_obj.width)
		windata_obj.size_y = int(lwd_obj.height)
	if lwd_obj.visible != -1: windata_obj.open = bool(lwd_obj.visible)
	if lwd_obj.maximized != -1:  windata_obj.maximized = int(lwd_obj.maximized)

def getvstparams(convproj_obj, plugin_obj, pluginid, lmms_plugin):
	global autoid_assoc
	
	pluginpath = str(lmms_plugin.get_param('plugin', ''))

	plugin_obj.datavals_global.add('path', pluginpath)

	vst2_pathid = pluginid+'_vstpath'
	convproj_obj.fileref__add(vst2_pathid, pluginpath, None)
	plugin_obj.filerefs_global['plugin'] = vst2_pathid

	windata_obj = convproj_obj.viswindow__add(['plugin', pluginid])
	windata_obj.open = bool(lmms_plugin.get_param('guivisible', False))

	prognum = int(lmms_plugin.get_param('program', 0))
	plugin_obj.clear_prog_keep(prognum)

	vst_numparams = int(lmms_plugin.get_param('numparams', -1))
	vst_data = str(lmms_plugin.get_param('chunk', ''))

	if vst_data:
		plugin_obj.datavals_global.add('datatype', 'chunk')
		plugin_obj.rawdata_add_b64('chunk', vst_data)

		for paramname, lmms_param in lmms_plugin.params.items():
			if paramname.startswith('param'):
				paramnum = 'ext_param_'+paramname[5:]
				autoid_assoc.define(lmms_param.id, ['plugin', pluginid, paramnum], 'float', None)
				plugin_obj.params.add(paramnum, lmms_param.value, 'float')

		for paramnum, vst_param in lmms_plugin.vst_params.items():
			cparamid = 'ext_param_'+str(paramnum)
			param_obj = plugin_obj.params.add(cparamid, vst_param.value, 'float')
			if vst_param.visname: param_obj.visual.name = vst_param.visname
			if vst_param.id: autoid_assoc.define(vst_param.id, ['plugin', pluginid, cparamid], 'float', None)

	elif vst_numparams != -1:
		plugin_obj.datavals_global.add('datatype', 'param')
		plugin_obj.datavals_global.add('numparams', int(vst_numparams))

	for param, vst_param in lmms_plugin.vst_params.items():
		paramnum = 'ext_param_'+str(param)
		param_obj = plugin_obj.params.add(paramnum, vst_param.value, 'float')
		if vst_param.visname: param_obj.visual.name = vst_param.visname
		if vst_param.id: autoid_assoc.define(vst_param.id, ['plugin', pluginid, paramnum], 'float', None)

	pluginfo_obj = globalstore.extplug.get('vst2', 'path', pluginpath, 'win', [32, 64])

	if pluginfo_obj.out_exists:
		plugin_obj.datavals_global.add('name', pluginfo_obj.name)
		plugin_obj.datavals_global.add('fourid', int(pluginfo_obj.id))

def doparam(lmms_param_obj, i_type, i_addmul, i_loc):
	global autoid_assoc
	outval = lmms_param_obj.value
	if lmms_param_obj.id and i_loc: autoid_assoc.define(str(lmms_param_obj.id), i_loc, i_type, i_addmul)
	outval = (float(outval)+i_addmul[0])*i_addmul[1] if i_addmul != None else float(outval)
	if i_type == 'float': outval = outval
	if i_type == 'int': outval = int(outval)
	if i_type == 'bool': outval = bool(int(outval))
	return outval

def dset_plugparams(pluginname, pluginid, lmms_plugin, plugin_obj):
	for param_id, dset_param in globalstore.dataset.get_params('lmms', 'plugin', pluginname):
		lmms_param = lmms_plugin.get_param(param_id, dset_param.defv)
		if not dset_param.noauto: outval = doparam(lmms_param, dset_param.type, None, ['plugin', pluginid, param_id])
		else: outval = lmms_param.value
		plugin_obj.dset_param__add(param_id, outval, dset_param)

# ------- Instruments and Plugins -------

def exp2sec(value): return (value*value)*5

def asdflfo_get(lmms_instrumenttrack, plugin_obj):
	eldata = lmms_instrumenttrack.eldata
	asdflfo(plugin_obj, eldata.elvol, 'vol')
	asdflfo(plugin_obj, eldata.elcut, 'cutoff')
	asdflfo(plugin_obj, eldata.elres, 'reso')
	plugin_obj.filter.on = bool(float(eldata.fwet))
	plugin_obj.filter.freq = float(eldata.fcut)
	plugin_obj.filter.q = float(eldata.fres)
	plugin_obj.filter.type.set_list(filtertype[int(eldata.ftype)])

def asdflfo(plugin_obj, elenv, asdrtype):
	envelopeparams = {}

	asdr_predelay = exp2sec(float(elenv.pdel))
	asdr_attack = exp2sec(float(elenv.att))
	asdr_hold = exp2sec(float(elenv.hold))
	asdr_decay = exp2sec(float(elenv.dec))
	asdr_sustain = float(elenv.sustain)
	asdr_release = exp2sec(float(elenv.rel))
	asdr_amount = float(elenv.amt)
	if asdrtype == 'cutoff': asdr_amount *= 6000

	plugin_obj.env_asdr_add(asdrtype, asdr_predelay, asdr_attack, asdr_hold, asdr_decay, asdr_sustain, asdr_release, asdr_amount)

	lfo_predelay = float(elenv.pdel)
	lfo_attack = exp2sec(float(elenv.latt))
	lfo_amount = float(elenv.lamt)
	lfo_shape = lfoshape[int(elenv.lshp)]
	if asdrtype == 'cutoff': lfo_amount *= 6000

	lfo_speed = (float(elenv.lspd)*0.2) if elenv.x100 == 1 else (float(elenv.lspd)*20)

	lfo_obj = plugin_obj.lfo_add(asdrtype)
	lfo_obj.predelay = exp2sec(lfo_predelay*4)
	lfo_obj.attack = lfo_attack
	lfo_obj.prop.shape = lfo_shape
	lfo_obj.time.set_seconds(lfo_speed)
	lfo_obj.amount = lfo_amount
	lfo_obj.retrigger = False

def decodeplugin(convproj_obj, lmms_plugin, pluginname):
	out_color = None
	pluginid = ''

	plugin_obj = None

	if pluginname == "sf2player":
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'soundfont2', None)
		plugin_obj.role = 'synth'
		bank = int(lmms_plugin.get_param('bank', 0))
		patch = int(lmms_plugin.get_param('patch', 0))
		plugin_obj.midi.from_sf2(bank, patch)
		
		sf2_path = str(lmms_plugin.get_param('src', 0))
		convproj_obj.fileref__add(sf2_path, sf2_path, None)
		plugin_obj.filerefs['file'] = sf2_path

		param_obj = plugin_obj.params.add('gain', float(lmms_plugin.get_param('gain', 0)), 'float')
		param_obj.visual.name = 'Gain'
		for cvpj_name, lmmsname in [['chorus_depth','chorusDepth'],['chorus_level','chorusLevel'],['chorus_lines','chorusNum'],['chorus_speed','chorusSpeed'],['reverb_damping','reverbDamping'],['reverb_level','reverbLevel'],['reverb_roomsize','reverbRoomSize'],['reverb_width','reverbWidth']]:
			plugin_obj.params.add(cvpj_name, float(lmms_plugin.get_param(lmmsname, 0)), 'float')
			param_obj.visual.name = lmmsname
		param_obj = plugin_obj.params.add('chorus_enabled', float(lmms_plugin.get_param('chorusOn', 0)), 'bool')
		param_obj = plugin_obj.params.add('reverb_enabled', float(lmms_plugin.get_param('reverbOn', 0)), 'bool')

	elif pluginname == "audiofileprocessor":
		filepath = get_sample(str(lmms_plugin.get_param('src', '')))
		plugin_obj, pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(filepath, None)
		lmms_interpolation = int(lmms_plugin.get_param('interp', 0))

		looped = int(lmms_plugin.get_param('looped', 0))

		sp_obj.reverse = bool(int(lmms_plugin.get_param('reversed', 0)))
		sp_obj.vol = float(lmms_plugin.get_param('amp', 1))/100
		sp_obj.data['continueacrossnotes'] = bool(int(lmms_plugin.get_param('stutter', 0)))
		sp_obj.point_value_type = "percent"
		sp_obj.loop_active = looped != 0
		sp_obj.start = float(lmms_plugin.get_param('sframe', 0))
		sp_obj.loop_start = float(lmms_plugin.get_param('lframe', 0))
		sp_obj.loop_end = float(lmms_plugin.get_param('eframe', 1))
		sp_obj.end = sp_obj.loop_end

		if looped == 2: sp_obj.loop_mode = "pingpong"
		if lmms_interpolation == 0: sp_obj.interpolation = "none"
		if lmms_interpolation == 1: sp_obj.interpolation = "linear"
		if lmms_interpolation == 2: sp_obj.interpolation = "sinc"


	elif pluginname == "vestige":
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst2', 'win')
		plugin_obj.role = 'synth'
		getvstparams(convproj_obj, plugin_obj, pluginid, lmms_plugin)

	elif pluginname == "sid":
		plugin_obj, pluginid = convproj_obj.plugin__add__genid(None, None, None)
		sid_obj = chip_sid.sid_inst()

		sid_obj.filter_cutoff = int(lmms_plugin.get_param('filterFC', 0))
		sid_obj.filter_resonance = int(lmms_plugin.get_param('filterResonance', 0))
		sid_obj.filter_mode = int(lmms_plugin.get_param('filterMode', 0))

		sid_obj.oscs[0].on = 1
		sid_obj.oscs[1].on = 1
		sid_obj.oscs[2].on = int(not lmms_plugin.get_param('voice3Off', 0))

		for num in range(3):
			s_sid_osc = sid_obj.oscs[num]
			sid_waveform = int(lmms_plugin.get_param('waveform'+str(num), 0))
			s_sid_osc.pulse_width = int(lmms_plugin.get_param('pulsewidth'+str(num), 0))
			s_sid_osc.coarse = int(lmms_plugin.get_param('coarse'+str(num), 0))
			s_sid_osc.attack = int(lmms_plugin.get_param('attack'+str(num), 0))
			s_sid_osc.decay = int(lmms_plugin.get_param('decay'+str(num), 0))
			s_sid_osc.sustain = int(lmms_plugin.get_param('sustain'+str(num), 0))
			s_sid_osc.release = int(lmms_plugin.get_param('release'+str(num), 0))
			s_sid_osc.ringmod = int(lmms_plugin.get_param('ringmod'+str(num), 0))
			s_sid_osc.syncmod = int(lmms_plugin.get_param('sync'+str(num), 0))
			s_sid_osc.to_filter = int(lmms_plugin.get_param('filtered'+str(num), 0))
			if sid_waveform == 0: s_sid_osc.wave_pulse = True
			if sid_waveform == 1: s_sid_osc.wave_triangle = True
			if sid_waveform == 2: s_sid_osc.wave_saw = True
			if sid_waveform == 3: s_sid_osc.wave_noise = True

		plugin_obj = sid_obj.to_cvpj(convproj_obj, pluginid)

	elif pluginname == "OPL2":
		opl_obj = fm_opl.opl_inst()
		opl_obj.set_opl2()

		opl_obj.feedback_1 = int(lmms_plugin.get_param('feedback', 0))
		opl_obj.fm_1 = bool(lmms_plugin.get_param('fm', 0))
		opl_obj.tremolo_depth = bool(lmms_plugin.get_param('trem_depth', 0))
		opl_obj.vibrato_depth = bool(lmms_plugin.get_param('vib_depth', 0))
		for opnum in range(2):
			op_obj = opl_obj.ops[opnum]
			optxt = 'op'+str(opnum+1)+'_'

			op_obj.env_attack = 15-int(lmms_plugin.get_param(optxt+'a', 0))
			op_obj.env_decay = 15-int(lmms_plugin.get_param(optxt+'d', 0))
			op_obj.env_sustain = 15-int(lmms_plugin.get_param(optxt+'s', 0))
			op_obj.env_release = 15-int(lmms_plugin.get_param(optxt+'r', 0))
			op_obj.ksr = bool(lmms_plugin.get_param(optxt+'ksr', 0))
			op_obj.level = 63-int(lmms_plugin.get_param(optxt+'lvl', 0))
			op_obj.freqmul = lmms_plugin.get_param(optxt+'mul', 0)
			op_obj.ksl = lmms_plugin.get_param(optxt+'scale', 0)
			op_obj.tremolo = bool(lmms_plugin.get_param(optxt+'trem', 0))
			op_obj.vibrato = bool(lmms_plugin.get_param(optxt+'vib', 0))
			op_obj.waveform = lmms_plugin.get_param(optxt+'waveform', 0)

		plugin_obj = opl_obj.to_cvpj(convproj_obj, pluginid)

	else:
		if pluginname == 'freeboy': pluginname = 'papu'

		plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'lmms', pluginname)
		plugin_obj.role = 'synth'
		dset_plugparams(pluginname, pluginid, lmms_plugin, plugin_obj)

		if pluginname == "papu":
			wave_data = get_wavestr(lmms_plugin, 'sampleShape')
			wave_obj = plugin_obj.wave_add('shape')
			wave_obj.set_all_range(wave_data, 0, 15)

		if pluginname == "watsyn":
			for shapename in ['b1_wave', 'a2_wave', 'b2_wave', 'a1_wave']:
				wave_data = get_wavestr(lmms_plugin, shapename)
				wave_obj = plugin_obj.wave_add(shapename)
				wave_obj.set_all_range(wave_data, -1, 1)

		if pluginname == "vibedstrings":
			for num in range(9):
				graphid = 'graph'+str(num)
				wave_data = get_wavestr(lmms_plugin, graphid)
				wave_obj = plugin_obj.wave_add(graphid)
				wave_obj.set_all_range(wave_data, 0, 1)
				wave_obj.smooth = True

		if pluginname == "bitinvader":
			wave_data = get_wavestr(lmms_plugin, 'sampleShape')

			wave_obj = plugin_obj.wave_add('main')
			wave_obj.set_all_range(wave_data, -1, 1)
			wave_obj.smooth = False

			wave_obj = plugin_obj.wave_add('main_smooth')
			wave_obj.set_all_range(wave_data, -1, 1)
			wave_obj.smooth = True

			wavetable_obj = plugin_obj.wavetable_add('main')
			src_obj = wavetable_obj.add_source()

			wt_part = src_obj.parts.add_pos(0)
			wt_part.wave_id = 'main'

			wt_part = src_obj.parts.add_pos(1)
			wt_part.wave_id = 'main_smooth'

			osc_data = plugin_obj.osc_add()
			osc_data.prop.type = 'wave'
			osc_data.prop.nameid = 'main'

		if pluginname == "zynaddsubfx":
			if 'ZynAddSubFX-data' in lmms_plugin.custom:
				plugin_obj.rawdata_add('data', ET.tostring(lmms_plugin.custom['ZynAddSubFX-data'], encoding='utf-8'))

		if pluginname == "tripleoscillator":
			for oscnum in range(1, 4):
				out_str = 'userwavefile'+str(oscnum)
				sampleid = pluginid+'_'+out_str
				filepath = get_sample(lmms_plugin.get_param(out_str, ''))
				sampleref_obj = convproj_obj.sampleref__add(sampleid, filepath, None)
				sp_obj = plugin_obj.samplepart_add(out_str)
				sp_obj.sampleid = sampleid

	plugin_obj.visual.from_dset('lmms', 'plugin', pluginname, True)

	return plugin_obj.visual.color, pluginid, plugin_obj

def lmms_decode_effectslot(convproj_obj, lmms_effect):

	lmms_plugin = lmms_effect.plugin

	if lmms_effect.name == 'vsteffect':
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst2', 'win')
		plugin_obj.role = 'effect'
		getvstparams(convproj_obj, plugin_obj, pluginid, lmms_plugin)

	elif lmms_effect.name == 'ladspaeffect':
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'ladspa', None)
		plugin_obj.role = 'effect'

		if 'file' in lmms_effect.keys:
			plugin_obj.datavals.add('name', lmms_effect.keys['file'])
			plugin_obj.datavals.add('path', lmms_effect.keys['file'])

		if 'plugin' in lmms_effect.keys:
			plugin_obj.datavals.add('plugin', lmms_effect.keys['plugin'])

		seperated_channels = False
		if lmms_plugin.ladspa_link != -1: 
			lmms_plugin.ladspa_ports //= 2
			if lmms_plugin.ladspa_link == 0: seperated_channels = True

		plugin_obj.datavals.add('numparams', lmms_plugin.ladspa_ports)

		for paramname, lmms_ladspa_param in lmms_plugin.ladspa_params.items():
			if paramname.startswith('port'):
				l_ch = paramname[4]
				l_val = paramname[5:]
				paramid = 'ext_param_'+l_val if l_ch == '0' else 'ext_param_'+l_val+'_'+l_ch
				paramval = doparam(lmms_ladspa_param.data, 'float', None, ['plugin', pluginid, paramid])
				plugin_obj.params.add(paramid, paramval, 'float')

		plugin_obj.datavals.add('seperated_channels', seperated_channels)
		
	elif lmms_effect.name == 'delay':
		DelayTimeSamples = lmms_plugin.get_param('DelayTimeSamples', 1)
		delay_obj = fx_delay.fx_delay()
		delay_obj.feedback[0] = float(lmms_plugin.get_param('FeebackAmount', 0.5))
		is_steps, timeval = get_timedata(DelayTimeSamples)
		timing_obj = delay_obj.timing_add(0)
		if is_steps: timing_obj.set_steps(timeval, convproj_obj)
		else: timing_obj.set_seconds(float(DelayTimeSamples))
		plugin_obj, pluginid = delay_obj.to_cvpj(convproj_obj, None)
	else:
		plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'lmms', lmms_effect.name)
		plugin_obj.role = 'effect'
		dset_plugparams(lmms_effect.name, pluginid, lmms_plugin, plugin_obj)

	fxenabled = doparam(lmms_effect.on, 'bool', None, ['slot', pluginid, 'enabled'])
	fxwet = doparam(lmms_effect.wet, 'float', None, ['slot', pluginid, 'wet'])
	plugin_obj.fxdata_add(fxenabled, fxwet)
	return pluginid

def decodefxchain(convproj_obj, fxchain_obj):
	fxchain = []
	for lmms_effect in fxchain_obj.effects:
		fxchain.append(lmms_decode_effectslot(convproj_obj, lmms_effect))
	return fxchain

# ------- Main -------

def lmms_decode_tracks(convproj_obj, lmms_tracks, isbb, startstr):
	global bbpld

	numbb = 0

	tracks = {}
	bbtracks = {}
	for tracknum, lmms_track in enumerate(lmms_tracks):
		cvpj_trackid = startstr+str(tracknum)

		if lmms_track.type == 0: 
			bbpld[cvpj_trackid] = []
			track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
			tracks[cvpj_trackid] = track_obj
			cvpj_enabled = doparam(lmms_track.muted, 'bool', [-1, -1], ['track', cvpj_trackid, 'enabled'])
			cvpj_solo = doparam(lmms_track.solo, 'bool', None, ['track', cvpj_trackid, 'solo'])
			track_obj.params.add('enabled', cvpj_enabled, 'bool')
			track_obj.params.add('solo', cvpj_solo, 'bool')
			track_obj.visual.name = lmms_track.name
			if isbb: track_obj.visual.name += ' [BB]'

			insttr_obj = lmms_track.instrumenttrack

			cvpj_pan = doparam(insttr_obj.pan, 'float', [0, 0.01], ['track', cvpj_trackid, 'pan'])
			cvpj_vol = doparam(insttr_obj.vol, 'float', [0, 0.01], ['track', cvpj_trackid, 'vol'])
			cvpj_pitch = doparam(insttr_obj.pitch, 'float', [0, 0.01], ['track', cvpj_trackid, 'pitch'])
			cvpj_usemasterpitch = insttr_obj.usemasterpitch.value
	
			track_obj.params.add('vol', cvpj_vol, 'float')
			track_obj.params.add('pan', cvpj_pan, 'float')
			track_obj.params.add('usemasterpitch', cvpj_usemasterpitch, 'bool')
			track_obj.params.add('pitch', cvpj_pitch, 'float')

			pluginname = insttr_obj.instrument.name
			insttr_obj = lmms_track.instrumenttrack
			plug_color, instpluginid, plugin_obj = decodeplugin(convproj_obj, insttr_obj.instrument.plugin, pluginname)

			if lmms_track.color: track_obj.visual.color.set_hex(lmms_track.color)
			elif plug_color: track_obj.visual.color = plug_color

			track_obj.inst_pluginid = instpluginid
			if plugin_obj: asdflfo_get(insttr_obj, plugin_obj)

			midiport_obj = insttr_obj.midiport
			track_obj.midi.in_enabled = bool(int(midiport_obj.readable))
			track_obj.midi.in_chan = int(midiport_obj.inputchannel)-1
			track_obj.midi.in_fixedvelocity = int(midiport_obj.fixedinputvelocity)
			track_obj.midi.out_enabled = int(midiport_obj.writable)
			track_obj.midi.out_chan = int(midiport_obj.outputchannel)
			track_obj.midi.out_inst.patch = int(midiport_obj.outputprogram)
			track_obj.midi.out_fixedvelocity = int(midiport_obj.fixedoutputvelocity)
			track_obj.midi.out_inst.key = int(midiport_obj.fixedoutputnote)
			track_obj.midi.basevelocity = int(midiport_obj.basevelocity)

			track_obj.fxslots_audio += decodefxchain(convproj_obj, insttr_obj.fxchain)

			if insttr_obj.fxch != -1: track_obj.fxrack_channel = int(insttr_obj.fxch)

			basenote = int(insttr_obj.basenote)-57
			noteoffset = 0
			if pluginname == 'audiofileprocessor': noteoffset = 3
			elif pluginname == 'sf2player': noteoffset = 12
			elif pluginname == 'OPL2': noteoffset = 24
			elif pluginname == 'zynaddsubfx': noteoffset = 0
			elif pluginname == 'vestige': noteoffset = 0
			else: noteoffset = 12

			middlenote = basenote - noteoffset
			track_obj.datavals.add('middlenote', middlenote)

			for lmms_pattern in lmms_track.patterns:
				placement_obj = track_obj.placements.add_notes() if not isbb else placements_notes.cvpj_placement_notes(track_obj.time_ppq, track_obj.time_float)
				placement_obj.time.position = lmms_pattern.pos
				placement_obj.visual.name = lmms_pattern.name
				if lmms_pattern.color: placement_obj.visual.color.set_float(lmms_pattern.color)
				placement_obj.muted = bool(int(lmms_pattern.muted))
				for lmms_note in lmms_pattern.notes:
					placement_obj.notelist.add_r(lmms_note.pos, max(lmms_note.len, 0), lmms_note.key-60, lmms_note.vol/100, {'pan': lmms_note.pan/100})
					for a_name, a_data in lmms_note.auto.items():
						if a_name == 'detuning':
							for p_pos, p_val in a_data.auto_points.items():
								autopoint_obj = placement_obj.notelist.last_add_auto('pitch')
								autopoint_obj.pos = p_pos
								autopoint_obj.value = p_val
								autopoint_obj.type = 'instant' if a_data.prog == 0 else 'normal'
				if isbb: bbpld[cvpj_trackid].append([0, placement_obj, lmms_pattern.steps])
				else: placement_obj.auto_dur(192, 192)

			# ------------------------------- arpeggiator -------------------------------
			arpeggiator_obj = insttr_obj.arpeggiator
			nfx_plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'arpeggiator', None)
			nfx_plugin_obj.role = 'notefx'
			nfx_plugin_obj.fxdata_add(bool(arpeggiator_obj.arp_enabled), None)
			doparam(arpeggiator_obj.arp_enabled, 'bool', None, ['slot', pluginid, 'enabled'])

			is_steps, timeval = get_timedata(arpeggiator_obj.arptime)
			timing_obj = nfx_plugin_obj.timing_add('main')
			if is_steps: timing_obj.set_steps(timeval, convproj_obj)
			else: timing_obj.set_seconds(int(arpeggiator_obj.arptime)/1000)
	
			chord_obj = nfx_plugin_obj.chord_add('main')
			chord_obj.find_by_id(0, chordids[int(arpeggiator_obj.arp)])
	
			direction = ['up','down','up_down','up_down','random'][int(arpeggiator_obj.arpdir)]
			nfx_plugin_obj.datavals.add('direction', direction)
			if arpeggiator_obj.arpdir == 3: nfx_plugin_obj.datavals.add('direction_mode', 'reverse')
			nfx_plugin_obj.datavals.add('mode', ['free','sort','sync'][int(arpeggiator_obj.arpmode)])
			nfx_plugin_obj.datavals.add('range', int(arpeggiator_obj.arprange))
			nfx_plugin_obj.datavals.add('gate', int(arpeggiator_obj.arpgate))
			nfx_plugin_obj.datavals.add('miss_rate', int(arpeggiator_obj.arpmiss))
			nfx_plugin_obj.datavals.add('skip_rate', int(arpeggiator_obj.arpskip))
			nfx_plugin_obj.datavals.add('cycle', int(arpeggiator_obj.arpcycle))
	
			track_obj.fxslots_notes.append(pluginid)

			# ------------------------------- chordcreator -------------------------------
			chordcreator_obj = insttr_obj.chordcreator
	
			nfx_plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'chord_creator', None)
			nfx_plugin_obj.role = 'notefx'
			nfx_plugin_obj.fxdata_add(bool(chordcreator_obj.chord_enabled), None)
			doparam(chordcreator_obj.chord_enabled, 'bool', None, ['slot', pluginid, 'enabled'])

			chord_obj = nfx_plugin_obj.chord_add('main')
			chord_obj.find_by_id(0, chordids[int(chordcreator_obj.chord)])
			nfx_plugin_obj.datavals.add('range', int(chordcreator_obj.chordrange))
	
			track_obj.fxslots_notes.append(pluginid)

		elif lmms_track.type == 1: 
			bbtrack_obj = lmms_track.bbtrack
			if bbtrack_obj.trackcontainer_used:
				bbtracks = lmms_decode_tracks(convproj_obj, bbtrack_obj.trackcontainer.tracks, True, 'LMMS_BB_Track')

			for bbtco in lmms_track.bbtcos:
				for bbtrackid, bbtrack_obj in bbtracks.items():
					if bbtrack_obj:
						lane_pl = bbtrack_obj.add_lane(cvpj_trackid)
						if bbtrackid in bbpld:
							s_bbpld = bbpld[bbtrackid]
							pl_type, pl_data, steps = s_bbpld[numbb]
							#print(bbtrackid, bbtrack_obj, pl_type, pl_data)
							if pl_type == 0:
								if pl_data.notelist.notesfound():
									pl_copy = copy.deepcopy(pl_data)
									pl_copy.muted = bbtco.muted
									pl_copy.visual.name = bbtco.name
									pl_copy.time.set_posdur(bbtco.pos, bbtco.len)
									pl_copy.time.set_loop_data(0, 0, steps*12)

									if lmms_track.color: pl_copy.visual.color.set_hex(track_color)
									lane_pl.placements.pl_notes.data.append(pl_copy)

			for bbtrackid, bbtrack_obj in bbtracks.items():
				bbtrack_obj.lanefit()

			tracks[cvpj_trackid] = None
			numbb += 1

		elif lmms_track.type == 2: 
			bbpld[cvpj_trackid] = []
			track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			tracks[cvpj_trackid] = track_obj
			cvpj_enabled = doparam(lmms_track.muted, 'bool', [-1, -1], ['track', cvpj_trackid, 'enabled'])
			cvpj_solo = doparam(lmms_track.solo, 'bool', None, ['track', cvpj_trackid, 'solo'])
			track_obj.params.add('enabled', cvpj_enabled, 'bool')
			track_obj.params.add('solo', cvpj_solo, 'bool')
			track_obj.visual.name = lmms_track.name
			if isbb: track_obj.visual.name += ' [BB]'
			if lmms_track.color: track_obj.visual.color.set_hex(track_color)

			samptr_obj = lmms_track.sampletrack
			cvpj_pan = doparam(samptr_obj.pan, 'float', [0, 0.01], ['track', cvpj_trackid, 'pan'])
			cvpj_vol = doparam(samptr_obj.vol, 'float', [0, 0.01], ['track', cvpj_trackid, 'vol'])
			track_obj.params.add('vol', cvpj_vol, 'float')
			track_obj.params.add('pan', cvpj_pan, 'float')

			track_obj.fxslots_audio += decodefxchain(convproj_obj, samptr_obj.fxchain)
			
			if samptr_obj.fxch != -1: track_obj.fxrack_channel = int(samptr_obj.fxch)

			for lmms_sampletco in lmms_track.sampletcos:
				placement_obj = track_obj.placements.add_audio() if not isbb else placements_audio.cvpj_placement_audio()
				placement_obj.time.set_posdur(lmms_sampletco.pos, lmms_sampletco.len)
				placement_obj.time.set_offset(lmms_sampletco.off*-1 if lmms_sampletco.off != -1 else 0)
				placement_obj.muted = bool(lmms_sampletco.muted)
				filepath = get_sample(lmms_sampletco.src)
				convproj_obj.sampleref__add(filepath, filepath, None)
				sp_obj = placement_obj.sample
				sp_obj.sampleref = filepath

				if isbb: bbpld[cvpj_trackid].append([1, placement_obj])

		elif lmms_track.type == 5:
			for lmms_automationpattern in lmms_track.automationpatterns:
				if not isbb:
					for id_num in lmms_automationpattern.auto_target:
						autopl_obj = convproj_obj.automation.add_pl_points(['id',str(id_num)], 'float')
						autopl_obj.time.set_posdur(lmms_automationpattern.pos, lmms_automationpattern.len)
						for p_pos, p_val in lmms_automationpattern.auto_points.items():
							autopoint_obj = autopl_obj.data.add_point()
							autopoint_obj.pos = p_pos
							autopoint_obj.value = p_val
							autopoint_obj.type = 'instant' if lmms_automationpattern.prog == 0 else 'normal'

		else:
			tracks[cvpj_trackid] = None

	return tracks

class input_lmms(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'lmms'
	def get_name(self): return 'LMMS'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mmp', 'mmpz']
		in_dict['fxtype'] = 'rack'
		in_dict['fxrack_params'] = ['enabled','vol']
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['auto_types'] = ['pl_points']
		in_dict['track_lanes'] = True
		in_dict['plugin_included'] = ['universal:sampler:single','chip:fm:opl2','universal:soundfont2','native:lmms','universal:arpeggiator','universal:chord_creator','universal:delay']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_ext'] = ['vst2', 'ladspa']
	def supported_autodetect(self): return True
	def detect(self, input_file):
		try:
			root = get_xml_tree(input_file)
			if root.tag == "lmms-project": output = True
			else: output = False
		except ET.ParseError: output = False
		return output
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_lmms

		global dataset
		global autoid_assoc
		global bbpld

		bbpld = {}

		autoid_assoc = auto_id.convproj2autoid(48, False)

		globalstore.dataset.load('lmms', './data_main/dataset/lmms.dset')

		convproj_obj.type = 'r'
		convproj_obj.set_timings(48, False)

		project_obj = proj_lmms.lmms_project()
		if not project_obj.load_from_file(input_file): exit()

		head_obj = project_obj.head
		song_obj = project_obj.song

		add_window_data(song_obj.trackcontainer.window, convproj_obj, 'main', 'tracklist')

		timesig_numerator = int(doparam(head_obj.timesig_numerator, 'float', None, None))
		timesig_denominator = int(doparam(head_obj.timesig_denominator, 'float', None, None))
		cvpj_vol = float(doparam(head_obj.mastervol, 'float', [0, 0.01], ['main', 'vol']))
		cvpj_pitch = doparam(head_obj.masterpitch, 'float', None, ['main', 'pitch'])
		cvpj_bpm = doparam(head_obj.bpm, 'float', None, ['main', 'bpm'])

		self.timesig = [timesig_numerator, timesig_denominator]
		convproj_obj.params.add('bpm', cvpj_bpm, 'float')
		convproj_obj.params.add('vol', cvpj_vol, 'float')
		convproj_obj.params.add('pitch', cvpj_pitch, 'float')

		if len(song_obj.projectnotes.text): 
			convproj_obj.metadata.comment_text = song_obj.projectnotes.text
			convproj_obj.metadata.comment_datatype = 'html'
			add_window_data(song_obj.projectnotes.window, convproj_obj, 'main', 'project_notes')

		lmms_decode_tracks(convproj_obj, song_obj.trackcontainer.tracks, False, 'LMMS_Track')

		for channum, lmms_fxchannel in song_obj.fxmixer.fxchannels.items():
			chan_vol = doparam(lmms_fxchannel.volume, 'float', None, ['fxmixer', str(channum), 'vol'])

			fxchannel_obj = convproj_obj.fx__chan__add(channum)
			if lmms_fxchannel.name: fxchannel_obj.visual.name = lmms_fxchannel.name
			fxchannel_obj.params.add('vol', chan_vol, 'float')
			fxchannel_obj.params.add('enabled', lmms_fxchannel.muted.value, 'bool')

			fxchannel_obj.fxslots_audio += decodefxchain(convproj_obj, lmms_fxchannel.fxchain)
			
			fxchannel_obj.sends.to_master_active = False

			for target_id, amount_obj in lmms_fxchannel.sends.items():
				send_id = send_auto_id_counter.get_str()

				if target_id == 0:
					fx_amount = doparam(amount_obj, 'float', None, ['send_master', send_id, 'amount'])
					fxchannel_obj.sends.to_master_active = True
					master_send = fxchannel_obj.sends.to_master
					master_send.params.add('amount', fx_amount, 'float')
					master_send.sendautoid = send_id
				else:
					fx_amount = doparam(amount_obj, 'float', None, ['send', send_id, 'amount'])
					fxchannel_obj.sends.add(target_id, send_id, fx_amount)

		autoid_assoc.output(convproj_obj)

		add_window_data(song_obj.fxmixer.window, convproj_obj, 'main', 'fxmixer')
		add_window_data(song_obj.ControllerRackView, convproj_obj, 'main', 'controller_rack_view')
		add_window_data(song_obj.pianoroll, convproj_obj, 'main', 'piano_roll')
		add_window_data(song_obj.automationeditor, convproj_obj, 'main', 'automation_editor')
		add_window_data(song_obj.projectnotes.window, convproj_obj, 'main', 'project_notes')

		convproj_obj.loop_active = bool(int(song_obj.timeline.lpstate))
		convproj_obj.loop_start = song_obj.timeline.lp0pos
		convproj_obj.loop_end = song_obj.timeline.lp1pos
		
		#convproj_obj.do_actions.append('force_addloop')

def get_xml_tree(path):
	with open(path, 'rb') as file:
		try:
			file.seek(4)
			data = zlib.decompress(file.read())
			return ET.fromstring(data)

		except zlib.error:
			return ET.parse(path).getroot()
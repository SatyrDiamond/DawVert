# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import lxml.etree as ET
import math
import plugins
import struct
from pathlib import Path
from objects import globalstore
from functions import data_values
import xml.etree

import logging
logger_output = logging.getLogger('output')

chordids = [None,"major","majb5","minor","minb5","sus2","sus4","aug","augsus4","tri","6","6sus4","6add9","m6","m6add9","7","7sus4","7#5","7b5","7#9","7b9","7#5#9","7#5b9","7b5b9","7add11","7add13","7#11","maj7","maj7b5","maj7#5","maj7#11","maj7add13","m7","m7b5","m7b9","m7add11","m7add13","m-maj7","m-maj7add11","m-maj7add13","9","9sus4","add9","9#5","9b5","9#11","9b13","maj9","maj9sus4","maj9#5","maj9#11","m9","madd9","m9b5","m9-maj7","11","11b9","maj11","m11","m-maj11","13","13#9","13b9","13b5b9","maj13","m13","m-maj13","full_major","harmonic_minor","melodic_minor","whole_tone","diminished","major_pentatonic","minor_pentatonic","jap_in_sen","major_bebop","dominant_bebop","blues","arabic","enigmatic","neopolitan","neopolitan_minor","hungarian_minor","dorian","phrygian","lydian","mixolydian","aeolian","locrian","full_minor","chromatic","half-whole_diminished","5","phrygian_dominant","persian"]

lfoshape = {'sine': 0,'triangle': 1,'saw_down': 2,'saw': 2,'square': 3,'custom': 4,'random': 5}
l_arpdirection = {'up': 0,'down': 1,'updown': 2,'downup': 3,'random': 4}
l_arpmode = {'free': 0,'sort': 1,'sync': 2}

fxlist = {}
fxlist['amplifier'] = 'AmplifierControls'
fxlist['bassbooster'] = 'bassboostercontrols'
fxlist['bitcrush'] = 'bitcrushcontrols'
fxlist['crossovereq'] = 'crossoevereqcontrols'
fxlist['delay'] = 'Delay'
fxlist['dualfilter'] = 'DualFilterControls'
fxlist['dynamicsprocessor'] = 'dynamicsprocessor_controls'
fxlist['eq'] = 'Eq'
fxlist['flanger'] = 'Flanger'
fxlist['multitapecho'] = 'multitapechocontrols'
fxlist['peakcontrollereffect'] = 'peakcontrollereffectcontrols'
fxlist['reverbsc'] = 'ReverbSCControls'
fxlist['spectrumanalyzer'] = 'spectrumanaylzercontrols'
fxlist['stereoenhancer'] = 'stereoenhancercontrols'
fxlist['stereomatrix'] = 'stereomatrixcontrols'
fxlist['waveshaper'] = 'waveshapercontrols'

def filternum(i_filtertype):
	i_type = i_filtertype.type
	i_subtype = i_filtertype.subtype

	lmms_filternum = 0
	if i_type == 'all_pass': lmms_filternum = 5

	if i_type == 'band_pass':
		if i_subtype == 'csg': lmms_filternum = 2
		if i_subtype == 'czpg': lmms_filternum = 3
		if i_subtype == 'rc12': lmms_filternum = 9
		if i_subtype == 'rc24': lmms_filternum = 12
		if i_subtype == 'sv': lmms_filternum = 17

	if i_type == 'formant':
		lmms_filternum = 14
		if i_subtype == 'fast': lmms_filternum = 20

	if i_type == 'high_pass':
		lmms_filternum = 1
		if i_subtype == 'rc12': lmms_filternum = 10
		if i_subtype == 'rc24': lmms_filternum = 13
		if i_subtype == 'sv': lmms_filternum = 18

	if i_type == 'low_pass':
		lmms_filternum = 0
		if i_subtype == 'double': lmms_filternum = 7
		if i_subtype == 'rc12': lmms_filternum = 8
		if i_subtype == 'rc24': lmms_filternum = 11
		if i_subtype == 'sv': lmms_filternum = 16

	if i_type == 'moog':
		lmms_filternum = 6
		if i_subtype == 'double': lmms_filternum = 15

	if i_type == 'notch':
		lmms_filternum = 4
		if i_subtype == 'sv': lmms_filternum = 19

	if i_type == 'tripole':
		lmms_filternum = 21

	return lmms_filternum

def add_window_data(lobj, w_group, w_name, w_pos, w_size, w_open, w_max):
	wobj = cvpj_obj.viswindow__get([w_group, w_name])
	if w_pos != None and wobj.pos_x == -1 and wobj.pos_y == -1: wobj.pos_x, wobj.pos_y = w_pos
	if w_size != None and wobj.size_x == -1 and wobj.size_y == -1: wobj.size_x, wobj.size_y = w_size
	lobj.visible = int(wobj.open if wobj.open != -1 else w_open)
	lobj.maximized = int(wobj.maximized if wobj.maximized != -1 else w_max)
	lobj.x = wobj.pos_x
	lobj.y = wobj.pos_y
	lobj.width = wobj.size_x
	lobj.height = wobj.size_y

def fix_value(val_type, value):
	if val_type == 'float': return float(value)
	elif val_type == 'int': return int(value)
	elif val_type == 'bool': return int(value)
	else: return value

def parse_auto(lmms_points, autopoints_obj):
	curpoint = 0
	auto_points = {}
	for point in autopoints_obj:
		if point.pos in auto_points: 
			auto_points[point.pos-1] = auto_points[point.pos]
			del auto_points[point.pos]
		auto_points[point.pos] = [point.value, point.type]

	for p, d in auto_points.items():
		if curpoint != 0 and autopoints_obj.val_type != 'bool' and d[1] == 'instant': 
			lmms_points[p-1] = fix_value(autopoints_obj.val_type, prevvalue)
		lmms_points[p] = fix_value(autopoints_obj.val_type, d[0])
		prevvalue = d[0]
		curpoint += 1

def make_auto_track(autoidnum, autodata, visualname, automode):
	from objects.file_proj import proj_lmms

	global song_obj
	lmms_track = proj_lmms.lmms_track()
	lmms_track.type = 5
	lmms_track.name = visualname

	for autopl_obj in autodata:
		autopl_obj.remove_cut()
		lmms_autopat = proj_lmms.lmms_automationpattern()
		lmms_autopat.pos = autopl_obj.time.position
		lmms_autopat.len = autopl_obj.time.duration
		lmms_autopat.prog = automode
		lmms_autopat.name = visualname
		parse_auto(lmms_autopat.auto_points, autopl_obj.data)
		lmms_autopat.auto_target.append(autoidnum)
		lmms_track.automationpatterns.append(lmms_autopat)

	song_obj.trackcontainer.tracks.append(lmms_track)

def paramauto(lmms_param, paramset_obj, c_name, c_defval, i_addmul, autoloc, v_type, v_name):
	param_obj = paramset_obj.get(c_name, c_defval)
	i_value = fix_value(param_obj.type, param_obj.value)
	if i_addmul != None: i_value = (i_value+i_addmul[0])*i_addmul[1]
	lmms_param.value = i_value
	aid_found, aid_data = cvpj_obj.automation.get(autoloc+[c_name], 'float')
	if aid_found:
		if i_addmul != None: aid_data.calc('addmul', i_addmul[0], i_addmul[1], 0, 0)
		lmms_param.id = aid_data.id
		lmms_param.scale_type = 'linear'
		lmms_param.expanded = True
		if aid_data.pl_points:
			make_auto_track(aid_data.id, aid_data.pl_points, v_type+': '+(v_name if v_name else param_obj.visual.name), 1 if param_obj.type != 'bool' else 0)

def set_timedata(lmms_param, timing_obj):
	lmms_param.value = timing_obj.speed_seconds*1000
	if timing_obj.type == 'steps':
		lmms_param.is_sync = True
		if timing_obj.speed_steps == 16*8: lmms_param.sync_mode = 1
		elif timing_obj.speed_steps == 16: lmms_param.sync_mode = 2
		elif timing_obj.speed_steps == 8: lmms_param.sync_mode = 3
		elif timing_obj.speed_steps == 4: lmms_param.sync_mode = 4
		elif timing_obj.speed_steps == 2: lmms_param.sync_mode = 5
		elif timing_obj.speed_steps == 1: lmms_param.sync_mode = 6
		elif timing_obj.speed_steps == 0.5: lmms_param.sync_mode = 7
		else: 
			lmms_param.sync_mode = 8
			lmms_param.sync_numerator, lmms_param.sync_denominator = timing_obj.get_frac()

def oneto100(input): return round(float(input) * 100)

def setvstparams(lmms_plug_obj, plugin_obj, pluginid, keysdict):
	vstpath = plugin_obj.getpath_fileref_global(cvpj_obj, 'plugin', 'win', False)

	lmms_plug_obj.add_param('program', str(plugin_obj.current_program))
	lmms_plug_obj.add_param('plugin', vstpath)

	if keysdict != None: keysdict['file'] = vstpath

	middlenotefix = plugin_obj.datavals_global.get('middlenotefix', 0)
	datatype = plugin_obj.datavals_global.get('datatype', 'chunk')
	numparams = plugin_obj.datavals_global.get('numparams', 0)

	if datatype == 'chunk':
		lmms_plug_obj.add_param('chunk', plugin_obj.rawdata_get_b64('chunk'))

		for cvpj_paramid in plugin_obj.params.list():
			if cvpj_paramid.startswith('ext_param_'):
				paramnum = int(cvpj_paramid[10:])
				param_obj = plugin_obj.params.get(cvpj_paramid, 0)
				vst_param = lmms_plug_obj.add_vst_param(paramnum)
				vst_param.value = param_obj.value
				aid_found, aid_data = cvpj_obj.automation.get(['plugin', pluginid, cvpj_paramid], 'float')
				if aid_found:
					vst_param.id = aid_data.id
					if aid_data.pl_points:
						make_auto_track(aid_data.id, aid_data.pl_points, 'VST: #'+str(paramnum), 1)

	if datatype == 'param':
		lmms_plug_obj.add_param('numparams', str(numparams))
		for param in range(numparams):
			cvpj_paramid = 'ext_param_'+str(param)
			param_obj = plugin_obj.params.get(cvpj_paramid, 0)
			vst_param = lmms_plug_obj.add_vst_param(param)
			vst_param.inlist = True
			vst_param.visname = param_obj.visual.name if param_obj.visual.name else 'noname'
			vst_param.value = param_obj.value
			aid_found, aid_data = cvpj_obj.automation.get(['plugin', pluginid, cvpj_paramid], 'float')

			if aid_found:
				vst_param.id = aid_data.id
				if aid_data.pl_points:
					make_auto_track(aid_data.id, aid_data.pl_points, 'VST: #'+str(param), 1)

	return middlenotefix

def encode_effectslot(effect_obj, plugin_obj, pluginid):
	from objects.file_proj import proj_lmms

	paramauto(effect_obj.on, plugin_obj.params_slot, 'enabled', True, None, ['slot', pluginid], 'Slot', 'On')
	paramauto(effect_obj.wet, plugin_obj.params_slot, 'wet', 1, None, ['slot', pluginid], 'Slot', 'Wet')

	lmms_plug_obj = effect_obj.plugin

	effect_obj.name = 'stereomatrix'
	lmms_plug_obj.name = 'stereomatrixcontrols'

	if plugin_obj.check_match('simple', 'reverb', None):
		effect_obj.name = 'reverbsc'
		lmms_plug_obj.name = 'ReverbSCControls'
		lmms_plug_obj.add_param('size', 0.2)
		lmms_plug_obj.add_param('color', 15000)

	elif plugin_obj.check_wildmatch('native', 'lmms', None):
		effect_obj.name = plugin_obj.type.subtype
		lmms_plug_obj.name = fxlist[plugin_obj.type.subtype]
		dset_plugparams(plugin_obj.type.subtype, pluginid, lmms_plug_obj, plugin_obj)

	elif plugin_obj.check_match('external', 'vst2', 'win'):
		if 'plugin' in plugin_obj.filerefs_global:
			effect_obj.name = 'vsteffect'
			lmms_plug_obj.name = 'vsteffectcontrols'
			setvstparams(lmms_plug_obj, plugin_obj, pluginid, effect_obj.keys)
		else:
			logger_output.warning('VST2 plugin not placed: file path not found.')

	elif plugin_obj.check_wildmatch('external', 'ladspa', None):
		effect_obj.name = 'ladspaeffect'
		lmms_plug_obj.name = 'ladspacontrols'

		effect_obj.keys['file'] = Path(plugin_obj.datavals.get('path', '')).stem
		effect_obj.keys['plugin'] = plugin_obj.datavals.get('plugin', '')

		ladspa_sep_chan = plugin_obj.datavals.get('seperated_channels', False)
		ladspa_numparams = plugin_obj.datavals.get('numparams', 0)
		lmms_plug_obj.ladspa_ports = ladspa_numparams*2
		lmms_plug_obj.ladspa_link = int(not ladspa_sep_chan)

		for paramid in plugin_obj.params.list():
			if paramid.startswith('ext_param_'):
				paramdata = paramid[10:].split('_')
				if len(paramdata) == 2: paramnum, channum = paramdata
				else: paramnum, channum = paramdata[0], 0
				paramnum = int(paramnum)
				lmms_paramid = 'port'+str(channum)+str(paramnum)
				cvpj_paramvisname = 'LADSPA: #'+str(paramnum+1)
				aid_found, aid_data = cvpj_obj.automation.get(['plugin', pluginid, paramid], 'float')
				ladspa_param_obj = proj_lmms.lmms_ladspa_param()
				ladspa_param_obj.data.value = plugin_obj.params.get(paramid, -1).value
				if channum == 0: ladspa_param_obj.link.value = int(not ladspa_sep_chan)
				paramauto(ladspa_param_obj.data, plugin_obj.params, paramid, ladspa_param_obj.data.value, None, ['plugin', pluginid], 'Plugin', cvpj_paramvisname)
				lmms_plug_obj.ladspa_params[lmms_paramid] = ladspa_param_obj

def encode_fxchain(lmms_fxchain, track_obj, trackname, autoloc):
	from objects.file_proj import proj_lmms

	#paramauto(lmms_fxchain.enabled, track_obj.params, 'fx_enabled', False, None, autoloc, trackname, 'FX Enabled')
	for pluginid in track_obj.plugslots.slots_audio:
		plugin_found, plugin_obj = cvpj_obj.plugin__get(pluginid)
		if plugin_found: 
			effect_obj = proj_lmms.lmms_effect()
			encode_effectslot(effect_obj, plugin_obj, pluginid)
			lmms_fxchain.effects.append(effect_obj)

def dset_plugparams(pluginname, pluginid, lmms_plug_obj, plugin_obj):
	for param_id, dset_param in globalstore.dataset.get_params('lmms', 'plugin', pluginname):
		if not dset_param.noauto: paramauto(lmms_plug_obj.add_param(param_id, dset_param.defv), plugin_obj.params, param_id, dset_param.defv, None, ['plugin', pluginid], 'Plugin', dset_param.name)
		else: lmms_plug_obj.add_param(param_id, plugin_obj.datavals.get(param_id, dset_param.defv))

def sec2exp(value): return math.sqrt(value/5)

def asdrlfo(plugin_obj, elpart, asdrtype):
	adsr_obj = plugin_obj.env_asdr_get(asdrtype)

	if asdrtype == 'cutoff': elpart.amt.value = adsr_obj.amount/6000
	else: elpart.amt.value = adsr_obj.amount
	elpart.pdel.value = sec2exp(adsr_obj.predelay)
	elpart.att.value = sec2exp(adsr_obj.attack)
	elpart.hold.value = sec2exp(adsr_obj.hold)
	elpart.dec.value = sec2exp(adsr_obj.decay)
	elpart.sustain.value = adsr_obj.sustain
	elpart.rel.value = sec2exp(adsr_obj.release*( pow(2, adsr_obj.release_tension*2) ))

	lfo_obj = plugin_obj.lfo_get(asdrtype)
	if asdrtype == 'cutoff': elpart.lamt.value = lfo_obj.amount/6000
	else: elpart.lamt.value = lfo_obj.amount
	if lfo_obj.prop.shape == 'saw': elpart.lamt.value = -elpart.lamt.value
	elpart.lpdel.value = sec2exp(lfo_obj.predelay/4)
	elpart.latt.value = sec2exp(lfo_obj.attack)
	elpart.lshp.value = lfoshape[lfo_obj.prop.shape] if lfo_obj.prop.shape in lfoshape else 'sine'
	lfospeed = lfo_obj.time.speed_seconds / 20
	if lfospeed > 1:
		elpart.x100.value = 1
		lfospeed = lfospeed/100
	elpart.lspd.value = lfospeed

def asdrlfo_set(plugin_obj, eldata):
	filter_obj = plugin_obj.filter

	eldata.fcut.value = filter_obj.freq
	eldata.ftype.value = filternum(filter_obj.type)
	eldata.fwet.value = int(filter_obj.on)
	eldata.fres.value = filter_obj.q

	asdrlfo(plugin_obj, eldata.elvol, 'vol')
	asdrlfo(plugin_obj, eldata.elcut, 'cutoff')
	asdrlfo(plugin_obj, eldata.elres, 'reso')

class output_lmms(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'LMMS'
	def get_shortname(self): return 'lmms'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'mmp'
		in_dict['fxtype'] = 'rack'
		in_dict['fxrack_params'] = ['enabled','vol']
		in_dict['auto_types'] = ['pl_points']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:soundfont2','native:lmms','universal:arpeggiator','universal:chord_creator','universal:delay']
		in_dict['plugin_ext'] = ['vst2','ladspa']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['projtype'] = 'r'
		
	def parse(self, i_cvpj_obj, output_file):
		from objects.file_proj import proj_lmms

		global lmms_bpm
		global cvpj_obj
		global project_obj
		global song_obj
		
		cvpj_obj = i_cvpj_obj

		globalstore.dataset.load('lmms', './data_main/dataset/lmms.dset')

		i_cvpj_obj.change_timings(48, False)

		project_obj = proj_lmms.lmms_project()
		song_obj = project_obj.song
		head_obj = project_obj.head

		add_window_data(song_obj.trackcontainer.window, 'main', 'tracklist', [5,5], [720,300], True, False)
		add_window_data(song_obj.fxmixer.window, 'main', 'fxmixer', [102,280], [543,333], True, False)
		add_window_data(song_obj.ControllerRackView, 'main', 'controller_rack_view', [680,310], [350,200], False, False)
		add_window_data(song_obj.pianoroll, 'main', 'piano_roll', [5,5], [970,480], False, False)
		add_window_data(song_obj.projectnotes.window, 'main', 'automation_editor', [1,1], [860,400], False, False)

		lmms_bpm = cvpj_obj.params.get('bpm', 140).value

		paramauto(head_obj.bpm, cvpj_obj.params, 'bpm', 120, None, ['main'], 'Main', 'Tempo')
		paramauto(head_obj.masterpitch, cvpj_obj.params, 'pitch', 0, None, ['main'], 'Main', 'Pitch')
		paramauto(head_obj.mastervol, cvpj_obj.params, 'vol', 1, [0, 100], ['main'], 'Main', 'Volume')
		head_obj.timesig_numerator.value = cvpj_obj.timesig[0]
		head_obj.timesig_denominator.value = cvpj_obj.timesig[1]

		for trackid, track_obj in cvpj_obj.track__iter():
			autoloc = ['track', trackid]
			trackname = track_obj.visual.name if track_obj.visual.name else 'noname'
			trackcolor = track_obj.visual.color

			if track_obj.type in ['instrument', 'audio']:
				lmms_track = proj_lmms.lmms_track()
				lmms_track.name = trackname
				song_obj.trackcontainer.tracks.append(lmms_track)

				if trackcolor: lmms_track.color = '#' + trackcolor.get_hex()
				paramauto(lmms_track.solo, track_obj.params, 'solo', False, None, autoloc, trackname, 'Solo')
				paramauto(lmms_track.muted, track_obj.params, 'muted', True, [-1, -1], autoloc, trackname, 'On')

				if track_obj.type == 'instrument':
					lmms_track.type = 0
					insttrack_obj = lmms_track.instrumenttrack

					insttrack_obj.fxch.value = track_obj.fxrack_channel
					insttrack_obj.pitchrange.value = 12

					paramauto(insttrack_obj.vol, track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol')
					paramauto(insttrack_obj.pan, track_obj.params, 'pan', 0, [0, -100], autoloc, trackname, 'Pan')
					paramauto(insttrack_obj.usemasterpitch, track_obj.params, 'usemasterpitch', not track_obj.is_drum, None, autoloc, trackname, 'Use Master Pitch')
					paramauto(insttrack_obj.pitch, track_obj.params, 'pitch', 0, [0, 100], autoloc, trackname, 'Pitch')

					for pluginid in track_obj.plugslots.slots_notes:
						plugin_found, plugin_obj = cvpj_obj.plugin__get(pluginid)
						if plugin_found:
							if plugin_obj.check_match('universal', 'arpeggiator', None):
								arp_obj = insttrack_obj.arpeggiator
								paramauto(arp_obj.arp_enabled, plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Arp', 'On')

								arpdir = plugin_obj.datavals.get('direction', 'up')
								arpmode = plugin_obj.datavals.get('mode', 'free')

								set_timedata(arp_obj.arptime, plugin_obj.timing_get('main'))
								arp_obj.arpdir.value = l_arpdirection[arpdir] if arpdir in l_arpdirection else 0
								arp_obj.arpmode.value = l_arpmode[arpmode] if arpmode in l_arpmode else 0
								arp_obj.arpgate.value = plugin_obj.datavals.get('gate', 1)*100
								arp_obj.arpcycle.value = plugin_obj.datavals.get('cycle', 0)
								arp_obj.arprange.value = plugin_obj.datavals.get('range', 0)
								arp_obj.arpmiss.value = plugin_obj.datavals.get('miss_rate', 0)*100
								arp_obj.arpskip.value = plugin_obj.datavals.get('skip_rate', 0)*100
								chord_obj = plugin_obj.chord_get('main')
								arp_obj.arp.value = chordids.index(chord_obj.chord_type) if chord_obj.chord_type in chordids else 0

							if plugin_obj.check_match('universal', 'chord_creator', None):
								cc_obj = insttrack_obj.chordcreator
								paramauto(cc_obj.chord_enabled, plugin_obj.params_slot, 'enabled', False, None, ['slot', pluginid], 'Chord', 'On')
								chord_obj = plugin_obj.chord_get('main')
								cc_obj.chord.value = chordids.index(chord_obj.chord_type) if chord_obj.chord_type in chordids else 0
								cc_obj.chordrange.value = plugin_obj.datavals.get('range', 0)

					lmms_inst_obj = insttrack_obj.instrument
					lmms_plug_obj = lmms_inst_obj.plugin

					middlenotefix = 0

					plugin_found, plugin_obj = cvpj_obj.plugin__get(track_obj.plugslots.synth)
					if plugin_found:
						if plugin_obj.check_match('universal', 'sampler', 'single') or plugin_obj.check_match('universal', 'sampler', 'drumsynth'):
							lmms_inst_obj.name = 'audiofileprocessor'
							lmms_plug_obj.name = 'audiofileprocessor'

							sp_obj = plugin_obj.samplepart_get('sample')
							_, sampleref_obj = cvpj_obj.sampleref__get(sp_obj.sampleref)
							sp_obj.convpoints_percent(sampleref_obj)

							lmms_plug_obj.add_param('reversed', int(sp_obj.reverse))
							lmms_plug_obj.add_param('amp', oneto100(sp_obj.vol))
							lmms_plug_obj.add_param('stutter', int(sp_obj.get_data('continueacrossnotes', False)))
							lmms_plug_obj.add_param('src', sp_obj.get_filepath(cvpj_obj, False) )
				
							lmms_plug_obj.add_param('sframe', sp_obj.start)
							lmms_plug_obj.add_param('lframe', sp_obj.loop_start)
							lmms_plug_obj.add_param('eframe', sp_obj.loop_end if sp_obj.loop_active else sp_obj.end)
				
							if sp_obj.loop_active == 0: lmms_plug_obj.add_param('looped', 0)
							if sp_obj.loop_active == 1:
								if sp_obj.loop_mode == "normal": lmms_plug_obj.add_param('looped', 1)
								if sp_obj.loop_mode == "pingpong": lmms_plug_obj.add_param('looped', 2)
				
							if sp_obj.interpolation == "none": lmms_plug_obj.add_param('interp', 0)
							elif sp_obj.interpolation == "linear": lmms_plug_obj.add_param('interp', 1)
							elif sp_obj.interpolation == "sinc": lmms_plug_obj.add_param('interp', 2)
							else: lmms_plug_obj.add_param('interp', 2)
							middlenotefix += 3

						elif plugin_obj.check_wildmatch('universal', 'soundfont2', None):
							lmms_inst_obj.name = 'sf2player'
							lmms_plug_obj.name = 'sf2player'
							bank, patch = plugin_obj.midi.to_sf2()
							lmms_plug_obj.add_param('bank', bank)
							lmms_plug_obj.add_param('patch', patch)
							ref_found, fileref_obj = plugin_obj.fileref__get('file', cvpj_obj)
							if ref_found: lmms_plug_obj.add_param('src', fileref_obj.get_path(None, False))
							paramauto(lmms_plug_obj.add_param('gain', 1), plugin_obj.params, 'gain', 1, None, ['plugin', track_obj.plugslots.synth], 'Plugin', 'gain')
							middlenotefix += 12

						elif plugin_obj.check_match('external', 'vst2', 'win'):
							if 'plugin' in plugin_obj.filerefs_global:
								lmms_inst_obj.name = 'vestige'
								lmms_plug_obj.name = 'vestige'
								middlenotefix += setvstparams(lmms_plug_obj, plugin_obj, track_obj.plugslots.synth, None)
							else:
								logger_output.warning('VST2 plugin not placed: file path not found.')

						elif plugin_obj.check_wildmatch('native', 'lmms', None):
							lmms_inst_obj.name = plugin_obj.type.subtype
							lmms_plug_obj.name = plugin_obj.type.subtype
							dset_plugparams(plugin_obj.type.subtype, track_obj.plugslots.synth, lmms_plug_obj, plugin_obj)

							if plugin_obj.type.subtype == 'zynaddsubfx':
								zdata = plugin_obj.rawdata_get('data')
								if zdata != b'':
									xmlstr = zdata.decode('ascii')
									lmms_plug_obj.custom['ZynAddSubFX-data'] = xml.etree.ElementTree.fromstring(xmlstr)

							if plugin_obj.type.subtype == 'tripleoscillator':
								for oscnum in range(3):
									sp_obj = plugin_obj.samplepart_get('userwavefile'+str(oscnum))
									lmms_plug_obj.add_param('userwavefile'+str(oscnum), sp_obj.get_filepath(cvpj_obj, None))

							if plugin_obj.type.subtype == 'vibedstrings':
								for num in range(9):
									graphid = 'graph'+str(num)
									wave_obj = plugin_obj.wave_get(graphid)
									wave_data = wave_obj.get_wave(128)
									graphdata = base64.b64encode(struct.pack('f'*128, *wave_data)).decode()
									lmms_plug_obj.add_param(graphid, graphdata)

					if plugin_obj: asdrlfo_set(plugin_obj, insttrack_obj.eldata)

					middlenote = track_obj.datavals.get('middlenote', 0)+middlenotefix
					insttrack_obj.basenote = middlenote+57

					track_obj.placements.pl_notes.sort()
					for notespl_obj in track_obj.placements.pl_notes:
						lmms_pattern = proj_lmms.lmms_pattern()
						lmms_pattern.pos = int(notespl_obj.time.position)
						lmms_pattern.muted = int(notespl_obj.muted)
						lmms_pattern.name = notespl_obj.visual.name if notespl_obj.visual.name else ""
						if notespl_obj.visual.color: lmms_pattern.color = '#' + notespl_obj.visual.color.get_hex()
						notespl_obj.notelist.sort()
						notespl_obj.notelist.notemod_conv()
						for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
							for t_key in t_keys:
								lmms_note = proj_lmms.lmms_note()
								lmms_note.key = int(t_key)+60
								lmms_note.pos = int(t_pos)
								if t_extra: 
									if 'pan' in t_extra: lmms_note.pan = oneto100(t_extra['pan'])
								lmms_note.len = int(max(1,t_dur))
								lmms_note.vol = int(oneto100(t_vol))
								lmms_pattern.notes.append(lmms_note)
								if t_auto:
									if 'pitch' in t_auto: 
										detuneauto = proj_lmms.lmms_automationpattern()
										detuneauto.prog = 1
										parse_auto(detuneauto.auto_points, t_auto['pitch'])
										lmms_note.auto['detuning'] = detuneauto

						lmms_track.patterns.append(lmms_pattern)

					midiport_obj = insttrack_obj.midiport
					midiport_obj.fixedoutputvelocity = track_obj.midi.out_fixedvelocity
					midiport_obj.readable = int(track_obj.midi.in_enabled)
					midiport_obj.basevelocity = track_obj.midi.basevelocity
					midiport_obj.outputprogram = track_obj.midi.out_inst.patch
					midiport_obj.writable = int(track_obj.midi.out_enabled)
					midiport_obj.fixedinputvelocity = track_obj.midi.in_fixedvelocity
					midiport_obj.inputchannel = track_obj.midi.in_chan+1
					midiport_obj.outputchannel = track_obj.midi.out_chan+1
					midiport_obj.fixedoutputnote = track_obj.midi.out_inst.key
					encode_fxchain(insttrack_obj.fxchain, track_obj, trackname, autoloc)

				if track_obj.type == 'audio':
					lmms_track.type = 2
					samptrack_obj = lmms_track.sampletrack

					samptrack_obj.fxch.value = track_obj.fxrack_channel
					paramauto(samptrack_obj.vol, track_obj.params, 'vol', 1, [0, 100], autoloc, trackname, 'Vol')
					paramauto(samptrack_obj.pan, track_obj.params, 'pan', 0, [0, -100], autoloc, trackname, 'Pan')

					track_obj.placements.pl_audio.sort()
					for audiopl_obj in track_obj.placements.pl_audio:
						lmms_sampletco = proj_lmms.lmms_sampletco()
						lmms_sampletco.pos = int(audiopl_obj.time.position)
						lmms_sampletco.len = int(audiopl_obj.time.duration)
						ref_found, sampleref_obj = cvpj_obj.sampleref__get(audiopl_obj.sample.sampleref)
						if ref_found: lmms_sampletco.src = sampleref_obj.fileref.get_path(None, False)
						lmms_sampletco.muted = int(audiopl_obj.muted)
						if audiopl_obj.visual.color: lmms_sampletco.color = '#' + audiopl_obj.visual.color.get_hex()
						if audiopl_obj.time.cut_type == 'cut': lmms_sampletco.off = int(audiopl_obj.time.cut_start*-1)
						lmms_track.sampletcos.append(lmms_sampletco)

					encode_fxchain(samptrack_obj.fxchain, track_obj, trackname, autoloc)

		for num, fxchannel_obj in cvpj_obj.fx__chan__iter():
			autoloc = ['fxmixer', str(num)]
			autoname = 'FX' + str(num)

			lmms_fxchannel = proj_lmms.lmms_fxchannel()

			lmms_fxchannel.name = fxchannel_obj.visual.name if fxchannel_obj.visual.name else 'FX '+str(num)
			if fxchannel_obj.visual.color: lmms_fxchannel.color = '#' + fxchannel_obj.visual.color.get_hex()

			paramauto(lmms_fxchannel.soloed, fxchannel_obj.params, 'solo', False, None, autoloc, autoname, 'Solo')
			paramauto(lmms_fxchannel.muted, fxchannel_obj.params, 'muted', True, [-1, -1], autoloc, autoname, 'Enabled')
			paramauto(lmms_fxchannel.volume, fxchannel_obj.params, 'vol', 1, None, autoloc, autoname, 'Volume')

			encode_fxchain(lmms_fxchannel.fxchain, fxchannel_obj, autoname, autoloc)

			if fxchannel_obj.sends.to_master_active:
				master_send_obj = fxchannel_obj.sends.to_master

				sendamount = proj_lmms.lmms_param('amount', 1)
				sendamount.value = master_send_obj.params.get('amount', 1).value
				lmms_fxchannel.sends[0] = sendamount
				visual_name = 'Send '+str(num)+' > Master'
				if master_send_obj.sendautoid: 
					paramauto(sendamount, master_send_obj.params, 'amount', sendamount.value, None, ['send_master', master_send_obj.sendautoid], visual_name, 'Amount')

			if fxchannel_obj.sends.check():
				for target, send_obj in fxchannel_obj.sends.iter():
					sendamount = proj_lmms.lmms_param('amount', 1)
					sendamount.value = send_obj.params.get('amount', 1).value
					lmms_fxchannel.sends[target] = sendamount

					if send_obj.sendautoid: 
						visual_name = 'Send '+str(num)+' > '+str(target)
						paramauto(sendamount, send_obj.params, 'amount', sendamount.value, None, ['send', send_obj.sendautoid], visual_name, 'Amount')

			elif num != 0:
				sendamount = proj_lmms.lmms_param('amount', 1)
				sendamount.value = 1
				lmms_fxchannel.sends[0] = sendamount

			song_obj.fxmixer.fxchannels[num] = lmms_fxchannel

		if cvpj_obj.metadata.name: 
			song_obj.projectnotes.text += '"'+cvpj_obj.metadata.name+'"'
			if cvpj_obj.metadata.author: song_obj.projectnotes.text += ' by ' + cvpj_obj.metadata.author
			song_obj.projectnotes.text += '<hr>'

		if cvpj_obj.metadata.comment_text:
			add_window_data(song_obj.projectnotes.window, 'main', 'project_notes', [728, 5], [389, 300], True, False)
			song_obj.projectnotes.window.visible = 1
			if cvpj_obj.metadata.comment_datatype == 'html': 
				song_obj.projectnotes.text += cvpj_obj.metadata.comment_text
			if cvpj_obj.metadata.comment_datatype == 'text': 
				song_obj.projectnotes.text += cvpj_obj.metadata.comment_text.replace('\n', '<br/>').replace('\r', '<br/>')

		if cvpj_obj.loop_active:
			song_obj.timeline.lpstate = int(cvpj_obj.loop_active)
			song_obj.timeline.lp0pos = cvpj_obj.loop_start
			song_obj.timeline.lp1pos = cvpj_obj.loop_end
		else:
			song_obj.timeline.lpstate = 1
			song_obj.timeline.lp0pos = cvpj_obj.start_pos
			song_obj.timeline.lp1pos = cvpj_obj.get_dur()

		project_obj.save_to_file(output_file)
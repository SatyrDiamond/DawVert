# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import rpp
import struct
import base64
import os.path
from rpp import Element
from objects import globalstore
from functions import data_bytes
from functions import data_values
from functions import xtramath
from objects.data_bytes import bytewriter

import logging
logger_output = logging.getLogger('output')

base_sampler = {'filename': '', 'volume': 1.0, 'pan': 0.5, 'min_vol_gain': 0.0, 'key_start': 0.0, 'key_end': 1.0, 'pitch_start': 0.06875, 'pitch_end': 0.86875, 'midi_chan': 0.0, 'voices': 4.0, 'env_attack': 0.0005, 'env_release': 0.0005, 'obey_note_offs': 0.0, 'loop_on': 0.0, 'start': 0.0, 'end': 1.0, 'pitch_offset': 0.5, 'mode': 2, '__unk17': 0.0, '__unk18': 1.0, 'cache_sample_size': 64, 'pitch_bend': 0.16666666666666666, 'resample_mode': -1, 'vel_max': 0.007874015748031496, 'vel_min': 1.0, 'prob_hitting': 1.0, 'round_robin': 0.0, 'filter_played': 0.0, 'xfade': 0.0, 'loop_start': 0.0, 'env_decay': 0.016010673782521682, 'env_sustain': 1.0, 'note_off_release_override': 0.00025, 'note_off_release_override__enabled': 0.0, 'legacy_voice_reuse': 0.0, 'porta': 0.0}

def make_sampler(rpp_fxchain, sampler_params):
	rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
	rpp_vst_obj.vst_lib = 'reasamplomatic.dll'
	rpp_vst_obj.vst_fourid = 1920167789
	rpp_vst_obj.vst_name = 'VSTi: ReaSamplOmatic5000 (Cockos)'

	rpp_vst_obj.data_chunk = datadef_obj.create('reasamplomatic', sampler_params)
	vstheader_ints = (1920167789, 4276969198, 0, 2, 1, 0, 2, 0, len(rpp_vst_obj.data_chunk), 1, 1048576)
	rpp_vst_obj.data_con = struct.pack('IIIIIIIIIII', *vstheader_ints)

def do_sample_part(sampler_params, sampleref_obj, sp_obj):
	if sampleref_obj:
		dur = sampleref_obj.dur_samples
		hz = sampleref_obj.hz

		sampler_params['loop_on'] = int(sp_obj.loop_active)

		if hz:
			sampler_params['loop_start'] = sp_obj.loop_start/30/hz
		if dur:
			sampler_params['start'] = sp_obj.start/dur
			sampler_params['end'] = sp_obj.end/dur
			if sp_obj.loop_active:
				sampler_params['end'] = max(sampler_params['end'], sp_obj.loop_end/dur)

def do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj):
	dur_sec = sampleref_obj.dur_sec

	if adsr_obj.amount:
		if not sp_obj.loop_active: 
			if dur_sec:
				sampler_params['env_attack'] = adsr_obj.attack/dur_sec
				sampler_params['env_decay'] = adsr_obj.decay/15
				sampler_params['env_sustain'] = adsr_obj.sustain
				sampler_params['env_release'] = adsr_obj.release/dur_sec
		else: 
			sampler_params['env_attack'] = adsr_obj.attack/2
			sampler_params['env_decay'] = adsr_obj.decay/15
			sampler_params['env_sustain'] = adsr_obj.sustain
			sampler_params['env_release'] = adsr_obj.release/2

def add_auto(rpp_env, autopoints_obj):
	for x in autopoints_obj:
		rpp_env.points.append([x.pos_real, x.value])

def add_plugin(rpp_fxchain, pluginid, convproj_obj):
	plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
	if plugin_found:
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.check_wildmatch('universal', 'sampler', 'single'):
			sp_obj = plugin_obj.samplepart_get('sample')
			_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
			sp_obj.convpoints_samples(sampleref_obj)

			sampler_params = base_sampler.copy()
			sampler_params['filename'] = sp_obj.get_filepath(convproj_obj, False)
			sampler_params['pitch_start'] = (-60/80)/2 + 0.5
			sampler_params['obey_note_offs'] = int(sp_obj.trigger != 'oneshot')

			adsr_obj = plugin_obj.env_asdr_get('vol')
			do_sample_part(sampler_params, sampleref_obj, sp_obj)
			do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj)

			make_sampler(rpp_fxchain, sampler_params)

		if plugin_obj.check_wildmatch('universal', 'sampler', 'multi'):
			for sampleregion in plugin_obj.sampleregions:
				key_l, key_h, key_r, samplerefid, extradata = sampleregion

				sp_obj = plugin_obj.samplepart_get(samplerefid)

				sampler_params = base_sampler.copy()
				sampler_params['mode'] = 2
				sampler_params['filename'] = sp_obj.get_filepath(convproj_obj, False)
				sampler_params['key_start'] = (key_l+60)/127
				sampler_params['key_end'] = (key_h+60)/127

				pitch = -60 + key_l+60 - key_r

				sampler_params['pitch_start'] = (pitch/80)/2 + 0.5
				sampler_params['obey_note_offs'] = int(sp_obj.trigger != 'oneshot')
				_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
				do_sample_part(sampler_params, sampleref_obj, sp_obj)
				make_sampler(rpp_fxchain, sampler_params)


		if plugin_obj.check_wildmatch('external', 'vst2', None):
			vst_fx_fourid = plugin_obj.datavals_global.get('fourid', 0)
			if vst_fx_fourid:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
				vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
				vst_fx_datatype = plugin_obj.datavals_global.get('datatype', None)
				vst_fx_numparams = plugin_obj.datavals_global.get('numparams', 0)

				rpp_vst_obj.vst_name = plugin_obj.datavals_global.get('basename', '')
				if not rpp_vst_obj.vst_name: plugin_obj.datavals_global.get('name', '')

				rpp_vst_obj.vst_lib = os.path.basename(vst_fx_path)
				rpp_vst_obj.vst_fourid = vst_fx_fourid

				vstparamsnum = 0
				vstparams = None
		
				if vst_fx_datatype == 'chunk': 
					vstparams = plugin_obj.rawdata_get('chunk')
					vstparamsnum = len(vstparams)
				if vst_fx_datatype == 'param': 
					floatdata = []
					for num in range(vst_fx_numparams):
						floatdata.append(float(plugin_obj.params.get('ext_param_'+str(num), 0).value))
					vstparams = b'\xef\xbe\xad\xde\r\xf0\xad\xde'+struct.pack('f'*vst_fx_numparams, *floatdata)
					vstparamsnum = len(vstparams)

				pluginfo_obj = globalstore.extplug.get('vst2', 'id', vst_fx_fourid, None, [64, 32])

				vsthdrwriter = bytewriter.bytewriter()
				vsthdrwriter.uint32(vst_fx_fourid)
				vsthdrwriter.uint32(4276969198)
				vsthdrwriter.uint32(2)
				vsthdrwriter.uint32(1)
				for _ in range(pluginfo_obj.audio_num_inputs if pluginfo_obj.audio_num_inputs else 2):
					vsthdrwriter.flags64([33])
				for n in range(pluginfo_obj.audio_num_outputs if pluginfo_obj.audio_num_inputs else 2):
					vsthdrwriter.flags64([n])
				vsthdrwriter.uint32(vstparamsnum)
				vsthdrwriter.uint32(vst_fx_datatype == 'chunk')
				vsthdrwriter.uint16(plugin_obj.current_program)
				vsthdrwriter.uint8(16)
				vsthdrwriter.uint8(0)

				rpp_vst_obj.data_con = vsthdrwriter.getvalue()
				if vstparams: rpp_vst_obj.data_chunk = vstparams
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_nopl_points_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto(parmenv_obj, autodata)
			else:
				logger_output.warning('VST2 plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'vst3', None):
			vst_fx_id = plugin_obj.datavals_global.get('id', 0)
			if vst_fx_id:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
				vst_fx_name = plugin_obj.datavals_global.get('name', None)
				vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
				vst_fx_version = plugin_obj.datavals_global.get('version', None)

				chunkdata = plugin_obj.rawdata_get('chunk')
				vstparams = struct.pack('II', len(chunkdata), 1)+chunkdata+b'\x00\x00\x00\x00\x00\x00\x00\x00'
				vstheader = b':\xfbA+\xee^\xed\xfe'
				vstheader += struct.pack('II', 0, plugin_obj.audioports.num_outputs)
				for n in range(plugin_obj.audioports.num_outputs): 
					if n < len(plugin_obj.audioports.ports): vstheader += data_bytes.set_bitnums(plugin_obj.audioports.ports[n], 8)
					else: vstheader += b'\x00\x00\x00\x00\x00\x00\x00\x00'
				vstheader_end = (len(chunkdata)+16).to_bytes(4, 'little')+b'\x01\x00\x00\x00\xff\xff\x10\x00'

				rpp_vst_obj.vst_fourid = 0
				rpp_vst_obj.vst3_uuid = vst_fx_id
				rpp_vst_obj.data_con = vstheader+vstheader_end
				rpp_vst_obj.data_chunk = vstparams
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_nopl_points_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto(parmenv_obj, autodata)
			else:
				logger_output.warning('VST3 plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'clap', None):
			clap_fx_id = plugin_obj.datavals_global.get('id', '')
			if clap_fx_id:
				rpp_plug_obj, rpp_clap_obj, rpp_guid = rpp_fxchain.add_clap()
				clap_fx_name = plugin_obj.visual.name
	
				chunkdata = plugin_obj.rawdata_get('chunk')
				rpp_clap_obj.data_chunk = chunkdata
				rpp_clap_obj.clap_name = clap_fx_name
				rpp_clap_obj.clap_id = clap_fx_id
	
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_nopl_points_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto(parmenv_obj, autodata)
			else:
				logger_output.warning('CLAP plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'jesusonic', None):
			rpp_plug_obj, rpp_js_obj, rpp_guid = rpp_fxchain.add_js()
			rpp_js_obj.js_id = plugin_obj.type.subtype
			rpp_js_obj.data = [plugin_obj.datavals_global.get(str(n), '-') for n in range(64)]
			rpp_plug_obj.bypass['bypass'] = not fx_on
			rpp_plug_obj.wet['wet'] = fx_wet
			if fx_wet != 1: rpp_plug_obj.wet.used = True



def cvpj_color_to_reaper_color(i_color): 
	cvpj_trackcolor = bytes(i_color.get_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

def cvpj_color_to_reaper_color_clip(i_color): 
	cvpj_trackcolor = bytes(i_color.getbgr_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

def midi_add_cmd(i_list, i_pos, i_cmd):
	if i_pos not in i_list: i_list[i_pos] = []
	i_list[i_pos].append(i_cmd)

def convert_midi(rpp_source_obj,notelist, tempo, num, dem, notespl_obj):
	i_list = {}
	notelist.sort()
	notelist.change_timings(960, False)

	n_enddur = notelist.get_dur()
	p_enddur = notespl_obj.time.duration*(960//4)

	for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notelist.iter():
		for t_key in t_keys:
			cvmi_n_pos = int(t_pos)
			cvmi_n_dur = int(t_dur)
			cvmi_n_key = int(t_key)+60
			cvmi_n_vol = xtramath.clamp(int(t_vol*127), 0, 127)
			midi_add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
			midi_add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

	if p_enddur-n_enddur >= 0:
		midi_add_cmd(i_list, p_enddur, ['end'])

	i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

	prevpos = 0
	for i_list_e in i_list:
		for midi_notedata in i_list[i_list_e]:
			if midi_notedata[0] == 'note_on': 
				rpp_source_obj.notes.append([False,i_list_e-prevpos, '90', hex(midi_notedata[1])[2:], hex(midi_notedata[2])[2:]])
			if midi_notedata[0] == 'note_off': 
				rpp_source_obj.notes.append([False,i_list_e-prevpos, '80', hex(midi_notedata[1])[2:], '00'])
			if midi_notedata[0] == 'end': 
				rpp_source_obj.notes.append([False,int(i_list_e-prevpos), 'b0', '7b', '00'])
			prevpos = i_list_e
	
def file_source(rpp_source_obj, fileref_obj, filename):
	rpp_source_obj.file.set(filename)
	if fileref_obj.file.extension == 'mp3': rpp_source_obj.type = 'MP3'
	elif fileref_obj.file.extension == 'flac': rpp_source_obj.type = 'FLAC'
	elif fileref_obj.file.extension == 'ogg': rpp_source_obj.type = 'VORBIS'
	else: rpp_source_obj.type = 'WAVE'

def do_fade(fade_data, fadevals, bpm): 
	fadevals['fade_time'] = fade_data.get_dur_seconds(bpm)
	fadevals['fade_type'] = 2
	fadevals['curve'] = 0

class output_reaper(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'REAPER'
	def get_shortname(self): return 'reaper'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'rpp'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['fxtype'] = 'route'
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['auto_types'] = ['nopl_points']
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_ext'] = ['vst2', 'vst3', 'clap']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:sampler:multi']
		in_dict['projtype'] = 'r'
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_reaper
		from objects.file_proj._rpp import fxchain as rpp_fxchain
		from objects.file_proj._rpp import source as rpp_source

		global reaper_tempo
		global tempomul
		global datadef_obj

		globalstore.datadef.load('reaper', './data_main/datadef/reaper.ddef')
		datadef_obj = globalstore.datadef.get('reaper')

		convproj_obj.change_timings(4, True)

		reaper_numerator, reaper_denominator = convproj_obj.timesig
		reaper_tempo = convproj_obj.params.get('bpm', 120).value

		tempomul = reaper_tempo/120
		project_obj = proj_reaper.rpp_song()

		rpp_project = project_obj.project
		rpp_project.tempo['tempo'] = reaper_tempo
		rpp_project.tempo['num'] = convproj_obj.timesig[0]
		rpp_project.tempo['denom'] = convproj_obj.timesig[1]

		track_uuids = ['{'+str(uuid.uuid4())+'}' for _ in convproj_obj.track__iter()]

		trackdata = []

		tracknum = 0
		for trackid, track_obj in convproj_obj.track__iter():
			track_uuid = track_uuids[tracknum]

			rpp_track_obj = rpp_project.add_track()

			rpp_track_obj.trackid.set(track_uuid)
			if track_obj.visual.name: rpp_track_obj.name.set(track_obj.visual.name)
			if track_obj.visual.color: rpp_track_obj.peakcol.set(cvpj_color_to_reaper_color(track_obj.visual.color))
			rpp_track_obj.volpan['vol'] = track_obj.params.get('vol', 1.0).value
			rpp_track_obj.volpan['pan'] = track_obj.params.get('pan', 0).value

			rpp_track_obj.rec['armed'] = int(track_obj.armed.on)

			middlenote = track_obj.datavals.get('middlenote', 0)

			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.plugslots.synth)
			if plugin_found: middlenote += plugin_obj.datavals_global.get('middlenotefix', 0)

			rpp_track_obj.fxchain = rpp_fxchain.rpp_fxchain()

			if middlenote != 0:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_track_obj.fxchain.add_vst()
				rpp_vst_obj.data_con = b'\x64\x6d\x63\x72\xee\x5e\xed\xfe\x00\x00\x00\x00\x00\x00\x00\x00\xe6\x00\x00\x00\x01\x00\x00\x00\x00\x00\x10\x00'
				midictrlstate1 = b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\xff?\x00\x00\x00 \x00\x00\x00 \x00\x00\x00\x00\x00\x005\x00\x00\x00C:\\Users\\colby\\AppData\\Roaming\\REAPER\\Data\\GM.reabank\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
				midictrlstate2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00Major\x00\r\x00\x00\x00102034050607\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\r\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00'
				midictrlstate3 = struct.pack('i', -middlenote)
				rpp_vst_obj.data_chunk = midictrlstate1+midictrlstate3+midictrlstate2
				rpp_vst_obj.vst_name = 'ReaControlMIDI (Cockos)'
				rpp_vst_obj.vst_lib = 'reacontrolmidi.dll'
				rpp_vst_obj.vst_fourid = 1919118692
				rpp_vst_obj.vst_uuid = '56535472636D64726561636F6E74726F'

			for notespl_obj in track_obj.placements.pl_notes:

				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()
				if notespl_obj.time.cut_type == 'cut': rpp_item_obj.soffs.set(notespl_obj.time.cut_start/8/tempomul)
				rpp_item_obj.position.set(notespl_obj.time.position_real)
				rpp_item_obj.length.set(notespl_obj.time.duration_real)
				rpp_item_obj.mute['mute'] = int(notespl_obj.muted)
				if notespl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(notespl_obj.visual.color))
				if notespl_obj.visual.name: rpp_item_obj.name.set(notespl_obj.visual.name)
				rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()
				rpp_source_obj.type = 'MIDI'
				rpp_source_obj.hasdata.used = True
				rpp_source_obj.hasdata['hasdata'] = 1

				convert_midi(rpp_source_obj,notespl_obj.notelist,reaper_tempo,'4','4',notespl_obj)

			for audiopl_obj in track_obj.placements.pl_audio:
				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()

				audiorate = audiopl_obj.sample.stretch.calc_real_speed
				clip_startat = 0
				if audiopl_obj.time.cut_type == 'cut': clip_startat = audiopl_obj.time.cut_start/8
				clip_startat *= audiopl_obj.sample.stretch.calc_tempo_speed
				rpp_item_obj.soffs.set(clip_startat)

				rpp_item_obj.position.set(audiopl_obj.time.position_real)
				rpp_item_obj.length.set(audiopl_obj.time.duration_real)
				rpp_item_obj.mute['mute'] = int(audiopl_obj.muted)
				if audiopl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(audiopl_obj.visual.color))
				if audiopl_obj.visual.name: rpp_item_obj.name.set(audiopl_obj.visual.name)
				rpp_item_obj.volpan['vol'] = audiopl_obj.sample.vol
				rpp_item_obj.volpan['pan'] = audiopl_obj.sample.pan

				do_fade(audiopl_obj.fade_in, rpp_item_obj.fadein, reaper_tempo)
				do_fade(audiopl_obj.fade_out, rpp_item_obj.fadeout, reaper_tempo)

				rpp_item_obj.playrate['rate'] = audiorate
				rpp_item_obj.playrate['preserve_pitch'] = int(audiopl_obj.sample.stretch.preserve_pitch)
				rpp_item_obj.playrate['pitch'] = audiopl_obj.sample.pitch

				ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)
				if ref_found:
					fileref_obj = sampleref_obj.fileref
					filename = fileref_obj.get_path(None, False)
					rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()
					if not audiopl_obj.sample.reverse: file_source(rpp_source_obj, fileref_obj, filename)
					else:
						rpp_source_obj.type = 'SECTION'
						rpp_source_obj.mode.set(3)
						rpp_insource_obj = rpp_source_obj.source = rpp_source.rpp_source()
						file_source(rpp_insource_obj, fileref_obj, filename)

			for fxid in track_obj.plugslots.slots_synths:
				add_plugin(rpp_track_obj.fxchain, fxid, convproj_obj)

			for fxid in track_obj.plugslots.slots_audio:
				add_plugin(rpp_track_obj.fxchain, fxid, convproj_obj)

			trackdata.append(rpp_track_obj)

			tracknum += 1

		if convproj_obj.trackroute:
			for tracknum, trackid in enumerate(convproj_obj.track_order):
				if trackid in convproj_obj.trackroute:
					sends_obj = convproj_obj.trackroute[trackid]
					tracksendnum = convproj_obj.track_order.index(trackid)
					trackdata[tracknum].mainsend['tracknum'] = int(sends_obj.to_master_active)
					for target, send_obj in sends_obj.iter():
						if target in convproj_obj.track_order:
							trackrecnum = convproj_obj.track_order.index(target)
							auxrecv_obj = trackdata[trackrecnum].add_auxrecv()
							auxrecv_obj['tracknum'] = tracksendnum
							auxrecv_obj['vol'] = send_obj.params.get('amount', 1).value
							auxrecv_obj['pan'] = send_obj.params.get('pan', 0).value

		
		project_obj.save_to_file(output_file)
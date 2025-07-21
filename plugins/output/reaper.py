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
		dur = sampleref_obj.get_dur_sec()
		hz = sampleref_obj.get_hz()

		sp_obj.convpoints_samples(sampleref_obj)

		sampler_params['loop_on'] = int(sp_obj.loop_active)

		if hz:
			sampler_params['loop_start'] = sp_obj.loop_start/30/hz
		if dur:
			sampler_params['start'] = sp_obj.start/dur
			sampler_params['end'] = sp_obj.end/dur
			if sp_obj.loop_active:
				sampler_params['end'] = max(sampler_params['end'], sp_obj.loop_end/dur)

def do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj):
	dur_sec = sampleref_obj.get_dur_sec()

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

def add_auto_all(rpp_project, convproj_obj, rpp_env, autopath, valtype, inverted):
	if_found, autodata = convproj_obj.automation.get(autopath, valtype)

	if if_found:
		rpp_env.used = True
		rpp_env.eguid.set('{'+str(uuid.uuid4()).upper()+'}')

		if autodata.u_pl_points:
			if autodata.pl_points:
				rpp_env.used = True
				rpp_env.act['bypass'] = 1
				rpp_env.arm.set(1)
				
				if not autodata.persist:
					rpp_env.points.append([0, autodata.defualt_val, 0])

				for n, p in enumerate(autodata.pl_points):
					time_obj = p.time
					position, duration = time_obj.get_posdur_real()

					poolid = len(rpp_project.pooledenvs)+1
					pooledenv = rpp_project.add_pooledenv()
					pooledenv.id.set(poolid)
					if p.visual.name: pooledenv.name.set(p.visual.name)
					pooledenv.srclen.set(duration*2)

					for pn, x in enumerate(p.data):
						out = float(x.value)
						if inverted: out = 1-out
						#if n==0 and pn==0: rpp_env.points.append([0, out])
						pooledenv.points.append([(x.pos*2), out, 5 if x.tension else 0, -x.tension])
	
					init_pooledenvinst = rpp_env.init_pooledenvinst()
					init_pooledenvinst['id'] = poolid
					init_pooledenvinst['unk1'] = poolid
					init_pooledenvinst['position'] = position
					init_pooledenvinst['length'] = duration
					init_pooledenvinst['enabled'] = int(bool(p.muted))

		elif autodata.u_nopl_points:
			autodata.nopl_points.remove_instant()
			for x in autodata.nopl_points:
				rpp_env.act['bypass'] = 1
				out = float(x.value)
				if inverted: out = 1-out

				if x.tension == 0:
					rpp_env.points.append([x.pos, out, 0])
				else:
					rpp_env.points.append([x.pos, out, 5, 1, 0, 0, -x.tension])

def add_auto(rpp_env, autopoints_obj):
	for x in autopoints_obj:
		rpp_env.points.append([x.pos, x.value])

def add_plugin(rpp_project, rpp_fxchain, pluginid, convproj_obj, track_obj):
	plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)

	if plugin_found:
		fx_on, fx_wet = plugin_obj.fxdata_get()

		pitch = track_obj.params.get('pitch',0).value

		if plugin_obj.check_wildmatch('universal', 'sampler', 'single'):
			sp_obj = plugin_obj.samplepart_get('sample')
			_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)
			sp_obj.convpoints_samples(sampleref_obj)

			sampler_params = base_sampler.copy()
			sampler_params['filename'] = sp_obj.get_filepath(convproj_obj, False)
			sampler_params['pitch_start'] = (-60/80)/2 + 0.5
			sampler_params['obey_note_offs'] = int(sp_obj.trigger != 'oneshot')
			sampler_params['pitch_offset'] = (pitch/80)/2 + 0.5

			adsr_obj = plugin_obj.env_asdr_get('vol')
			do_sample_part(sampler_params, sampleref_obj, sp_obj)
			do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj)

			make_sampler(rpp_fxchain, sampler_params)

		if plugin_obj.check_match('universal', 'sampler', 'drums'):
			for drumpad in plugin_obj.drumpad_getall():
				keys = [drumpad.key]+drumpad.key_copy
				for key in keys:
					for layer_obj in drumpad.layers:
						sp_obj = plugin_obj.samplepart_get(layer_obj.samplepartid)
		
						sampler_params = base_sampler.copy()
						sampler_params['mode'] = 2
						sampler_params['filename'] = sp_obj.get_filepath(convproj_obj, False)
						sampler_params['key_start'] = (key+60)/127
						sampler_params['key_end'] = (key+60)/127
						sampler_params['obey_note_offs'] = 0

						pitch = -60 + key+60 - key
						sampler_params['pitch_start'] = (pitch/80)/2 + 0.5

						_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)

						do_sample_part(sampler_params, sampleref_obj, sp_obj)
						if sampleref_obj:
							adsr_obj = plugin_obj.env_asdr_get(sp_obj.envs['vol'] if 'vol' in sp_obj.envs else 'vol')
							do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj)
						make_sampler(rpp_fxchain, sampler_params)

		if plugin_obj.check_wildmatch('universal', 'sampler', 'multi'):
			adsr_obj = plugin_obj.env_asdr_get('vol')
			for sampleregion in plugin_obj.sampleregion_getall():
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
				if sampleref_obj:
					adsr_obj = plugin_obj.env_asdr_get(sp_obj.envs['vol'] if 'vol' in sp_obj.envs else 'vol')
					do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj)
				make_sampler(rpp_fxchain, sampler_params)

		if plugin_obj.check_wildmatch('universal', 'sampler', 'drums'):
			adsr_obj = plugin_obj.env_asdr_get('vol')
			for sampleregion in plugin_obj.sampleregion_getall():
				key_l, key_h, key_r, samplerefid, extradata = sampleregion

				sp_obj = plugin_obj.samplepart_get(samplerefid)

				sampler_params = base_sampler.copy()
				sampler_params['mode'] = 2
				sampler_params['filename'] = sp_obj.get_filepath(convproj_obj, False)
				sampler_params['key_start'] = (key_l+60)/127
				sampler_params['key_end'] = (key_h+60)/127

				pitch = -60 + key_l+60 - key_r

				sampler_params['pitch_start'] = (pitch/80)/2 + 0.5
				sampler_params['obey_note_offs'] = 0
				_, sampleref_obj = convproj_obj.sampleref__get(sp_obj.sampleref)

				#do_sample_part(sampler_params, sampleref_obj, sp_obj)
				if sampleref_obj:
					adsr_obj = plugin_obj.env_asdr_get(sp_obj.envs['vol'] if 'vol' in sp_obj.envs else 'vol')
					#do_adsr(sampler_params, adsr_obj, sampleref_obj, sp_obj)
				make_sampler(rpp_fxchain, sampler_params)


		if plugin_obj.check_wildmatch('external', 'vst2', None):
			vst_fx_fourid = plugin_obj.external_info.fourid
			if vst_fx_fourid:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
				vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
				vst_fx_datatype = plugin_obj.external_info.datatype
				vst_fx_numparams = max(plugin_obj.external_info.numparams, 0)

				rpp_vst_obj.vst_name = plugin_obj.external_info.basename
				if not rpp_vst_obj.vst_name: rpp_vst_obj.vst_name = plugin_obj.external_info.name

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
				vsthdrwriter.int16(plugin_obj.current_program)
				vsthdrwriter.uint8(16)
				vsthdrwriter.uint8(0)

				rpp_vst_obj.data_con = vsthdrwriter.getvalue()
				if vstparams: rpp_vst_obj.data_chunk = vstparams
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_all_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto_all(rpp_project, convproj_obj, parmenv_obj, list(autoloc), 'float', False)
			else:
				logger_output.warning('VST2 plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'vst3', None):
			vst_fx_id = plugin_obj.external_info.id
			if vst_fx_id:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
				vst_fx_name = plugin_obj.external_info.name
				vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
				vst_fx_version = plugin_obj.external_info.version

				chunkdata = plugin_obj.rawdata_get('chunk')
				vstparams = struct.pack('II', len(chunkdata), 1)+chunkdata+b'\x00\x00\x00\x00\x00\x00\x00\x00'
				vstheader = b':\xfbA+\xee^\xed\xfe'
				vstheader += struct.pack('II', 0, plugin_obj.audioports.num_outputs)
				for n in range(plugin_obj.audioports.num_outputs): 
					if n < len(plugin_obj.audioports.ports): vstheader += data_bytes.set_bitnums(plugin_obj.audioports.ports[n], 8)
					else: vstheader += b'\x00\x00\x00\x00\x00\x00\x00\x00'
				vstheader_end = (len(chunkdata)+16).to_bytes(4, 'little')+b'\x01\x00\x00\x00\xff\xff\x10\x00'

				rpp_vst_obj.vst_name = plugin_obj.external_info.name
				rpp_vst_obj.vst_fourid = 0
				rpp_vst_obj.vst3_uuid = vst_fx_id
				rpp_vst_obj.data_con = vstheader+vstheader_end
				rpp_vst_obj.data_chunk = vstparams
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_all_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto_all(rpp_project, convproj_obj, parmenv_obj, list(autoloc), 'float', False)
			else:
				logger_output.warning('VST3 plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'clap', None):
			clap_fx_id = plugin_obj.external_info.id
			if clap_fx_id:
				rpp_plug_obj, rpp_clap_obj, rpp_guid = rpp_fxchain.add_clap()
				clap_fx_name = plugin_obj.visual.name
				if not clap_fx_name: clap_fx_name = plugin_obj.external_info.name

				chunkdata = plugin_obj.rawdata_get('chunk')
				rpp_clap_obj.data_chunk = chunkdata
				if clap_fx_name: rpp_clap_obj.clap_name = clap_fx_name
				rpp_clap_obj.clap_id = clap_fx_id
	
				rpp_plug_obj.bypass['bypass'] = not fx_on
				rpp_plug_obj.wet['wet'] = fx_wet
				if fx_wet != 1: rpp_plug_obj.wet.used = True

				for autoloc, autodata, paramnum in convproj_obj.automation.iter_all_external(pluginid):
					parmenv_obj = rpp_plug_obj.add_env()
					parmenv_obj.param_id = paramnum
					add_auto_all(rpp_project, convproj_obj, parmenv_obj, list(autoloc), 'float', False)
			else:
				logger_output.warning('CLAP plugin not placed: no ID found.')

		if plugin_obj.check_wildmatch('external', 'jesusonic', None):
			rpp_plug_obj, rpp_js_obj, rpp_guid = rpp_fxchain.add_js()
			rpp_js_obj.js_id = plugin_obj.type.subtype
			rpp_js_obj.data = [plugin_obj.datavals_global.get(str(n), '-') for n in range(64)]
			rpp_plug_obj.bypass['bypass'] = not fx_on
			rpp_plug_obj.wet['wet'] = fx_wet
			if fx_wet != 1: rpp_plug_obj.wet.used = True

		if plugin_obj.check_wildmatch('external', 'directx', None):
			rpp_plug_obj, rpp_dx_obj, rpp_guid = rpp_fxchain.add_dx()
			external_info = plugin_obj.external_info
			if external_info.name:
				if plugin_obj.role == 'fx': rpp_dx_obj.dx_name = 'DXi: '+external_info.name
				if plugin_obj.role == 'synth': rpp_dx_obj.dx_name = 'DX: '+external_info.name
			extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
			rpp_dx_obj.data_chunk = extmanu_obj.dx__export_presetdata()

def cvpj_color_to_reaper_color(i_color): 
	cvpj_trackcolor = bytes(i_color.get_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

def cvpj_color_to_reaper_color_clip(i_color): 
	cvpj_trackcolor = bytes(i_color.getbgr_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

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

def do_auto_clip(placement_obj, rpp_env, mpetype, paramtype, invert, instant): 
	if mpetype in placement_obj.auto:
		autopoints_obj = placement_obj.auto[mpetype]
		autopoints_obj.remove_instant()
		rpp_env.used = True
		rpp_env.act['bypass'] = 1
		for x in autopoints_obj:
			out = float(x.value)
			if invert: out = 1-out
			rpp_env.points.append([x.pos, out])

class output_reaper(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_name(self):
		return 'REAPER'
	
	def get_shortname(self):
		return 'reaper'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'rpp'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['fxtype'] = 'route'
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['notes_midi'] = True
		in_dict['auto_types'] = ['nopl_points']
		#in_dict['auto_types'] = ['nopl_points', 'pl_points']
		in_dict['audio_stretch'] = ['rate', 'warp']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_ext'] = ['vst2', 'vst3', 'clap']
		in_dict['plugin_ext_arch'] = [32, 64]
		in_dict['plugin_ext_platforms'] = ['win', 'unix']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:sampler:multi']
		in_dict['projtype'] = 'r'
	
	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import reaper as proj_reaper
		from objects.file_proj._rpp import fxchain as rpp_fxchain
		from objects.file_proj._rpp import source as rpp_source

		global reaper_tempo
		global datadef_obj

		globalstore.datadef.load('reaper', './data_main/datadef/reaper.ddef')
		datadef_obj = globalstore.datadef.get('reaper')

		convproj_obj.change_timings(4.0)

		reaper_numerator, reaper_denominator = convproj_obj.timesig
		reaper_tempo = convproj_obj.params.get('bpm', 120).value

		project_obj = proj_reaper.rpp_song()

		rpp_project = project_obj.project
		rpp_project.tempo['tempo'] = reaper_tempo
		rpp_project.tempo['num'] = convproj_obj.timesig[0]
		rpp_project.tempo['denom'] = convproj_obj.timesig[1]

		groupassoc = {}
		groupcounter = 2

		if convproj_obj.metadata.name:
			rpp_project.title.set(convproj_obj.metadata.name)
		if convproj_obj.metadata.author:
			rpp_project.author.set(convproj_obj.metadata.author)
		for t in convproj_obj.metadata.comment_text.replace("\r\n", "\r").replace("\n", "\r").split('\r'):
			rpp_project.notes_data.append(t)
		if convproj_obj.metadata.show == 1:
			rpp_project.notes_vals.read([3,3])

		#tempo env
		tempoenvex = rpp_project.tempoenvex

		if_found, autodata = convproj_obj.automation.get(['main', 'bpm'], 'float')
		if if_found:
			if autodata.u_nopl_points:
				tempoenvex.used = 1
				nextinstant = True
				for x in autodata.nopl_points:
					tempoenvex.points.append([x.pos, x.value, int(nextinstant)])
					nextinstant = x.instant_mode

		#tempo env end


		rpp_project.loop.set(int(convproj_obj.transport.loop_active))
		rpp_project.selection['start'] = convproj_obj.transport.loop_start
		rpp_project.selection['end'] = convproj_obj.transport.loop_end
		rpp_project.cursor.set(convproj_obj.transport.current_pos)

		track_uuids = ['{'+str(uuid.uuid4())+'}' for _ in convproj_obj.track__iter()]

		for num, timemarker_obj in enumerate(convproj_obj.timemarkers):
			name = timemarker_obj.visual.name if timemarker_obj.visual.name else ''
			color = cvpj_color_to_reaper_color(timemarker_obj.visual.color) if timemarker_obj.visual.color else 0
			outmarker = [num+1, timemarker_obj.position, name, int(timemarker_obj.type == 'region'), color, 1, 'R', '{'+str(uuid.uuid4()).upper()+'}', 0]
			rpp_project.markers.append(outmarker)
			if timemarker_obj.type == 'region':
				outmarker = [num+1, timemarker_obj.position+timemarker_obj.duration, '', 1]
				rpp_project.markers.append(outmarker)

		trackdata = []

		tracknum = 0
		for trackid, track_obj in convproj_obj.track__iter():
			track_uuid = track_uuids[tracknum]

			rpp_track_obj = rpp_project.add_track()

			rpp_track_obj.trackid.set(track_uuid)
			if track_obj.visual.name: rpp_track_obj.name.set(track_obj.visual.name)
			if track_obj.visual.color: 
				rpp_track_obj.peakcol.set(cvpj_color_to_reaper_color(track_obj.visual.color))
			rpp_track_obj.volpan['vol'] = track_obj.params.get('vol', 1.0).value
			rpp_track_obj.volpan['pan'] = track_obj.params.get('pan', 0).value
			rpp_track_obj.mutesolo['mute'] = int(not track_obj.params.get('enabled', 1).value)
			rpp_track_obj.mutesolo['solo'] = int(track_obj.params.get('solo', 0).value)

			pan_mode = track_obj.datavals.get('pan_mode', '')
			if pan_mode == 'mono': rpp_track_obj.panmode.set(3)
			if pan_mode == 'stereo': rpp_track_obj.panmode.set(5)
			if pan_mode == 'split': 
				rpp_track_obj.panmode.set(6)
				rpp_track_obj.volpan['left'] = track_obj.params.get('splitpan_left', -1).value
				rpp_track_obj.volpan['right'] = track_obj.params.get('splitpan_right', 1).value

			for pluginid in track_obj.plugslots.slots_mixer:
				plugin_found, plugin_obj = convproj_obj.plugin__get(pluginid)
				if plugin_found:
					if plugin_obj.check_match('universal', 'invert', None):
						inverse_on, _ = plugin_obj.fxdata_get()
						rpp_track_obj.iphase.set(int(inverse_on))

			add_auto_all(rpp_project, convproj_obj, rpp_track_obj.volenv2, ['track', trackid, 'vol'], "float", False)
			add_auto_all(rpp_project, convproj_obj, rpp_track_obj.panenv2, ['track', trackid, 'pan'], "float", False)
			add_auto_all(rpp_project, convproj_obj, rpp_track_obj.muteenv, ['track', trackid, 'enabled'], "bool", True)
			add_auto_all(rpp_project, convproj_obj, rpp_track_obj.dualpanenvl2, ['track', trackid, 'splitpan_left'], "float", False)
			add_auto_all(rpp_project, convproj_obj, rpp_track_obj.dualpanenv2, ['track', trackid, 'splitpan_right'], "float", False)

			rpp_track_obj.rec['armed'] = int(track_obj.armed.on)

			middlenote = track_obj.datavals.get('middlenote', 0)

			plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.plugslots.synth)
			if plugin_found: middlenote += plugin_obj.datavals_global.get('middlenotefix', 0)

			rpp_track_obj.fxchain = rpp_fxchain.rpp_fxchain()

			rpp_track_obj.playoffs['time'] = track_obj.latency_offset/1000
			rpp_track_obj.playoffs['mode'] = 0 if track_obj.latency_offset else 1

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

			for midipl_obj in track_obj.placements.pl_midi:
				time_obj = midipl_obj.time

				position, duration = time_obj.get_posdur_real()
				
				tempomul = (time_obj.realtime_tempo/120)

				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()
				if time_obj.cut_type == 'cut': 
					if time_obj.cut_start.timemode == 'ppq':
						rpp_item_obj.soffs.set(time_obj.cut_start.value/8/tempomul)
					if time_obj.cut_start.timemode == 'seconds':
						rpp_item_obj.soffs.set(time_obj.cut_start.value)

				if time_obj.duration.timemode == 'ppq':
					rpp_item_obj.length.set(time_obj.duration.value/8/tempomul)
				if time_obj.duration.timemode == 'seconds':
					rpp_item_obj.length.set(time_obj.duration.value)

				rpp_item_obj.position.set(position)
				#rpp_item_obj.length.set(duration)
				rpp_item_obj.mute['mute'] = int(midipl_obj.muted)
				if midipl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(midipl_obj.visual.color))
				if midipl_obj.visual.name: rpp_item_obj.name.set(midipl_obj.visual.name)
				rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()

				midievents_obj = midipl_obj.midievents

				rpp_source_obj.type = 'MIDI'
				rpp_source_obj.hasdata.used = True
				rpp_source_obj.hasdata['hasdata'] = 1
				rpp_source_obj.hasdata['ppq'] = midievents_obj.ppq

				do_auto_clip(midipl_obj, rpp_item_obj.volenv, 'gain', 'float', False, False)
				do_auto_clip(midipl_obj, rpp_item_obj.panenv, 'pan', 'float', False, False)
				do_auto_clip(midipl_obj, rpp_item_obj.muteenv, 'mute', 'bool', False, True)
				do_auto_clip(midipl_obj, rpp_item_obj.pitchenv, 'pitch', 'float', False, False)

				midievents_obj.sort()
				midievents_obj.del_note_durs()
				midievents_obj.sort()

				ppos = 0
				for x in midievents_obj.iter_events():
					etype = x[1]
					posdir = int(x[0])-ppos
					if etype == 'NOTE_ON':
						rpp_source_obj.notes.append([True, posdir, f'{(144+int(x[2])):x}', f'{(int(x[3])):x}', f'{(int(x[4])):x}'])
						ppos = int(x[0])
					if etype == 'NOTE_OFF':
						rpp_source_obj.notes.append([True,	posdir, f'{(128+int(x[2])):x}', f'{(int(x[3])):x}', '00'])
						ppos = int(x[0])

				#convert_midi(rpp_source_obj,midipl_obj.notelist,reaper_tempo,'4','4',midipl_obj)

				if midipl_obj.locked: rpp_item_obj.lock.set(int(midipl_obj.locked))

				if midipl_obj.group:
					groupidtr = midipl_obj.group
					if groupidtr not in groupassoc:
						groupassoc[groupidtr] = groupcounter
						groupcounter += 1
					rpp_item_obj.group.set(groupassoc[groupidtr])

			for audiopl_obj in track_obj.placements.pl_audio:
				time_obj = audiopl_obj.time
				position, duration = time_obj.get_posdur_real()
				
				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()
				
				clip_startat = 0

				rpp_item_obj.position.set(position)
				rpp_item_obj.length.set(duration)
				rpp_item_obj.mute['mute'] = int(audiopl_obj.muted)
				if audiopl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(audiopl_obj.visual.color))
				if audiopl_obj.visual.name: rpp_item_obj.name.set(audiopl_obj.visual.name)
				rpp_item_obj.volpan['vol'] = audiopl_obj.sample.vol
				rpp_item_obj.volpan['pan'] = audiopl_obj.sample.pan

				do_auto_clip(audiopl_obj, rpp_item_obj.volenv, 'gain', 'float', False, False)
				do_auto_clip(audiopl_obj, rpp_item_obj.panenv, 'pan', 'float', False, False)
				do_auto_clip(audiopl_obj, rpp_item_obj.muteenv, 'mute', 'bool', False, True)
				do_auto_clip(audiopl_obj, rpp_item_obj.pitchenv, 'pitch', 'float', False, False)

				do_fade(audiopl_obj.fade_in, rpp_item_obj.fadein, reaper_tempo)
				do_fade(audiopl_obj.fade_out, rpp_item_obj.fadeout, reaper_tempo)

				sp_obj = audiopl_obj.sample
				stretch_obj = sp_obj.stretch

				rppart_audio_params = 0
				rppart_audio_stretch = 9

				stretch_algo = stretch_obj.algorithm

				if stretch_algo.type == 'elastique_v3':
					if stretch_algo.subtype == 'pro': rppart_audio_stretch = 9
					if stretch_algo.subtype == 'efficient': rppart_audio_stretch = 10
					if stretch_algo.subtype == 'mono': rppart_audio_stretch = 11
					if stretch_algo.subtype == 'speech': 
						rppart_audio_stretch = 11
						rppart_audio_params = 2

				if stretch_algo.type == 'elastique_v2':
					if stretch_algo.subtype == 'pro': rppart_audio_stretch = 6
					if stretch_algo.subtype == 'efficient': rppart_audio_stretch = 7
					if stretch_algo.subtype == 'mono': rppart_audio_stretch = 8
					if stretch_algo.subtype == 'speech': 
						rppart_audio_stretch = 8
						rppart_audio_params = 2

				if stretch_algo.type == 'rubberband': rppart_audio_stretch = 13

				if stretch_algo.type == 'soundtouch':
					stmode = stretch_obj.params['mode'] if 'mode' in stretch_obj.params else None
					if stmode == 'hq': rppart_audio_params = 1
					elif stmode == 'fast': rppart_audio_params = 2
					rppart_audio_stretch = 0

				if stretch_algo.type == 'simple_windowing': rppart_audio_stretch = 2

				rpp_item_obj.playrate['stretch_mode'] = (rppart_audio_stretch<<16) + rppart_audio_params

				ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)

				tempomul = (time_obj.realtime_tempo/120)

				if time_obj.cut_type == 'cut': clip_startat = time_obj.get_offset_real()
				#print(clip_startat)

				s_timing_obj = stretch_obj.timing

				if s_timing_obj.time_type != 'warp':
					audiorate = s_timing_obj.get__real_rate(sampleref_obj, reaper_tempo)
					rpp_item_obj.playrate['rate'] = audiorate
					clip_startat *= audiorate
				else:
					warp_obj = s_timing_obj.warp
					warprate = warp_obj.speed
					audiorate = warprate*tempomul

					rpp_item_obj.playrate['rate'] = round(audiorate, 14) 
					rpp_item_obj.stretchmarks = []

					offmod = clip_startat*audiorate
					offmod = round(offmod, 7)

					warp_obj.fix__onlyone()
					warp_obj.manp__speed_mul(warprate)
					for num, warp_point_obj in enumerate(warp_obj.points__iter()):
						m_beat = (warp_point_obj.beat/4)*2
						m_second = warp_point_obj.second
						m_beat -= offmod
						rpp_item_obj.stretchmarks.append([m_beat, m_second])

				if time_obj.cut_type == 'cut': 
					if time_obj.cut_start.timemode == 'ppq':
						rpp_item_obj.soffs.set(clip_startat)
					if time_obj.cut_start.timemode == 'seconds':
						rpp_item_obj.soffs.set(time_obj.get_offset_real())

				rpp_item_obj.playrate['preserve_pitch'] = int(stretch_obj.preserve_pitch)
				rpp_item_obj.playrate['pitch'] = audiopl_obj.sample.pitch

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

				if audiopl_obj.locked: rpp_item_obj.lock.set(int(audiopl_obj.locked))

				if audiopl_obj.group:
					groupidtr = audiopl_obj.group
					if groupidtr not in groupassoc:
						groupassoc[groupidtr] = groupcounter
						groupcounter += 1
					rpp_item_obj.group.set(groupassoc[groupidtr])

			for videopl_obj in track_obj.placements.pl_video:
				time_obj = videopl_obj.time
				position, duration = time_obj.get_posdur_real()

				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()

				rpp_item_obj.position.set(position)
				rpp_item_obj.length.set(duration)
				rpp_item_obj.mute['mute'] = int(videopl_obj.muted)
				if videopl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(videopl_obj.visual.color))
				if videopl_obj.visual.name: rpp_item_obj.name.set(videopl_obj.visual.name)
				rpp_item_obj.volpan['vol'] = videopl_obj.vol

				tempomul = (time_obj.realtime_tempo/120)

				clip_startat = 0
				if time_obj.cut_type == 'cut': clip_startat = (time_obj.cut_start/8)/tempomul
				rpp_item_obj.soffs.set(clip_startat)

				ref_found, videoref_obj = convproj_obj.videoref__get(videopl_obj.videoref)
				if ref_found:
					filename = videoref_obj.fileref.get_path(None, False)
					rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()
					rpp_source_obj.type = 'VIDEO'
					rpp_source_obj.file.set(filename)
	
			for fxid in track_obj.plugslots.slots_synths:
				add_plugin(rpp_project, rpp_track_obj.fxchain, fxid, convproj_obj, track_obj)

			for fxid in track_obj.plugslots.slots_audio:
				add_plugin(rpp_project, rpp_track_obj.fxchain, fxid, convproj_obj, track_obj)

			if track_obj.visual_keynotes:
				rpp_track_obj.midinotenames = []
				for k, v in track_obj.visual_keynotes.items():
					note = str(k+60)
					rpp_track_obj.midinotenames.append(['-1', note, v.name, '0', note])

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
							rpp_track = trackdata[trackrecnum]
							auxrecv_obj = rpp_track.add_auxrecv()
							auxrecv_obj['tracknum'] = tracksendnum
							auxrecv_obj['vol'] = send_obj.params.get('amount', 1).value
							auxrecv_obj['pan'] = send_obj.params.get('pan', 0).value
							if send_obj.sendautoid:
								aux_env = rpp_track.add_aux_env('vol', tracksendnum)
								add_auto_all(rpp_project, convproj_obj, aux_env, ['send', send_obj.sendautoid, 'amount'], 'float', False)
								aux_env = rpp_track.add_aux_env('pan', tracksendnum)
								add_auto_all(rpp_project, convproj_obj, aux_env, ['send', send_obj.sendautoid, 'pan'], 'float', False)
		
		if dawvert_intent.output_mode == 'file':
			project_obj.save_to_file(dawvert_intent.output_file)
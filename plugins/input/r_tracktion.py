# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter
from objects import globalstore
from functions import xtramath
import plugins
import logging
import math
import os

logger_input = logging.getLogger('input')

sampler_filter_types = {
	0: 'low_pass',
	1: 'low_pass',
	2: 'low_pass',
	3: 'band_pass',
	4: 'band_pass',
	5: 'high_pass',
	6: 'high_pass',
	7: 'high_pass',
	8: 'notch',
	9: 'notch'
}

sampler_filter_slopes = {
	0: 6,
	1: 12,
	2: 24,
	3: 12,
	4: 24,
	5: 6,
	6: 12,
	7: 24,
	8: 12,
	9: 24
}

def get_dictval_fb(d, key, fb, checktype): 
	if key in d:
		if d[key] is not None: 
			outv = d[key]
			if checktype is None: return outv
			elif isinstance(outv, checktype): return outv
	return fb

def sampler_soundlayer_samplepart(sp_obj, soundlayer, layerparams): 
	sp_obj.visual.name = soundlayer.name
	sp_obj.point_value_type = 'samples'
	sp_obj.sampleref = soundlayer.sampleDataName
	if sp_obj.sampleref[0] == ':': sp_obj.sampleref = sp_obj.sampleref[1:]
	sp_obj.start = int(soundlayer.sampleIn)
	sp_obj.end = int(soundlayer.sampleOut)
	sp_obj.reverse = bool(soundlayer.reverse)
	sp_obj.vel_min = int(soundlayer.lowVelocity)/127
	sp_obj.vel_max = int(soundlayer.highVelocity)/127
	sp_obj.loop_start = int(soundlayer.sampleLoopIn)
	sp_obj.loop_end = int(soundlayer.sampleLoopOut)
	sp_obj.loop_active = int(soundlayer.looped)
	sp_obj.enabled = not soundlayer.mute

	sp_obj.vol = get_dictval_fb(layerparams, 'gainParam', 1, float)
	sp_obj.pan = get_dictval_fb(layerparams, 'gainParam', 0, float)
	sp_obj.pitch = soundlayer.offlinePitchShift
	sp_obj.no_pitch = soundlayer.fixedPitch

	stretch_obj = sp_obj.stretch
	stretch_obj.timing.set__speed(soundlayer.offlineTimeStretch)
	if soundlayer.pitchShift or soundlayer.offlineTimeStretch != 1: stretch_obj.preserve_pitch = True

	if 'sensParam' in layerparams:
		if layerparams['sensParam'] is not None: sp_obj.data['vel_sens'] = layerparams['sensParam']

def sampler_soundlayer_adsr(plugin_obj, layerparams, env_name): 
	adsr_att = get_dictval_fb(layerparams, 'attackParam', 0, float)
	adsr_dec = get_dictval_fb(layerparams, 'decayParam', 0, float)
	adsr_sus = get_dictval_fb(layerparams, 'sustainParam', 100, float)/100
	adsr_rel = get_dictval_fb(layerparams, 'releaseParam', 0, float)
	plugin_obj.env_asdr_add(env_name, 0, adsr_att, 0, adsr_dec, adsr_sus, adsr_rel, 1)

def sampler_soundlayer_filter(plugin_obj, soundlayer, filter_obj):
	layerparams = soundlayer.soundparameters
	filter_obj.on = bool(get_dictval_fb(layerparams, 'filterEnableParam', 0, float))
	filter_obj.freq = get_dictval_fb(layerparams, 'cuttoffParam', 20000, float)
	filter_obj.q = get_dictval_fb(layerparams, 'qParam', 0, float)+1
	filterModeParam = int(get_dictval_fb(layerparams, 'filterModeParam', 0, float))
	if filterModeParam in sampler_filter_types: filter_obj.type.set(sampler_filter_types[filterModeParam], None)
	if filterModeParam in sampler_filter_slopes: filter_obj.slope = sampler_filter_slopes[filterModeParam]

def do_auto(convproj_obj, autocurvespoints, autoloc):
	for time, val, curve in autocurvespoints:
		convproj_obj.automation.add_autopoint_real(autoloc, 'float', time, val, 'normal')

def decodevst3_chunk(memoryblock): 
	from functions.juce import juce_memoryblock
	from functions.juce import data_vc2xml
	from functions import data_xml
	chunkdata = juce_memoryblock.fromJuceBase64Encoding(memoryblock)
	pluginstate_x = data_vc2xml.get(chunkdata)
	IComponent = data_xml.find_first(pluginstate_x, 'IComponent')
	chunkdata = juce_memoryblock.fromJuceBase64Encoding(IComponent.text)
	return chunkdata

def do_plugin(convproj_obj, wf_plugin, track_obj, software_mode): 
	from functions.juce import juce_memoryblock
	from objects.file_proj._waveform import sampler

	pitch = None

	plugtype = str(wf_plugin.plugtype)

	if plugtype == 'vst':
		vstname = str(wf_plugin.params['name']) if "name" in wf_plugin.params else ''

		internal_vst = False

		if software_mode == 'waveform':
			if vstname in ['Multi Sampler', 'Micro Sampler']:
				internal_vst = True
				if "state" in wf_plugin.params:
					sampler_obj = sampler.waveform_sampler_main()
					sampler_obj.read( juce_memoryblock.fromJuceBase64Encoding(wf_plugin.params['state']) )
	
					program = sampler_obj.program.programdata
	
					if isinstance(program, sampler.prosampler) or isinstance(program, sampler.tinysampler):
						soundlayers = program.soundlayers
						if len(soundlayers) == 1:
							firstlayer = soundlayers[0]
							layerparams = firstlayer.soundparameters
							plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'single')
							track_obj.plugslots.set_synth(pluginid)
							sp_obj = plugin_obj.samplepart_add('sample')
							if sp_obj.visual.name: track_obj.visual_inst.name = sp_obj.visual.name
							sampler_soundlayer_samplepart(sp_obj, firstlayer, layerparams)
							sampler_soundlayer_adsr(plugin_obj, layerparams, 'vol')
							sampler_soundlayer_filter(plugin_obj, firstlayer, plugin_obj.filter)
	
							pitch = 0
							if 'pitchParam' in layerparams:
								if layerparams['pitchParam'] is not None: pitch = layerparams['pitchParam']
							transpose, tune = xtramath.transpose_tune(pitch)
							transpose -= firstlayer.rootNote-60
							track_obj.datavals.add('middlenote', -transpose)
							track_obj.params.add('pitch', tune, 'float')
	
						elif len(soundlayers) > 1:
							plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
							playMode = program.playMode
							if playMode == 0: plugin_obj.datavals.add('multi_mode', 'all')
							if playMode == 1: plugin_obj.datavals.add('multi_mode', 'round_robin')
							if playMode == 2: plugin_obj.datavals.add('multi_mode', 'random')
							plugin_obj.poly.mono = program.mono
							track_obj.plugslots.set_synth(pluginid)
							for layernum, soundlayer in enumerate(soundlayers):
								layerparams = soundlayer.soundparameters
								endstr = str(layernum)
								sp_obj = plugin_obj.sampleregion_add(soundlayer.lowNote-60, soundlayer.highNote-60, soundlayer.rootNote-60, None)
								sp_obj.envs['vol'] = 'vol_'+endstr
								sampler_soundlayer_samplepart(sp_obj, soundlayer, layerparams)
								sampler_soundlayer_adsr(plugin_obj, layerparams, 'vol_'+endstr)
								filter_obj = plugin_obj.named_filter_add(endstr)
								sampler_soundlayer_filter(plugin_obj, soundlayer, filter_obj)
								sp_obj.filter_assoc = endstr
								if 'pitchParam' in layerparams:
									if layerparams['pitchParam'] is not None:
										sp_obj.pitch = layerparams['pitchParam']
	
			elif vstname == 'Micro Drum Sampler':
				internal_vst = True
				from objects import colors
	
				plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'drums')
				track_obj.plugslots.set_synth(pluginid)
	
				if "state" in wf_plugin.params:
					colordata = colors.colorset.from_dataset('waveform', 'plugin', 'drum_sampler')
					sampler_obj = sampler.waveform_sampler_main()
					sampler_obj.read( juce_memoryblock.fromJuceBase64Encoding(wf_plugin.params['state']) )
					program = sampler_obj.program.programdata

					if isinstance(program, sampler.microsampler):
						soundlayers = program.soundlayers
						for layernum, soundlayer in enumerate(soundlayers):
							layerparams = soundlayer.soundparameters
							#endstr = str(layernum)

							#sp_obj = plugin_obj.sampleregion_add(soundlayer.lowNote-60, soundlayer.highNote-60, soundlayer.rootNote-60, None)
							if soundlayer.rootNote in program.pads:
								drumpad_obj, layer_obj = plugin_obj.drumpad_add_singlelayer()
								layer_obj.samplepartid = 'drum_%i' % soundlayer.rootNote
								sp_obj = plugin_obj.samplepart_add(layer_obj.samplepartid)
								sp_obj.pitch = layerparams['pitchParam'] if 'pitchParam' in layerparams else 0
								sampler_soundlayer_samplepart(sp_obj, soundlayer, layerparams)

								paddata = program.pads[soundlayer.rootNote]
								if paddata.name: drumpad_obj.visual.name = paddata.name

								colorint = colordata.getcolornum(paddata.colour)
								drumpad_obj.visual.color.set_int(colorint)
								sp_obj.visual.color.fx_allowed = ['saturate', 'brighter']

		elif software_mode == 'soundbug':
			if vstname == 'SoundSynth':
				try:
					chunkdata = decodevst3_chunk(str(wf_plugin.params['state']))
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst3', None)
					plugin_obj.role = 'synth'
					plugin_obj.fxdata_add(bool(wf_plugin.enabled), None)
					extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
					extmanu_obj.vst3__replace_data('name', 'Surge XT', chunkdata, None)
					track_obj.plugin_autoplace(plugin_obj, pluginid)
					internal_vst = True
				except:
					pass

		if not internal_vst:
			try:
				from objects.inst_params import juce_plugin
				juceobj = juce_plugin.juce_plugin()
				juceobj.uniqueId = wf_plugin.params['uniqueId'] if "uniqueId" in wf_plugin.params else ''
				juceobj.name = wf_plugin.params['name'] if "name" in wf_plugin.params else ''
				juceobj.filename = wf_plugin.params['filename'] if "filename" in wf_plugin.params else ''
				juceobj.manufacturer = wf_plugin.params['manufacturer'] if "manufacturer" in wf_plugin.params else ''
				if "programNum" in wf_plugin.params: juceobj.program_num = int(wf_plugin.params['programNum'])
				juceobj.memoryblock = wf_plugin.params['state']
				plugin_obj, pluginid = juceobj.to_cvpj(convproj_obj, None)
				plugin_obj.fxdata_add(bool(wf_plugin.enabled), None)
				track_obj.plugin_autoplace(plugin_obj, pluginid)
				if pluginid:
					if wf_plugin.windowX and wf_plugin.windowY:
						windata_obj = convproj_obj.viswindow__add(['plugin',pluginid])
						windata_obj.pos_x = wf_plugin.windowX
						windata_obj.pos_y = wf_plugin.windowY
					for autocurves in wf_plugin.automationcurves:
						if autocurves.paramid: 
							do_auto(convproj_obj, autocurves.points, ['plugin',pluginid,'ext_param_'+autocurves.paramid])

			except:
				#import traceback
				#print(traceback.format_exc())
				pass

	elif software_mode == 'waveform':
		if plugtype not in ['volume', 'level'] and plugtype != '':
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'tracktion', plugtype)
			plugin_obj.role = 'effect'
			plugin_obj.fxdata_add(wf_plugin.enabled, None)
	
			if wf_plugin.windowX and wf_plugin.windowY:
				windata_obj = convproj_obj.viswindow__add(['plugin',pluginid])
				windata_obj.pos_x = wf_plugin.windowX
				windata_obj.pos_y = wf_plugin.windowY
	
			for param_id, dset_param in globalstore.dataset.get_params('waveform', 'plugin', plugtype):
				paramval = wf_plugin.params[param_id] if param_id in wf_plugin.params else None
				plugin_obj.dset_param__add(param_id, paramval, dset_param)
	
			for autocurves in wf_plugin.automationcurves:
				if autocurves.paramid:
					do_auto(convproj_obj, autocurves.points, ['plugin',pluginid,autocurves.paramid])
	
			plugin_obj.fxdata_add(wf_plugin.enabled, 1)
			if plugtype not in ['4osc']: track_obj.plugslots.slots_audio.append(pluginid)
			else: track_obj.plugslots.set_synth(pluginid)

autonames = {
	'PITCHBEND': 'pitch',
	'TIMBRE': 'timbre',
	'PRESSURE': 'pressure',
}

def do_foldertrack(convproj_obj, wf_track, counter_track, software_mode): 
	groupid = str(wf_track.id_num)
	track_obj = convproj_obj.fx__group__add(groupid)
	track_obj.visual.name = str(wf_track.name)
	if wf_track.colour != '0': 
		track_obj.visual.color.set_hex(wf_track.colour)
		track_obj.visual.color.fx_allowed = ['saturate', 'brighter']
	#track_obj.visual_ui.height = wf_track.height/35.41053828354546

	vol = 1
	pan = 0

	for wf_plugin in wf_track.plugins:
		if wf_plugin.plugtype == 'volume':
			if 'volume' in wf_plugin.params: vol *= wf_plugin.params['volume']
			if 'pan' in wf_plugin.params: pan = wf_plugin.params['pan']
			for autocurves in wf_plugin.automationcurves:
				if autocurves.paramid == 'volume': do_auto(convproj_obj, autocurves.points, ['group',groupid,'vol'])
				if autocurves.paramid == 'pan': do_auto(convproj_obj, autocurves.points, ['group',groupid,'pan'])
		else:
			do_plugin(convproj_obj, wf_plugin, track_obj, software_mode)

	track_obj.params.add('vol', vol, 'float')
	track_obj.params.add('pan', pan, 'float')
	do_tracks(convproj_obj, wf_track.tracks, counter_track, groupid, software_mode)

def do_track(convproj_obj, wf_track, track_obj, software_mode): 
	track_obj.visual.name = str(wf_track.name)
	colour = str(wf_track.colour)
	try:
		if colour != '0': 
			if len(colour)==8:
				track_obj.visual.color.set_hex(colour[2:])
				track_obj.visual.color.fx_allowed = ['saturate', 'brighter']
			if len(colour)==6:
				track_obj.visual.color.set_hex(colour)
				track_obj.visual.color.fx_allowed = ['saturate', 'brighter']
	except:
		pass

	#track_obj.visual_ui.height = wf_track.height/35.41053828354546

	bpm = convproj_obj.params.get('bpm', 120).value

	vol = 1
	pan = 0

	middlenote = 0

	for wf_plugin in wf_track.plugins:
		if wf_plugin.plugtype == 'volume':
			if 'volume' in wf_plugin.params: vol *= wf_plugin.params['volume']
			if 'pan' in wf_plugin.params: pan = wf_plugin.params['pan']

		elif wf_plugin.plugtype == 'midiModifier':
			if 'semitonesUp' in wf_plugin.params: middlenote -= int(wf_plugin.params['semitonesUp'])

		else:
			do_plugin(convproj_obj, wf_plugin, track_obj, software_mode)

	track_obj.params.add('vol', vol, 'float')
	track_obj.params.add('pan', pan, 'float')
	track_obj.params.add('enabled', int(not wf_track.mute), 'bool')
	track_obj.params.add('solo', wf_track.solo, 'bool')

	for midiclip in wf_track.midiclips:
		placement_obj = track_obj.placements.add_notes()
		time_obj = placement_obj.time
		time_obj.set_posdur_real(midiclip.start, midiclip.length)
		if midiclip.loopStartBeats == 0 and midiclip.loopLengthBeats == 0:
			time_obj.set_offset(midiclip.offset*4)
		else:
			time_obj.set_loop_data(midiclip.offset*4, midiclip.loopStartBeats*4, (midiclip.loopStartBeats+midiclip.loopLengthBeats)*4)
	
		placement_obj.group = str(midiclip.groupID) if midiclip.groupID!=-1 else None

		cvpj_notelist = placement_obj.notelist
		for note in midiclip.sequence.notes:
			cvpj_notelist.add_r(note.pos*4, note.dur*4, note.key-60, note.vel/100, {})
			for a_type, a_data in note.auto.items():
				autoname = autonames[a_type] if a_type in autonames else None
				if autoname:
					for pos, val in a_data.items():
						cvpj_notelist.last_add_auto_instant(autoname, pos*4, val)

	for audioclip in wf_track.audioclips:

		if not audioclip.srcVideo:
			placement_obj = track_obj.placements.add_audio()
			time_obj = placement_obj.time
	
			placement_obj.sample.sampleref = audioclip.source
			sampleref_exists, sampleref_obj = convproj_obj.sampleref__get(audioclip.source)
	
			time_obj.set_posdur_real(audioclip.start, audioclip.length)
			placement_obj.fade_in.set_dur(audioclip.fadeIn, 'seconds')
			placement_obj.fade_out.set_dur(audioclip.fadeOut, 'seconds')
			placement_obj.group = str(audioclip.groupID) if audioclip.groupID!=-1 else None
	
			bpmdiv = (bpm/120)
			if audioclip.loopStartBeats == 0 and audioclip.loopLengthBeats == 0:
				time_obj.set_offset(audioclip.offset*8*bpmdiv)
			else:
				time_obj.set_loop_data(
					audioclip.offset*8*bpmdiv, 
					audioclip.loopStartBeats*4, 
					(audioclip.loopStartBeats+audioclip.loopLengthBeats)*4
					)
		
			sp_obj = placement_obj.sample
			sp_obj.vol = xtramath.from_db(audioclip.gain)
			sp_obj.pan = audioclip.pan
	
			stretch_obj = sp_obj.stretch
			stretch_obj.preserve_pitch = True
		
			for fx in audioclip.effects:
				params = fx.plugin.params
				if fx.fx_type == 'pitchShift':
					if 'semitonesUp' in params: sp_obj.pitch += float(params['semitonesUp'])
				if fx.fx_type == 'reverse':
					sp_obj.reverse = True
				if fx.fx_type == 'warpTime':
					if fx.warptime:
						bpmmul = (1/bpmdiv)
						warptime = fx.warptime
						stretch_obj.is_warped = True
						warp_obj = sp_obj.stretch.warp
						warp_obj.seconds = warptime.warpEndMarkerTime
						sampleref_obj.set_dur_sec(warptime.warpEndMarkerTime)

						secbeat = audioclip.loopinfo.numBeats/2
						stretchrate = warptime.warpEndMarkerTime/secbeat

						for warpmarker in warptime.warpmarkers:
							warp_point_obj = warp_obj.points__add()
							warp_point_obj.beat = (warpmarker.warpTime*2)/stretchrate
							warp_point_obj.second = warpmarker.sourceTime

						warp_obj.calcpoints__speed()

			if not stretch_obj.is_warped:
				stretch_obj.timing.set__beats(audioclip.loopinfo.numBeats)

		else:
			placement_obj = track_obj.placements.add_video()
			time_obj = placement_obj.time
			time_obj.set_posdur_real(audioclip.start, audioclip.length)
			placement_obj.videoref = audioclip.srcVideo
	
	middlenote += track_obj.datavals.get('middlenote', 0)
	track_obj.datavals.add('middlenote', middlenote)

def do_tracks(convproj_obj, in_tracks, counter_track, groupid, software_mode):
	from objects.file_proj import tracktion_edit as proj_tracktion_edit
	for wf_track in in_tracks:
		tracknum = counter_track.get()
		if isinstance(wf_track, proj_tracktion_edit.tracktion_track):
			track_obj = convproj_obj.track__add(str(tracknum), 'hybrid', 1, False)
			if groupid: track_obj.group = groupid
			do_track(convproj_obj, wf_track, track_obj, software_mode)
		if isinstance(wf_track, proj_tracktion_edit.tracktion_foldertrack):
			do_foldertrack(convproj_obj, wf_track, counter_track, software_mode)

class input_tracktion_edit(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'tracktion_edit'
	
	def get_name(self):
		return 'Waveform'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['native:tracktion','universal:sampler:single','universal:sampler:multi']
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import tracktion_edit as proj_tracktion_edit
		from objects.file_proj import tracktion_project as proj_tracktion_project
		global cvpj_l

		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_stretch = ['rate', 'warp']
		traits_obj.auto_types = ['nopl_points']
		traits_obj.placement_cut = True
		traits_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		traits_obj.plugin_ext = ['vst2', 'vst3']
		traits_obj.plugin_ext_arch = [64]
		traits_obj.plugin_ext_platforms = ['win', 'unix']
		traits_obj.time_seconds = True
		traits_obj.track_hybrid = True

		convproj_obj.set_timings(4.0)

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		samples = {}
		videos = {}
		project_obj = proj_tracktion_edit.tracktion_edit()

		software_mode = ''

		if dawvert_intent.input_mode == 'file':
			try:
				project_obj.load_from_file(dawvert_intent.input_file)

				logger_input.info('Software Mode: Waveform')
				software_mode = 'waveform'

				if project_obj.projectID:
					projectfile = project_obj.projectID.split('/')
					if projectfile:
						projectid = projectfile[0]
						projfolder = os.path.dirname(dawvert_intent.input_file)
						projfolder = os.path.abspath(projfolder)
						tprojpaths = onlyfiles = [f for f in os.listdir(projfolder) if (os.path.isfile(os.path.join(projfolder, f)) and f.endswith('.tracktion'))]
						for tprojpath in tprojpaths:
							try:
								tproj = proj_tracktion_project.tracktion_project()
								tproj.load_from_file(os.path.join(projfolder, tprojpath))
								samples |= dict([(tproj.projectId+'/'+i, o.path) for i, o in tproj.objects.items() if (o.type == 'wave')])
								videos |= dict([(tproj.projectId+'/'+i, o.path) for i, o in tproj.objects.items() if (o.type == 'video')])
							except:
								pass
			except:
				pass

			try:
				from objects.data_bytes import bytereader
				from objects.binary_fmt import juce_binaryxml
				import zlib

				byr_stream = bytereader.bytereader()
				byr_stream.load_file(dawvert_intent.input_file)
				byr_stream.magic_check(b'SNDR')
				compdata = byr_stream.raw(byr_stream.uint32())
				decompdata = zlib.decompress(compdata)
				decompdata = zlib.decompress(decompdata)
		
				main_obj = juce_binaryxml.juce_binaryxml_element()
				main_obj.read_bytes(decompdata)
				project_obj.load_from_elementdata(main_obj)
				logger_input.info('Software Mode: Soundbug')
				software_mode = 'soundbug'
			except:
				pass


		if not software_mode:
			logger_input.error('Not a Valid File.')
			exit()

		for sid, spath in samples.items(): 
			sampleref_obj = convproj_obj.sampleref__add(sid, spath, None)

		for sid, spath in videos.items(): 
			videoref_obj = convproj_obj.videoref__add(sid, spath, None)
			videoref_obj.search_local(dawvert_intent.input_folder)

		if project_obj.temposequence.tempo:
			pos, tempo = next(iter(project_obj.temposequence.tempo.items()))
			convproj_obj.params.add('bpm', tempo[0], 'float')
			for pos, tempo in project_obj.temposequence.tempo.items():
				convproj_obj.automation.add_autopoint_real(['main', 'bpm'], 'float', pos, tempo[0], 'normal')

		if project_obj.temposequence.timesig:
			pos, timesig = next(iter(project_obj.temposequence.timesig.items()))
			convproj_obj.timesig = timesig
			for pos, timesig in project_obj.temposequence.timesig.items():
				convproj_obj.timesig_auto.add_point(pos, timesig)

		for wf_plugin in project_obj.masterplugins:
			do_plugin(convproj_obj, wf_plugin, convproj_obj.track_master, software_mode)

		transport_obj = project_obj.transport

		convproj_obj.transport.loop_active = bool(transport_obj.looping)
		convproj_obj.transport.loop_start = max(0, transport_obj.loopPoint1)
		convproj_obj.transport.loop_end = max(0, transport_obj.loopPoint2)
		#convproj_obj.transport.start_pos = max(0, transport_obj.start)
		convproj_obj.transport.current_pos = transport_obj.position
		convproj_obj.transport.is_seconds = True
		convproj_obj.timemarkers.is_seconds = True
		
		tracknum = 0
		counter_track = counter.counter(1000, '')

		do_tracks(convproj_obj, project_obj.tracks, counter_track, None, software_mode)
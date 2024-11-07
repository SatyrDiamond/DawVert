# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import plugins
import zipfile
import os
import logging
logger_input = logging.getLogger('input')

def do_realparam(convproj_obj, paramset, dp_param, cvpj_paramid, i_addmul, i_type, i_loc):
	global autoid_assoc
	if dp_param.id and i_loc: autoid_assoc.define(str(dp_param.id), i_loc, i_type, i_addmul)
	outval = dp_param.value
	if i_type == 'bool': outval = int(outval=='true')
	outval = (float(outval)+i_addmul[0])*i_addmul[1] if i_addmul != None else float(outval)
	if i_type == 'bool': outval = bool(outval)
	if i_type == 'int': outval = int(outval)
	param_obj = paramset.add(cvpj_paramid, outval, i_type)
	if dp_param.name: param_obj.visual.name = dp_param.name

def do_param(convproj_obj, paramset, dp_param, cvpj_paramid, i_addmul, i_type, i_loc):
	global autoid_assoc
	if dp_param.used:
		if dp_param.unit == 'normalized': i_addmul = [-0.5, 2]
		if dp_param.id and i_loc: autoid_assoc.define(str(dp_param.id), i_loc, i_type, i_addmul)
		outval = dp_param.value
		if i_type == 'bool': outval = int(outval=='true')
		outval = (float(outval)+i_addmul[0])*i_addmul[1] if i_addmul != None else float(outval)
		if i_type == 'bool': outval = bool(outval)
		if i_type == 'int': outval = int(outval)
		paramset.add(cvpj_paramid, outval, i_type)

def do_visual(track_obj, dp_track):
	if dp_track.name: track_obj.visual.name = dp_track.name
	if dp_track.color: track_obj.visual.color.set_hex(dp_track.color)

def do_trackparams(convproj_obj, dp_channel, paramset, trackid):
	do_param(convproj_obj, paramset, dp_channel.mute, 'enabled', [-1, -1], 'bool', ['track', trackid, 'enabled'])
	do_param(convproj_obj, paramset, dp_channel.pan, 'pan', None, 'float', ['track', trackid, 'pan'])
	do_param(convproj_obj, paramset, dp_channel.volume, 'vol', None, 'float', ['track', trackid, 'vol'])

def do_groupparams(convproj_obj, dp_channel, paramset, trackid):
	do_param(convproj_obj, paramset, dp_channel.mute, 'enabled', [-1, -1], 'bool', ['group', trackid, 'enabled'])
	do_param(convproj_obj, paramset, dp_channel.pan, 'pan', None, 'float', ['group', trackid, 'pan'])
	do_param(convproj_obj, paramset, dp_channel.volume, 'vol', None, 'float', ['group', trackid, 'vol'])

def do_returnparams(convproj_obj, dp_channel, paramset, trackid):
	do_param(convproj_obj, paramset, dp_channel.mute, 'enabled', [-1, -1], 'bool', ['return', trackid, 'enabled'])
	do_param(convproj_obj, paramset, dp_channel.pan, 'pan', None, 'float', ['return', trackid, 'pan'])
	do_param(convproj_obj, paramset, dp_channel.volume, 'vol', None, 'float', ['return', trackid, 'vol'])

def do_masterparams(convproj_obj, dp_channel, paramset):
	do_param(convproj_obj, paramset, dp_channel.mute, 'enabled', [-1, -1], 'bool', ['master', 'enabled'])
	do_param(convproj_obj, paramset, dp_channel.pan, 'pan', None, 'float', ['master', 'pan'])
	do_param(convproj_obj, paramset, dp_channel.volume, 'vol', None, 'float', ['master', 'vol'])

def do_sends(convproj_obj, track_obj, dp_channel):
	for send in dp_channel.sends:
		send_obj = track_obj.sends.add(send.destination, send.id, 1)
		do_param(convproj_obj, send_obj.params, send.volume, 'amount', None, 'float', ['send', send.id, 'amount'])

def do_devices(convproj_obj, track_obj, ismaster, dp_devices):
	from functions_plugin_ext import plugin_vst2
	from functions_plugin_ext import plugin_vst3
	from functions_plugin_ext import plugin_clap

	for device in dp_devices:
		plugin_obj = None

		if device.plugintype == 'Vst3Plugin':
			plugin_obj = convproj_obj.plugin__add(device.id, 'external', 'vst3', None)
			do_param(convproj_obj, plugin_obj.params_slot, device.enabled, 'enabled', None, 'bool', ['slot', device.id, 'enabled'])
			vst3_state = zip_data.read(str(device.state))
			plugin_vst3.import_presetdata_raw(convproj_obj, plugin_obj, vst3_state, None)
			for realparam in device.realparameter:
				cvpj_paramid = 'ext_param_'+str(realparam.parameterID)
				do_realparam(convproj_obj, plugin_obj.params, realparam, cvpj_paramid, None, 'float', ['plugin', device.id, cvpj_paramid])

		if device.plugintype == 'Vst2Plugin':
			plugin_obj = convproj_obj.plugin__add(device.id, 'external', 'vst2', None)
			do_param(convproj_obj, plugin_obj.params_slot, device.enabled, 'enabled', None, 'bool', ['slot', device.id, 'enabled'])
			vst2_state = zip_data.read(str(device.state))
			plugin_vst2.import_presetdata_raw(convproj_obj, plugin_obj, vst2_state, None)
			for realparam in device.realparameter:
				cvpj_paramid = 'ext_param_'+str(realparam.parameterID)
				do_realparam(convproj_obj, plugin_obj.params, realparam, cvpj_paramid, None, 'float', ['plugin', device.id, cvpj_paramid])

		if device.plugintype == 'ClapPlugin':
			plugin_obj = convproj_obj.plugin__add(device.id, 'external', 'clap', None)
			do_param(convproj_obj, plugin_obj.params_slot, device.enabled, 'enabled', None, 'bool', ['slot', device.id, 'enabled'])
			clap_state = zip_data.read(str(device.state))
			plugin_clap.import_presetdata_raw(convproj_obj, plugin_obj, clap_state, None)
			if device.deviceName: plugin_obj.datavals_global.add('name', device.deviceName)
			for realparam in device.realparameter:
				cvpj_paramid = 'ext_param_'+str(realparam.parameterID)
				do_realparam(convproj_obj, plugin_obj.params, realparam, cvpj_paramid, None, 'float', ['plugin', device.id, cvpj_paramid])

		if plugin_obj:
			do_param(convproj_obj, plugin_obj.params_slot, device.enabled, 'enabled', None, 'bool', ['slot', device.id, 'enabled'])
			if device.deviceRole == 'instrument' and not ismaster:
				plugin_obj.role = 'inst'
				track_obj.inst_pluginid = device.id
			elif device.deviceRole == 'audioFX':
				plugin_obj.role = 'effect'
				track_obj.fxslots_audio.append(device.id)

def do_tracks(convproj_obj, dp_tracks, groupid):
	global samplefolder
	global trackdata
	for dp_track in dp_tracks:
		dp_channel = dp_track.channel

		track_obj = None

		if dp_track.contentType == 'notes' and dp_channel.role == 'regular': 
			track_obj = convproj_obj.track__add(dp_track.id, 'instrument', 1, False)
			do_visual(track_obj, dp_track)
			do_trackparams(convproj_obj, dp_channel, track_obj.params, dp_track.id)
			do_sends(convproj_obj, track_obj, dp_channel)
			do_devices(convproj_obj, track_obj, False, dp_channel.devices)
			if groupid: track_obj.group = groupid
			if dp_channel.solo: track_obj.params.add('solo', dp_channel.solo=='true', 'bool')

		if dp_track.contentType == 'audio' and dp_channel.role == 'regular': 
			track_obj = convproj_obj.track__add(dp_track.id, 'audio', 1, False)
			do_visual(track_obj, dp_track)
			do_trackparams(convproj_obj, dp_channel, track_obj.params, dp_track.id)
			do_sends(convproj_obj, track_obj, dp_channel)
			do_devices(convproj_obj, track_obj, False, dp_channel.devices)
			if groupid: track_obj.group = groupid
			if dp_channel.solo: track_obj.params.add('solo', dp_channel.solo=='true', 'bool')

		if dp_track.contentType == 'audio notes' and dp_channel.role == 'regular': 
			track_obj = convproj_obj.track__add(dp_track.id, 'hybrid', 1, False)
			do_visual(track_obj, dp_track)
			do_trackparams(convproj_obj, dp_channel, track_obj.params, dp_track.id)
			do_sends(convproj_obj, track_obj, dp_channel)
			do_devices(convproj_obj, track_obj, False, dp_channel.devices)
			if groupid: track_obj.group = groupid
			if dp_channel.solo: track_obj.params.add('solo', dp_channel.solo=='true', 'bool')

		if dp_track.contentType == 'tracks' and dp_channel.role == 'master': 
			track_obj = convproj_obj.fx__group__add(dp_track.id)
			do_visual(track_obj, dp_track)
			do_groupparams(convproj_obj, dp_channel, track_obj.params, dp_track.id)
			do_tracks(convproj_obj, dp_track.tracks, dp_track.id)
			do_sends(convproj_obj, track_obj, dp_channel)
			do_devices(convproj_obj, track_obj, True, dp_channel.devices)
			if groupid: track_obj.group = groupid
			if dp_channel.solo: track_obj.params.add('solo', dp_channel.solo=='true', 'bool')

		if dp_track.contentType == 'audio' and dp_channel.role == 'effect': 
			return_obj = convproj_obj.track_master.fx__return__add(dp_track.id)
			do_visual(return_obj, dp_track)
			do_returnparams(convproj_obj, dp_channel, return_obj.params, dp_track.id)
			do_sends(convproj_obj, return_obj, dp_channel)
			do_devices(convproj_obj, track_obj, True, dp_channel.devices)
			if dp_channel.solo: return_obj.params.add('solo', dp_channel.solo=='true', 'bool')

		if dp_track.contentType == 'audio notes' and dp_channel.role == 'master': 
			master_track_obj = convproj_obj.track_master
			do_visual(master_track_obj, dp_track)
			do_masterparams(convproj_obj, dp_channel, master_track_obj.params)
			do_devices(convproj_obj, track_obj, True, dp_channel.devices)

		if dp_track.id: trackdata[dp_track.id] = track_obj

def docliptime(pl_time, clip):
	pl_time.set_posdur(clip.time, clip.duration)
	offset = clip.playStart if clip.playStart else 0
	if clip.loopStart != None and clip.loopEnd != None: 
		pl_time.set_loop_data(offset, clip.loopStart if clip.loopStart else 0, clip.loopEnd if clip.loopEnd else clip.duration)
	elif offset:
		pl_time.set_offset(offset)

def do_mpe(notelist, mpepoints):
	target_obj = mpepoints.target
	mpetype = target_obj.expression
	if mpetype:
		if mpetype == 'transpose': mpetype = 'pitch'
		for point in mpepoints.points:
			autopoint_obj = notelist.last_add_auto(mpetype)
			autopoint_obj.pos = point.time
			autopoint_obj.value = point.value

def do_notes(track_obj, clip, notes):
	placement_obj = track_obj.placements.add_notes()
	docliptime(placement_obj.time, clip)
	if clip.name: placement_obj.visual.name = clip.name
	if clip.color: placement_obj.visual.color.set_hex(clip.color.upper())
	for note in notes.notes:
		note_vel = note.vel if note.vel != None else 1
		note_extra = {}
		if note.rel != None: note_extra['release'] = note.rel
		if note.channel != None: note_extra['channel'] = note.channel
		placement_obj.notelist.add_r(note.time, note.duration, note.key-60, note_vel, note_extra)
		if note.points: 
			do_mpe(placement_obj.notelist, note.points)
		if note.lanes:
			for points in note.lanes.points: 
				do_mpe(placement_obj.notelist, points)

def do_audio(convproj_obj, npa_obj, audio_obj):
	global samplefolder
	global zip_data

	channels = audio_obj.channels
	duration = audio_obj.duration
	samplerate = audio_obj.sampleRate
	filepath = str(audio_obj.file)
	extfilepath = os.path.join(samplefolder, filepath)
	try: zip_data.extract(filepath, path=samplefolder, pwd=None)
	except: pass
	sampleref_obj = convproj_obj.sampleref__add(filepath, extfilepath, None)
	if not sampleref_obj.dur_samples and not sampleref_obj.dur_sec:
		if samplerate:
			sampleref_obj.hz = samplerate
			sampleref_obj.timebase = samplerate
			if duration:
				sampleref_obj.dur_samples = duration*samplerate
				sampleref_obj.dur_sec = duration
	if not sampleref_obj.channels and channels: sampleref_obj.channels = channels
	npa_obj.sample.sampleref = filepath
	return sampleref_obj

def do_audioclip(convproj_obj, npa_obj, inclip):
	if inclip.fadeTimeUnit == 'beats':
		if inclip.fadeInTime: npa_obj.fade_in.set_dur(inclip.FadeInLength, 'beats')
		if inclip.fadeOutTime: npa_obj.fade_out.set_dur(inclip.FadeInLength, 'beats')

	if inclip.audio: 
		sampleref_obj = do_audio(convproj_obj, npa_obj, inclip.audio)
	if inclip.warps:
		if inclip.warps.audio:
			stretch_algo = inclip.warps.audio.algorithm

			sampleref_obj = do_audio(convproj_obj, npa_obj, inclip.warps.audio)
			sample_obj = npa_obj.sample
			stretch_obj = sample_obj.stretch

			if stretch_algo == 'stretch_subbands': stretch_obj.algorithm = 'stretch_subbands'
			if stretch_algo == 'slice': stretch_obj.algorithm = 'slice'
			if stretch_algo == 'elastique_solo': stretch_obj.algorithm = 'elastique_solo'
			if stretch_algo == 'elastique': stretch_obj.algorithm = 'elastique'
			if stretch_algo == 'elastique_eco': stretch_obj.algorithm = 'elastique_eco'
			if stretch_algo == 'elastique_pro': stretch_obj.algorithm = 'elastique_pro'

			stretch_obj.preserve_pitch = stretch_algo != 'repitch'
			stretch_obj.is_warped = True
			for x in inclip.warps.points:
				warp_point_obj = stretch_obj.add_warp_point()
				warp_point_obj.beat = x.time
				warp_point_obj.second = x.contentTime
			stretch_obj.calc_warp_points()

def do_audioauto(npa_obj, mpepoints):
	target_obj = mpepoints.target
	mpetype = target_obj.expression
	if mpetype:
		if mpetype == 'transpose': mpetype = 'pitch'

		if len(mpepoints.points)==1:
			outval = mpepoints.points[0].value
			if mpetype == 'pan': 
				npa_obj.sample.pan = outval
			if mpetype == 'pitch': 
				npa_obj.sample.pitch = outval
			if mpetype == 'gain': 
				npa_obj.sample.vol = outval
			if mpetype == 'formant': 
				npa_obj.sample.stretch.params['formant'] = outval

		elif len(mpepoints.points)>1:
			autopoints_obj = npa_obj.add_autopoints(mpetype, 1, True)
			for point in mpepoints.points:
				autopoint_obj = autopoints_obj.add_point()
				autopoint_obj.pos = point.time
				autopoint_obj.value = point.value

def do_clips(convproj_obj, track_obj, clip, clips):
	placement_obj = track_obj.placements.add_nested_audio()
	if clip.name: placement_obj.visual.name = clip.name
	if clip.color: placement_obj.visual.color.set_hex(clip.color.upper())
	docliptime(placement_obj.time, clip)

	if clip.fadeTimeUnit == 'beats':
		if clip.fadeInTime: placement_obj.fade_in.set_dur(clip.fadeInTime, 'beats')
		if clip.fadeOutTime: placement_obj.fade_out.set_dur(clip.fadeOutTime, 'beats')

	for inclip in clips.clips:
		npa_obj = placement_obj.add()
		if clip.name: npa_obj.visual.name = clip.name
		if clip.color: npa_obj.visual.color.set_hex(clip.color.upper())
		docliptime(npa_obj.time, inclip)
		do_audioclip(convproj_obj, npa_obj, inclip)
		if inclip.lanes:
			do_audioclip(convproj_obj, npa_obj, inclip.lanes)
			for points in inclip.lanes.points:
				do_audioauto(npa_obj, points)

class input_dawproject(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'dawproject'
	def get_name(self): return 'DawProject'
	def get_priority(self): return 0
	def supported_autodetect(self): return True
	def detect(self, input_file): 
		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
			if 'project.xml' in zip_data.namelist(): return True
			else: return False
		except:
			return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['dawproject']
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'ogg', 'flac']
		in_dict['placement_cut'] = True
		in_dict['auto_types'] = ['nopl_points']
		in_dict['audio_stretch'] = ['warp']
		in_dict['audio_nested'] = True
		in_dict['plugin_ext'] = ['vst2', 'vst3', 'clap']
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_dawproject
		from objects import auto_id

		convproj_obj.type = 'r'
		convproj_obj.set_timings(1, True)

		global autoid_assoc
		global samplefolder
		global trackdata
		global zip_data

		trackdata = {}

		autoid_assoc = auto_id.convproj2autoid(48, False)

		samplefolder = dv_config.path_samples_extracted

		project_obj = proj_dawproject.dawproject_song()
		try:
			zip_data = zipfile.ZipFile(input_file, 'r')
		except zipfile.BadZipFile as t:
			raise ProjectFileParserException('dawproject: Bad ZIP File: '+str(t))

		try: 
			meta_xmldata = zip_data.read('metadata.xml')
			project_obj.load_metadata(meta_xmldata)
		except: 
			pass

		try: xmldata = zip_data.read('project.xml')
		except KeyError as t: raise ProjectFileParserException('dawproject: project.xml not found')

		project_obj.load_from_data(xmldata.decode())

		dp_timesig = project_obj.transport.TimeSignature
		convproj_obj.timesig[0] = int(dp_timesig.numerator)
		convproj_obj.timesig[1] = int(dp_timesig.denominator)

		do_param(convproj_obj, convproj_obj.params, project_obj.transport.Tempo, 'bpm', None, 'float', ['main', 'bpm'])
		do_tracks(convproj_obj, project_obj.tracks, None)

		for lane in project_obj.arrangement.lanes.lanes:
			if lane.track in trackdata:
				track_obj = trackdata[lane.track]
				if track_obj:
					for clip in lane.clips.clips:
						if clip.notes: do_notes(track_obj, clip, clip.notes)
						if clip.clips: do_clips(convproj_obj, track_obj, clip, clip.clips)
				for points in lane.points:
					target_obj = points.target
					if target_obj.parameter:
						autoloc = ['id',target_obj.parameter]
						for point in points.points: 
							convproj_obj.automation.add_autopoint(autoloc, 'float', point.time, point.value, 'normal')
						for point in points.points_bool: 
							convproj_obj.automation.add_autopoint(autoloc, 'bool', point.time, point.value, 'instant')

		timesigauto = project_obj.arrangement.timesignatureautomation
		if timesigauto:
			for point in timesigauto.points:
				convproj_obj.timesig_auto.add_point(point.time, [point.numerator, point.denominator])

		tempoauto = project_obj.arrangement.tempoautomation
		if tempoauto:
			target_obj = tempoauto.target
			if target_obj.parameter:
				autoloc = ['id',target_obj.parameter]
				for point in tempoauto.points: 
					convproj_obj.automation.add_autopoint(autoloc, 'float', point.time, point.value, 'normal')

		if project_obj.arrangement.markers:
			markers = project_obj.arrangement.markers.markers
			for marker in markers:
				timemarker_obj = convproj_obj.timemarker__add()
				if marker.name: timemarker_obj.visual.name = marker.name
				if marker.color: timemarker_obj.visual.color.set_hex(marker.color)
				timemarker_obj.position = marker.time

		autoid_assoc.output(convproj_obj)

		dp_obj = project_obj.metadata
		meta_obj = convproj_obj.metadata

		if 'Title' in dp_obj: meta_obj.name = dp_obj['Title']
		if 'Artist' in dp_obj: meta_obj.author = dp_obj['Artist']
		if 'Album' in dp_obj: meta_obj.album = dp_obj['Album']
		if 'OriginalArtist' in dp_obj: meta_obj.original_author = dp_obj['OriginalArtist']
		if 'Songwriter' in dp_obj: meta_obj.songwriter = dp_obj['Songwriter']
		if 'Producer' in dp_obj: meta_obj.producer = dp_obj['Producer']
		if 'Year' in dp_obj: meta_obj.t_year = int(dp_obj['Year'])
		if 'Genre' in dp_obj: meta_obj.genre = dp_obj['Genre']
		if 'Copyright' in dp_obj: meta_obj.copyright = dp_obj['Copyright']
		if 'Comment' in dp_obj: meta_obj.comment_text = dp_obj['Comment']
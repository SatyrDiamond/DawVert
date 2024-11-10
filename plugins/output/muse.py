# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import lxml.etree as ET
import mido
import zlib
import base64
import math

import logging
logger_output = logging.getLogger('output')

def addvalue(xmltag, name, value):
	x_temp = ET.SubElement(xmltag, name)
	x_temp.text = str(value)

def addroute_audioout(project_obj, in_channel, in_track, in_type, in_name):
	route_obj = project_obj.add_route()
	route_obj.channel = in_channel
	route_obj.input_track = in_track
	route_obj.output_name = in_name
	route_obj.output_type = in_type

def addroute_audio(project_obj, in_source, in_dest):
	route_obj = project_obj.add_route()
	route_obj.input_track = in_source
	route_obj.output_track = in_dest

def maketrack_synth(project_obj, convproj_obj, track_obj, portnum):
	global tracknum
	global synthidnum
	logger_output.info('MusE: Synth Track '+str(tracknum)+(': '+track_obj.visual.name if track_obj.visual.name else ''))
	addroute_audio(project_obj, tracknum, 0)

	muse_track = project_obj.add_track('SynthI')
	controller_obj = muse_track.add_controller(0)
	controller_obj.cur = track_obj.params.get('vol', 1).value
	controller_obj.color = '#ff0000'

	track_mute = not track_obj.params.get('enabled', True).value
	if track_obj.visual.name: muse_track.name = track_obj.visual.name
	if track_obj.visual.color: muse_track.color = '#'+track_obj.visual.color.get_hex()
	muse_track.channels = 2
	muse_track.synth_port = portnum

	pluginsupported = False

	plugin_found, plugin_obj = convproj_obj.plugin__get(track_obj.inst_pluginid)
	if plugin_found: 
		if plugin_obj.check_match('external', 'vst2', 'win'):
			pluginsupported = True
			muse_track.synth_synthType = 'VST (synths)'

			vstname = plugin_obj.datavals_global.get('name', '')
			vstclass = plugin_obj.datavals_global.get('name', '')
			if vstclass == 'Vitalium': vstclass = 'vitalium'
			muse_track.synth_class = vstclass
			muse_track.synth_label = vstname

			vstdata_bytes = plugin_obj.rawdata_get('chunk')
			muse_track.synth_customData = b''
			muse_track.synth_customData += len(vstdata_bytes).to_bytes(4, 'big')
			muse_track.synth_customData += zlib.compress(vstdata_bytes)

	if pluginsupported == False:
		muse_track.synth_synthType = 'MESS'
		muse_track.synth_class = 'vam'
		track_mute = 1

	muse_track.mute = track_mute

	tracknum += 1
	synthidnum += 1

def maketrack_midi(project_obj, placements_obj, trackname, portnum, track_obj):
	from objects.file_proj import proj_muse
	global tracknum
	global synthidnum
	logger_output.info('MusE:  Midi Track '+str(tracknum)+(': '+trackname if trackname else ''))

	muse_track = project_obj.add_track('miditrack')
	muse_track.name = trackname
	if track_obj.visual.color: muse_track.color = '#'+track_obj.visual.color.get_hex()
	muse_track.height = 70
	muse_track.device = portnum
	muse_track.transposition = -track_obj.datavals.get('middlenote', 0)

	for notespl_obj in placements_obj.pl_notes:
		muse_part = proj_muse.muse_midi_part()
		if notespl_obj.visual.name: muse_part.name = notespl_obj.visual.name
		muse_part.poslen.len = int(notespl_obj.time.duration)
		muse_part.poslen.tick = int(notespl_obj.time.position)

		notespl_obj.notelist.sort()
		for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
			for t_key in t_keys:
				muse_event = proj_muse.muse_midi_event()
				muse_event.tick = int(t_pos+muse_part.poslen.tick)
				muse_event.len = int(t_dur)
				muse_event.a = int(t_key+60)
				muse_event.b = int(t_vol*100)
				muse_part.events.append(muse_event)

		muse_track.note_parts.append(muse_part)

	tracknum += 1

WAVE_FREQUENCY = 48000

wavetime = WAVE_FREQUENCY/768

def maketrack_wave(project_obj, placements_obj, convproj_obj, track_obj, muse_bpm):
	from objects.file_proj import proj_muse
	global tracknum
	global synthidnum
	logger_output.info('MusE:  Wave Track '+str(tracknum)+(': '+track_obj.visual.name if track_obj.visual.name else ''))
	addroute_audio(project_obj, tracknum, 0)

	muse_track = project_obj.add_track('wavetrack')
	muse_track.name = track_obj.visual.name
	muse_track.channels = 2
	if track_obj.visual.color: muse_track.color = '#'+track_obj.visual.color.get_hex()
	muse_track.height = 70

	bpmcalc = (120/muse_bpm)

	for audiopl_obj in placements_obj.pl_audio:
		muse_part = proj_muse.muse_audio_part()

		if audiopl_obj.visual.name: muse_part.name = audiopl_obj.visual.name

		muse_part.poslen.len = (int(audiopl_obj.time.duration)*wavetime)*bpmcalc
		muse_part.poslen.sample = (int(audiopl_obj.time.position)*wavetime)*bpmcalc

		offset = audiopl_obj.time.cut_start
		frameval = int((offset*(wavetime))*(120/muse_bpm))

		ref_found, sampleref_obj = convproj_obj.sampleref__get(audiopl_obj.sample.sampleref)
		if ref_found: 
			frameval *= sampleref_obj.hz/WAVE_FREQUENCY

			event_obj = muse_part.new_event()
			event_obj.file = sampleref_obj.fileref.get_path('unix', False)
			event_obj.frame = int(frameval)
			event_obj.poslen.len = (int(audiopl_obj.time.duration)*wavetime)*bpmcalc
			event_obj.poslen.sample = (int(audiopl_obj.time.position)*wavetime)*bpmcalc

			sample_obj = audiopl_obj.sample

			if not sample_obj.stretch.is_warped:
				stretch_speed = 1
				stretch_pitch = 1
				muse_pitch = pow(2, sample_obj.pitch/12)
				if sample_obj.stretch.preserve_pitch:
					stretch_speed = sample_obj.stretch.calc_real_size*muse_pitch
					stretch_pitch = muse_pitch
				else: stretch_pitch = sample_obj.stretch.calc_real_speed
				stretchlist = [1, stretch_speed, stretch_pitch, 1, 7]
				event_obj.stretchlist.append(stretchlist)

		muse_track.audio_parts.append(muse_part)
	tracknum += 1

def add_timesig(x_siglist, pos, numerator, denominator):
	x_sig = ET.SubElement(x_siglist, "sig")
	x_sig.set('at', str(int(pos*NoteStep)))
	addvalue(x_sig, 'tick', 0)
	addvalue(x_sig, 'nom', str(int(numerator)))
	addvalue(x_sig, 'denom', str(int(denominator)))

class output_cvpj(plugins.base):
	def __init__(self): pass
	def get_name(self): return 'MusE'
	def is_dawvert_plugin(self): return 'output'
	def get_shortname(self): return 'muse'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'med'
		in_dict['plugin_arch'] = [64]
		in_dict['track_lanes'] = True
		in_dict['placement_cut'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['projtype'] = 'r'
	def getsupportedplugformats(self): return ['vst2']
	def getsupportedplugins(self): return []
	def getfileextension(self): return 'med'
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_muse
		global tracknum
		global synthidnum
		tracknum = 1
		synthidnum = 4

		midiDivision = 384
		convproj_obj.change_timings(midiDivision, False)
		muse_bpm = convproj_obj.params.get('bpm', 120).value

		project_obj = proj_muse.muse_song()
		project_obj.midiDivision = midiDivision

		addroute_audioout(project_obj, 0, 0, 1, "system:playback_1")
		addroute_audioout(project_obj, 1, 0, 1, "system:playback_2")

		muse_track = proj_muse.muse_track('AudioOutput')
		muse_track.channels = 2

		project_obj.tracks.append(muse_track)

		for trackid, track_obj in convproj_obj.track__iter():

			if track_obj.type == 'instrument':
				if track_obj.is_laned:
					for laneid, lane_obj in track_obj.lanes.items():
						lanename = lane_obj.visual.name if lane_obj.visual.name else laneid
						maketrack_midi(project_obj, lane_obj.placements, lanename, synthidnum, track_obj)
				else:
					maketrack_midi(project_obj, track_obj.placements, track_obj.visual.name, synthidnum, track_obj)

				maketrack_synth(project_obj, convproj_obj, track_obj, synthidnum)

			if track_obj.type == 'audio':
				maketrack_wave(project_obj, track_obj.placements, convproj_obj, track_obj, muse_bpm)

		tempo_point = proj_muse.muse_tempo()
		tempo_point.at = 21474837
		tempo_point.tick = 0
		tempo_point.val = mido.bpm2tempo(muse_bpm)
		project_obj.tempolist.events.append(tempo_point)
		project_obj.tempolist.fix = mido.bpm2tempo(muse_bpm)

		muse_numerator, muse_denominator = convproj_obj.timesig

		timesig_point = proj_muse.muse_sig()
		timesig_point.at = 21474837
		timesig_point.tick = 0
		timesig_point.nom = muse_numerator
		timesig_point.denom = muse_denominator
		project_obj.siglist.append(timesig_point)

		#for pos, value in convproj_obj.timesig_auto.iter():
		#	timesig_point = proj_muse.muse_sig()
		#	timesig_point.at = int(pos*NoteStep)
		#	timesig_point.nom = value[0]
		#	timesig_point.denom = value[1]
		#	project_obj.siglist.append(timesig_point)

		project_obj.save_to_file(output_file)
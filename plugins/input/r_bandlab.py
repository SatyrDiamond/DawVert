# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
from objects.convproj import fileref
import xml.etree.ElementTree as ET
import plugins
import json
import os
import glob

class input_cvpj_f(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'bandlab_blx'
	
	def get_name(self):
		return 'BandLab BLX'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['audio_filetypes'] = ['wav', 'mp3', 'flac']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'groupreturn'
		in_dict['time_seconds'] = True
		in_dict['file_ext'] = ['blx']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_eq', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['plugin_included'] = ['native:bandlab']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import proj_bandlab

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.set_timings(4, False)

		project_obj = proj_bandlab.bandlab_project()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		bpm = 120
		if 'bpm' in project_obj.metronome:
			bpm = project_obj.metronome['bpm']

		convproj_obj.params.add('bpm', bpm, 'float')

		convproj_obj.track_master.params.add('vol', project_obj.volume, 'float')

		tempomul = 120/bpm

		sampledurs = {}

		for blx_auxChannel in project_obj.auxChannels:
			track_obj = convproj_obj.track_master.fx__return__add(blx_auxChannel.id)
			track_obj.params.add('vol', blx_auxChannel.returnLevel, 'float')

		for blx_sample in project_obj.samples:

			filename = os.path.dirname(dawvert_intent.input_file)
			filename = os.path.join(filename, 'Assets', 'Audio', blx_sample.id+'.*')

			for file in glob.glob(filename):
				sampleref_obj = convproj_obj.sampleref__add(blx_sample.id, file, 'win')
				sampleref_obj.convert(['wav'], dawvert_intent.path_samples['extracted'])
				sampledurs[blx_sample.id] = sampleref_obj.dur_sec
				break

		for blx_track in project_obj.tracks:

			if blx_track.type == 'voice':
				track_obj = convproj_obj.track__add(blx_track.id, 'audio', 1, False)
				do_track_common(convproj_obj, track_obj, blx_track)
				for blx_region in blx_track.regions:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.time.position_real = blx_region.startPosition
					placement_obj.time.duration_real = blx_region.endPosition-blx_region.startPosition
					if blx_region.name: placement_obj.visual.name = blx_region.name

					reverse = blx_region.playbackRate<0
					speed = abs(blx_region.playbackRate)

					do_loop(placement_obj.time, blx_region, tempomul, speed)

					sp_obj = placement_obj.sample
					sp_obj.pitch = blx_region.pitchShift
					sp_obj.sampleref = blx_region.sampleId
					sp_obj.vol = blx_region.gain
					sp_obj.stretch.set_rate_speed(bpm, (1/speed), True)
					sp_obj.stretch.preserve_pitch = True

					placement_obj.fade_in.set_dur(blx_region.fadeIn, 'seconds')
					placement_obj.fade_out.set_dur(blx_region.fadeOut, 'seconds')

			if blx_track.type in ['piano', 'creators-kit']:
				track_obj = convproj_obj.track__add(blx_track.id, 'instrument', 1, False)
				do_track_common(convproj_obj, track_obj, blx_track)
				for blx_region in blx_track.regions:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.time.position_real = blx_region.startPosition
					placement_obj.time.duration_real = blx_region.endPosition-blx_region.startPosition
					if blx_region.name: placement_obj.visual.name = blx_region.name

					filename = os.path.dirname(dawvert_intent.input_file)
					midipath = os.path.join(filename, 'Assets', 'MIDI', blx_region.sampleId+'.mid')
			
					do_loop(placement_obj.time, blx_region, tempomul, 1)

					placement_obj.notelist.midi_from(midipath)

def do_loop(time_obj, blx_region, tempomul, speed):
	loopLength = (blx_region.loopLength/tempomul)*8
	sampleOffset = (blx_region.sampleOffset/tempomul)*8
	duration = ((blx_region.startPosition-blx_region.endPosition)/tempomul)*8

	if loopLength == 0:
		time_obj.set_offset(sampleOffset)
	else:
		time_obj.set_loop_data(sampleOffset, sampleOffset, loopLength)

def do_automation(convproj_obj, blx_auto, autoloc):
	for p in blx_auto.points:
		convproj_obj.automation.add_autopoint_real(autoloc, 'float', p.position, p.value, 'normal')

def do_track_common(convproj_obj, track_obj, blx_track):
	track_obj.visual.name = blx_track.name
	track_obj.visual.color.set_hex(blx_track.color)
	track_obj.params.add('enabled', not blx_track.isMuted, 'bool')
	track_obj.params.add('solo', blx_track.isSolo, 'bool')
	track_obj.params.add('vol', blx_track.volume, 'float')
	track_obj.params.add('pan', blx_track.pan, 'float')

	for blx_auxSend in blx_track.auxSends:
		sendautoid = blx_track.id+'__'+'return__'+str(blx_auxSend.id)
		track_obj.sends.add(blx_auxSend.id, sendautoid, blx_auxSend.sendLevel)
		do_automation(convproj_obj, blx_auxSend.automation, ['send', sendautoid, 'amount'])

	if blx_track.automation:
		do_automation(convproj_obj, blx_track.automation.pan, ['track', blx_track.id, 'pan'])
		do_automation(convproj_obj, blx_track.automation.volume, ['track', blx_track.id, 'vol'])
		
	for n, blx_effect in enumerate(blx_track.effects):
		fxid = blx_track.id+'_'+str(n)

		plugin_obj = convproj_obj.plugin__add(fxid, 'native', 'bandlab', blx_effect.slug)
		plugin_obj.role = 'fx'
		plugin_obj.fxdata_add(not blx_effect.bypass, 1)

		for n, v in blx_effect.params.items():
			if not isinstance(v, str):
				plugin_obj.params.add(n, v, 'float')
				if n in blx_effect.automation:
					do_automation(convproj_obj, blx_effect.automation[n], ['plugin', fxid, n])
			else:
				plugin_obj.datavals.add(n, v)

		track_obj.plugin_autoplace(plugin_obj, fxid)

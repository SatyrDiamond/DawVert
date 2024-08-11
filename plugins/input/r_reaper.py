# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
import plugins
import json
import os
import struct
import rpp
import base64
from io import BytesIO
from objects.file_proj import proj_reaper

def reaper_color_to_cvpj_color(i_color, isreversed): 
	bytecolors = struct.pack('i', i_color)
	if bytecolors[3]:
		if isreversed == True: return colors.rgb_int_to_rgb_float([bytecolors[0],bytecolors[1],bytecolors[2]])
		else: return colors.rgb_int_to_rgb_float([bytecolors[2],bytecolors[1],bytecolors[0]])
	else:
		return [0.51, 0.54, 0.54]

class midi_notes():
	def __init__(self): 
		self.active_notes = [[[] for x in range(127)] for x in range(16)]
		self.midipos = 0
		pass

	def do_note(self, tracksource_var):
		self.midipos += int(tracksource_var[1])
		midicmd, midich = data_bytes.splitbyte(int(tracksource_var[2],16))
		midikey = int(tracksource_var[3],16)
		midivel = int(tracksource_var[4],16)
		if midicmd == 9: self.active_notes[midich][midikey].append([self.midipos, None, midivel])
		if midicmd == 8: self.active_notes[midich][midikey][-1][1] = self.midipos

	def do_output(self, cvpj_notelist, ppq):
		for c_mid_ch in range(16):
			for c_mid_key in range(127):
				if self.active_notes[c_mid_ch][c_mid_key] != []:
					for notedurpos in self.active_notes[c_mid_ch][c_mid_key]:
						if notedurpos[1] != None:
							cvpj_notelist.add_r(
								notedurpos[0]/(ppq), 
								(notedurpos[1]-notedurpos[0])/(ppq), 
								c_mid_key-60, 
								notedurpos[2]/127, 
								{'channel': c_mid_ch}
								)
							cvpj_notelist.time_ppq = 1
							cvpj_notelist.time_float = True

class input_reaper(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'reaper'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'REAPER'
		dawinfo_obj.file_ext = 'rpp'
		dawinfo_obj.fxtype = 'track'
		dawinfo_obj.placement_cut = True
		dawinfo_obj.placement_loop = []
		dawinfo_obj.time_seconds = True
		dawinfo_obj.track_hybrid = True
		dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		dawinfo_obj.audio_stretch = ['rate']
		
	def parse(self, convproj_obj, input_file, dv_config):
		bytestream = open(input_file, 'r')
		rpp_data = rpp.load(bytestream)

		project_obj = proj_reaper.rpp_song()
		project_obj.load_from_file(input_file)

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		rpp_project = project_obj.project

		bpm = rpp_project.tempo['tempo']
		convproj_obj.params.add('bpm', bpm, 'float')
		tempomul = bpm/120
		convproj_obj.timesig = [int(rpp_project.tempo['num']), int(rpp_project.tempo['denom'])]

		trackdata = []

		for tracknum, rpp_track in enumerate(rpp_project.tracks):
			cvpj_trackid = rpp_track.trackid.get()

			if not cvpj_trackid: cvpj_trackid = 'track'+str(tracknum)

			trackroute = [rpp_track.mainsend['tracknum'], rpp_track.auxrecv]

			track_obj = convproj_obj.add_track(cvpj_trackid, 'hybrid', 1, False)
			track_obj.visual.name = rpp_track.name.get()
			track_obj.visual.color.set_float(reaper_color_to_cvpj_color(rpp_track.peakcol.get(), True))
			track_obj.params.add('vol', rpp_track.volpan['vol'], 'float')
			track_obj.params.add('pan', rpp_track.volpan['pan'], 'float')

			if rpp_track.fxchain != None:
				rpp_plugins = rpp_track.fxchain.plugins
				for rpp_plugin in rpp_plugins:
					rpp_extplug = rpp_plugin.plugin
					fxid = rpp_plugin.fxid.get()
					if rpp_plugin.type == 'VST':
						if rpp_extplug.vst3_uuid == None:
							fourid = rpp_extplug.vst_fourid
							plugin_obj = convproj_obj.add_plugin(fxid, 'vst2', None)
							plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])
							pluginfo_obj = plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, fourid, 'chunk', rpp_extplug.data_chunk, None)
							if fourid == 1919118692: track_obj.fxslots_notes.append(fxid)
							elif plugin_obj.role == 'synth': track_obj.inst_pluginid = fxid
							elif plugin_obj.role == 'effect': track_obj.fxslots_audio.append(fxid)
						else:
							plugin_obj = convproj_obj.add_plugin(fxid, 'vst3', None)
							plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])
							pluginfo_obj = plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, rpp_extplug.vst3_uuid, rpp_extplug.data_chunk[8:-8])
							if plugin_obj.role == 'synth': track_obj.inst_pluginid = fxid
							elif plugin_obj.role == 'effect': track_obj.fxslots_audio.append(fxid)

					if rpp_plugin.type == 'JS':
						plugin_obj = convproj_obj.add_plugin(fxid, 'jesusonic', rpp_extplug.js_id)
						plugin_obj.role = 'effect'
						plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])
						for n, v in enumerate(rpp_extplug.data):
							if v != '-': plugin_obj.datavals.add(str(n), v)
						track_obj.fxslots_audio.append(fxid)


			for rpp_trackitem in rpp_track.items:
				cvpj_placement_type = 'notes'

				cvpj_position = rpp_trackitem.position.get()
				cvpj_duration = rpp_trackitem.length.get()
				cvpj_offset = rpp_trackitem.soffs.get()
				cvpj_vol = rpp_trackitem.volpan['vol']
				cvpj_pan = rpp_trackitem.volpan['pan']
				cvpj_muted = rpp_trackitem.mute['mute']
				cvpj_color = reaper_color_to_cvpj_color(rpp_trackitem.color.get(), False) if rpp_trackitem.color.used else None
				cvpj_name = rpp_trackitem.name.get()

				cvpj_audio_rate = rpp_trackitem.playrate['rate']
				cvpj_audio_preserve_pitch = rpp_trackitem.playrate['preserve_pitch']
				cvpj_audio_pitch = rpp_trackitem.playrate['pitch']
				cvpj_audio_file = ''

				midi_notes_out = midi_notes()
				midi_ppq = 960

				samplemode = 0
				startpos = 0
				if rpp_trackitem.source != None:
					rpp_source = rpp_trackitem.source
					if rpp_source.type in ['MP3','FLAC','VORBIS','WAVE','WAVPACK']:
						cvpj_placement_type = 'audio'
						cvpj_audio_file = rpp_source.file.get()
					if rpp_source.type in ['MIDI']:
						midi_ppq = rpp_source.hasdata['ppq']
						for note in rpp_source.notes: midi_notes_out.do_note(note)
					if rpp_source.type == 'SECTION':
						samplemode = int(rpp_source.mode.get())
						startpos = float(rpp_source.startpos.get())
						if rpp_source.source != None:
							insource = rpp_source.source
							if insource != None:
								if insource.type in ['MP3','FLAC','VORBIS','WAVE','WAVPACK']:
									cvpj_placement_type = 'audio'
									cvpj_audio_file = insource.file.get()

				cvpj_offset_bpm = ((cvpj_offset)*8)*tempomul
				cvpj_end_bpm = ((midi_notes_out.midipos/midi_ppq)*4)

				if cvpj_placement_type == 'notes': 
					placement_obj = track_obj.placements.add_notes()
					if cvpj_name: placement_obj.visual.name = cvpj_name
					if cvpj_color: placement_obj.visual.color.set_float(cvpj_color)
					placement_obj.position_real = cvpj_position
					placement_obj.duration_real = cvpj_duration

					placement_obj.cut_type = 'loop'
					placement_obj.cut_start = cvpj_offset_bpm
					placement_obj.cut_loopend = cvpj_end_bpm

					midi_notes_out.do_output(placement_obj.notelist, midi_ppq)

				if cvpj_placement_type == 'audio': 
					placement_obj = track_obj.placements.add_audio()
					if cvpj_name: placement_obj.visual.name = cvpj_name
					if cvpj_color: placement_obj.visual.color.set_float(cvpj_color)
					placement_obj.position_real = cvpj_position
					placement_obj.duration_real = cvpj_duration
					placement_obj.sample.pan = cvpj_pan
					placement_obj.sample.pitch = cvpj_audio_pitch
					placement_obj.sample.vol = cvpj_vol
					sampleref_obj = convproj_obj.add_sampleref(cvpj_audio_file, cvpj_audio_file)
					sampleref_obj.find_relative('projectfile')
					placement_obj.sample.sampleref = cvpj_audio_file
					if samplemode == 3: placement_obj.sample.reverse = True

					placement_obj.sample.stretch.set_rate_speed(bpm, cvpj_audio_rate, False)
					placement_obj.sample.stretch.preserve_pitch = cvpj_audio_preserve_pitch
					
					placement_obj.cut_type = 'cut'
					placement_obj.cut_start = (cvpj_offset_bpm/cvpj_audio_rate) + (startpos/cvpj_audio_rate)*8

			convproj_obj.add_trackroute(cvpj_trackid)
			trackdata.append([cvpj_trackid, trackroute])

		for to_track, trackroute in trackdata:
			convproj_obj.trackroute[to_track].to_master_active = bool(trackroute[0])
			for rpp_auxrecv_obj in trackroute[1]:
				from_track = trackdata[rpp_auxrecv_obj['tracknum']][0]
				sends_obj = convproj_obj.trackroute[from_track]
				send_obj = sends_obj.add(to_track, None, rpp_auxrecv_obj['vol'])
				send_obj.params.add('pan', rpp_auxrecv_obj['pan'], 'float')

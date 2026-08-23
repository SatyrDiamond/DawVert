# SPDX-FileCopyrightText: 2026 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import json
from objects import globalstore
from functions import xtramath
from functions import data_values

def to_color(visual_obj):
	return '#'+visual_obj.color.get_hex()

def ticks_to_time(v, bpm):
	return int((v/480)*(120/bpm)*1000)

def do_track_visual(gs_track, cvpj_track, fallbackname):
	visual_obj = cvpj_track.visual
	visual_inst_obj = cvpj_track.visual_inst
	gs_track.name = visual_obj.name if visual_obj.name else fallbackname
	if visual_obj.comment: gs_track.comments = visual_obj.comment
	if visual_obj.color: gs_track.color = to_color(visual_obj)
	elif visual_inst_obj.color: gs_track.color = to_color(visual_inst_obj)

def clipGain(clipGain):
	return 0 if clipGain is None else xtramath.to_db(clipGain)

def do_track_params(gs_track, cvpj_track):
	gs_track.faderGainDb = clipGain(cvpj_track.params.get('vol', 1).value)

class output_greysound(plugins.base):
	def is_dawvert_plugin(self):
		return 'output'
	
	def get_shortname(self):
		return 'greysound'
	
	def get_name(self):
		return 'Greysound'
	
	def gettype(self):
		return 'r'
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['fxtype'] = 'none'
		in_dict['file_ext'] = ''
		in_dict['auto_types'] = ['nopl_points']

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import greysound as proj_greysound

		convproj_obj.change_timings(960)
		
		session_obj = proj_greysound.greysound_session()
		bpm = session_obj.tempo = int(convproj_obj.params.get('bpm', 120).value)

		session_obj.metadata['name'] = convproj_obj.metadata.name if convproj_obj.metadata.name else 'untitled'

		# master
		track_obj = convproj_obj.track_master
		greysound_track = proj_greysound.greysound_track()
		greysound_track.id = 5000000000
		greysound_track.type = 'MASTER'
		greysound_track.timeBase = 'TICKS'
		do_track_visual(greysound_track, track_obj, 'Master')
		do_track_params(greysound_track, track_obj)
		session_obj.tracks.append(greysound_track)

		clipsdata = {}
		sampleref_assoc = {}

		folder = dawvert_intent.output_folder
		namet = dawvert_intent.output_visname
		audiofilepath = os.path.join(folder, namet, 'audio-files')
		os.makedirs(audiofilepath, exist_ok=True)

		# tracks
		tracknum = 0
		pointnum = 1000
		for trackid, track_obj in convproj_obj.track__iter():
			gtracknum = 1000000000+tracknum
			greysound_track = proj_greysound.greysound_track()
			greysound_track.id = gtracknum
			greysound_track.position = tracknum
			greysound_track.type = 'AUX'
			session_obj.tracks.append(greysound_track)

			visual_obj = track_obj.visual
			visual_inst_obj = track_obj.visual_inst
			do_track_visual(greysound_track, track_obj, 'Track')
			do_track_params(greysound_track, track_obj)

			if track_obj.type == 'instrument':
				greysound_track.type = 'INSTRUMENT'
				greysound_track.timeBase = 'TICKS'
				for rnum, notespl_obj in enumerate(track_obj.placements.pl_notes):
					greysound_region = proj_greysound.greysound_region()
					greysound_region.id = 'converted_region_%s_%i' % (gtracknum, rnum)
					greysound_region.trackId = gtracknum
					start, end = notespl_obj.time.get_startend()
					greysound_region.start = {"ticks": start, "millis": ticks_to_time(start, bpm)}
					greysound_region.end = {"ticks": end, "millis": ticks_to_time(end, bpm)}
					notespl_obj.notelist.mod_limit(-60, 67)
					for cnote in notespl_obj.notelist.iter_notes():
						note_obj = proj_greysound.greysound_midinote()
						note_obj.startTicks = int(cnote.pos)
						note_obj.durationTicks = int(cnote.dur)
						note_obj.pitch = int(cnote.key)+60
						note_obj.velocity = int(float(cnote.vol)*100)
						greysound_region.midiNotes.append(note_obj)
					session_obj.regions.append(greysound_region)

			if track_obj.type in ['audio']:
				greysound_track.type = 'AUDIO'
				greysound_track.timeBase = 'TIME'
				for rnum, placement_obj in enumerate(track_obj.placements.pl_audio):
					greysound_region = proj_greysound.greysound_region()
					greysound_region.id = 'converted_region_%s_%i' % (gtracknum, rnum)
					greysound_region.trackId = gtracknum
					pos, dur = placement_obj.time.get_posdur_real()
					greysound_region.start = {"millis": (pos)*1000}
					greysound_region.end = {"millis": (pos+dur)*1000}

					sp_obj = placement_obj.sample
					sampleref_id = greysound_region.clipId = sp_obj.sampleref

					if sampleref_id not in clipsdata:
						ref_found, sampleref_obj = convproj_obj.sampleref__get(sampleref_id)
						uuiddata = sampleref_assoc[sampleref_id] = str(data_values.bytes__to_uuid( sampleref_id.encode()))

						sampleref_assoc[sampleref_id] = uuiddata

						if ref_found:
							fileref_obj = sampleref_obj.fileref
							fileext = fileref_obj.file.extension

							outfilename = '%s.%s' % (uuiddata, fileext)

							greysound_clip = clipsdata[sampleref_id] = proj_greysound.greysound_clip()
							greysound_clip.id = uuiddata
							greysound_clip.filename = str(fileref_obj.file)
							greysound_clip.storagePath = "/".join(['audio-files', outfilename])
							greysound_clip.durationSec = sampleref_obj.get_dur_sec()
							session_obj.clips.append(greysound_clip)

							sampleref_obj.copy_file(None, os.path.join(audiofilepath, outfilename))

					greysound_region.clipId = sampleref_assoc[sampleref_id]
					session_obj.regions.append(greysound_region)


			v_ap_f, v_ap_d = convproj_obj.automation.get(['track', trackid, 'vol'], 'float')
			if v_ap_f:
				if v_ap_d.u_nopl_points:
					gs_lane = proj_greysound.greysound_automationLane()
					gs_lane.id = "automation-%s-track-volume" % (gtracknum)
					gs_lane.trackId = gtracknum
					greysound_track.automationLanes.append(gs_lane)

					target = gs_lane.target
					target.type = "TRACK"
					target.parameterId = "volume"
					target.label = "Volume"
					target.minValue = -60
					target.maxValue = 12
					target.defaultValue = 0
					target.unit = "dB"
					
					for point in v_ap_d.nopl_points:
						pointnum += 1
						p = proj_greysound.greysound_automationLane_point()
						p.id = "automationpoint-%s" % (pointnum)
						p.position = {"ticks": point.pos/16}
						p.value = clipGain(point.value) if point.value else  -60
						gs_lane.points.append(p)

			p_ap_f, p_ap_d = convproj_obj.automation.get(['track', trackid, 'pan'], 'float')
			if p_ap_f:
				if p_ap_d.u_nopl_points:
					gs_lane = proj_greysound.greysound_automationLane()
					gs_lane.id = "automation-%s-track-pan" % (gtracknum)
					gs_lane.trackId = gtracknum
					greysound_track.automationLanes.append(gs_lane)

					target = gs_lane.target
					target.type = "TRACK"
					target.parameterId = "pan"
					target.label = "Pan"
					target.minValue = -1
					target.maxValue =1
					target.defaultValue = 0
					
					for point in p_ap_d.nopl_points:
						pointnum += 1
						p = proj_greysound.greysound_automationLane_point()
						p.id = "automationpoint-%s" % (pointnum)
						p.position = {"ticks": point.pos/16}
						p.value = point.value
						gs_lane.points.append(p)

			tracknum += 1

		for num, timemarker_obj in enumerate(convproj_obj.timemarkers):
			greysound_marker = proj_greysound.greysound_marker()
			greysound_marker.id = 'converted_marker_%i' % (num)
			greysound_marker.name = timemarker_obj.visual.name if timemarker_obj.visual.name else 'Marker'
			greysound_marker.position = {"ticks": timemarker_obj.time.get_pos()}
			session_obj.markers.append(greysound_marker)

		if dawvert_intent.output_mode == 'file':
			folder = dawvert_intent.output_folder
			namet = dawvert_intent.output_visname
			foldpath = os.path.join(folder, namet)
			
			os.makedirs(foldpath, exist_ok=True)

			outfile = os.path.join(foldpath, 'session.json')

			f = open(outfile, 'w')
			f.write(json.dumps(session_obj.write(), indent=4))

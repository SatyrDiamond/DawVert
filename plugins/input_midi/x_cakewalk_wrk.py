# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import note_data
from functions import value_midi
import xml.etree.ElementTree as ET
import plugins
import json

class input_cvpj_f(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'cakewalk_wrk'
	
	def get_name(self):
		return 'Cakewalk Work'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['projtype'] = 'multi'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import cakewalk_wrk as proj_cakewalk_wrk

		project_obj = proj_cakewalk_wrk.cakewalk_wrk_file()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(96, False)
		trackchannel = 0

		traits_obj = convproj_obj.traits
		traits_obj.fxrack_params = ['vol','pan','pitch']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.audio_filetypes = ['wav']

		if project_obj.version == 2:
			convproj_obj.fxtype = 'rack'
			convproj_obj.type = 'cm'

			traits_obj.track_nopl = True
			convproj_obj.do_actions.append('do_addloop')
			convproj_obj.do_actions.append('do_singlenotelistcut')

			controltrack_obj = convproj_obj.track__add('control', 'midi', 1, False)
			controltrack_obj.visual.name = 'Control'
			controlevents_obj = controltrack_obj.placements.midievents

			sysex_data = {}
			sysex_points = []
			sysex_num = 0

			for chunk in project_obj.chunks:
				if chunk.is_parsed:
					parseddata = chunk.content
	
					if chunk.id == 10: #Gen1:Global:Timebase
						convproj_obj.set_timings(parseddata.timebase, False)

					elif chunk.id == 15: #Gen1:Global:Auto:Tempo_V3
						for x in parseddata.points: controlevents_obj.add_tempo(x[0], x[1]/100)

					elif chunk.id == 1: #Gen1:Track:Header
						cvpj_trackid = str(parseddata.trackno)
						track_obj = convproj_obj.track__add(cvpj_trackid, 'midi', 1, False)
						track_obj.visual.name = parseddata.name.decode()
						if parseddata.channel != 255:
							track_obj.midi.out_enabled = True
							track_obj.midi.out_chanport.chan = parseddata.channel
							track_obj.midi.out_chanport.port = parseddata.port
							trackchannel = parseddata.channel
						else:
							trackchannel = 0
						events_obj = track_obj.placements.midievents
						events_obj.has_duration = True
						
					elif chunk.id == 24: #Gen1:Track:Name
						track_obj.visual.name = parseddata.name.decode()
	
					elif chunk.id == 2: #Gen1:Track:Events
						for event in parseddata.events:
							event_type = event.type
							event_data = event.data
							event_time = event.time

							if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
							elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
							elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
							elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
							elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
							elif event_type == 0xE0: events_obj.add_pitch(event_time, trackchannel, event_data.data1+(event_data.data2<<8)-16384)
							elif event_type == 0xF0: sysex_points.append([events_obj, event_time, event_data.data1])

					elif chunk.id == 6: #Gen1:Global:SysEx
						sysex_num += 1
						sysex_data[sysex_num] = parseddata.data[1:-1]

			for sysex_point in sysex_points:
				sysex_point[0].add_sysex(sysex_point[1], sysex_data[sysex_point[2]])

		if project_obj.version == 3:
			convproj_obj.type = 'r'
			traits_obj.notes_midi = True

			convproj_obj.do_actions.append('do_addloop')

			controltrack_obj = convproj_obj.track__add('control', 'midi', 1, False)
			controltrack_obj.visual.name = 'Control'
			controlevents_obj = controltrack_obj.placements.midievents

			segment_data_store = {}

			for chunk in project_obj.chunks:
				if chunk.is_parsed:
					parseddata = chunk.content
	
					if chunk.id == 10: #Gen1:Global:Timebase
						convproj_obj.set_timings(parseddata.timebase, False)

					elif chunk.id == 15: #Gen1:Global:Auto:Tempo_V3
						for x in parseddata.points: controlevents_obj.add_tempo(x[0], x[1]/100)

					elif chunk.id == 36: #Gen2:Track:Header
						cvpj_trackid = str(parseddata.trackno)
						track_obj = convproj_obj.track__add(cvpj_trackid, 'midi', 1, False)
						track_obj.visual.name = parseddata.name.decode()
						if parseddata.channel != 255:
							trackchannel = max(0, parseddata.channel)
							track_obj.midi.out_enabled = True
							track_obj.midi.out_chanport.chan = trackchannel
							track_obj.midi.out_chanport.port = parseddata.port
						else:
							trackchannel = 0
						events_obj = track_obj.placements.midievents
						events_obj.has_duration = True
						
					elif chunk.id == 49: #Gen2:Track:Segment
						if parseddata.is_nonlinked: 
							segment_data_store[parseddata.id] = [parseddata.events, parseddata.name, parseddata.color, parseddata.offset]
						cw_events, cw_name, cw_color, startoffs = segment_data_store[parseddata.id]

						placement_obj = track_obj.placements.add_midi()
						events_obj = placement_obj.midievents
						events_obj.has_duration = True
						events_obj.ppq = int(convproj_obj.time_ppq)

						if cw_name: placement_obj.visual.name = cw_name.decode()
						if cw_color is not None: 
							placement_obj.visual.color.set_int(list(cw_color))
							placement_obj.visual.color.fx_allowed = ['saturate', 'brighter']

						for event in cw_events:
							event_type = event.type
							event_data = event.data
							event_time = event.time-startoffs

							if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
							elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
							elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
							elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
							elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
							elif event_type == 0xE0: events_obj.add_pitch(event_time, trackchannel, event_data.data1+(event_data.data2<<8)-16384)

						time_obj = placement_obj.time
						time_obj.set_posdur(parseddata.offset, events_obj.get_dur())

					elif chunk.id == 45: #Gen2:Track:Events
						cw_events = parseddata.events
						
						if cw_events:
							firstpos = cw_events[0].time

							placement_obj = track_obj.placements.add_midi()
							events_obj = placement_obj.midievents
							events_obj.has_duration = True
							events_obj.ppq = int(convproj_obj.time_ppq)

							if parseddata.name: placement_obj.visual.name = parseddata.name.decode()

							for event in parseddata.events:
								event_type = event.type
								event_data = event.data
								event_time = event.time-firstpos
	
								if event_type == 0x90: events_obj.add_note_dur(event_time, trackchannel, event_data.data1, event_data.data2, event_data.dur)
								elif event_type == 0xA0: events_obj.add_note_pressure(event_time, trackchannel, event_data.data1, event_data.data2)
								elif event_type == 0xB0: events_obj.add_control(event_time, trackchannel, event_data.data1, event_data.data2)
								elif event_type == 0xC0: events_obj.add_program(event_time, trackchannel, event_data.data1)
								elif event_type == 0xD0: events_obj.add_chan_pressure(event_time, trackchannel, event_data.data1)
								elif event_type == 0xE0: events_obj.add_pitch(event_time, trackchannel, event_data.data1+(event_data.data2<<8)-16384)

							time_obj = placement_obj.time
							time_obj.set_posdur(firstpos, events_obj.get_dur())


					#else:
					#	print(chunk)
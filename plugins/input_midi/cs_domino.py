# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
import plugins
import xml.etree.ElementTree as ET
from objects import globalstore

class input_domino(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'domino'
	
	def get_name(self):
		return 'Domino'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['dms']
		in_dict['fxrack_params'] = ['vol','pan','pitch']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'cs'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import domino as proj_domino
		from objects import colors

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'cs'

		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')
		colordata = colors.colorset.from_dataset('midi', 'track', 'domino')

		project_obj = proj_domino.dms_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.set_timings(project_obj.ppq, False)

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.copyright = project_obj.copyright

		for n, track in enumerate(project_obj.tracks):
			channel = track.channel
			track_obj = convproj_obj.track__add(str(n), 'midi', 1, False)
			track_obj.visual.name = track.name
			if track.color != 255:
				track_obj.visual.color.set_int(colordata.getcolornum(track.color))
			track_obj.midi.out_enabled = True
			track_obj.midi.out_chanport.chan = channel
			track_obj.midi.out_chanport.port = track.out_port

			events_obj = track_obj.placements.midievents
			events_obj.has_duration = True
			events_obj.data.alloc_size = 256

			for x in track.notes:
				events_obj.add_note_dur(x.pos, channel, x.key, x.vel, x.dur)

			for x in track.timesigs:
				events_obj.add_timesig(x.pos, x.num, x.nenom)

			for x in track.programchanges:
				events_obj.add_program(x.pos, channel, x.patch-1)

			for x in track.sysex:
				events_obj.add_sysex(x.pos, x.sysex)

			for x in track.texts:
				events_obj.add_text(x.pos, x.text)

			for x in track.lyrics:
				events_obj.add_lyric(x.pos, x.text)

			for x in track.tempos:
				events_obj.add_tempo(x.pos, x.val)

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects import dv_dataset
from objects_proj import proj_orgyana
import plugin_input

class input_orgyana(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'orgyana'
	def gettype(self): return 'r'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Orgyana'
		dawinfo_obj.file_ext = 'org'
		dawinfo_obj.auto_types = ['nopl_points']
		dawinfo_obj.track_nopl = True
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(6)
		if bytesdata == b'Org-02' or bytesdata == b'Org-03': return True
		else: return False

	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		dataset = dv_dataset.dataset('./data_dset/orgyana.dset')
		colordata = colors.colorset(dataset.colorset_e_list('track', 'orgmaker_2'))

		project_obj = proj_orgyana.orgyana_project()
		project_obj.load_from_file(input_file)

		for tracknum, orgtrack_obj in enumerate(project_obj.tracks):
			if len(orgtrack_obj.notes) != 0:

				trackname = "Melody "+str(tracknum+1) if tracknum < 8 else dataset.object_get_name_color('drums', str(orgtrack_obj.instrument))[0]
				idval = 'org_'+str(tracknum)

				track_obj = convproj_obj.add_track(idval, 'instrument', 0, False)
				track_obj.visual.name = trackname
				track_obj.visual.color = colordata.getcolornum(tracknum)
				track_obj.params.add('pitch', (orgtrack_obj.pitch-1000)/1800, 'float')

				posnotes = {}
				for org_note in orgtrack_obj.notes: posnotes[org_note[0]] = org_note[1:5]
				posnotes = dict(sorted(posnotes.items(), key=lambda item: item[0]))
				endnote = None
				notedur = 0
				org_notelist = []
				for pos, orgnote in posnotes.items():
					note, dur, vol, pan = orgnote
					if endnote != None: 
						if pos >= endnote: endnote = None
					if orgnote[1] != 1:
						notedur = orgnote[1]
						endnote = pos+notedur
					if endnote != None: isinsidenote = False if endnote-pos == notedur else True
					else: isinsidenote = False
					if not isinsidenote: track_obj.placements.notelist.add_r(pos, dur, note-48, vol/254, {'pan': (pan-6)/6})

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.do_actions.append('do_singlenotelistcut')
		convproj_obj.params.add('bpm', (1/(project_obj.wait/122))*122, 'float')
		convproj_obj.timesig = [project_obj.stepsperbar, project_obj.beatsperstep]

		if project_obj.loop_beginning != 0: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = project_obj.loop_beginning
			convproj_obj.loop_end = project_obj.loop_end
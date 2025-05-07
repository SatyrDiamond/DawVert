# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os.path
import bisect
from objects import globalstore
from objects.convproj import fileref

class rootnote_stor():
	def __init__(self):
		self.data = []
	
	def add_pos(self, p):
		if self.data:
			for n, x in enumerate(self.data):
				if x[1]==-1:
					self.data[n][0] = p
					self.data.insert(n, [0,p,60])
					break
				elif x[1]>p:
					self.data.insert(n, [0,p,60])
					break
		else:
			self.data = [[p,-1,60]]

		for n, x in enumerate(self.data):
			if (len(self.data)-1)>n>0:
				self.data[n][0] = self.data[n-1][1]

	def add_notes(self, notedata):
		notepos = list(notedata)
		for x in notepos:
			b = bisect.bisect_left(notepos, x)
			if b<len(self.data): self.data[b][2] = notedata[x]

	def iterd(self, ostart, oend):
		for start, end, root_note in self.data:
			if end != -1:
				cond = ((end>ostart) and (start<oend))
				if cond: yield max(start, ostart), min(end, oend), root_note
			else:
				cond = (start<oend)
				if cond: yield max(start, ostart), oend, root_note

def calc_root(proj_root, track_root):
	roottrack = (proj_root-60)
	roottrack = roottrack%12

	notetrack = track_root-60
	notetrack = notetrack%12

	outt = roottrack-notetrack
	outt -= ((outt+6)//12)*12
	return outt

def extract_audio(filename, sampleref_obj, dawvert_intent, zipfile):
	filename = str(sampleref_obj.fileref.file)
	try: zipfile.extract(filename, path=dawvert_intent.path_samples['extracted'], pwd=None)
	except PermissionError: pass
	filepath = os.path.join(dawvert_intent.path_samples['extracted'], filename)
	sampleref_obj.set_path(None, filepath)

volumeversion = 4

def add_audio_regions(
	placements_obj, ppq, rootnote_auto, 
	region, stretch_type, num_beats, seconds,
	stretchflags, filename, tempo,
	track_root_note, audiotempo, pitch, version
	):

	mul1 = audiotempo/120 if audiotempo else 1

	if seconds is not None:
		mul2 = num_beats/(seconds*2)
		samplemul = mul2
	else:
		mul2 = mul1
		samplemul = mul1

	pls = []

	if stretch_type == 0:
		ppq_beats = num_beats*ppq
		calc_offset = region.offset*(mul2**1.000004)
		calc_offset = calc_offset/5000000
		offset = calc_offset*ppq

		if 1 in stretchflags:
			for start, end, cur_root in rootnote_auto.iterd(region.pos, region.pos+region.size):
				placement_obj = placements_obj.add_audio()
				time_obj = placement_obj.time
				time_obj.set_startend(start, end)
				time_obj.set_loop_data((offset)+((start-region.pos)%ppq_beats), 0, ppq_beats)

				sp_obj = placement_obj.sample 
				sp_obj.sampleref = filename
				sp_obj.stretch.set_rate_tempo(tempo, samplemul, True)
				sp_obj.stretch.preserve_pitch = True
				if 1 in region.flags: placement_obj.muted = True
				if 3 in region.flags: placement_obj.locked = True
				if 5 in region.flags: sp_obj.reverse = True
				if version>volumeversion: sp_obj.vol = region.vol

				if cur_root != 127:
					notetrack = calc_root(cur_root, track_root_note)
					sp_obj.pitch = notetrack+region.pitch+pitch
				else:
					sp_obj.usemasterpitch = False
					sp_obj.pitch = region.pitch+pitch

				pls.append(placement_obj)
		else:
			placement_obj = placements_obj.add_audio()
			time_obj = placement_obj.time
			time_obj.set_startend(region.pos, region.pos+region.size)
			time_obj.set_loop_data(offset, 0, ppq_beats)
			sp_obj = placement_obj.sample 
			sp_obj.sampleref = filename
			sp_obj.stretch.set_rate_tempo(tempo, samplemul, True)
			sp_obj.stretch.preserve_pitch = True
			sp_obj.usemasterpitch = False
			sp_obj.pitch = region.pitch+pitch
			if 1 in region.flags: placement_obj.muted = True
			if 3 in region.flags: placement_obj.locked = True
			if 5 in region.flags: sp_obj.reverse = True
			if version>volumeversion: sp_obj.vol = region.vol
			pls.append(placement_obj)

	if stretch_type == 1:
		calc_offset = region.offset/5000000
		calc_offset = calc_offset*ppq

		placement_obj = placements_obj.add_audio()
		ssize = (int(region.size)/5000000)*ppq
		time_obj = placement_obj.time
		time_obj.set_posdur(region.pos, ssize)
		time_obj.set_offset(calc_offset)
		sp_obj = placement_obj.sample 
		sp_obj.sampleref = filename
		if 1 in region.flags: placement_obj.muted = True
		if 3 in region.flags: placement_obj.locked = True
		if 5 in region.flags: sp_obj.reverse = True
		if version>volumeversion: sp_obj.vol = region.vol
		pls.append(placement_obj)

	if stretch_type == 2:
		calc_offset = region.offset/5000000
		calc_offset = calc_offset*ppq*mul1

		placement_obj = placements_obj.add_audio()
		time_obj = placement_obj.time
		time_obj.set_posdur(region.pos, region.size)
		time_obj.set_offset(calc_offset)
		sp_obj = placement_obj.sample 
		sp_obj.sampleref = filename
		sp_obj.stretch.set_rate_tempo(tempo, mul1, True)
		sp_obj.pitch = region.pitch+pitch
		sp_obj.stretch.preserve_pitch = True
		if 1 in region.flags: sp_obj.muted = True
		if 3 in region.flags: sp_obj.locked = True
		if 5 in region.flags: sp_obj.reverse = True
		if version>volumeversion: sp_obj.vol = region.vol
		pls.append(placement_obj)

	return pls



class input_acid_3(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sf_acid_3'
	
	def get_name(self):
		return 'Sony ACID 3+'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'
		in_dict['audio_filetypes'] = ['wav']
		in_dict['placement_loop'] = ['loop', 'loop_off']
		in_dict['fxtype'] = 'groupreturn'
		in_dict['audio_stretch'] = ['rate']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['notes_midi'] = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import new_acid

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		project_obj = new_acid.sony_acid_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.dataset.load('sony_acid', './data_main/dataset/sony_acid.dset')
		colordata = colors.colorset.from_dataset('sony_acid', 'track', 'acid_4')
		
		auto_basenotes = {}

		tempo = 120
		starttempo = 0

		files = {}
		filecount = 0
		tracknum = -1

		for root_chunk, root_name in project_obj.root.iter_wtypes():
			if root_name == 'Group:TempoKeyPoints':
				prevpoint = 0
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'Group:TempoKeyPoints':
						def_data = regs_chunk.content
						if not def_data.pos_samples:
							if def_data.tempo:
								starttempo = (500000/def_data.tempo)*120
								tempo = starttempo
						if def_data.base_note:
							base_note = int(def_data.base_note)
							if prevpoint is not base_note:
								auto_basenotes[def_data.pos_samples] = base_note
							prevpoint = base_note

			if root_name == 'Group:StartingParams':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'Group:StartingParams':
						def_data = regs_chunk.content
						auto_basenotes[0] = int(def_data.root_note)
						starttempo = (500000/def_data.tempo)*120

		rootnote_auto = rootnote_stor()
		for pos in list(auto_basenotes): rootnote_auto.add_pos(pos)
		rootnote_auto.add_notes(auto_basenotes)

		version = 0

		for root_chunk, root_name in project_obj.root.iter_wtypes():
			if root_name == 'MainData':
				def_data = root_chunk.content
				ppq = def_data.ppq
				convproj_obj.set_timings(ppq, False)
				version = def_data.version

				if not starttempo: tempo = def_data.tempo
				else: tempo = starttempo
				convproj_obj.params.add('bpm', tempo, 'float')
				convproj_obj.timesig = [def_data.timesig_num, def_data.timesig_denom]

			elif root_name == 'Group:RegionDatas':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'RegionData':
						if regs_chunk.content:
							def_data = regs_chunk.content
							files[filecount] = def_data.filename
						filecount += 1

			elif root_name == 'Group:TrackList':
				for trks_chunk, trks_name in root_chunk.iter_wtypes():

					if trks_name == 'Group:Track':
						tracknum += 1

						track_header = None
						track_audioinfo = None
						track_audiostretch = None
						track_regions = []

						track_audiodefs = []

						for track_chunk, track_name in trks_chunk.iter_wtypes():

							if track_chunk.is_list:

								if track_name == 'Group:AudioInfo': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'TrackAudioInfo':
											track_audioinfo = trackg_chunk.content

								if track_name == 'Group:AudioDef': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'Group:AudioDefList':
											audiodefd = [None, None]
											for audiodef_chunk, audiodef_name in trackg_chunk.iter_wtypes():
												if audiodef_name == 'AudioDef:Info': audiodefd[0] = audiodef_chunk.content
												if audiodef_name == 'Group:AudioStretch': 
													for as_chunk, as_name in audiodef_chunk.iter_wtypes():
														if as_name == 'Group:AudioStretch':
															audiodefd[1] = as_chunk.content
											track_audiodefs.append(audiodefd)

								if track_name == 'Group:AudioStretch': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'Group:AudioStretch':
											track_audiostretch = trackg_chunk.content

								if track_name == 'TrackData': 
									for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
										if trackg_name == 'Group:Regions':
											for reg_chunk, reg_name in trackg_chunk.iter_wtypes():
												if reg_name == 'TrackRegion':
													track_regions.append(reg_chunk.content)

								#if track_name == 'Group:TrackAuto': 
								#	for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
								#		if trackg_name == 'TrackAutomation':
								#			if track_header:
								#				track_auto = trackg_chunk.content
								#				autoloc = None
								#				
								#				trackid = 'track_'+str(tracknum)
#
								#				if not track_auto.group:
								#					if track_auto.param == 0: autoloc = ['track', trackid, 'vol']
								#					if track_auto.param == 1: autoloc = ['track', trackid, 'pan']
#
								#				if autoloc:
								#					for p in track_auto.points:
								#						convproj_obj.automation.add_autopoint(autoloc, 'float', p[0], p[2], 'normal')


							else:
								if track_name == 'TrackData':
									track_header = track_chunk.content

						if track_header:

							cvpj_trackid = 'track_'+str(tracknum)

							if track_header.type == 2:
								track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
								color = colordata.getcolornum(track_header.color)
								track_obj.visual.name = track_header.name
								track_obj.visual.color.set_int(color)
								track_obj.visual.color.fx_allowed = ['brighter']
								if track_audioinfo:
									track_obj.params.add('vol', track_audioinfo.vol, 'float')
									track_obj.params.add('pan', track_audioinfo.pan, 'float')
									track_obj.datavals.add('pan_mode', 'stereo')

								if track_regions:

									pls = []

									if track_audiostretch is not None:
										filename = track_header.filename
	
										sampleref_obj = convproj_obj.sampleref__add(filename, filename, 'win')
										if not project_obj.zipped: sampleref_obj.search_local(dawvert_intent.input_folder)
										else: extract_audio(filename, sampleref_obj, dawvert_intent, project_obj.zipfile)
										sampleref_obj.set_dur_sec(track_header.seconds)
										sampleref_obj.convert__path__fileformat()

										for region in track_regions:
											pls += add_audio_regions(
												track_obj.placements, ppq, rootnote_auto, 
												region, track_header.stretchtype, track_audiostretch.downbeat_offset, track_header.seconds,
												track_audiostretch.flags, filename, tempo,
												track_audiostretch.root_note, track_audiostretch.tempo, 0, version
												)
	
											for p in pls:
												p.visual.name = track_header.name
												p.visual.color.set_int(color)
												p.visual.color.fx_allowed = ['brighter']
	
									elif track_audiodefs is not None:
										for audiodef, audiostretch in track_audiodefs:
											if audiodef and audiostretch:
												filename = audiodef.filename
												sampleref_obj = convproj_obj.sampleref__add(filename, filename, 'win')
												if not project_obj.zipped: sampleref_obj.search_local(dawvert_intent.input_folder)
												else: extract_audio(filename, sampleref_obj, dawvert_intent, project_obj.zipfile)
												sampleref_obj.set_dur_sec(audiodef.seconds)
												sampleref_obj.convert__path__fileformat()

										for region in track_regions:
											def_header, def_audiostretch = track_audiodefs[region.index]

											pls += add_audio_regions(
												track_obj.placements, ppq, rootnote_auto, 
												region, def_header.stretchtype, def_audiostretch.downbeat_offset, def_header.seconds,
												def_audiostretch.flags, def_header.filename, tempo,
												def_audiostretch.root_note, def_audiostretch.tempo, def_header.pitch, version
												)

											for p in pls:
												p.visual.name = def_header.name
												color = colordata.getcolornum(def_header.color)
												p.visual.color.set_int(color)
												p.visual.color.fx_allowed = ['brighter']

									track_obj.placements.pl_audio.sort()
									track_obj.placements.pl_audio.remove_overlaps()


							if track_header.type == 4:
								track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
								color = colordata.getcolornum(track_header.color)
								track_obj.visual.name = track_header.name
								track_obj.visual.color.set_int(color)
								track_obj.visual.color.fx_allowed = ['brighter']

								if track_regions:
									filename_obj = fileref.cvpj_fileref()
									filename_obj.set_path('win', track_header.filename, True)

									if not project_obj.zipped:
										filename_obj.search_local(dawvert_intent.input_folder)
									else:
										filename = str(filename_obj.file)
										try:
											project_obj.zipfile.extract(filename, path=dawvert_intent.path_samples['extracted'], pwd=None)
										except PermissionError:
											pass
										filepath = os.path.join(dawvert_intent.path_samples['extracted'], filename)
										filename_obj.set_path('win', filepath, True)

									filename = filename_obj.get_path('win', False)

									for region in track_regions:
	
										outsize = region.size
	
										placement_obj = track_obj.placements.add_midi()

										time_obj = placement_obj.time
										time_obj.set_posdur(region.pos, outsize)

										placement_obj.pitch = int(region.pitch)
										placement_obj.midi_from(filename)

										midievents_obj = placement_obj.midievents
										midievents_obj.sort()

										maxdur = (midievents_obj.get_dur()/midievents_obj.ppq)
										maxdur = maxdur.__ceil__()
										
										placement_obj.visual.name = midievents_obj.track_name

										if maxdur>0:
											time_obj.set_loop_data(region.offset, 0, maxdur*ppq)

			elif root_name == 'Group:TempoKeyPoints':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'Group:TempoKeyPoints':
						def_data = regs_chunk.content
						if def_data.tempo:
							tempov = (500000/def_data.tempo)*120
							convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', def_data.pos_samples, tempov, 'instant')
						if def_data.base_note:
							if def_data.pos_samples in auto_basenotes:
								timemarker_obj = convproj_obj.timemarker__add_key(auto_basenotes[def_data.pos_samples]-60)
								timemarker_obj.position = def_data.pos_samples
								timemarker_obj.visual.color.set_int([56, 95, 125])

			elif root_name == 'Group:Markers':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'Marker':
						marker = regs_chunk.content

						timemarker_obj = convproj_obj.timemarker__add()
						timemarker_obj.position = marker.pos
						timemarker_obj.duration = marker.end
						timemarker_obj.visual.name = marker.name if marker.name else '[%i]' % marker.id
						if marker.type == 1: 
							timemarker_obj.type = 'region'
							timemarker_obj.visual.color.set_int([84,158,101])
						else:
							timemarker_obj.visual.color.set_int([219,142,87])
						timemarker_obj.visual.color.fx_allowed = ['brighter']

			elif root_name == 'Group:MetaData':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'MetaData':
						metadata = regs_chunk.content.metadata
						if b'INAM' in metadata: convproj_obj.metadata.name = metadata[b'INAM']
						if b'IENG' in metadata: convproj_obj.metadata.author = metadata[b'IENG']
						if b'IART' in metadata: convproj_obj.metadata.original_author = metadata[b'IART']
						if b'ICMT' in metadata: convproj_obj.metadata.comment_text = metadata[b'ICMT']
						if b'ICOP' in metadata: convproj_obj.metadata.copyright = metadata[b'ICOP']
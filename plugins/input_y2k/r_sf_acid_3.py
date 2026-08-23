# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os.path
import bisect
from objects import globalstore
from objects import regions
from objects.convproj import fileref
from functions import xtramath

volumeversion = 5

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

def do_region_common(sp_obj, placement_obj, region, version):
	if 1 in region.flags: placement_obj.muted = True
	if 3 in region.flags: placement_obj.locked = True
	if 5 in region.flags: sp_obj.reverse = True
	if version>volumeversion: sp_obj.vol = region.vol

def do_color(colordata, visual_obj, icolor):
	color = colordata.getcolornum(icolor)
	visual_obj.color.set_int(color)
	visual_obj.color.fx_allowed = ['brighter']
	return color

class addregion_data():
	def __init__(self):
		self.rootnote_auto = None
		self.stretch_type = None
		self.num_beats = None
		self.seconds = None
		self.stretchflags = None
		self.filename = None
		self.tempo = None
		self.track_root_note = None
		self.audiotempo = None
		self.pitch = 0
		self.version = 0
		self.ppq = 96

#def add_audio_regions(
#	placements_obj, ppq, rootnote_auto, 
#	region, stretch_type, num_beats, seconds,
#	stretchflags, filename, tempo,
#	track_root_note, audiotempo, pitch, version):
def add_audio_regions(placements_obj, region, addr_d):
	rootnote_auto = addr_d.rootnote_auto
	stretch_type = addr_d.stretch_type
	num_beats = addr_d.num_beats
	seconds = addr_d.seconds
	stretchflags = addr_d.stretchflags
	filename = addr_d.filename
	tempo = addr_d.tempo
	track_root_note = addr_d.track_root_note
	audiotempo = addr_d.audiotempo
	pitch = addr_d.pitch
	version = addr_d.version
	ppq = addr_d.ppq

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
				sp_obj.stretch.timing.set__beats(num_beats)
				sp_obj.stretch.preserve_pitch = True
				do_region_common(sp_obj, placement_obj, region, version)

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
			sp_obj.stretch.timing.set__beats(num_beats)
			sp_obj.stretch.preserve_pitch = True
			sp_obj.usemasterpitch = False
			sp_obj.pitch = region.pitch+pitch
			do_region_common(sp_obj, placement_obj, region, version)
			pls.append(placement_obj)

	if stretch_type in [1,2,3]:
		placement_obj = placements_obj.add_audio()
		time_obj = placement_obj.time
		sp_obj = placement_obj.sample
		sp_obj.sampleref = filename

		if stretch_type == 1:
			real_offset = region.offset/10000000
			real_size = region.size/10000000
			sampmul = xtramath.pitch_to_speed(-(region.pitch+pitch))

			ssize = (real_size)*ppq
			time_obj.set_pos(region.pos)
			time_obj.set_dur_real(real_size)
			time_obj.set_offset_real(real_offset)
			sp_obj.stretch.timing.set__speed(sampmul)

		if stretch_type == 2:
			calc_offset = region.offset/5000000
			calc_offset = calc_offset*ppq*mul1

			time_obj.set_posdur(region.pos, region.size)
			time_obj.set_offset(calc_offset)
			sp_obj.stretch.timing.set__orgtempo(audiotempo)
			sp_obj.pitch = region.pitch+pitch
			sp_obj.stretch.preserve_pitch = True

		if stretch_type == 3:
			calc_offset = region.offset/10000000

			time_obj.set_posdur(region.pos, region.size)
			time_obj.set_offset_real(calc_offset)
			sp_obj.stretch.timing.set__orgtempo(audiotempo)
			sp_obj.pitch = region.pitch+pitch
			sp_obj.stretch.preserve_pitch = True

		do_region_common(sp_obj, placement_obj, region, version)
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

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import new_acid

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.placement_loop = ['loop', 'loop_off']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['pl_points','nopl_ticks']
		traits_obj.notes_midi = True
		traits_obj.time_seconds_auto = True

		project_obj = new_acid.sony_acid_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		globalstore.datapack.load('sony_acid', './data/datapack/app/sony_acid.xml')
		colordata = colors.colorset.from_datapack('sony_acid', 'track', 'acid_4')
		
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

		rootnote_auto = regions.rootnote_stor()
		for pos in list(auto_basenotes): rootnote_auto.add_pos(pos)
		rootnote_auto.add_notes(auto_basenotes)

		version = 0

		tracks_data = {}

		def do_orders_groups(riff_data, track_order, tracks_data, ingroup):
			for regs_chunk, regs_name in riff_data.iter_wtypes():
				if regs_name=='TrackSTrack':
					def_data = regs_chunk.content
					convproj_obj.track_order.append( 'track_'+str(def_data.tracknum) )
					track_obj = tracks_data[def_data.tracknum]
					track_obj.group = ingroup
				if regs_name=='TrackSFolder':
					def_data = regs_chunk.content
					groupid = 'group_'+str(def_data.idnum)
					group_obj = convproj_obj.fx__group__add(groupid)
					group_obj.visual.name = def_data.name
					group_obj.group = ingroup
					group_obj.params.add('enabled', 4 not in def_data.flags, 'float')
					group_obj.params.add('solo', 3 in def_data.flags, 'float')
					group_obj.visual_track.group_expanded = 1 not in def_data.flags
					do_orders_groups(def_data.inchunks, track_order, tracks_data, groupid)

		for root_chunk, root_name in project_obj.root.iter_wtypes():
			if root_name == 'MainData':
				def_data = root_chunk.content
				ppq = def_data.ppq
				convproj_obj.set_timings(ppq)
				version = def_data.version

				if not starttempo: tempo = def_data.tempo
				else: tempo = starttempo
				convproj_obj.params.add('bpm', tempo, 'float')
				convproj_obj.timesig = [def_data.timesig_num, def_data.timesig_denom]

			elif root_name == 'Group:RegionDatas':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'RegionDataAudio':
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


							else:
								if track_name == 'TrackData':
									track_header = track_chunk.content

						for track_chunk, track_name in trks_chunk.iter_wtypes():
							if track_chunk.is_list:
								if track_name == 'Group:TrackAuto': 
									if track_header:
										cvpj_trackid = 'track_'+str(track_header.id)
										for trackg_chunk, trackg_name in track_chunk.iter_wtypes():
											if trackg_name == 'TrackAutomation':
												if track_header:
													track_auto = trackg_chunk.content
													autoloc = None

													autotype = 'normal'
													invert = False

													if not track_auto.group:
														if track_auto.param == 0: autoloc = ['track', cvpj_trackid, 'vol']
														if track_auto.param == 1: autoloc = ['track', cvpj_trackid, 'pan']
														if track_auto.param == 31: 
															autoloc = ['track', cvpj_trackid, 'enabled']
															invert = True
	
													if autoloc:
														for p in track_auto.points:
															if not p[1]:
																convproj_obj.automation.add_autopoint(autoloc, 'float', p[0], p[2] if not invert else 1-p[2], autotype)


						if track_header:

							cvpj_trackid = 'track_'+str(track_header.id)

							if track_header.type == 2:
								track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
								tracks_data[track_header.id] = track_obj
								track_obj.visual.name = track_header.name
								color = do_color(colordata, track_obj.visual, track_header.color)

								if track_audioinfo:
									track_obj.params.add('vol', track_audioinfo.vol, 'float')
									track_obj.params.add('pan', track_audioinfo.pan, 'float')
									track_obj.datavals.add('pan_mode', 'stereo')
									track_obj.params.add('enabled', 1 not in track_header.flags, 'float')

								if track_regions:
									addr_d = addregion_data()
									addr_d.rootnote_auto = rootnote_auto
									addr_d.tempo = tempo
									addr_d.version = version
									addr_d.ppq = ppq

									pls = []

									if track_audiostretch is not None:
										filename = track_header.filename
	
										sampleref_obj = convproj_obj.sampleref__add(filename, filename, 'win')
										if not project_obj.zipped: sampleref_obj.search_local(dawvert_intent.input_folder)
										else: extract_audio(filename, sampleref_obj, dawvert_intent, project_obj.zipfile)
										sampleref_obj.set_dur_sec(track_header.seconds)
										sampleref_obj.convert__path__fileformat()

										addr_d.stretch_type = track_header.stretchtype
										addr_d.num_beats = track_audiostretch.downbeat_offset
										addr_d.seconds = track_header.seconds
										addr_d.stretchflags = track_audiostretch.flags
										addr_d.filename = filename
										addr_d.track_root_note = track_audiostretch.root_note
										addr_d.audiotempo = track_audiostretch.tempo
										addr_d.pitch = 0

										for region in track_regions:

											pls += add_audio_regions(track_obj.placements, region, addr_d)
	
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

											addr_d.stretch_type = def_header.stretchtype
											addr_d.num_beats = def_audiostretch.downbeat_offset
											addr_d.seconds = def_header.seconds
											addr_d.stretchflags = def_audiostretch.flags
											addr_d.filename = def_header.filename
											addr_d.track_root_note = def_audiostretch.root_note
											addr_d.audiotempo = def_audiostretch.tempo
											addr_d.pitch = def_header.pitch

											pls += add_audio_regions(track_obj.placements, region, addr_d)

											for p in pls:
												p.visual.name = def_header.name
												do_color(colordata, p.visual, def_header.color)

									track_obj.placements.pl_audio.sort()
									track_obj.placements.pl_audio.remove_overlaps()


							if track_header.type == 4:
								track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)
								tracks_data[track_header.id] = track_obj
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

			elif root_name == 'TrackOrder':
				old_track_order = convproj_obj.track_order
				convproj_obj.track_order = []
				do_orders_groups(root_chunk, old_track_order, tracks_data, None)

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
								timemarker_obj.time.set_pos(def_data.pos_samples)
								timemarker_obj.visual.color.set_int([56, 95, 125])

			elif root_name == 'Group:Markers':
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'Marker':
						marker = regs_chunk.content

						timemarker_obj = convproj_obj.timemarker__add()
						timemarker_obj.time.set_posdur(marker.pos, marker.end)
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

			elif root_name == 'Group:Arranger':
				arrcolordata = colors.colorset.from_datapack('sony_acid', 'track', 'arranger')
				for regs_chunk, regs_name in root_chunk.iter_wtypes():
					if regs_name == 'ArrangerPart':
						arrdata = regs_chunk.content

						timemarker_obj = convproj_obj.arranger.add()
						timemarker_obj.type = 'region'
						timemarker_obj.time.set_posdur(arrdata.pos, arrdata.dur)
						timemarker_obj.visual.name = arrdata.name
						color = arrcolordata.getcolornum(arrdata.color)
						timemarker_obj.visual.color.set_int(color)

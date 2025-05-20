# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os.path
import bisect
from objects import globalstore

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

class input_acid_old(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'sf_acid'
	
	def get_name(self):
		return 'Sonic Foundry ACID 1.x-2.x'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects import colors
		from objects.file_proj_past import sony_acid as sony_acid

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'groupreturn'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.placement_loop = ['loop', 'loop_off']
		traits_obj.audio_stretch = ['rate']
		traits_obj.auto_types = ['pl_points','nopl_ticks']

		project_obj = sony_acid.sony_acid_file()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		ppq = project_obj.ppq
		convproj_obj.set_timings(ppq, False)

		globalstore.dataset.load('sony_acid', './data_main/dataset/sony_acid.dset')
		colordata = colors.colorset.from_dataset('sony_acid', 'track', 'acid_1')
		convproj_obj.params.add('bpm', project_obj.tempo, 'float')
 
		samplefolder = dawvert_intent.path_samples['extracted']

		songroot = project_obj.root_note

		used_sends = []

		auto_basenotes = {}

		rootnote_auto = rootnote_stor()

		auto_basenotes[0] = project_obj.root_note

		convproj_obj.transport.loop_active = bool(project_obj.loop_enable)
		convproj_obj.transport.loop_start = project_obj.loop_start
		convproj_obj.transport.loop_end = project_obj.loop_end

		if len(project_obj.tempmap):
			convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', 0, project_obj.tempo)

			for x in project_obj.tempmap:
				if x['tempo']:
					tempov = (500000/x['tempo'])*120
					convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', int(x['pos']), tempov)
				if x['base_note']:
					pos = int(x['pos'])
					if pos:
						auto_basenotes[pos] = int(x['base_note'])
						timemarker_obj = convproj_obj.timemarker__add_key(auto_basenotes[pos]-60)
						timemarker_obj.position = pos
						timemarker_obj.visual.color.set_int([0,0,255] if not x['tempo'] else [0,192,0])
					else:
						auto_basenotes[0] = int(x['base_note'])

		for marker in project_obj.markers:
			timemarker_obj = convproj_obj.timemarker__add()
			timemarker_obj.position = marker.pos
			timemarker_obj.visual.name = marker.text if marker.text else '[%i]' % marker.id
			timemarker_obj.visual.color.set_int([255,0,0])

		timemarker_obj = convproj_obj.timemarker__add_key(auto_basenotes[0]-60)

		for pos in list(auto_basenotes): rootnote_auto.add_pos(pos)
		rootnote_auto.add_notes(auto_basenotes)

		for tracknum, track in enumerate(project_obj.tracks):
			cvpj_trackid = 'track_'+str(tracknum)
			track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			color = colordata.getcolornum(track.color)
			track_obj.visual.name = track.name
			track_obj.visual.color.set_int(color)
			track_obj.visual.color.fx_allowed = ['saturate', 'brighter']
			track_obj.params.add('vol', track.vol, 'float')
			track_obj.params.add('pan', track.pan, 'float')
			track_obj.is_drum = 1 not in track.flags

			if track.mutesolo == 2: 
				track_obj.params.add('enabled', False, 'float')

			for send in track.sends:
				returnid = 'return__'+str(send.id)
				track_obj.sends.add(returnid, 'send_%i_%i' % (tracknum, send.id), send.vol)
				if send.id not in used_sends: used_sends.append(send.id)

			sample_path = None
			sampleref_obj = None

			if project_obj.audios:
				if len(project_obj.audios)>=tracknum:
					wave_path = samplefolder+'track_'+str(tracknum)+'.wav'
					outaudio = bytearray(project_obj.audios[tracknum])
					if len(outaudio)>12:
						if outaudio[8:12] == b'wave': outaudio[8:12] = b'WAVE'

					wav_fileobj = open(wave_path, 'wb')
					wav_fileobj.write(outaudio)
					sampleref_obj = convproj_obj.sampleref__add(wave_path, wave_path, 'win')
					sample_path = wave_path
			else:
				sample_path = track.path
				sampleref_obj = convproj_obj.sampleref__add(sample_path, sample_path, 'win')
				sampleref_obj.search_local(dawvert_intent.input_folder)

			sampleref_obj.set_dur_samples(track.num_samples)
			
			trackpitch = track.pitch
			track_root_note = track.root_note

			sample_tempo = track.stretch__tempo
			sample_beats = track.num_beats

			stretch_type = track.stretch__type

			dur_sec = sampleref_obj.get_dur_sec()
			if dur_sec: samplemul = sample_beats/(dur_sec*2)
			else: samplemul = sample_tempo/120

			for region in track.regions:

				offsamp = 0
				if sampleref_obj is not None:
					if sampleref_obj.found:
						samp_hz = sampleref_obj.get_hz()
						if samp_hz: offsamp = region.offset/(samp_hz if samp_hz else 44100)

				pls = []

				if stretch_type == 1:

					offset = (offsamp*samplemul)*2

					if auto_basenotes and track.flags:
						ppq_beats = sample_beats*ppq
						if 1 in track.flags:
							for start, end, cur_root in rootnote_auto.iterd(region.start, region.end):
								placement_obj = track_obj.placements.add_audio()
								time_obj = placement_obj.time
								time_obj.set_startend(start, end)
								time_obj.set_loop_data((offset*ppq)+((start-region.start)%ppq_beats), 0, ppq_beats)
								sp_obj = placement_obj.sample
								sp_obj.sampleref = sample_path
								sp_obj.stretch.timing.set__beats(sample_beats)
								sp_obj.stretch.preserve_pitch = True
								if cur_root != 127:
									notetrack = calc_root(cur_root, track_root_note)
									sp_obj.pitch = notetrack+region.pitch
								else:
									sp_obj.usemasterpitch = False
									sp_obj.pitch = region.pitch
								pls.append(placement_obj)
						else:
							placement_obj = track_obj.placements.add_audio()
							time_obj = placement_obj.time
							time_obj.set_startend(region.start, region.end)
							time_obj.set_loop_data(offset, 0, ppq_beats)
							sp_obj = placement_obj.sample
							sp_obj.sampleref = sample_path
							sp_obj.stretch.timing.set__beats(sample_beats)
							sp_obj.stretch.preserve_pitch = True
							sp_obj.usemasterpitch = False
							sp_obj.pitch = region.pitch
							pls.append(placement_obj)

					else:
						placement_obj = track_obj.placements.add_audio()
						time_obj = placement_obj.time
						time_obj.set_startend(region.start, region.end)
						time_obj.set_loop_data(offset*ppq, 0, sample_beats*ppq)
						sp_obj = placement_obj.sample
						sp_obj.sampleref = sample_path
						sp_obj.stretch.timing.set__beats(sample_beats)
						sp_obj.stretch.preserve_pitch = True

						if songroot != 127 and 1 in track.flags:
							notetrack = calc_root(project_obj.root_note, track_root_note)
							sp_obj.pitch = notetrack+region.pitch
						else:
							sp_obj.usemasterpitch = False
							sp_obj.pitch = region.pitch
						pls.append(placement_obj)

				if stretch_type == 4:
					placement_obj = track_obj.placements.add_audio()
					time_obj = placement_obj.time
					sp_obj = placement_obj.sample
					sp_obj.sampleref = sample_path
					time_obj.set_startend(region.start, region.end)
					time_obj.set_offset(offsamp*(ppq*2))
					sampmul = pow(2, region.pitch/-12)
					sp_obj.usemasterpitch = False
					sp_obj.stretch.timing.set__speed(sampmul)
					pls.append(placement_obj)

				if stretch_type == 3:
					placement_obj = track_obj.placements.add_audio()
					time_obj = placement_obj.time
					sp_obj = placement_obj.sample
					sp_obj.sampleref = sample_path
					time_obj.set_startend(region.start, region.end)
					sp_obj.usemasterpitch = False
					if 2 not in track.flags:
						sp_obj.stretch.timing.set__speed(pow(2, region.pitch/-12))
						time_obj.set_offset(offsamp*(ppq*2))
					else:
						sp_obj.stretch.timing.set__speed(sample_tempo/120)
						time_obj.set_offset(offsamp*(ppq*2)*sample_tempo/120)
					sp_obj.stretch.preserve_pitch = True

				for p in pls:
					p.visual.name = track.name
					p.visual.color.set_int(color)
					p.visual.color.fx_allowed = ['saturate', 'brighter']

				for env in region.envs:
					if len(env.points)==1 and env.type == 0:
						for p in pls: placement_obj.sample.vol = env.points[0][1]
					if len(env.points)==1 and env.type == 1:
						for p in pls: placement_obj.sample.pan = env.points[0][1]

					else:
						autoloc = None
						if env.type == 0: autoloc = ['track', cvpj_trackid, 'vol']
						if env.type == 1: autoloc = ['track', cvpj_trackid, 'pan']
						if env.type > 1: 
							autoloc = ['send', 'send_%i_%i' % (tracknum, env.type-2), 'amount']
							if env.type-2 not in used_sends: used_sends.append(env.type-2)
						if autoloc:
							autopl_obj = convproj_obj.automation.add_pl_points(autoloc, 'float')
							autopl_obj.time.set_startend(region.start, region.end)
							for point in env.points:
								tension = 0
								if point[0] == 2: tension = 1
								if point[0] == -2: tension = -1
								autopl_obj.data.points__add_normal(point[0], point[1], tension, None)
							auto_obj = convproj_obj.automation.get_opt(autoloc)
							if auto_obj is not None: 
								if env.type == 0: auto_obj.defualt_val = track.vol
								if env.type == 1: auto_obj.defualt_val = track.pan

			track_obj.placements.pl_audio.sort()
			if stretch_type not in [1, 3]:
				track_obj.placements.pl_audio.remove_overlaps()

		send_fx = {}
		for fx in project_obj.fx_dx:
			if fx.fx_num not in send_fx: send_fx[fx.fx_num] = []
			if fx.fx_num not in used_sends: used_sends.append(fx.fx_num)
			send_fx[fx.fx_num].append(fx)

		for x in used_sends:
			returnid = 'return__'+str(x)
			track_obj = convproj_obj.track_master.fx__return__add(returnid)
			track_obj.visual.name = 'FX '+str(x+1)
			if x in send_fx:
				for fx in send_fx[x]:
					plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'directx', None)
					plugin_obj.role = 'fx'
					track_obj.plugin_autoplace(plugin_obj, pluginid)
					external_info = plugin_obj.external_info
					external_info.name = fx.name
					preset_obj = fx.preset_obj
					extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
					extmanu_obj.dx__replace_data(preset_obj.id, preset_obj.data)

		convproj_obj.automation.set_persist_all(False)

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.author = project_obj.artist
		convproj_obj.metadata.original_author = project_obj.createdBy
		convproj_obj.metadata.comment_text = project_obj.comments
		convproj_obj.metadata.copyright = project_obj.copyright
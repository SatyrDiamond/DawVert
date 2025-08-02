# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET
import plugins
from objects import globalstore
from objects import colors
from objects.data_bytes import bytewriter
from objects.data_bytes import bytereader

def do_plugchunk(fx_slot, fxid, chunkdata, convproj_obj, plugslots):
	try:
		if chunkdata:
			if len(chunkdata)>12:
				datasize = len(fx_slot.bindata)-8
				instate = bytereader.bytereader(fx_slot.bindata)
				outstate = bytewriter.bytewriter()
				unknown = instate.uint32()
				outstate.uint32_b(instate.uint32())
				outstate.uint32_b(instate.uint32())
				maintype = instate.uint32()
				if maintype == 1182286443: #kBxF
					outstate.uint32_b(maintype)
					for _ in range(4): outstate.uint32_b(instate.uint32())
					outstate.raw(instate.raw(128))
					while instate.remaining():
						outstate.uint32_b(instate.uint32())
						outstate.uint32_b(instate.uint32())
						cctype = instate.uint32()
						if cctype == 1182286699: # kCxF
							outstate.uint32_b(cctype)
							outstate.uint32_b(instate.uint32())
							outstate.uint32_b(instate.uint32())
							outstate.uint32_b(instate.uint32())
							numparams = instate.uint32()
							outstate.uint32_b(numparams)
							outstate.raw(instate.raw(28))
							for _ in range(numparams): outstate.float_b(instate.float())
						else:
							break
				plugin_obj = convproj_obj.plugin__add(fxid, 'external', 'vst2', None)
				extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, fxid)
				extmanu_obj.vst2__import_presetdata('raw', outstate.getvalue(), None)
				plugin_obj.role = 'fx'
				plugslots.slots_audio.append(fxid)
	except:
		pass


class input_kristal(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'kristal'
	
	def get_name(self):
		return 'KRISTAL Audio Engine'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def do_audiopart(self, convproj_obj, placement_obj, part, minpos, bpm):
		tempomul = 120/bpm

		time_obj = placement_obj.time
		time_obj.set_posdur(part.position-minpos, part.duration)
		time_obj.set_offset(part.offset)
		placement_obj.visual.name = part.name
		placement_obj.visual.color.set_int(part.color[0:3])
		placement_obj.fade_in.set_dur((part.fade_in/44100)*tempomul, 'seconds')
		placement_obj.fade_out.set_dur((part.fade_out/44100)*tempomul, 'seconds')

		sp_obj = placement_obj.sample
		sp_obj.vol = part.volume

		if part.path:
			if part.path[0] == 'CPath':
				filepath = part.path[1].path
				sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, 'win')
				sp_obj.sampleref = filepath

		stretch_obj = sp_obj.stretch
		stretch_obj.timing.set__real_rate(bpm, 1)
		stretch_obj.preserve_pitch = True

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_past import kristal as proj_kristal
		from objects import audio_data

		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.audio_nested = True

		project_obj = proj_kristal.kristal_song()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		tracknum = 0
		tracknums = {}

		bpmmul = 1
		bpm = 120

		if project_obj.globalinserts:
			for icid, inpart in project_obj.globalinserts:
				if icid == 'CTransport':
					convproj_obj.timesig = [inpart.timesig_num, inpart.timesig_denom]
				if icid == 'CMetronome':
					convproj_obj.params.add('bpm', inpart.bpm, 'float')
					bpm = inpart.bpm
					bpmmul = 120/inpart.bpm

		convproj_obj.set_timings((44100/2)*bpmmul)

		if project_obj.audio_input:
			inum, indata = project_obj.audio_input
			for inp in indata:
				if inp.type == b'Plug' and inp.name == 'Waver.cin':
					if inp.chunkdata:
						if inp.chunkdata[0] == 'CCrystalInput':
							for ch_track, ch_data in inp.chunkdata[1].tracks:
								if ch_track=='CAudioTrack':
									cvpj_trackid = 'track_'+str(tracknum)
									track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
									tracknums[tracknum] = track_obj
									track_obj.visual.name = ch_data.name
									self.audio_channels = 2 if 0 in ch_data.flags else 1
									#if 8 in ch_data.flags:
									#	track_obj.armed.on = True
									#	track_obj.armed.in_audio = True
										
									for cid, part in ch_data.parts:
										if cid == 'CAudioPart': 
											placement_obj = track_obj.placements.add_nested_audio()
											time_obj = placement_obj.time
											time_obj.set_posdur(part.position, part.duration)
											placement_obj.visual.name = part.name
											placement_obj.visual.color.set_int(part.color[0:3])
											placement_obj = placement_obj.add()
											placement_obj.muted = 0 in part.flags
											placement_obj.locked = 1 in part.flags
											self.do_audiopart(convproj_obj, placement_obj, part, part.position, bpm)
										if cid == 'CFolderPart': 
											placement_obj = track_obj.placements.add_nested_audio()
											time_obj = placement_obj.time
											time_obj.set_posdur(part.position, part.duration)
											time_obj.set_offset(part.offset)
											placement_obj.visual.name = part.name
											placement_obj.visual.color.set_int(part.color[0:3])
											placement_obj.muted = 0 in part.flags
											placement_obj.locked = 1 in part.flags
											for icid, inpart in part.parts:
												if icid == 'CAudioPart': 
													npa_obj = placement_obj.add()
													self.do_audiopart(convproj_obj, npa_obj, inpart, part.position, bpm)

									tracknum += 1

		if project_obj.infodata:
			for n, t in enumerate(project_obj.infodata.data):
				if n == 0: convproj_obj.metadata.name = t
				if n == 1: convproj_obj.metadata.author = t
				if n == 2: convproj_obj.metadata.comment_text = t+'\n\n'
				if n == 3: convproj_obj.metadata.comment_text += t

		channum = 0
		if project_obj.globalinserts:
			for icid, inpart in project_obj.globalinserts:
				if icid == 'CMixerChannel':
					if channum in tracknums:
						track_obj = tracknums[channum]
						track_obj.params.add('enabled', not bool(inpart.muted), 'bool')
						track_obj.params.add('solo', bool(inpart.solo), 'bool')
						track_obj.params.add('vol', inpart.vol, 'float')
						track_obj.params.add('pan', (inpart.pan-0.5)*2, 'float')
					channum += 1
				if icid == 'CMetronome':
					convproj_obj.params.add('bpm', inpart.bpm, 'float')

		if project_obj.mixer:
			for num, data in enumerate(project_obj.mixer[1]):
				if num in tracknums:
					track_obj = tracknums[num]
					fx_eq, fx_slots = data
					for fx_num, fx_slot in enumerate(fx_slots):
						fxid = 'track_'+str(tracknum)+'_fx_'+str(fx_num)
						chunkdata = fx_slot.bindata
						do_plugchunk(fx_slot, fxid, chunkdata, convproj_obj, track_obj.plugslots)
					fxid = 'track_'+str(tracknum)+'_fx_eq'
					do_plugchunk(fx_eq, fxid, chunkdata, convproj_obj, track_obj.plugslots)

		if project_obj.master:
			for fx_num, fx_slot in enumerate(project_obj.master[1]):
				fxid = 'master_fx_'+str(fx_num)
				chunkdata = fx_slot.bindata
				do_plugchunk(fx_slot, fxid, chunkdata, convproj_obj, convproj_obj.track_master.plugslots)
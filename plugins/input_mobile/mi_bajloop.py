# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
from objects.convproj import fileref
import os

class input_fl_mobile_old(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'bajloop'
	
	def get_name(self):
		return "Bhaji's Loops"
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		pass

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_mobile import bajloops
		from objects import audio_data

		project_obj = bajloops.bajloop_file()

		convproj_obj.type = 'mi'

		convproj_obj.set_timings(8)

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		convproj_obj.do_actions.append('do_addloop')

		convproj_obj.metadata.name = project_obj.name
		convproj_obj.metadata.comment_text = project_obj.info

		samplefolder = dawvert_intent.path_samples['extracted']
		
		for num, samp in enumerate(project_obj.samples):
			samplerefid = str(num)
			wave_path = samplefolder+samplerefid+'.wav'
			audio_obj = audio_data.audio_obj()
			audio_obj.channels = samp.channels
			audio_obj.rate = samp.freq
			audio_obj.set_codec('int16' if samp.bits==16 else 'uint8')
			audio_obj.pcm_from_bytes(samp.data)
			sampleref_obj = convproj_obj.sampleref__add(samplerefid, wave_path, None)
			sampleref_obj.set_fileformat('wav')
			sampleref_obj.visual.name = samp.name
			audio_obj.to_sampleref_obj(sampleref_obj)
			audio_obj.to_file_wav(wave_path)

		for num, binst in enumerate(project_obj.insts):
			samplenum = int(binst.sample_num)-1
			samp = project_obj.samples[samplenum]
			instid = str(num+1)
			inst_obj = convproj_obj.instrument__add(instid)
			inst_obj.datavals.add('middlenote', binst.basenote)
			inst_obj.params.add('vol', binst.vol/64, 'float')
			inst_obj.params.add('pan', -(binst.pan-32)/32, 'float')
			visual_obj = inst_obj.visual
			visual_obj.color.set_int(binst.color.tolist())
			visual_obj.name = binst.name
			plugin_obj, pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'single')
			plugin_obj.role = 'synth'
			sp_obj = plugin_obj.samplepart_add('sample')
			sp_obj.from_sampleref(convproj_obj, str(samplenum))
			if samp.loop_2:
				sp_obj.loop_start = int(samp.loop_1)
				sp_obj.loop_end = int(samp.loop_1)+int(samp.loop_2)
				sp_obj.loop_active = True
			inst_obj.plugslots.set_synth(pluginid)

		patsize = {}
		for num, bpattern in enumerate(project_obj.patterns):
			if len(bpattern.events):
				nle_obj = convproj_obj.notelistindex__add(str(num+1))
				visual_obj = nle_obj.visual
				visual_obj.name = bpattern.name
				visual_obj.color.set_int(bpattern.color.tolist())
				cvpj_notelist = nle_obj.notelist
				for event in bpattern.events:
					cvpj_notelist.add_m(str(event[3]), event[0], event[1]-event[0], int(event[2])-60, event[4]/127 if event[4]<128 else 1, None)
				nl_dur = cvpj_notelist.get_dur()
				patsize[num+1] = (nl_dur/32).__ceil__()

		playlist_stor = {}
		for num in range(8):
			playlist_stor[num] = {}

		for pos, data in enumerate(project_obj.placements):
			for num, patn in enumerate(data):
				if patn: 
					playlist_stor[num][pos] = int(patn)

		for num in range(8):
			playlist_obj = convproj_obj.playlist__add(num, 1, True)
			for pos, pnum in playlist_stor[num].items():
				s = (patsize[pnum] if pnum in patsize else 1)
				placement_obj = playlist_obj.placements.add_notes_indexed()
				placement_obj.fromindex = str(pnum)
				time_obj = placement_obj.time
				time_obj.set_posdur(pos*32, 32*s)
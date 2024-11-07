# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
import os
import plugins

@dataclass
class notestate:
	__slots__ = ['active','key','start','end','vol_env','pan_env','porta']

	active: int
	key: int
	start: int
	end: int
	vol_env: list
	pan_env: list
	porta: list

	@classmethod
	def blank(cls):
		return cls(0,0,0,0,[],[],[])

def decode_tempo(in_val): return (1/((in_val/40)/2+0.5))*120

def decode_tempopl(in_val, globaltempo): return ((((in_val-30)*-6)+60)/120)*globaltempo

class input_soundclub2(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'soundclub2'
	def get_name(self): return 'Sound Club 2'
	def get_priority(self): return 0
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['sn2']
		in_dict['track_lanes'] = True
		in_dict['audio_filetypes'] = ['wav']
		in_dict['plugin_included'] = ['universal:sampler:single']
		in_dict['projtype'] = 'rs'
	def supported_autodetect(self): return True
	def detect(self, input_file):
		bytestream = open(input_file, 'rb')
		bytestream.seek(0)
		bytesdata = bytestream.read(3)
		if bytesdata == b'SN2': return True
		else: return False
	def parse(self, convproj_obj, input_file, dv_config):
		from objects import audio_data
		from objects.file_proj import proj_soundclub2
		
		convproj_obj.type = 'rs'
		convproj_obj.set_timings(4, False)

		project_obj = proj_soundclub2.sn2_song()
		if not project_obj.load_from_file(input_file): exit()

		samplefolder = dv_config.path_samples_extracted
		
		for instnum, sn2_inst_obj in enumerate(project_obj.instruments):
			cvpj_instid = 'sn2_'+str(instnum)

			track_obj = convproj_obj.track__add(cvpj_instid, 'instrument', 1, False)
			track_obj.visual.name = sn2_inst_obj.name
			track_obj.params.add('vol', 0.3, 'float')

			if sn2_inst_obj.type == 0:
				wave_path = samplefolder + cvpj_instid + '.wav'

				audio_obj = audio_data.audio_obj()
				audio_obj.rate = sn2_inst_obj.freq
				audio_obj.set_codec('uint8')
				audio_obj.pcm_from_bytes(sn2_inst_obj.data)
				if sn2_inst_obj.loopstart != -1: audio_obj.loop = [sn2_inst_obj.loopstart, sn2_inst_obj.samplesize]
				audio_obj.to_file_wav(wave_path)

				plugin_obj, track_obj.inst_pluginid, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler__genid(wave_path, None)

				plugin_obj.env_asdr_add('vol', 0, 0, 0, 0, 1, 0, 1)
				sp_obj.point_value_type = "samples"
				sp_obj.start = 0
				sp_obj.end = len(sn2_inst_obj.data)
				sp_obj.length = len(sn2_inst_obj.data)
				sp_obj.loop_end = sn2_inst_obj.samplesize
				if sn2_inst_obj.loopstart != -1: 
					sp_obj.loop_start = sn2_inst_obj.loopstart
					sp_obj.loop_active = True
					
		scenedurs = []

		for patnum, sn2_pat_obj in enumerate(project_obj.patterns):
			sceneid = str(patnum)
			convproj_obj.scene__add(sceneid)

			scenedur = 0
			repeatnotes = {}

			for patvoice_obj in sn2_pat_obj.voices:
				if patvoice_obj.instid not in repeatnotes: repeatnotes[patvoice_obj.instid] = 1
				else: repeatnotes[patvoice_obj.instid] += 1
				laneid = str(repeatnotes[patvoice_obj.instid])
				cvpj_instid = 'sn2_'+str(patvoice_obj.instid)
				trscene_obj = convproj_obj.track__add_scene(cvpj_instid, sceneid, laneid)
				placement_obj = trscene_obj.add_notes()
				placement_obj.visual.name = sn2_pat_obj.name

				t_active_notes = [notestate.blank() for x in range(84)]

				n_curvol = 1
				n_curpan = 0
				curpos = 0
				for event in patvoice_obj.events:
					curpos += event.len
					if event.type == 17: 
						scnote_obj = t_active_notes[event.value]
						scnote_obj.active = 1
						scnote_obj.key = event.value
						scnote_obj.start = curpos
						scnote_obj.end = 0

					elif event.type == 19: 
						scnote_obj.end = curpos-scnote_obj.start
						scnote_obj = t_active_notes[event.value]
						if scnote_obj.active:
							placement_obj.notelist.add_r(scnote_obj.start, scnote_obj.end, scnote_obj.key-36, n_curvol, {})
							for s_pos, s_len, s_key in scnote_obj.porta: placement_obj.notelist.last_add_slide(s_pos, s_len, s_key-36, n_curvol, None)

					elif event.type == 20: n_curvol = event.value/31
					elif event.type == 21: n_curpan = (event.value-15)/-15
					elif event.type == 54: 
						t_active_notes[event.p_key] = t_active_notes[event.value]
						t_active_notes[event.p_key].porta.append([curpos-t_active_notes[event.value].start, event.p_len, event.p_key])
						t_active_notes[event.value] = notestate.blank() 

				placement_obj.notelist.notemod_conv()

				scenedur = max(scenedur, curpos)

				placement_obj.visual.name = sn2_pat_obj.name

				placement_obj.time.set_block_dur(curpos, 32)

			scenedurs.append(scenedur)

		globaltempo = decode_tempo(project_obj.tempo)

		curpos = 0
		for pat_num in project_obj.sequence:
			size = scenedurs[pat_num]
			scenepl_obj = convproj_obj.scene__add_pl()
			scenepl_obj.position = curpos
			scenepl_obj.duration = size
			scenepl_obj.id = str(pat_num)

			pat_tempos = project_obj.patterns[pat_num].tempos

			autopl_obj = convproj_obj.automation.add_pl_points(['main','bpm'], 'float')
			autopl_obj.time.set_posdur(curpos, size)
			for pat_tempo in pat_tempos:
				autopoint_obj = autopl_obj.data.add_point()
				autopoint_obj.pos = pat_tempo[0]
				autopoint_obj.value = decode_tempopl(pat_tempo[1], globaltempo)

			curpos += size

		outtempo = globaltempo

		if project_obj.sequence:
			vstart = project_obj.patterns[project_obj.sequence[0]].tempos 
			if vstart: 
				startpoint = vstart[0]
				if startpoint[0] == 0: outtempo = decode_tempopl(startpoint[1], globaltempo)

		convproj_obj.timesig = [project_obj.ts_num, project_obj.ts_denum]
		convproj_obj.params.add('bpm', outtempo, 'float')
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.exceptions import ProjectFileParserException
from objects import globalstore
from functions import data_bytes
from objects.data_bytes import bytereader
import plugins
import json
import os
import struct
import rpp

nativeids = {
	1919247213: 'reacomp',
	1919247468: 'readelay',
	1919247729: 'reaeq',
	1919247986: 'reafir',
	1919248244: 'reagate',
	1919708532: 'realimit',
	1919250531: 'reapitch',
	1919252066: 'reaverb',
	1920361016: 'reaverbate',
	1919252579: 'reaxcomp',
	1920167789: 'reasamplomatic'
}

def reaper_color_to_cvpj_color(i_color, isreversed): 
	bytecolors = struct.pack('i', i_color)
	if bytecolors[3]:
		if isreversed == True: return [bytecolors[0],bytecolors[1],bytecolors[2]]
		else: return [bytecolors[2],bytecolors[1],bytecolors[0]]
	else:
		return [60, 60, 60]

class midi_notes():
	def __init__(self): 
		self.active_notes = [[[] for x in range(127)] for x in range(16)]
		self.midipos = 0
		pass

	def do_note(self, tracksource_var):
		self.midipos += int(tracksource_var[1])
		midicmd, midich = data_bytes.splitbyte(int(tracksource_var[2],16))
		midikey = int(tracksource_var[3],16)
		midivel = int(tracksource_var[4],16)
		if midicmd == 9: self.active_notes[midich][midikey].append([self.midipos, None, midivel])
		if midicmd == 8: self.active_notes[midich][midikey][-1][1] = self.midipos

	def do_output(self, cvpj_notelist, ppq):
		for c_mid_ch in range(16):
			for c_mid_key in range(127):
				if self.active_notes[c_mid_ch][c_mid_key] != []:
					for notedurpos in self.active_notes[c_mid_ch][c_mid_key]:
						if notedurpos[1] != None:
							cvpj_notelist.add_r(
								notedurpos[0]/(ppq), 
								(notedurpos[1]-notedurpos[0])/(ppq), 
								c_mid_key-60, 
								notedurpos[2]/127, 
								{'channel': c_mid_ch}
								)
							cvpj_notelist.time_ppq = 1
							cvpj_notelist.time_float = True
		cvpj_notelist.sort()
		#print(cvpj_notelist.data[:])

def do_auto(convproj_obj, rpp_autodata, autoloc, instant, paramtype, invert): 
	isbool = paramtype=='bool'
	if rpp_autodata.used:
		for point in rpp_autodata.points:
			val = point[1] if not invert else 1-point[1]
			if isbool: val = bool(val)
			convproj_obj.automation.add_autopoint_real(autoloc, paramtype, point[0], val, 'normal' if not instant else 'instant')

def do_samplepart_loop(samplerj, sp_obj, sampleref_obj):
	dur = sampleref_obj.dur_samples
	dur_sec = sampleref_obj.dur_sec
	hz = sampleref_obj.hz

	loop_on = samplerj['loop_on'] if 'loop_on' in samplerj else 0
	start = samplerj['start'] if 'start' in samplerj else 0
	end = samplerj['end'] if 'end' in samplerj else 1
	loop_start = samplerj['loop_start'] if 'loop_start' in samplerj else 0
	sp_obj.start = start*dur
	sp_obj.end = end*dur
	sp_obj.loop_active = bool(loop_on)
	sp_obj.loop_start = loop_start*30*hz
	sp_obj.loop_end = sp_obj.end

def do_samplepart_adsr(samplerj, plugin_obj, sampleref_obj, asdrname):
	dur_sec = sampleref_obj.dur_sec
	loop_on = samplerj['loop_on'] if 'loop_on' in samplerj else 0
	env_attack = samplerj['env_attack'] if 'env_attack' in samplerj else 0
	env_decay = samplerj['env_decay'] if 'env_decay' in samplerj else 0
	env_sustain = samplerj['env_sustain'] if 'env_sustain' in samplerj else 1
	env_release = samplerj['env_release'] if 'env_release' in samplerj else 0
	if not loop_on: plugin_obj.env_asdr_add(asdrname, 0, env_attack*dur_sec, 0, env_decay*15, env_sustain, env_release*dur_sec, 1)
	else: plugin_obj.env_asdr_add(asdrname, 0, env_attack*2, 0, env_decay*15, env_sustain, env_release*2, 1)

def do_fade(fade_data, fadevals, tempomul): 
	fade_data.set_dur(fadevals['fade_time'], 'seconds')
	if fadevals['fade_type'] == 3: fade_data.slope = 1
	if fadevals['fade_type'] == 1: fade_data.slope = 0.5
	if fadevals['fade_type'] == 0: fade_data.slope = 0
	if fadevals['fade_type'] == 2: fade_data.slope = -0.5
	if fadevals['fade_type'] == 4: fade_data.slope = -1

class input_reaper(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'reaper'
	def get_name(self): return 'REAPER'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['rpp']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv']
		in_dict['audio_stretch'] = ['rate']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_ext'] = ['vst2', 'vst3', 'clap']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:sampler:multi']
		in_dict['fxtype'] = 'route'
		in_dict['projtype'] = 'r'
		
	def parse(self, convproj_obj, input_file, dv_config):
		from objects.file_proj import proj_reaper
		from functions_plugin_ext import plugin_vst2
		from functions_plugin_ext import plugin_vst3
		from functions_plugin_ext import plugin_clap

		bytestream = open(input_file, 'r')
		try:
			rpp_data = rpp.load(bytestream)
		except UnicodeDecodeError:
			raise ProjectFileParserException('reaper: File is not text')

		project_obj = proj_reaper.rpp_song()
		if not project_obj.load_from_file(input_file): exit()

		globalstore.dataset.load('reaper', './data_main/dataset/reaper.dset')
		globalstore.datadef.load('reaper', './data_main/datadef/reaper.ddef')
		datadef_obj = globalstore.datadef.get('reaper')

		convproj_obj.fxtype = 'route'
		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		rpp_project = project_obj.project

		bpm = rpp_project.tempo['tempo']
		convproj_obj.params.add('bpm', bpm, 'float')
		tempomul = bpm/120
		convproj_obj.timesig = [int(rpp_project.tempo['num']), int(rpp_project.tempo['denom'])]

		trackdata = []

		used_trackids = []

		for tracknum, rpp_track in enumerate(rpp_project.tracks):
			cvpj_trackid = rpp_track.trackid.get()
			used_trackids.append(cvpj_trackid)

			if not cvpj_trackid or cvpj_trackid in used_trackids: cvpj_trackid = 'track'+str(tracknum)

			trackroute = [rpp_track.mainsend['tracknum'], rpp_track.auxrecv]

			track_obj = convproj_obj.track__add(cvpj_trackid, 'hybrid', 1, False)
			track_obj.visual.name = rpp_track.name.get()

			track_obj.visual.color.set_int(reaper_color_to_cvpj_color(rpp_track.peakcol.get(), True))
			track_obj.params.add('vol', rpp_track.volpan['vol'], 'float')
			track_obj.params.add('pan', rpp_track.volpan['pan'], 'float')

			track_obj.armed.on = bool(rpp_track.rec['armed'])
			track_obj.armed.in_keys = bool(rpp_track.rec['armed'])
			track_obj.armed.in_audio = bool(rpp_track.rec['armed'])
			
			fxids = []

			samplers = []

			if rpp_track.fxchain != None:
				rpp_plugins = rpp_track.fxchain.plugins
				for n, rpp_plugin in enumerate(rpp_plugins):
					rpp_extplug = rpp_plugin.plugin
					fxid = os.urandom(15).hex()
					fxids.append(fxid)

					if rpp_plugin.type == 'VST':
						if rpp_extplug.vst3_uuid == None:
							fourid = rpp_extplug.vst_fourid

							if fourid == 1920167789:
								if datadef_obj:
									dfdict = datadef_obj.parse('reasamplomatic', rpp_extplug.data_chunk)
									if dfdict: 
										filenames = []
										if 'filename' in dfdict: filenames = dfdict['filename'].split('>0 YOU NEED A NEWER REASAMPLOMATIC, HIT LEAVE OFFLINE!')[0].split('|')
										samplers.append([filenames, dfdict])

							else:
								plugin_obj = convproj_obj.plugin__add(fxid, 'external', 'vst2', None)
								plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])

								pluginfo_obj = globalstore.extplug.get('vst2', 'id', fourid, None, [64, 32])

								try:
									vstdataconreader = bytereader.bytereader()
									vstdataconreader.load_raw(rpp_extplug.data_con)
									vstdataconreader.skip(4) # id
									vstdataconreader.skip(4) # unknown 2
									num_inchannels = vstdataconreader.uint32()
									vstdataconreader.skip(4) # 1
									aud_in_chan = [vstdataconreader.flags64() for x in range(num_inchannels)]
									aud_out_chan = [vstdataconreader.flags64() for x in range(pluginfo_obj.audio_num_outputs)]
									chunk_size = vstdataconreader.uint32() # chunk size
									uses_chunk = vstdataconreader.uint32() # uses chunk
									programnum = vstdataconreader.uint16() # program
									vstdataconreader.skip(1) # 16
									vstdataconreader.skip(1) # 16

									plugin_obj.clear_prog_keep(programnum)
									if uses_chunk:
										plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, fourid, 'chunk', rpp_extplug.data_chunk, None)
									else:
										numparams = (len(rpp_extplug.data_chunk)//4)-2
										vstparams = struct.unpack('f'*numparams, rpp_extplug.data_chunk[8:])
										plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, fourid, 'param', None, numparams)
										for n, v in enumerate(vstparams):
											param_obj = plugin_obj.params.add('ext_param_'+str(n), v, 'float')
								except:
									pass

								for parmenv in rpp_plugin.parmenv:
									if parmenv.is_param:
										do_auto(convproj_obj, parmenv, ['plugin', fxid, 'ext_param_'+str(parmenv.param_id)], False, 'float', False)

								if fourid == 1919118692: track_obj.fxslots_notes.append(fxid)
								else: track_obj.plugin_autoplace(plugin_obj, fxid)

						else:
							plugin_obj = convproj_obj.plugin__add(fxid, 'external', 'vst3', None)
							plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])
							if len(rpp_extplug.data_chunk)>8:
								try:
									preset_data = bytereader.bytereader()
									preset_data.load_raw(rpp_extplug.data_chunk)
									chunk_size = preset_data.int32()
									unk = preset_data.int32()
									chunk = preset_data.raw(chunk_size)

									pluginfo_obj = plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, rpp_extplug.vst3_uuid, chunk)
									track_obj.plugin_autoplace(plugin_obj, fxid)
								except:
									pass

							for parmenv in rpp_plugin.parmenv:
								if parmenv.is_param:
									do_auto(convproj_obj, parmenv, ['plugin', fxid, 'ext_param_'+str(parmenv.param_id)], False, 'float', False)

					if rpp_plugin.type == 'CLAP':
						plugin_obj = convproj_obj.plugin__add(fxid, 'external', 'clap', None)
						plugin_clap.replace_data(convproj_obj, plugin_obj, 'id', None, rpp_extplug.clap_id, rpp_extplug.data_chunk)
						plugin_obj.visual.name = rpp_extplug.clap_name
						track_obj.plugin_autoplace(plugin_obj, fxid)

						for parmenv in rpp_plugin.parmenv:
							if parmenv.is_param:
								do_auto(convproj_obj, parmenv, ['plugin', fxid, 'ext_param_'+str(parmenv.param_id)], False, 'float', False)

					if rpp_plugin.type == 'JS':
						plugin_obj = convproj_obj.plugin__add(fxid, 'external', 'jesusonic', rpp_extplug.js_id)
						plugin_obj.role = 'effect'
						plugin_obj.fxdata_add(not rpp_plugin.bypass['bypass'], rpp_plugin.wet['wet'])
						for n, v in enumerate(rpp_extplug.data):
							if v != '-': plugin_obj.datavals.add(str(n), v)
						track_obj.fxslots_audio.append(fxid)

			if not track_obj.inst_pluginid and samplers:
				outsamplers = []
				for f, x in samplers:
					for o in f:
						outsamplers.append([o, x])

				sampler_id = cvpj_trackid+'_sampler'

				if len(outsamplers) == 1:
					filename, samplerj = outsamplers[0]
					track_obj.inst_pluginid = sampler_id
					plugin_obj, sampleref_obj, sp_obj = convproj_obj.plugin__addspec__sampler(sampler_id, filename, 'win')
					do_samplepart_loop(samplerj, sp_obj, sampleref_obj)
					do_samplepart_adsr(samplerj, plugin_obj, sampleref_obj, 'vol')

				if len(outsamplers) > 1:
					plugin_obj, track_obj.inst_pluginid = convproj_obj.plugin__add__genid('universal', 'sampler', 'multi')
					plugin_obj.role = 'synth'

					key_start = 0
					key_end = 127
					key_middle = 60

					for n, d in enumerate(outsamplers):
						filename, samplerj = d
						sampmode = samplerj['mode'] if 'mode' in samplerj else 0

						sampleref_obj = convproj_obj.sampleref__add(filename, filename, None)

						if sampmode == 2:
							key_start = int((samplerj['key_start'] if 'key_start' in samplerj else 0)*127)
							key_end = int((samplerj['key_end'] if 'key_end' in samplerj else 1)*127)
							pitch_start = int((samplerj['pitch_start'] if 'pitch_start' in samplerj else 0)*160)-80
							pitch_start = -(60+(pitch_start-key_start))
							sp_obj = plugin_obj.sampleregion_add(key_start-60, key_end-60, pitch_start, None, samplepartid=cvpj_trackid+'_'+str(n))
							sp_obj.sampleref = filename
							do_samplepart_loop(samplerj, sp_obj, sampleref_obj)
							do_samplepart_adsr(samplerj, plugin_obj, sampleref_obj, 'vol')

			for rpp_trackitem in rpp_track.items:
				cvpj_placement_type = 'notes'

				cvpj_position = rpp_trackitem.position.get()
				cvpj_duration = rpp_trackitem.length.get()
				cvpj_offset = rpp_trackitem.soffs.get()
				cvpj_loop = rpp_trackitem.loop.get()
				cvpj_vol = rpp_trackitem.volpan['vol']
				cvpj_pan = rpp_trackitem.volpan['pan']
				cvpj_muted = rpp_trackitem.mute['mute']
				cvpj_color = reaper_color_to_cvpj_color(rpp_trackitem.color.get(), False) if rpp_trackitem.color.used else None
				cvpj_name = rpp_trackitem.name.get()

				cvpj_audio_rate = rpp_trackitem.playrate['rate']
				cvpj_audio_preserve_pitch = rpp_trackitem.playrate['preserve_pitch']
				cvpj_audio_pitch = rpp_trackitem.playrate['pitch']
				cvpj_audio_file = ''

				midi_notes_out = midi_notes()
				midi_ppq = 960

				samplemode = 0
				startpos = 0
				if rpp_trackitem.source != None:
					rpp_source = rpp_trackitem.source
					if rpp_source.type in ['MP3','FLAC','VORBIS','WAVE','WAVPACK']:
						cvpj_placement_type = 'audio'
						cvpj_audio_file = rpp_source.file.get()
					if rpp_source.type in ['MIDI']:
						midi_ppq = rpp_source.hasdata['ppq']
						for note in rpp_source.notes: midi_notes_out.do_note(note)
					if rpp_source.type == 'SECTION':
						samplemode = int(rpp_source.mode.get())
						startpos = float(rpp_source.startpos.get())
						if rpp_source.source != None:
							insource = rpp_source.source
							if insource != None:
								if insource.type in ['MP3','FLAC','VORBIS','WAVE','WAVPACK']:
									cvpj_placement_type = 'audio'
									cvpj_audio_file = insource.file.get()

				cvpj_offset_bpm = ((cvpj_offset)*8)*tempomul
				cvpj_end_bpm = ((midi_notes_out.midipos/midi_ppq)*4)

				if cvpj_placement_type == 'notes': 
					placement_obj = track_obj.placements.add_notes()
					if cvpj_name: placement_obj.visual.name = cvpj_name
					if cvpj_color: placement_obj.visual.color.set_float(cvpj_color)
					placement_obj.time.position_real = cvpj_position
					placement_obj.time.duration_real = cvpj_duration

					placement_obj.time.cut_type = 'loop'
					placement_obj.time.set_loop_data(cvpj_offset_bpm, 0, cvpj_end_bpm)

					midi_notes_out.do_output(placement_obj.notelist, midi_ppq)

				if cvpj_placement_type == 'audio': 
					placement_obj = track_obj.placements.add_audio()
					if cvpj_name: placement_obj.visual.name = cvpj_name
					if cvpj_color: placement_obj.visual.color.set_float(cvpj_color)
					placement_obj.time.position_real = cvpj_position
					placement_obj.time.duration_real = cvpj_duration
					placement_obj.sample.pan = cvpj_pan
					placement_obj.sample.pitch = cvpj_audio_pitch
					placement_obj.sample.vol = cvpj_vol

					do_fade(placement_obj.fade_in, rpp_trackitem.fadein, tempomul)
					do_fade(placement_obj.fade_out, rpp_trackitem.fadeout, tempomul)

					sampleref_obj = convproj_obj.sampleref__add(cvpj_audio_file, cvpj_audio_file, None)
					sampleref_obj.find_relative('projectfile')

					placement_obj.sample.sampleref = cvpj_audio_file
					if samplemode == 3: placement_obj.sample.reverse = True

					startoffset = (cvpj_offset_bpm/cvpj_audio_rate) + (startpos/cvpj_audio_rate)*8

					placement_obj.sample.stretch.set_rate_tempo(bpm, (1/cvpj_audio_rate)*tempomul, True)
					placement_obj.sample.stretch.preserve_pitch = cvpj_audio_preserve_pitch
					if not cvpj_loop:
						placement_obj.time.set_offset(startoffset)
					else:
						maxdur = ((sampleref_obj.dur_sec*8)/cvpj_audio_rate)*tempomul if sampleref_obj.dur_sec else cvpj_duration
						placement_obj.time.set_loop_data(startoffset, 0, maxdur)

			do_auto(convproj_obj, rpp_track.volenv2, ['track', cvpj_trackid, 'vol'], False, 'float', False)
			do_auto(convproj_obj, rpp_track.panenv2, ['track', cvpj_trackid, 'pan'], False, 'float', False)
			do_auto(convproj_obj, rpp_track.muteenv, ['track', cvpj_trackid, 'enabled'], True, 'bool', False)

			track_obj.placements.sort()
			convproj_obj.fx__route__add(cvpj_trackid)
			trackdata.append([cvpj_trackid, trackroute])

		for to_track, trackroute in trackdata:
			convproj_obj.trackroute[to_track].to_master_active = bool(trackroute[0])
			for rpp_auxrecv_obj in trackroute[1]:
				from_track = trackdata[rpp_auxrecv_obj['tracknum']][0]
				sends_obj = convproj_obj.trackroute[from_track]
				send_obj = sends_obj.add(to_track, None, rpp_auxrecv_obj['vol'])
				send_obj.params.add('pan', rpp_auxrecv_obj['pan'], 'float')

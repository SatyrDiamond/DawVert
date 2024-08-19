# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter
from functions import xtramath
from functions import data_values
from objects import globalstore
import base64
import bisect
import os
import logging

from functions import song_compat

from objects.convproj import sample_entry
from objects.convproj import automation
from objects.convproj import plugin
from objects.convproj import fileref
from objects.convproj import params
from objects.convproj import tracks
from objects.convproj import visual
from objects.convproj import sends
from objects.convproj import autoticks
from objects.convproj import autopoints
from objects.convproj import notelist
from objects.convproj import stretch

from functions_song import convert_r2m
from functions_song import convert_ri2mi
from functions_song import convert_ri2r
from functions_song import convert_rm2r
from functions_song import convert_m2r
from functions_song import convert_m2mi
from functions_song import convert_mi2m
from functions_song import convert_rm2m

from functions_song import convert_ms2rm
from functions_song import convert_rs2r

typelist = {}
typelist['r'] = 'Regular'
typelist['ri'] = 'RegularIndexed'
typelist['rm'] = 'RegularMultiple'
typelist['rs'] = 'RegularScened'
typelist['m'] = 'Multiple'
typelist['mi'] = 'MultipleIndexed'
typelist['ms'] = 'MultipleScened'

logger_project = logging.getLogger('project')

def autopath_encode(autol):
	return ';'.join(autol)

def vis_plugin(p_type, p_subtype):
	if p_type != None and p_subtype != None: return p_type+':'+p_subtype
	elif p_type != None and p_subtype == None: return p_type
	elif p_type == None and p_subtype == None: return 'None'

def autoloc_getname(autopath):
	if autopath[0] == 'main': autoname = 'Main'
	if autopath[0] == 'fxmixer': autoname = 'FX '+autopath[1]
	if autopath[0] == 'send': autoname = 'Send'
	if autopath[0] == 'plugin': autoname = autopath[1]
	if autopath[0] == 'track': autoname = 'Track'

plugin_id_counter = counter.counter(1000, 'plugin_')

class cvpj_timemarker:
	__slots__ = ['type','visual','position','duration']
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.type = ''
		self.position = 0
		self.duration = 0

class cvpj_fxchannel:
	def __init__(self):
		self.visual = visual.cvpj_visual()
		self.visual_ui = visual.cvpj_visual_ui()
		self.params = params.cvpj_paramset()
		self.fxslots_audio = []
		self.fxslots_mixer = []
		self.sends = sends.cvpj_sends()

class cvpj_scene:
	def __init__(self):
		self.visual = visual.cvpj_visual()

class cvpj_scenepl:
	def __init__(self):
		self.position = 0
		self.duration = 0
		self.id = ''

class cvpj_project:
	def __init__(self):
		self.type = None
		self.time_ppq = 96
		self.time_float = False
		self.track_data = {}
		self.track_order = []
		self.track_master = tracks.cvpj_track('master', self.time_ppq, self.time_float, False, False)
		self.track_returns = {}
		self.plugins = {}
		self.instruments = {}
		self.instruments_order = []
		self.sample_index = {}
		self.notelist_index = {}
		self.params = params.cvpj_paramset()
		self.fxrack = {}
		self.trackroute = {}
		self.playlist = {}
		self.timesig = [4,4]
		self.do_actions = []
		self.timemarkers = []
		self.metadata = visual.cvpj_metadata()
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
		self.loop_active = False
		self.loop_start = 0
		self.loop_end = 0
		self.start_pos = 0
		self.filerefs = {}
		self.samplerefs = {}
		self.window_data = {}
		self.automation = automation.cvpj_automation(self.time_ppq, self.time_float)
		self.groups = {}
		self.sample_folders = []
		self.scenes = {}
		self.scene_placements = []

		self._m2r_visual_playlist_first = False

	def add_scene(self, i_sceneid):
		scene_obj = cvpj_scene()
		#cpr_int('[project] Scene - '+str(i_sceneid), 'magenta')
		logger_project.info('Scene - '+str(i_sceneid))
		self.scenes[i_sceneid] = scene_obj
		return scene_obj

	def add_scenepl(self):
		scene_obj = cvpj_scenepl()
		self.scene_placements.append(scene_obj)
		return scene_obj

	def add_track_scene(self, i_track, i_sceneid, i_lane):
		if i_track in self.track_data: return self.track_data[i_track].add_scene(i_sceneid, i_lane)
		else: return None

	def sort_tracks(self):
		sortpos = {}
		for track_id, track_data in self.track_data.items():
			trackstart = track_data.placements.get_start()
			if trackstart not in sortpos: sortpos[trackstart] = []
			sortpos[trackstart].append([track_id])
		self.track_order = []
		for n in sorted(sortpos):
			for i in sortpos[n]: self.track_order += i
 
	def set_timings(self, time_ppq, time_float):
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.timesig_auto = autoticks.cvpj_autoticks(self.time_ppq, self.time_float, 'timesig')
		self.automation.time_ppq = self.time_ppq
		self.automation.time_float = self.time_float

	def change_timings(self, time_ppq, time_float):
		logger_project.info('Changing Timings from '+str(self.time_ppq)+':'+str(self.time_float)+' to '+str(time_ppq)+':'+str(time_float))
		for p in self.track_data: 
			track_data = self.track_data[p]
			track_data.change_timings(time_ppq, time_float)
			for e in track_data.notelist_index: 
				track_data.notelist_index[e].notelist.change_timings(time_ppq, time_float)
		for p in self.playlist: self.playlist[p].change_timings(time_ppq, time_float)
		for p in self.notelist_index: self.notelist_index[p].notelist.change_timings(time_ppq, time_float)
		for m in self.timemarkers: m.position = xtramath.change_timing(self.time_ppq, time_ppq, time_float, m.position)
		self.loop_start = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_start)
		self.loop_end = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.loop_end)
		self.start_pos = xtramath.change_timing(self.time_ppq, time_ppq, time_float, self.start_pos)
		self.timesig_auto.change_timings(time_ppq, time_float)
		self.time_ppq = time_ppq
		self.time_float = time_float
		self.automation.change_timings(time_ppq, time_float)

	def get_dur(self):
		duration_final = 0
		for p in self.track_data: 
			track_data = self.track_data[p]
			trk_dur = track_data.placements.get_dur()
			if duration_final < trk_dur: duration_final = trk_dur
		for p in self.playlist: 
			track_data = self.playlist[p]
			trk_dur = track_data.placements.get_dur()
			if duration_final < trk_dur: duration_final = trk_dur
		return duration_final

	def add_timemarker(self):
		timemarker_obj = cvpj_timemarker()
		self.timemarkers.append(timemarker_obj)
		return timemarker_obj

	def patlenlist_to_timemarker(self, PatternLengthList, pos_loop):
		prevtimesig = self.timesig
		timemarkers = []
		currentpos = 0
		blockcount = 0

		self.loop_end = sum(PatternLengthList)
		self.loop_active = True

		for PatternLengthPart in PatternLengthList:
			temptimesig = xtramath.get_timesig(PatternLengthPart, self.timesig[1])
			if prevtimesig != temptimesig: self.timesig_auto.add_point(currentpos, temptimesig)
			if pos_loop == blockcount: self.loop_start = currentpos
			prevtimesig = temptimesig
			currentpos += PatternLengthPart
			blockcount += 1

	def iter_automation(self):
		for autopath in self.automation:
			yield autopath.split(';'), self.automation[autopath]

	def add_fileref(self, fileid, filepath, os_type):
		if fileid not in self.filerefs: 
			self.filerefs[fileid] = fileref.cvpj_fileref()
			self.filerefs[fileid].set_path(os_type, filepath, 0)
			logger_project.info('FileRef - '+fileid+' - '+filepath)
		return self.filerefs[fileid]

	def add_sampleref(self, fileid, filepath, os_type):
		if fileid not in self.samplerefs: 
			self.samplerefs[fileid] = fileref.cvpj_sampleref()
			self.samplerefs[fileid].set_path(os_type, filepath)
			logger_project.info('SampleRef - '+fileid+' - '+filepath)
		return self.samplerefs[fileid]

	def iter_samplerefs(self):
		for sampleref_id, sampleref_obj in self.samplerefs.items():
			yield sampleref_id, sampleref_obj

	def add_fxchan(self, fxnum):
		logger_project.info('FX Channel - '+str(fxnum))
		if fxnum not in self.fxrack: self.fxrack[fxnum] = cvpj_fxchannel()
		return self.fxrack[fxnum]

	def fxchan_removeloopcrash(self):
		targalredy = {}
		crashfounds = []
		for fx_num, fxchannel_obj in self.fxrack.items():
			sendtargs = [x[0] for x in fxchannel_obj.sends.iter()]
			for target in sendtargs:
				if target not in targalredy: targalredy[target] = []
				targalredy[target].append(fx_num)
				iscrash = False
				if fx_num in targalredy:
					if target in targalredy[fx_num]: 
						crashfounds.append([target,fx_num])
		for target,fx_num in crashfounds:
			del self.fxrack[target].sends.data[fx_num]

	def add_trackroute(self, trackid):
		if trackid not in self.trackroute: 
			#cpr_int('[project] Track Route - '+str(trackid), 'yellow')
			logger_project.info('Track Route - '+str(trackid))
			self.trackroute[trackid] = sends.cvpj_sends()
		return self.trackroute[trackid]

	def add_notelistindex(self, i_id):
		self.notelist_index[i_id] = tracks.cvpj_nle(self.time_ppq, self.time_float)
		return self.notelist_index[i_id]

	def iter_notelistindex(self):
		for i_id in self.notelist_index: yield i_id, self.notelist_index[i_id]

	def add_sampleindex(self, i_id):
		self.sample_index[i_id] = sample_entry.cvpj_sample_entry()
		return self.sample_index[i_id]

	def iter_sampleindex(self):
		for i_id in self.sample_index: yield i_id, self.sample_index[i_id]

	def get_sampleref(self, fileid):
		if fileid in self.samplerefs: return True, self.samplerefs[fileid]
		else: return False, None

	def get_fileref(self, fileid):
		if fileid in self.filerefs: return True, self.filerefs[fileid]
		else: return False, None

	def add_timesig_lengthbeat(self, pat_len, notes_p_beat):
		self.timesig = xtramath.get_timesig(pat_len, notes_p_beat)

	def window_data_add(self, windowpath):
		windowpath = autopath_encode(windowpath)
		self.window_data[windowpath] = visual.cvpj_window_data()
		return self.window_data[windowpath]

	def window_data_get(self, windowpath):
		windowpath = autopath_encode(windowpath)
		if windowpath in self.window_data: return self.window_data[windowpath]
		else: return visual.cvpj_window_data()

	def add_playlist(self, idnum, uses_placements, is_indexed):
		if idnum not in self.playlist:
			logger_project.info('Playlist '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+str(idnum))
			self.playlist[idnum] = tracks.cvpj_track('hybrid', self.time_ppq, self.time_float, uses_placements, is_indexed)
		return self.playlist[idnum]

	def iter_playlist(self):
		for idnum, playlist_obj in self.playlist.items():
			yield idnum, playlist_obj

	def find_track(self, trackid):
		if trackid in self.track_data: return True, self.track_data[trackid]
		else: return False, None

	def iter_track(self):
		for trackid in self.track_order:
			if trackid in self.track_data: yield trackid, self.track_data[trackid]

	def add_group(self, groupid):
		logger_project.info('Group - '+groupid)
		self.groups[groupid] = tracks.cvpj_track('group', self.time_ppq, self.time_float, False, False)
		return self.groups[groupid]

	def find_group(self, groupid):
		if groupid in self.groups: return True, self.groups[groupid]
		else: return False, None

	def iter_group(self):
		for groupid, group_obj in self.groups.items():
			yield groupid, group_obj





	def add_track(self, track_id, tracktype, uses_placements, is_indexed):
		logger_project.info('Track '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+track_id)
		self.track_data[track_id] = tracks.cvpj_track(tracktype, self.time_ppq, self.time_float, uses_placements, is_indexed)
		self.track_order.append(track_id)
		return self.track_data[track_id]

	def add_track_midi(self, track_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed):
		plugin_obj = self.add_plugin_midi(plug_id, m_bank, m_inst, m_drum)
		plugin_obj.role = 'synth'

		track_obj = self.add_track(track_id, 'instrument', uses_pl, indexed)
		track_obj.midi.out_inst.patch = m_inst
		track_obj.midi.out_inst.bank = m_bank
		track_obj.midi.out_inst.drum = m_drum
		track_obj.inst_pluginid = plug_id
		track_obj.params.add('usemasterpitch', not m_drum, 'bool')
		return track_obj, plugin_obj

	def add_track_midi_dset(self, inst_id, plug_id, m_bank_hi, m_bank, m_inst, m_drum, def_name, def_color, uses_pl, indexed, **kwargs):
		midi_type = kwargs['device'] if 'device' in kwargs else 'gm'
		startcat = midi_type+'_inst' if not m_drum else midi_type+'_drums'

		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')

		track_obj, plugin_obj = self.add_track_midi(inst_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed)
		if def_name: track_obj.visual.name = def_name
		if def_color: track_obj.visual.color = def_color
		track_obj.midi.out_inst.bank_hi = m_bank_hi
		track_obj.midi.out_inst.device = midi_type

		plugin_obj.midi.bank_hi = m_bank_hi
		plugin_obj.midi.device = midi_type
		plugin_obj.datavals.add('device', midi_type)
		return track_obj, plugin_obj

	def add_track_from_dset(self, track_id, plug_id, dset_name, ds_id, def_name, def_color, uses_pl, indexed):
		main_dso = globalstore.dataset.get_obj(dset_name, 'inst', ds_id)
		ds_midi = main_dso.midi if main_dso else None

		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')

		midifound = False
		if ds_midi:
			if ds_midi.used != False:
				midifound = True
				track_obj, plugin_obj = self.add_track_midi_dset(track_id, plug_id, 0, ds_midi.bank, ds_midi.patch, ds_midi.is_drum, def_name, def_color, uses_pl, indexed)
				track_obj.visual.from_dset_opt(dset_name, 'inst', ds_id)
				track_obj.visual.from_dset_opt('midi', startcat, str(m_bank_hi)+'_'+str(m_bank)+'_'+str(m_inst) )
				track_obj.visual.from_dset_opt('midi', startcat, '0_0_'+str(m_inst) )

		if not midifound:
			plugin_obj = self.add_plugin(plug_id, None, None)
			plugin_obj.role = 'synth'
			track_obj = self.add_track(track_id, 'instrument', uses_pl, indexed)
			track_obj.inst_pluginid = plug_id
			track_obj.visual.name = def_name
			track_obj.visual.color = def_color
			track_obj.visual.from_dset_opt(dset_name, 'inst', ds_id)

		return track_obj, plugin_obj





	def add_return(self, track_id):
		self.track_returns[track_id] = tracks.cvpj_track('return', self.time_ppq, self.time_float, False, False)
		return self.track_returns[track_id]





	def get_plugin(self, plug_id):
		if plug_id in self.plugins: return True, self.plugins[plug_id]
		else: return False, None

	def add_plugin(self, plug_id, i_type, i_subtype):
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id]

	def add_plugin_genid(self, i_type, i_subtype):
		plug_id = plugin_id_counter.get_str_txt()
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id], plug_id

	def add_plugin_sampler_genid(self, file_path, os_type, **kwargs):
		plug_id = plugin_id_counter.get_str_txt()
		plugin_obj, sampleref_obj, samplepart_obj = self.add_plugin_sampler(plug_id, file_path, os_type, **kwargs)
		plugin_obj.role = 'synth'
		return plugin_obj, plug_id, sampleref_obj, samplepart_obj

	def add_plugin_sampler(self, plug_id, file_path, os_type, **kwargs):
		if file_path:
			sampleref = kwargs['sampleid'] if 'sampleid' in kwargs else file_path
			sampleref_obj = self.add_sampleref(sampleref, file_path, os_type)
			is_drumsynth = sampleref_obj.fileref.extension.lower() == 'ds'
		else:
			sampleref_obj = None
			is_drumsynth = False

		if not is_drumsynth:
			plugin_obj = self.add_plugin(plug_id, 'sampler', 'single')
			plugin_obj.role = 'synth'
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path: samplepart_obj.from_sampleref(self, sampleref)
		else:
			plugin_obj = self.add_plugin(plug_id, 'sampler', 'drumsynth')
			plugin_obj.role = 'synth'
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path:
				samplepart_obj.sampleref = sampleref
				from objects.file import audio_drumsynth
				from functions_plugin_cvpj import params_drumsynth
				drumsynth_obj = audio_drumsynth.drumsynth_main()
				drumsynth_obj.read(file_path)
				params_drumsynth.to_cvpj(drumsynth_obj, plugin_obj)

		return plugin_obj, sampleref_obj, samplepart_obj

	def add_plugin_midi(self, plug_id, m_bank_hi, m_bank, m_inst, m_drum, m_dev):
		plugin_obj = self.add_plugin(plug_id, 'midi', None)
		plugin_obj.role = 'synth'
		plugin_obj.midi.bank_hi = m_bank_hi
		plugin_obj.midi.bank = m_bank
		plugin_obj.midi.patch = m_inst
		plugin_obj.midi.drum = m_drum
		plugin_obj.midi.device = m_dev
		return plugin_obj




	def add_instrument(self, inst_id):
		logger_project.info('Instrument - '+str(inst_id))
		self.instruments[inst_id] = tracks.cvpj_instrument()
		self.instruments_order.append(inst_id)
		return self.instruments[inst_id]

	def iter_instrument(self):
		for inst_id in self.instruments_order:
			if inst_id in self.instruments: yield inst_id, self.instruments[inst_id]



	def do_lanefit(self):
		for trackid, track_obj in self.track_data.items():
			oldnum = len(track_obj.lanes)
			track_obj.lanefit()
			logger_project.info('LaneFit: '+ trackid+': '+str(oldnum)+' > '+str(len(track_obj.lanes)))

	def add_autopoints_twopoints(self, autopath, v_type, twopoints):
		for x in twopoints: self.add_autopoint(autopath, v_type, x[0], x[1], 'normal')



	def change_projtype(self, in_dawinfo, out_dawinfo, out_type, dv_config):
		compactclass = song_compat.song_compat()

		compactclass.makecompat(self, self.type, in_dawinfo, out_dawinfo, out_type)

		if self.type == 'ri' and out_type == 'mi': convert_ri2mi.convert(self)
		elif self.type == 'ri' and out_type == 'r': convert_ri2r.convert(self)

		elif self.type == 'm' and out_type == 'mi': convert_m2mi.convert(self)
		elif self.type == 'm' and out_type == 'r': convert_m2r.convert(self)

		elif self.type == 'r' and out_type == 'm': convert_r2m.convert(self)
		elif self.type == 'r' and out_type == 'mi': 
			convert_r2m.convert(self)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self)

		elif self.type == 'mi' and out_type == 'm': convert_mi2m.convert(self, dv_config)
		elif self.type == 'mi' and out_type == 'r': 
			convert_mi2m.convert(self, dv_config)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2r.convert(self)
	
		elif self.type == 'rm' and out_type == 'r': convert_rm2r.convert(self)
		elif self.type == 'rm' and out_type == 'm': convert_rm2m.convert(self, True)
		elif self.type == 'rm' and out_type == 'mi': 
			convert_rm2m.convert(self, True)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self)

		elif self.type == 'rs' and out_type == 'mi': 
			convert_rs2r.convert(self)
			convert_r2m.convert(self)
			compactclass.makecompat(self, 'm', in_dawinfo, out_dawinfo, out_type)
			convert_m2mi.convert(self)

		elif self.type == 'rs' and out_type == 'r': convert_rs2r.convert(self)

		elif self.type == 'ms' and out_type == 'mi': 
			convert_ms2rm.convert(self)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type)
			convert_rm2m.convert(self, True)
			convert_m2mi.convert(self)

		elif self.type == 'ms' and out_type == 'r': 
			convert_ms2rm.convert(self)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type)
			convert_rm2r.convert(self)

		elif self.type == out_type: 
			pass
		
		else:
			logger_project.error(typelist[in_type]+' to '+typelist[out_type]+' is not supported.')
			exit()

		compactclass.makecompat(self, out_type, in_dawinfo, out_dawinfo, out_type)
# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import counter as idcounter
from functions import xtramath
from functions import data_values
from objects import globalstore
from collections import Counter

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
from objects.convproj import timemarker

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

def vis_plugin(p_category, p_type, p_subtype):
	if p_category != None and p_type != None and p_subtype != None: return p_category+':'+p_type+':'+p_subtype
	elif p_category != None and p_type != None and p_subtype == None: return p_category+':'+p_type
	elif p_category != None and p_type == None and p_subtype == None: return p_category
	elif p_category == None and p_type == None and p_subtype == None: return 'None'

def autoloc_getname(autopath):
	if autopath[0] == 'main': autoname = 'Main'
	if autopath[0] == 'fxmixer': autoname = 'FX '+autopath[1]
	if autopath[0] == 'send': autoname = 'Send'
	if autopath[0] == 'plugin': autoname = autopath[1]
	if autopath[0] == 'track': autoname = 'Track'

plugin_id_counter = idcounter.counter(1000, 'plugin_')

def routetrackord(trackord, groupdata, outl, insidegroup):
	for t, i in trackord:
		outl.append([t, i, insidegroup])
		if t == 'GROUP': routetrackord(groupdata[i], groupdata, outl, i)

class groupassoc():
	def __init__(self):
		self.groupdata = []
		self.inside_found = []

	def add_part(self, groupname, insidegroup):
		for x in self.groupdata:
			if x[0] == groupname: 
				if insidegroup: 
					x[1] = insidegroup
					self.inside_found.append(x[1])
				return True
		self.groupdata.append([groupname, insidegroup])
		if insidegroup: 
			self.inside_found.append(insidegroup)
		return True

	def filter(self, insidegroup):
		for x in self.groupdata:
			if insidegroup == x[1]:
				yield x

	def iter(self, i):
		if i in self.inside_found or not i:
			for x in self.filter(i):
				yield x
				for d in self.iter(x[0]):
					yield d

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
		self.fxtype = 'none'

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
		self.timemarkers = timemarker.cvpj_timemarkers(self.time_ppq, self.time_float)
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

# --------------------------------------------------------- MAIN ---------------------------------------------------------

	def main__sort_tracks(self):
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
		self.timemarkers = timemarker.cvpj_timemarkers(self.time_ppq, self.time_float)

	def change_timings(self, time_ppq, time_float):
		logger_project.info('Changing Timings from '+str(self.time_ppq)+':'+str(self.time_float)+' to '+str(time_ppq)+':'+str(time_float))
		for p in self.track_data: 
			track_data = self.track_data[p]
			track_data.change_timings(time_ppq, time_float)
			for e in track_data.notelist_index: 
				track_data.notelist_index[e].notelist.change_timings(time_ppq, time_float)
		for p in self.playlist: self.playlist[p].change_timings(time_ppq, time_float)
		for _, n in self.notelist_index.items(): 
			n.notelist.change_timings(time_ppq, time_float)
			n.timesig_auto.change_timings(time_ppq, time_float)
		self.timemarkers.change_timings(time_ppq, time_float)
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

	def add_timesig_lengthbeat(self, pat_len, notes_p_beat):
		self.timesig = xtramath.get_timesig(pat_len, notes_p_beat)

	def main__do_lanefit(self):
		for trackid, track_obj in self.track_data.items():
			oldnum = len(track_obj.lanes)
			track_obj.lanefit()
			logger_project.info('LaneFit: '+ trackid+': '+str(oldnum)+' > '+str(len(track_obj.lanes)))

	def add_autopoints_twopoints(self, autopath, v_type, twopoints):
		for x in twopoints: self.add_autopoint(autopath, v_type, x[0], x[1], 'normal')

	def main__change_type(self, in_dawinfo, out_dawinfo, out_type, dv_config):
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
			convert_ms2rm.convert(self, out_dawinfo)
			compactclass.makecompat(self, 'rm', in_dawinfo, out_dawinfo, out_type)
			convert_rm2m.convert(self, True)
			convert_m2mi.convert(self)

		elif self.type == 'ms' and out_type == 'r': 
			convert_ms2rm.convert(self, out_dawinfo)
			compactclass.makecompat(self, 'r', in_dawinfo, out_dawinfo, out_type)
			convert_rm2r.convert(self)

		elif self.type == out_type: 
			pass
		
		else:
			logger_project.error(typelist[in_type]+' to '+typelist[out_type]+' is not supported.')
			exit()

		compactclass.makecompat(self, out_type, in_dawinfo, out_dawinfo, out_type)

# --------------------------------------------------------- GROUPS ---------------------------------------------------------

	def group__iter_inside(self):
		groups_assoc = groupassoc()

		for groupid, track_obj in self.groups.items():
			groups_assoc.add_part(groupid, track_obj.group)

		for groupid, insidegroup in groups_assoc.iter(None):
			yield groupid, insidegroup

	def group__iter_stream_inside(self):
		track_group = {}
		track_nongroup = []

		for groupid, group_obj in self.fx__group__iter():
			if group_obj.group:
				if group_obj.group not in track_group: track_group[group_obj.group] = []
				track_group[group_obj.group].append(['GROUP', groupid])
			else: track_nongroup.append(['GROUP', groupid])

		for trackid, track_obj in self.track__iter():
			if track_obj.group: 
				if track_obj.group not in track_group: track_group[track_obj.group] = []
				track_group[track_obj.group].append(['TRACK', trackid])
			else: track_nongroup.append(['TRACK', trackid])

		outl = []
		routetrackord(track_nongroup, track_group, outl, None)
		return outl

# --------------------------------------------------------- SCENE ---------------------------------------------------------

	def scene__add(self, i_sceneid):
		scene_obj = cvpj_scene()
		#cpr_int('[project] Scene - '+str(i_sceneid), 'magenta')
		logger_project.info('Scene - '+str(i_sceneid))
		self.scenes[i_sceneid] = scene_obj
		return scene_obj

	def scene__add_pl(self):
		scene_obj = cvpj_scenepl()
		self.scene_placements.append(scene_obj)
		return scene_obj

# --------------------------------------------------------- TIMEMARKERS ---------------------------------------------------------

	def timemarker__add(self):
		return self.timemarkers.add()

	def timemarker__from_patlenlist(self, PatternLengthList, pos_loop):
		prevtimesig = self.timesig
		currentpos = 0
		blockcount = 0

		self.loop_end = sum(PatternLengthList)
		self.loop_active = True

		for PatternLengthPart in PatternLengthList:
			temptimesig = xtramath.get_timesig(PatternLengthPart, self.timesig[1])
			if prevtimesig != temptimesig: 
				outtimesig = temptimesig.copy()
				if not outtimesig[0]%outtimesig[1]: outtimesig[0] = outtimesig[1]
				self.timesig_auto.add_point(currentpos, outtimesig)
			if pos_loop == blockcount: self.loop_start = currentpos
			prevtimesig = temptimesig
			currentpos += PatternLengthPart
			blockcount += 1

# --------------------------------------------------------- TRACKS ---------------------------------------------------------

	def track__get(self, trackid):
		return self.track_data[trackid] if trackid in self.track_data else None

	def track__iter(self):
		for trackid in self.track_order:
			if trackid in self.track_data: yield trackid, self.track_data[trackid]

	def track__add_scene(self, i_track, i_sceneid, i_lane):
		if i_track in self.track_data: return self.track_data[i_track].scene__add(i_sceneid, i_lane)
		else: return None

	def track__add(self, track_id, tracktype, uses_placements, is_indexed):
		logger_project.info('Track '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+track_id)
		self.track_data[track_id] = tracks.cvpj_track(tracktype, self.time_ppq, self.time_float, uses_placements, is_indexed)
		self.track_order.append(track_id)
		return self.track_data[track_id]

	def track__addspec__midi(self, track_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed):
		plugin_obj = self.plugin__addspec__midi(plug_id, 0, m_bank, m_inst, m_drum, 'gm')
		plugin_obj.role = 'synth'

		track_obj = self.track__add(track_id, 'instrument', uses_pl, indexed)
		track_obj.midi.out_inst.patch = m_inst
		track_obj.midi.out_inst.bank = m_bank
		track_obj.midi.out_inst.drum = m_drum
		track_obj.inst_pluginid = plug_id
		track_obj.params.add('usemasterpitch', not m_drum, 'bool')
		return track_obj, plugin_obj

	def track__addspec__midi__dset(self, inst_id, plug_id, m_bank_hi, m_bank, m_inst, m_drum, def_name, def_color, uses_pl, indexed, **kwargs):
		midi_type = kwargs['device'] if 'device' in kwargs else 'gm'
		startcat = midi_type+'_inst' if not m_drum else midi_type+'_drums'

		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')

		track_obj, plugin_obj = self.track__addspec__midi(inst_id, plug_id, m_bank, m_inst, m_drum, uses_pl, indexed)
		if def_name: track_obj.visual.name = def_name
		if def_color: track_obj.visual.color = def_color
		track_obj.midi.out_inst.bank_hi = m_bank_hi
		track_obj.midi.out_inst.device = midi_type

		plugin_obj.midi.bank_hi = m_bank_hi
		plugin_obj.midi.device = midi_type
		plugin_obj.datavals.add('device', midi_type)
		return track_obj, plugin_obj

	def track__add__dset(self, track_id, plug_id, dset_name, ds_id, def_name, def_color, uses_pl, indexed):
		main_dso = globalstore.dataset.get_obj(dset_name, 'inst', ds_id)
		ds_midi = main_dso.midi if main_dso else None

		globalstore.dataset.load('midi', './data_main/dataset/midi.dset')

		midifound = False
		if ds_midi:
			if ds_midi.used != False:
				midifound = True
				track_obj, plugin_obj = self.track__addspec__midi__dset(track_id, plug_id, 0, ds_midi.bank, ds_midi.patch, ds_midi.is_drum, def_name, def_color, uses_pl, indexed)
				track_obj.visual.from_dset_opt(dset_name, 'inst', ds_id)
				track_obj.visual.from_dset_opt('midi', startcat, str(m_bank_hi)+'_'+str(m_bank)+'_'+str(m_inst) )
				track_obj.visual.from_dset_opt('midi', startcat, '0_0_'+str(m_inst) )

		if not midifound:
			plugin_obj = self.plugin__add(plug_id, None, None, None)
			plugin_obj.role = 'synth'
			track_obj = self.track__add(track_id, 'instrument', uses_pl, indexed)
			track_obj.inst_pluginid = plug_id
			track_obj.visual.name = def_name
			track_obj.visual.color = def_color
			track_obj.visual.from_dset_opt(dset_name, 'inst', ds_id)

		return track_obj, plugin_obj

# --------------------------------------------------------- AUTOMATION ---------------------------------------------------------

	def automation__iter(self):
		for autopath in self.automation:
			yield autopath.split(';'), self.automation[autopath]

# --------------------------------------------------------- FILEREF ---------------------------------------------------------

	def fileref__add(self, fileid, filepath, os_type):
		if fileid not in self.filerefs: 
			self.filerefs[fileid] = fileref.cvpj_fileref()
			self.filerefs[fileid].set_path(os_type, filepath, 0)
			logger_project.info('FileRef - '+fileid+' - '+filepath)
		return self.filerefs[fileid]

	def fileref__get(self, fileid):
		if fileid in self.filerefs: return True, self.filerefs[fileid]
		else: return False, None

# --------------------------------------------------------- SAMPLEREF ---------------------------------------------------------

	def sampleref__add(self, fileid, filepath, os_type):
		if fileid not in self.samplerefs: 
			self.samplerefs[fileid] = fileref.cvpj_sampleref()
			self.samplerefs[fileid].set_path(os_type, filepath)
			logger_project.info('SampleRef - '+fileid+' - '+filepath)
		return self.samplerefs[fileid]

	def sampleref__iter(self):
		for sampleref_id, sampleref_obj in self.samplerefs.items():
			yield sampleref_id, sampleref_obj

	def sampleref__get(self, fileid):
		if fileid in self.samplerefs: return True, self.samplerefs[fileid]
		else: return False, None

# --------------------------------------------------------- FX ---------------------------------------------------------

	def fx__chan__add(self, fxnum):
		logger_project.info('FX Channel - '+str(fxnum))
		if fxnum not in self.fxrack: self.fxrack[fxnum] = cvpj_fxchannel()
		return self.fxrack[fxnum]

	def fx__chan__get(self, fxnum):
		return self.fxrack[fxnum] if fxnum in self.fxrack else None

	def fx__chan__remove(self, fxnum):
		if fxnum in self.fxrack:
			del self.fxrack[fxnum]
			return True
		else:
			return False

	def fx__chan__iter(self):
		for num, fxchannel_obj in self.fxrack.items():
			yield num, fxchannel_obj

	def fx__chan__clear(self):
		self.fxrack = {}

	def fx__chan__removeloopcrash(self):
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

	def fx__chan__remove_unused(self):
		unused_fx = list(self.fxrack)
		for trackid, track_obj in self.track_data.items():
			if track_obj.fxrack_channel in unused_fx: unused_fx.remove(track_obj.fxrack_channel)

		for n, d in self.fxrack.items():
			if d.visual or d.visual_ui or d.fxslots_audio or d.fxslots_mixer:
				if n in unused_fx: unused_fx.remove(n)
			if d.sends.to_master_active:
				if 0 in unused_fx: unused_fx.remove(0)
			for i in list(d.sends.data):
				if i in unused_fx: unused_fx.remove(i)

		for x in unused_fx: del self.fxrack[x]
		logger_project.info('Removed '+str(len(unused_fx))+' FX Channels')


	def fx__route__add(self, trackid):
		if trackid not in self.trackroute: 
			#cpr_int('[project] Track Route - '+str(trackid), 'yellow')
			logger_project.info('Track Route - '+str(trackid))
			self.trackroute[trackid] = sends.cvpj_sends()
		return self.trackroute[trackid]

	def fx__route__clear(self):
		self.trackroute = {}


	def fx__group__add(self, groupid):
		logger_project.info('Group - '+groupid)
		self.groups[groupid] = tracks.cvpj_track('group', self.time_ppq, self.time_float, False, False)
		return self.groups[groupid]

	def fx__group__get(self, groupid):
		return self.groups[groupid] if groupid in self.groups else None

	def fx__group__iter(self):
		for groupid, group_obj in self.groups.items():
			yield groupid, group_obj

	def fx__group__clear(self):
		self.groups = {}

	def fx__group__count_usage(self):
		groupcount = [x.group for _, x in self.groups.items() if x.group != None]
		groupcount += [x.group for _, x in self.track_data.items() if x.group != None]
		return list(Counter(groupcount))

	def fx__group__remove_unused(self):
		groupcount = self.fx__group__count_usage()
		unusedgroups = [x for x in list(self.groups) if x not in groupcount]
		for x in unusedgroups: del self.groups[x]


	def fx__return__add(self, track_id):
		self.track_returns[track_id] = tracks.cvpj_track('return', self.time_ppq, self.time_float, False, False)
		return self.track_returns[track_id]

	def fx__return__clear(self):
		self.track_returns = {}

# --------------------------------------------------------- NOTELIST INDEX ---------------------------------------------------------

	def notelistindex__add(self, i_id):
		self.notelist_index[i_id] = tracks.cvpj_nle(self.time_ppq, self.time_float)
		return self.notelist_index[i_id]

	def notelistindex__iter(self):
		for i_id in self.notelist_index: yield i_id, self.notelist_index[i_id]

# --------------------------------------------------------- SAMPLE INDEX ---------------------------------------------------------

	def sampleindex__add(self, i_id):
		self.sample_index[i_id] = sample_entry.cvpj_sample_entry()
		return self.sample_index[i_id]

	def sampleindex__iter(self):
		for i_id in self.sample_index: yield i_id, self.sample_index[i_id]

# --------------------------------------------------------- VISUAL WINDOW ---------------------------------------------------------

	def viswindow__add(self, windowpath):
		windowpath = autopath_encode(windowpath)
		self.window_data[windowpath] = visual.cvpj_window_data()
		return self.window_data[windowpath]

	def viswindow__get(self, windowpath):
		windowpath = autopath_encode(windowpath)
		if windowpath in self.window_data: return self.window_data[windowpath]
		else: return visual.cvpj_window_data()

# --------------------------------------------------------- PLAYLIST ---------------------------------------------------------

	def playlist__add(self, idnum, uses_placements, is_indexed):
		if idnum not in self.playlist:
			logger_project.info('Playlist '+('NoPl' if not uses_placements else 'w/Pl')+(' + Indexed' if is_indexed else '')+' - '+str(idnum))
			self.playlist[idnum] = tracks.cvpj_track('hybrid', self.time_ppq, self.time_float, uses_placements, is_indexed)
		return self.playlist[idnum]

	def playlist__iter(self):
		for idnum, playlist_obj in self.playlist.items():
			yield idnum, playlist_obj

# --------------------------------------------------------- PLUGIN ---------------------------------------------------------

	def plugin__get(self, plug_id):
		if plug_id in self.plugins: return True, self.plugins[plug_id]
		else: return False, None

	def plugin__add(self, plug_id, i_category, i_type, i_subtype):
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_category, i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_category, i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id]

	def plugin__add__genid(self, i_category, i_type, i_subtype):
		plug_id = plugin_id_counter.get_str_txt()
		logger_project.info('Plugin - '+str(plug_id)+' - '+vis_plugin(i_category, i_type, i_subtype))
		plugin_obj = plugin.cvpj_plugin()
		plugin_obj.replace(i_category, i_type, i_subtype)
		self.plugins[plug_id] = plugin_obj
		return self.plugins[plug_id], plug_id

	def plugin__addspec__sampler__genid(self, file_path, os_type, **kwargs):
		plug_id = plugin_id_counter.get_str_txt()
		plugin_obj, sampleref_obj, samplepart_obj = self.plugin__addspec__sampler(plug_id, file_path, os_type, **kwargs)
		plugin_obj.role = 'synth'
		return plugin_obj, plug_id, sampleref_obj, samplepart_obj

	def plugin__addspec__sampler(self, plug_id, file_path, os_type, **kwargs):
		if file_path:
			sampleref = kwargs['sampleid'] if 'sampleid' in kwargs else file_path
			sampleref_obj = self.sampleref__add(sampleref, file_path, os_type)
			is_drumsynth = sampleref_obj.fileref.file.extension.lower() == 'ds'
		else:
			sampleref_obj = None
			is_drumsynth = False

		if not is_drumsynth:
			plugin_obj = self.plugin__add(plug_id, 'universal', 'sampler', 'single')
			plugin_obj.role = 'synth'
			samplepart_obj = plugin_obj.samplepart_add('sample')
			if file_path: samplepart_obj.from_sampleref(self, sampleref)
		else:
			plugin_obj = self.plugin__add(plug_id, 'universal', 'sampler', 'drumsynth')
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

	def plugin__addspec__midi(self, plug_id, m_bank_hi, m_bank, m_inst, m_drum, m_dev):
		plugin_obj = self.plugin__add(plug_id, 'universal', 'midi', None)
		plugin_obj.role = 'synth'
		plugin_obj.midi.bank_hi = m_bank_hi
		plugin_obj.midi.bank = m_bank
		plugin_obj.midi.patch = m_inst
		plugin_obj.midi.drum = m_drum
		plugin_obj.midi.device = m_dev
		return plugin_obj

# --------------------------------------------------------- INSTRUMENT ---------------------------------------------------------

	def instrument__add(self, inst_id):
		logger_project.info('Instrument - '+str(inst_id))
		self.instruments[inst_id] = tracks.cvpj_instrument()
		self.instruments_order.append(inst_id)
		return self.instruments[inst_id]

	def instrument__iter(self):
		for inst_id in self.instruments_order:
			if inst_id in self.instruments: yield inst_id, self.instruments[inst_id]

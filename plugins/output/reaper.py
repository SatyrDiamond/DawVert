# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import uuid
import rpp
import struct
import base64
import os.path
from rpp import Element
from functions import data_bytes
from functions import data_values
from functions import colors
from functions import xtramath

def add_plugin(rpp_fxchain, pluginid, convproj_obj):
	plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
	if plugin_found:
		fx_on, fx_wet = plugin_obj.fxdata_get()

		if plugin_obj.check_wildmatch('vst2', None):
			rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
			vst_fx_fourid = plugin_obj.datavals.get('fourid', 0)
			vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
			vst_fx_datatype = plugin_obj.datavals.get('datatype', None)
			vst_fx_numparams = plugin_obj.datavals.get('numparams', 0)

			rpp_vst_obj.vst_name = plugin_obj.datavals_global.get('basename', '')
			if not rpp_vst_obj.vst_name: plugin_obj.datavals_global.get('name', '')

			rpp_vst_obj.vst_lib = os.path.basename(vst_fx_path)
			rpp_vst_obj.vst_fourid = vst_fx_fourid

			vstparamsnum = 0
			vstparams = None
		
			if vst_fx_datatype == 'chunk': 
				vstparams = plugin_obj.rawdata_get('chunk')
				vstparamsnum = len(vstparams)
			if vst_fx_datatype == 'param': 
				floatdata = []
				for num in range(vst_fx_numparams):
					floatdata.append(float(plugin_obj.params.get('vst_param_'+str(num), 0).value))
				vstparams = struct.pack('f'*vst_fx_numparams, *floatdata)
				vstparamsnum = len(vstparams)

			vstheader_ints = (vst_fx_fourid, 4276969198,0,2,1,0,2,0,vstparamsnum,1,1048576)

			rpp_vst_obj.data_con = struct.pack('IIIIIIIIIII', *vstheader_ints)
			if vstparams: rpp_vst_obj.data_chunk = vstparams
			rpp_plug_obj.bypass['bypass'] = not fx_on
			rpp_plug_obj.wet['wet'] = fx_wet
			if fx_wet != 1: rpp_plug_obj.wet.used = True

		if plugin_obj.check_wildmatch('vst3', None):
			rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_fxchain.add_vst()
			vst_fx_name = plugin_obj.datavals.get('name', None)
			vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
			vst_fx_version = plugin_obj.datavals.get('version', None)
			vst_fx_id = plugin_obj.datavals.get('id', 0)

			chunkdata = plugin_obj.rawdata_get('chunk')
			vstparams = struct.pack('II', len(chunkdata), 1)+chunkdata+b'\x00\x00\x00\x00\x00\x00\x00\x00'
			vstheader = b':\xfbA+\xee^\xed\xfe'
			vstheader += struct.pack('II', 0, plugin_obj.audioports.num_outputs)
			for n in range(plugin_obj.audioports.num_outputs): 
				if n < len(plugin_obj.audioports.ports): vstheader += data_bytes.set_bitnums(plugin_obj.audioports.ports[n], 8)
				else: vstheader += b'\x00\x00\x00\x00\x00\x00\x00\x00'
			vstheader_end = (len(chunkdata)+16).to_bytes(4, 'little')+b'\x01\x00\x00\x00\xff\xff\x10\x00'

			rpp_vst_obj.vst_fourid = 0
			rpp_vst_obj.vst3_uuid = vst_fx_id
			rpp_vst_obj.data_con = vstheader+vstheader_end
			rpp_vst_obj.data_chunk = vstparams
			rpp_plug_obj.bypass['bypass'] = not fx_on
			rpp_plug_obj.wet['wet'] = fx_wet
			if fx_wet != 1: rpp_plug_obj.wet.used = True

		if plugin_obj.check_wildmatch('jesusonic', None):
			rpp_plug_obj, rpp_js_obj, rpp_guid = rpp_fxchain.add_js()
			rpp_js_obj.js_id = plugin_obj.type.subtype
			rpp_js_obj.data = [plugin_obj.datavals.get(str(n), '-') for n in range(64)]
			rpp_plug_obj.bypass['bypass'] = not fx_on
			rpp_plug_obj.wet['wet'] = fx_wet
			if fx_wet != 1: rpp_plug_obj.wet.used = True



def cvpj_color_to_reaper_color(i_color): 
	cvpj_trackcolor = bytes(i_color.get_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

def cvpj_color_to_reaper_color_clip(i_color): 
	cvpj_trackcolor = bytes(i_color.getbgr_int())+b'\x01'
	return int.from_bytes(cvpj_trackcolor, 'little')

def midi_add_cmd(i_list, i_pos, i_cmd):
	if i_pos not in i_list: i_list[i_pos] = []
	i_list[i_pos].append(i_cmd)

def convert_midi(rpp_source_obj,notelist, tempo, num, dem, notespl_obj):
	i_list = {}
	notelist.sort()
	notelist.change_timings(960, False)

	n_enddur = notelist.get_dur()
	p_enddur = notespl_obj.time.duration*(960//4)

	for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notelist.iter():
		for t_key in t_keys:
			cvmi_n_pos = int(t_pos)
			cvmi_n_dur = int(t_dur)
			cvmi_n_key = int(t_key)+60
			cvmi_n_vol = xtramath.clamp(int(t_vol*127), 0, 127)
			midi_add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
			midi_add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

	if p_enddur-n_enddur >= 0:
		midi_add_cmd(i_list, p_enddur, ['end'])

	i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

	prevpos = 0
	for i_list_e in i_list:
		for midi_notedata in i_list[i_list_e]:
			if midi_notedata[0] == 'note_on': 
				rpp_source_obj.notes.append([False,i_list_e-prevpos, '90', hex(midi_notedata[1])[2:], hex(midi_notedata[2])[2:]])
			if midi_notedata[0] == 'note_off': 
				rpp_source_obj.notes.append([False,i_list_e-prevpos, '80', hex(midi_notedata[1])[2:], '00'])
			if midi_notedata[0] == 'end': 
				rpp_source_obj.notes.append([False,int(i_list_e-prevpos), 'b0', '7b', '00'])
			prevpos = i_list_e
	
def file_source(rpp_source_obj, fileref_obj, filename):
	rpp_source_obj.file.set(filename)
	if fileref_obj.file.extension == 'mp3': rpp_source_obj.type = 'MP3'
	elif fileref_obj.file.extension == 'flac': rpp_source_obj.type = 'FLAC'
	elif fileref_obj.file.extension == 'ogg': rpp_source_obj.type = 'VORBIS'
	else: rpp_source_obj.type = 'WAVE'

class output_reaper(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'REAPER'
	def get_shortname(self): return 'reaper'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = 'rpp'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = []
		in_dict['fxtype'] = 'track'
		in_dict['time_seconds'] = True
		in_dict['track_hybrid'] = True
		in_dict['audio_stretch'] = ['rate']
		in_dict['plugin_ext'] = ['vst2', 'vst3']
	def parse(self, convproj_obj, output_file):
		from objects.file_proj import proj_reaper
		from objects.file_proj._rpp import fxchain as rpp_fxchain
		from objects.file_proj._rpp import source as rpp_source

		global reaper_tempo
		global tempomul

		convproj_obj.change_timings(4, True)

		reaper_numerator, reaper_denominator = convproj_obj.timesig
		reaper_tempo = convproj_obj.params.get('bpm', 120).value

		tempomul = reaper_tempo/120
		project_obj = proj_reaper.rpp_song()

		rpp_project = project_obj.project
		rpp_project.tempo['tempo'] = reaper_tempo
		rpp_project.tempo['num'] = convproj_obj.timesig[0]
		rpp_project.tempo['denom'] = convproj_obj.timesig[1]

		track_uuids = ['{'+str(uuid.uuid4())+'}' for _ in convproj_obj.iter_track()]

		trackdata = []

		tracknum = 0
		for trackid, track_obj in convproj_obj.iter_track():
			track_uuid = track_uuids[tracknum]

			rpp_track_obj = rpp_project.add_track()

			rpp_track_obj.trackid.set(track_uuid)
			if track_obj.visual.name: rpp_track_obj.name.set(track_obj.visual.name)
			if track_obj.visual.color: rpp_track_obj.peakcol.set(cvpj_color_to_reaper_color(track_obj.visual.color))
			rpp_track_obj.volpan['vol'] = track_obj.params.get('vol', 1.0).value
			rpp_track_obj.volpan['pan'] = track_obj.params.get('pan', 0).value

			middlenote = track_obj.datavals.get('middlenote', 0)

			rpp_track_obj.fxchain = rpp_fxchain.rpp_fxchain()

			if middlenote != 0:
				rpp_plug_obj, rpp_vst_obj, rpp_guid = rpp_track_obj.fxchain.add_vst()
				rpp_vst_obj.data_con = b'\x64\x6d\x63\x72\xee\x5e\xed\xfe\x00\x00\x00\x00\x00\x00\x00\x00\xe6\x00\x00\x00\x01\x00\x00\x00\x00\x00\x10\x00'
				midictrlstate1 = b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\xff?\x00\x00\x00 \x00\x00\x00 \x00\x00\x00\x00\x00\x005\x00\x00\x00C:\\Users\\colby\\AppData\\Roaming\\REAPER\\Data\\GM.reabank\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
				midictrlstate2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00Major\x00\r\x00\x00\x00102034050607\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\r\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00'
				midictrlstate3 = struct.pack('i', -middlenote)
				rpp_vst_obj.data_chunk = midictrlstate1+midictrlstate3+midictrlstate2
				rpp_vst_obj.vst_name = 'ReaControlMIDI (Cockos)'
				rpp_vst_obj.vst_lib = 'reacontrolmidi.dll'
				rpp_vst_obj.vst_fourid = 1919118692
				rpp_vst_obj.vst_uuid = '56535472636D64726561636F6E74726F'

			add_plugin(rpp_track_obj.fxchain, track_obj.inst_pluginid, convproj_obj)

			for notespl_obj in track_obj.placements.pl_notes:

				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()
				if notespl_obj.time.cut_type == 'cut': rpp_item_obj.soffs.set(notespl_obj.time.cut_start/8/tempomul)
				rpp_item_obj.position.set(notespl_obj.time.position_real)
				rpp_item_obj.length.set(notespl_obj.time.duration_real)
				rpp_item_obj.mute['mute'] = int(notespl_obj.muted)
				if notespl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(notespl_obj.visual.color))
				if notespl_obj.visual.name: rpp_item_obj.name.set(notespl_obj.visual.name)
				rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()
				rpp_source_obj.type = 'MIDI'
				rpp_source_obj.hasdata.used = True
				rpp_source_obj.hasdata['hasdata'] = 1

				convert_midi(rpp_source_obj,notespl_obj.notelist,reaper_tempo,'4','4',notespl_obj)

			for audiopl_obj in track_obj.placements.pl_audio:
				rpp_item_obj, clip_guid, clip_iguid = rpp_track_obj.add_item()

				audiorate = audiopl_obj.sample.stretch.calc_real_speed
				clip_startat = 0
				if audiopl_obj.time.cut_type == 'cut': clip_startat = audiopl_obj.time.cut_start/8
				clip_startat *= audiopl_obj.sample.stretch.calc_tempo_speed
				rpp_item_obj.soffs.set(clip_startat)

				rpp_item_obj.position.set(audiopl_obj.time.position_real)
				rpp_item_obj.length.set(audiopl_obj.time.duration_real)
				rpp_item_obj.mute['mute'] = int(audiopl_obj.muted)
				if audiopl_obj.visual.color: rpp_item_obj.color.set(cvpj_color_to_reaper_color(audiopl_obj.visual.color))
				if audiopl_obj.visual.name: rpp_item_obj.name.set(audiopl_obj.visual.name)
				rpp_item_obj.volpan['vol'] = audiopl_obj.sample.vol
				rpp_item_obj.volpan['pan'] = audiopl_obj.sample.pan

				rpp_item_obj.playrate['rate'] = audiorate
				rpp_item_obj.playrate['preserve_pitch'] = int(audiopl_obj.sample.stretch.preserve_pitch)
				rpp_item_obj.playrate['pitch'] = audiopl_obj.sample.pitch

				ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sample.sampleref)
				if ref_found:
					fileref_obj = sampleref_obj.fileref
					filename = fileref_obj.get_path(None, False)
					rpp_source_obj = rpp_item_obj.source = rpp_source.rpp_source()
					if not audiopl_obj.sample.reverse: file_source(rpp_source_obj, fileref_obj, filename)
					else:
						rpp_source_obj.type = 'SECTION'
						rpp_source_obj.mode.set(3)
						rpp_insource_obj = rpp_source_obj.source = rpp_source.rpp_source()
						file_source(rpp_insource_obj, fileref_obj, filename)


			for fxid in track_obj.fxslots_audio:
				add_plugin(rpp_track_obj.fxchain, fxid, convproj_obj)

			trackdata.append(rpp_track_obj)

			tracknum += 1

		if convproj_obj.trackroute:
			for tracknum, trackid in enumerate(convproj_obj.track_order):
				if trackid in convproj_obj.trackroute:
					sends_obj = convproj_obj.trackroute[trackid]
					tracksendnum = convproj_obj.track_order.index(trackid)
					trackdata[tracknum].mainsend['tracknum'] = int(sends_obj.to_master_active)
					for target, send_obj in sends_obj.iter():
						trackrecnum = convproj_obj.track_order.index(target)
						auxrecv_obj = trackdata[trackrecnum].add_auxrecv()
						auxrecv_obj['tracknum'] = tracksendnum
						auxrecv_obj['vol'] = send_obj.params.get('amount', 1).value
						auxrecv_obj['pan'] = send_obj.params.get('pan', 0).value
		
		project_obj.save_to_file(output_file)
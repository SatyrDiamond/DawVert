# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import lxml.etree as ET
from functions import xtramath
from functions import colors
from objects.file_proj import proj_waveform
from objects.inst_params import juce_plugin
from objects import globalstore
from objects import counter
import math

def get_plugin(convproj_obj, cvpj_fxid, isinstrument):
	plugin_found, plugin_obj = convproj_obj.get_plugin(cvpj_fxid)
	if plugin_found: 
		fx_on, fx_wet = plugin_obj.fxdata_get()
		if plugin_obj.check_wildmatch('vst2', None):
			juceobj = juce_plugin.juce_plugin()
			juceobj.from_cvpj(convproj_obj, plugin_obj)

			fx_on, fx_wet = plugin_obj.fxdata_get()
			wf_plugin = proj_waveform.waveform_plugin()
			wf_plugin.enabled = int(fx_on)
			wf_plugin.params['type'] = 'vst'
			if juceobj.name: wf_plugin.params['name'] = juceobj.name
			if juceobj.filename: wf_plugin.params['filename'] = juceobj.filename
			if juceobj.manufacturer: wf_plugin.params['manufacturer'] = juceobj.manufacturer
			if juceobj.fourid: 
				wf_plugin.params['uniqueId'] = f'{juceobj.fourid:x}'
				wf_plugin.params['uid'] = f'{juceobj.fourid:x}'
			wf_plugin.params['state'] = juceobj.memoryblock
			return wf_plugin

		if plugin_obj.check_wildmatch('native-tracktion', None):
			wf_plugin = proj_waveform.waveform_plugin()
			wf_plugin.plugtype = plugin_obj.type.subtype
			wf_plugin.presetDirty = 1
			wf_plugin.enabled = fx_on
			for param_id, dset_param in globalstore.dataset.get_params('waveform', 'plugin', wf_plugin.plugtype):
				wf_plugin.params[param_id] = plugin_obj.params.get(param_id, dset_param.defv).value
			return wf_plugin
	elif isinstrument:
		wf_plugin = proj_waveform.waveform_plugin()
		wf_plugin.plugtype = '4osc'
		wf_plugin.presetDirty = 1
		return wf_plugin

def get_plugins(convproj_obj, wf_plugins, cvpj_fxids):
	for cvpj_fxid in cvpj_fxids:
		wf_plugin = get_plugin(convproj_obj, cvpj_fxid, False)
		if wf_plugin:
			wf_plugins.append(wf_plugin)

class output_waveform_edit(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def getname(self): return 'Waveform Edit'
	def getshortname(self): return 'waveform_edit'
	def gettype(self): return 'r'
	def plugin_archs(self): return None
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Waveform'
		dawinfo_obj.file_ext = 'tracktionedit'
		dawinfo_obj.placement_cut = True
		dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		dawinfo_obj.time_seconds = True
		dawinfo_obj.audio_stretch = ['rate']
		dawinfo_obj.plugin_included = ['native-tracktion']
		dawinfo_obj.plugin_ext = ['vst2']
	def parse(self, convproj_obj, output_file):
		global dataset

		convproj_obj.change_timings(4, True)

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		project_obj = proj_waveform.waveform_edit()
		project_obj.appVersion = "Waveform 11.5.18"
		project_obj.modifiedBy = "DawVert"

		bpm = convproj_obj.params.get('bpm', 140).value
		tempomul = 120/bpm

		project_obj.temposequence.tempo[0] = [bpm, 1]
		project_obj.temposequence.timesig[0] = convproj_obj.timesig

		counter_id = counter.counter(1000, '')

		get_plugins(convproj_obj, project_obj.masterplugins, convproj_obj.track_master.fxslots_audio)

		for trackid, track_obj in convproj_obj.iter_track():
			wf_track = proj_waveform.waveform_track()
			if track_obj.visual.name: wf_track.name = track_obj.visual.name
			if track_obj.visual.color: wf_track.colour ='ff'+track_obj.visual.color.get_hex()
			
			middlenote = track_obj.datavals.get('middlenote', 0)
			if middlenote != 0:
				wf_plugin = proj_waveform.waveform_plugin()
				wf_plugin.plugtype = 'midiModifier'
				wf_plugin.presetDirty = 1
				wf_plugin.params['semitonesUp'] = -middlenote
				wf_track.plugins.append(wf_plugin)

			wf_plugin = get_plugin(convproj_obj, track_obj.inst_pluginid, True)
			if wf_plugin: wf_track.plugins.append(wf_plugin)

			get_plugins(convproj_obj, wf_track.plugins, track_obj.fxslots_audio)

			for notespl_obj in track_obj.placements.pl_notes:
				wf_midiclip = proj_waveform.waveform_midiclip()
				wf_midiclip.id_num = counter_id.get()

				offset, loopstart, loopend = notespl_obj.get_loop_data()

				wf_midiclip.start = notespl_obj.position_real
				wf_midiclip.length = notespl_obj.duration_real

				if notespl_obj.cut_type == 'cut':
					wf_midiclip.offset = (offset/8)*tempomul
				elif notespl_obj.cut_type in ['loop', 'loop_off', 'loop_adv']:
					wf_midiclip.offset = (offset/8)*tempomul
					wf_midiclip.loopStartBeats = (loopstart/4)
					wf_midiclip.loopLengthBeats = (loopend/4)

				if notespl_obj.visual.name: wf_midiclip.name = notespl_obj.visual.name
				if notespl_obj.visual.color: wf_midiclip.colour = 'ff'+notespl_obj.visual.color.get_hex()
				wf_midiclip.mute = int(notespl_obj.muted)

				notespl_obj.notelist.sort()
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
					for t_key in t_keys:
						wf_note = proj_waveform.waveform_note()
						wf_note.key = t_key+60
						wf_note.pos = t_pos/4
						wf_note.dur = t_dur/4
						wf_note.vel = int(xtramath.clamp(t_vol*127, 0, 127))
						wf_midiclip.sequence.notes.append(wf_note)

				wf_track.midiclips.append(wf_midiclip)


			cvpj_track_vol = track_obj.params.get('vol', 1.0).value
			cvpj_track_pan = track_obj.params.get('pan', 0).value

			wf_plugin = proj_waveform.waveform_plugin()
			wf_plugin.plugtype = 'volume'
			wf_plugin.enabled = 1
			wf_plugin.params['volume'] = cvpj_track_vol
			wf_plugin.params['pan'] = cvpj_track_pan
			wf_track.plugins.append(wf_plugin)

			wf_plugin = proj_waveform.waveform_plugin()
			wf_plugin.plugtype = 'level'
			wf_plugin.enabled = 1
			wf_track.plugins.append(wf_plugin)

			project_obj.tracks.append(wf_track)

		project_obj.save_to_file(output_file)
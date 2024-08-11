# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import colors
from objects.file_proj import proj_waveform
from objects.inst_params import juce_plugin
from objects import globalstore
from lxml import etree
import plugins
import json
import math

def do_plugin(convproj_obj, wf_plugin, track_obj): 
	if wf_plugin.plugtype == 'vst':
		juceobj = juce_plugin.juce_plugin()
		juceobj.name = wf_plugin.params['name'] if "name" in wf_plugin.params else ''
		juceobj.filename = wf_plugin.params['filename'] if "filename" in wf_plugin.params else ''
		juceobj.manufacturer = wf_plugin.params['manufacturer'] if "manufacturer" in wf_plugin.params else ''
		juceobj.memoryblock = wf_plugin.params['state']

		plugin_obj, pluginid = juceobj.to_cvpj(convproj_obj, None)

		if plugin_obj.role == 'inst': track_obj.inst_pluginid = pluginid
		elif plugin_obj.role == 'effect': track_obj.fxslots_audio.append(pluginid)

		if pluginid:
			if wf_plugin.windowX and wf_plugin.windowY:
				windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
				windata_obj.pos_x = wf_plugin.windowX
				windata_obj.pos_y = wf_plugin.windowY

	elif wf_plugin.plugtype not in ['volume', 'level'] and wf_plugin.plugtype != '':
		plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-tracktion', wf_plugin.plugtype)
		plugin_obj.role = 'effect'

		if wf_plugin.windowX and wf_plugin.windowY:
			windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
			windata_obj.pos_x = wf_plugin.windowX
			windata_obj.pos_y = wf_plugin.windowY

		for param_id, dset_param in globalstore.dataset.get_params('waveform', 'plugin', wf_plugin.plugtype):
			paramval = wf_plugin.params[paramid] if paramid in wf_plugin.params else None
			plugin_obj.dset_param__add(param_id, paramval, dset_param)

		plugin_obj.fxdata_add(wf_plugin.enabled, 1)
		if wf_plugin.plugtype not in ['4osc']:
			track_obj.fxslots_audio.append(pluginid)
		else:
			track_obj.inst_pluginid = pluginid

autonames = {
	'PITCHBEND': 'pitch',
	'TIMBRE': 'timbre',
	'PRESSURE': 'pressure',
}

def do_track(convproj_obj, wf_track, track_obj): 
	track_obj.visual.name = wf_track.name
	#track_obj.visual.color = colors.hex_to_rgb_float(wf_track.colour)
	track_obj.visual_ui.height = wf_track.height/35.41053828354546

	vol = 1
	pan = 0

	for wf_plugin in wf_track.plugins:
		if wf_plugin.plugtype == 'volume':
			if 'volume' in wf_plugin.params: vol *= wf_plugin.params['volume']
			if 'pan' in wf_plugin.params: pan = wf_plugin.params['pan']
		else:
			do_plugin(convproj_obj, wf_plugin, track_obj)

	track_obj.params.add('vol', vol, 'float')
	track_obj.params.add('pan', pan, 'float')
	track_obj.params.add('enabled', int(not wf_track.mute), 'bool')
	track_obj.params.add('solo', wf_track.solo, 'bool')

	for midiclip in wf_track.midiclips:
		placement_obj = track_obj.placements.add_notes()

		placement_obj.position_real = midiclip.start
		placement_obj.duration_real = midiclip.length
		if midiclip.loopStartBeats == 0 and midiclip.loopLengthBeats == 0:
			if midiclip.start == 0:
				placement_obj.cut_type = 'cut'
				placement_obj.cut_start = midiclip.offset
		else:
			placement_obj.cut_loop_data(midiclip.offset, midiclip.loopStartBeats, midiclip.loopStartBeats+midiclip.loopLengthBeats)
	
		for note in midiclip.sequence.notes:
			placement_obj.notelist.add_r(note.pos*4, note.dur*4, note.key-60, note.vel/100, {})
			for a_type, a_data in note.auto.items():
				autoname = autonames[a_type] if a_type in autonames else None
				if autoname:
					for pos, val in a_data.items():
						autopoint_obj = placement_obj.notelist.last_add_auto(autoname)
						autopoint_obj.pos = pos*4
						autopoint_obj.value = val
						autopoint_obj.type = 'instant'

class input_cvpj_f(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'waveform_edit'
	def gettype(self): return 'r'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Waveform'
		dawinfo_obj.file_ext = 'tracktionedit'
		dawinfo_obj.placement_cut = True
		dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		dawinfo_obj.time_seconds = True
		dawinfo_obj.audio_stretch = ['rate']
		dawinfo_obj.auto_types = ['nopl_points']
		dawinfo_obj.plugin_included = ['native-tracktion']
		dawinfo_obj.plugin_ext = ['vst2']
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		global cvpj_l

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)

		globalstore.dataset.load('waveform', './data_main/dataset/waveform.dset')

		project_obj = proj_waveform.waveform_edit()
		project_obj.load_from_file(input_file)

		if project_obj.temposequence.tempo:
			pos, tempo = next(iter(project_obj.temposequence.tempo.items()))
			convproj_obj.params.add('bpm', tempo[0], 'float')
			for pos, tempo in project_obj.temposequence.tempo.items():
				convproj_obj.automation.add_autopoint(['main', 'bpm'], 'float', pos, tempo[0], 'normal')

		if project_obj.temposequence.timesig:
			pos, timesig = next(iter(project_obj.temposequence.timesig.items()))
			convproj_obj.timesig = timesig
			for pos, timesig in project_obj.temposequence.timesig.items():
				convproj_obj.timesig_auto.add_point(pos, timesig)

		for wf_plugin in project_obj.masterplugins:
			do_plugin(convproj_obj, wf_plugin, convproj_obj.track_master)

		tracknum = 0
		for wf_track in project_obj.tracks:
			if isinstance(wf_track, proj_waveform.waveform_track):
				track_obj = convproj_obj.add_track(str(tracknum), 'instrument', 1, False)
				do_track(convproj_obj, wf_track, track_obj)


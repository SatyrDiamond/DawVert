# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
import math
import base64

import logging
logger_input = logging.getLogger('input')

def calcsec(val, ppq):
	return (val/ppq)/50

class input_midi(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'qtractor'
	
	def get_name(self):
		return 'Qtractor'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'MThd'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj import qtractor as proj_qtractor
		convproj_obj.fxtype = 'groupreturn'
		convproj_obj.type = 'r'

		traits_obj = convproj_obj.traits
		traits_obj.audio_filetypes = ['wav']
		traits_obj.auto_types = ['nopl_ticks']
		traits_obj.notes_midi = True
		traits_obj.time_seconds = True

		convproj_obj.set_timings(4, True)

		project_obj = proj_qtractor.qtractor_project()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		ppq = project_obj.properties.ticks_per_beat
		tempo = project_obj.properties.tempo
		tempomul = tempo/120

		convproj_obj.params.add('bpm', tempo, 'float')
		
		#for audioid, filename in project_obj.files.audio_list.items():
		#	sampleref_obj = convproj_obj.sampleref__add(audioid, filename, None)

		for tracknum, qtrack in enumerate(project_obj.tracks):
			cvpj_trackid = str(tracknum)

			if qtrack.type == 'audio':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			if qtrack.type == 'midi':
				track_obj = convproj_obj.track__add(cvpj_trackid, 'instrument', 1, False)

			track_obj.visual.name = qtrack.name
			if qtrack.view.foreground_color:
				track_obj.visual.color.set_hex(qtrack.view.foreground_color)

			if qtrack.view.height:
				track_obj.visual_ui.height = qtrack.view.height/96

			track_obj.params.add('vol', qtrack.state.gain, 'float')
			track_obj.params.add('pan', qtrack.state.panning, 'float')
			track_obj.params.add('enabled', bool(not qtrack.state.mute), 'bool')
			track_obj.params.add('solo', bool(qtrack.state.solo), 'bool')

			midiauto_obj = convproj_obj.automation.create_midi_auto_obj()

			if qtrack.curve_file.used:
				midipath = os.path.join(os.path.dirname(dawvert_intent.input_file), qtrack.curve_file.filename)

				for curve_item in qtrack.curve_file.curve_items:
					if curve_item.index == 1:
						midiauto_obj.define_auto(curve_item.p_channel, curve_item.p_param, ['track', cvpj_trackid, 'pan'], -1, 1, False)
					if curve_item.index == 2:
						midiauto_obj.define_auto(curve_item.p_channel, curve_item.p_param, ['track', cvpj_trackid, 'vol'], 0, 1, False)
					if curve_item.index == 4:
						midiauto_obj.define_auto(curve_item.p_channel, curve_item.p_param, ['track', cvpj_trackid, 'enabled'], 0, 1, True)
					if curve_item.index == 5:
						midiauto_obj.define_auto(curve_item.p_channel, curve_item.p_param, ['track', cvpj_trackid, 'solo'], 0, 1, True)

				midiauto_obj.do_midi_file(midipath, 4, True, tempomul)
			#print(midiauto_obj)

			for qplug in qtrack.plugins:
				if qplug.type == 'VST2':
					plugfilename = qplug.filename
					chunkdata = None

					for config in qplug.configs:
						if config[0] == 'chunk':
							try:
								chunkdata = config[2].replace('\n', '').replace(' ', '')
							except:
								pass

					if plugfilename and chunkdata:
						plugfilename = plugfilename.replace('/', '\\')
						plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst2', 'unix')
						extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
						extmanu_obj.vst2__replace_data('path_unix', plugfilename, None, None, False)
						plugin_obj.external_info.datatype = 'chunk'
						try: plugin_obj.rawdata_add_b64('chunk', chunkdata)
						except: pass

						for param in qplug.params:
							extmanu_obj.add_param(param.index, param.value, param.name)

						track_obj.plugslots.plugin_autoplace(plugin_obj, pluginid)
						

			clipcolor = qtrack.view.background_color
			
			if qtrack.type == 'audio':
				for clip in qtrack.clips:
					placement_obj = track_obj.placements.add_audio()
					time_obj = placement_obj.time
					time_obj.position_real = calcsec(clip.properties.start, ppq)
					time_obj.duration_real = calcsec(clip.properties.length, ppq)
					placement_obj.visual.name = clip.name

					if clipcolor: placement_obj.visual.color.set_hex(clipcolor)
					filepath = clip.audioclip.filename

					pitch = math.log2(1/clip.audioclip.pitch_shift)*-12
					placement_obj.sample.pitch = pitch
					sp_obj = placement_obj.sample
					sp_obj.sampleref = filepath
					sp_obj.vol = clip.properties.gain
					sp_obj.pan = clip.properties.panning
					placement_obj.fade_in.set_dur(calcsec(clip.properties.fade_in, ppq), 'seconds')
					placement_obj.fade_out.set_dur(calcsec(clip.properties.fade_out, ppq), 'seconds')
					sampleref_obj = convproj_obj.sampleref__add(filepath, filepath, None)
					sampleref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
					
					stretch_obj = placement_obj.sample.stretch
					if clip.audioclip.time_stretch:
						stretch_obj.timing.set__real_rate(tempo, 1/clip.audioclip.time_stretch)
					stretch_obj.preserve_pitch = True

			if qtrack.type == 'midi':
				for clip in qtrack.clips:
					placement_obj = track_obj.placements.add_midi()
					time_obj = placement_obj.time
					time_obj.position_real = calcsec(clip.properties.start, ppq)
					time_obj.duration_real = calcsec(clip.properties.length, ppq)
					placement_obj.visual.name = clip.name

					if clipcolor: placement_obj.visual.color.set_hex(clipcolor)
					filepath = clip.midiclip.filename
					fileref_obj = convproj_obj.fileref__add(filepath, filepath, None)
					fileref_obj.search_local(os.path.dirname(dawvert_intent.input_file))
					placement_obj.midi_from(fileref_obj.get_path(None, False))
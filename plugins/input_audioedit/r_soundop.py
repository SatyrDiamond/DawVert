# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import struct
from functions import xtramath
from objects import globalstore
from objects.data_bytes import bytereader

def do_auto(convproj_obj, hz, autopoints, autoloc, valtype, minval, maxval):
	auto_obj = convproj_obj.automation.create(autoloc, valtype, True)
	auto_obj.is_seconds = True
	for a in autopoints:
		auto_obj.add_autopoint(a['Position']/(hz/2), xtramath.between_from_one(minval, maxval, a['Value']), None)

def do_fx(convproj_obj, fxdata):
	StateParams = fxdata.StateParams
	StateChunk = fxdata.StateChunk
	Envelops = fxdata.Envelops
	TypeID = fxdata.TypeID

	fxtype = None
	fxname = None
	fxdata = None

	if ':' in TypeID:
		numtype, numdata = TypeID.split(':', 1)
		if numtype == '2':
			fxtype = 'native'
			fxname = numdata
		if numtype == '3':
			fxtype = 'vst2'
			fxdata = numdata.split(' ', 3)
		if numtype == '4':
			fxtype = 'vst3'
			fxdata = numdata.split(' ', 3)

	if fxtype == 'native' and StateChunk:
		#try:
		if True:
			vstdataconreader = bytereader.bytereader()
			vstdataconreader.load_raw(StateChunk)
			vstdataconreader.magic_check(b'XEFD')
			unk1 = vstdataconreader.uint32()
			unk2 = vstdataconreader.uint32()
			numparams = vstdataconreader.uint32()
			fxparams = dict([[vstdataconreader.uint32(), vstdataconreader.double()] for _ in range(numparams)])

			plugin_obj, pluginid = convproj_obj.plugin__add__genid('native', 'soundop', fxname)

			for param_id, dset_param in globalstore.dataset.get_params('soundop', 'plugin', fxname):
				paramval = fxparams[dset_param.num] if param_id in fxparams else None
				plugin_obj.dset_param__add(param_id, paramval, dset_param)
	
			return pluginid

	#elif fxtype == 'vst2':
	#	if len(fxdata) == 4:
	#		vstid = int(fxdata[1])
	#		plugin_obj, pluginid = convproj_obj.plugin__add__genid('external', 'vst2', None)
	#		extmanu_obj = plugin_obj.create_ext_manu_obj(convproj_obj, pluginid)
	#		if StateChunk: 
	#			extmanu_obj.vst2__replace_data('id', vstid, StateChunk, None, False)
	#		elif StateParams: 
	#			extmanu_obj.vst2__setup_params('id', vstid, len(StateParams), None, False)
	#			for n, v in enumerate(StateParams): extmanu_obj.vst2__set_param(n, v)
	#			extmanu_obj.vst2__params_output()
		#print(fxdata)


	#print(fxdata.Name)
	#print(TypeID)
	#print(StateChunk )
	#print(StateParams )

class input_soundop(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'soundop'
	
	def get_name(self):
		return 'Soundop'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['projtype'] = 'r'

	def parse(self, convproj_obj, dawvert_intent):
		from objects.file_proj_audioedit import soundop as proj_soundop
		from objects import colors
		from objects.convproj import fileref

		convproj_obj.type = 'r'
		convproj_obj.fxtype = 'none'

		traits_obj = convproj_obj.traits
		traits_obj.auto_types = ['nopl_points']
		traits_obj.placement_loop = ['loop']
		traits_obj.time_seconds = True

		globalstore.dataset.load('soundop', './data_main/dataset/soundop.dset')

		project_obj = proj_soundop.soundop_proj()
		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()
		
		projformat = project_obj.Format

		samplerate = projformat['SampleRate'] if 'SampleRate' in projformat else 44100

		convproj_obj.set_timings(samplerate)

		sampleref_ids = {}
		for file in project_obj.Files:
			sampleref_obj = convproj_obj.sampleref__add(str(file.FileID), file.FilePath, None)
			sampleref_obj.set_hz(file.SampleRate)
			sampleref_obj.set_dur_samples(file.Length)
			sampleref_obj.set_channels(file.Channel)
			sampleref_obj.search_local(dawvert_intent.input_folder)
			sampleref_ids[file.FileID] = sampleref_obj

		for track in project_obj.Tracks:
			cvpj_trackid = str(track.ID)

			track_obj = None
			if track.Type == 0:
				autoloc_s = ['track', cvpj_trackid]
				track_obj = convproj_obj.track__add(cvpj_trackid, 'audio', 1, False)
			elif track.Type == 1:
				autoloc_s = ['master']
				track_obj = convproj_obj.track_master

			if track_obj is not None:
				#print(track_obj)
				if track.Title is not None: track_obj.visual.name = track.Title
				if track.Solo is not None: track_obj.params.add('solo', track.Solo, 'bool')
				if track.Height is not None and track.HeightOrg is not None: 
					if track.HeightOrg and track.Height:
						track_obj.visual_ui.height = track.Height/track.HeightOrg

				if track.Hue is not None: 
					track_obj.visual.color.set_hsv(track.Hue/360, 0.8, 1)
					track_obj.visual.color.fx_allowed = ['saturate', 'brighter']

				for x in track.EffectData.Effects:
					StateParams = x.StateParams
					StateChunk = x.StateChunk
					Envelops = x.Envelops
					TypeID = x.TypeID
					pluginid = do_fx(convproj_obj, x)
					if pluginid: track_obj.plugslots.slots_audio.append(pluginid)

				for x in track.EffectData.FixedEffects:
					StateParams = x.StateParams
					Envelops = x.Envelops

					if x.Name == 'Volume':
						if StateParams: track_obj.params.add('vol', StateParams[0], 'float')
						if Envelops:
							if 'Points' in Envelops[0]:
								do_auto(
									convproj_obj, samplerate, Envelops[0]['Points'], 
									autoloc_s+['vol'], 'float', 0, 1
									)
					if x.Name == 'Pan':
						if StateParams: track_obj.params.add('pan', (StateParams[0]-0.5)*2, 'float')
						auto_obj = convproj_obj.automation.create(['track', cvpj_trackid, 'vol'], 'float', True)
						if Envelops:
							if 'Points' in Envelops[0]:
								do_auto(
									convproj_obj, samplerate, Envelops[0]['Points'], 
									autoloc_s+['pan'], 'float', -1, 1
									)
					if x.Name == 'Mute':
						if StateParams: track_obj.params.add('enabled', not int(StateParams[0]), 'bool')


				for clip in track.data_clips:
					sampleref_obj = sampleref_ids[clip.FileID]
					hz = sampleref_obj.get_hz()
					dur_samples = sampleref_obj.get_dur_samples()

					placement_obj = track_obj.placements.add_audio()

					time_obj = placement_obj.time
					time_obj.set_posdur_real(clip.TrackPos/samplerate, clip.Length/samplerate)
					time_obj.set_offset_real(clip.FilePos/hz)

					sp_obj = placement_obj.sample
					sp_obj.sampleref = str(clip.FileID)
					sp_obj.vol = clip.Gain

					placement_obj.visual.name = clip.Title
					placement_obj.muted = clip.Mute

					if clip.Hue is not None and clip.UseHue: 
						placement_obj.visual.color.set_hsv(clip.Hue/360, 0.8, 1)
						placement_obj.visual.color.fx_allowed = ['saturate', 'brighter']


					if 'Length' in clip.FadeIn: placement_obj.fade_in.set_dur(clip.FadeIn['Length']/hz, 'seconds')
					if 'Length' in clip.FadeOut: placement_obj.fade_out.set_dur(clip.FadeOut['Length']/hz, 'seconds')

					StretchData = clip.StretchData

					actuallen = dur_samples
					stretchsize = 0
					stretch_obj = sp_obj.stretch
					stretch_obj.preserve_pitch = True
					#if 'Stretch' in StretchData:
					#	stretchsize = StretchData['Stretch']
					#	stretch_obj.timing.set__real_rate(120, stretchsize)
					#	actuallen = StretchData['Length']
					#	time_obj.set_offset_real((clip.FilePos/hz)/stretchsize)
					#else:
					#	time_obj.set_offset_real(clip.FilePos/hz)
					if 'Pitch' in StretchData: sp_obj.pitch = StretchData['Pitch']
					if clip.Loop: time_obj.set_loop_data(clip.FilePos*2, 0, actuallen*2)
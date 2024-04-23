# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import data_values
from objects import dv_dataset
from functions_plugin_ext import plugin_vst2
from functions_plugin_ext import plugin_vst3
from objects_proj import proj_ableton
from functions_plugin import ableton_values
from objects import auto_id

from io import BytesIO
import base64
import struct
import xml.etree.ElementTree as ET
import plugin_input
import json
import gzip
import math
import os

colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]

def get_sampleref(convproj_obj, alssampleref_obj):
	filename = alssampleref_obj.FileRef.Path
	sampleref_obj = convproj_obj.add_sampleref(filename, filename)
	sampleref_obj.dur_samples = alssampleref_obj.DefaultDuration
	sampleref_obj.hz = alssampleref_obj.DefaultSampleRate
	sampleref_obj.timebase = sampleref_obj.hz
	sampleref_obj.dur_sec = sampleref_obj.dur_samples / sampleref_obj.hz
	return filename

def get_param(alsparam, varname, vartype, i_fallback, i_loc, i_addmul): 
	global autoid_assoc
	out_value = alsparam.Manual if alsparam.exists else i_fallback
	if alsparam.AutomationTarget.exists: autoid_assoc.define(alsparam.AutomationTarget.id, i_loc, vartype, i_addmul)
	return out_value

def alsparam(dictdata, name):
	return [int(dictdata[name+x][1]) for x in ['Min','Max']]

def do_devices(x_trackdevices, track_id, track_obj, convproj_obj):
	global vector_shapesdata
	for device in x_trackdevices:
		is_instrument = False

		able_plug_id = str(device.id)
		if track_id != None: pluginid = track_id+'_'+able_plug_id
		else: pluginid = 'master_'+able_plug_id

		if device.name in ['OriginalSimpler', 'MultiSampler']:
			track_obj.inst_pluginid = pluginid

			SampleParts = device.params['Player/MultiSampleMap/SampleParts']

			numzones = len(SampleParts[1])

			if numzones > 1:
				for n, p in SampleParts[1].items():
					plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
					plugin_obj.role = 'synth'
	
					MultiSamplePart = p[0]
					samplerefid = get_sampleref(convproj_obj, MultiSamplePart['MultiSamplePart/SampleRef'][1])
	
					key_r = alsparam(MultiSamplePart, 'MultiSamplePart/KeyRange/')
					key_cf = alsparam(MultiSamplePart, 'MultiSamplePart/KeyRange/Crossfade')
					vel_r = alsparam(MultiSamplePart, 'MultiSamplePart/VelocityRange/')
					vel_cf = alsparam(MultiSamplePart, 'MultiSamplePart/VelocityRange/Crossfade')
	
					regionparams = {}
					regionparams['name'] = MultiSamplePart['MultiSamplePart/Name'][1]
					regionparams['key_fade'] = [key_cf[0]-key_r[0], key_r[1]-key_cf[1]]
					regionparams['r_vel'] = [x/127 for x in vel_r]
					regionparams['r_vel_fade'] = [x/127 for x in vel_cf]
	
					regionparams['middlenote'] = int(MultiSamplePart['MultiSamplePart/RootKey'][1])-60
					regionparams['volume'] = float(MultiSamplePart['MultiSamplePart/Volume'][1])
					regionparams['pan'] = float(MultiSamplePart['MultiSamplePart/Panorama'][1])
	
					for xmlname, dictname in [['MultiSamplePart/SustainLoop/', 'loop_sustain'], ['MultiSamplePart/ReleaseLoop/', 'loop']]:
						xv_Start = int(MultiSamplePart[xmlname+'Start'][1])
						xv_End = int(MultiSamplePart[xmlname+'End'][1])
						xv_Mode = int(MultiSamplePart[xmlname+'Mode'][1])
						xv_Crossfade = int(MultiSamplePart[xmlname+'Crossfade'][1])
						xv_Detune = int(MultiSamplePart[xmlname+'Detune'][1])
						loopdata = {}
						if xv_Mode == 0: loopdata['enabled'] = 0
						else:
							loopdata['enabled'] = 1
							loopdata['mode'] = 'normal'
							loopdata['points'] = [xv_Start, xv_End]
							loopdata['crossfade'] = xv_Crossfade
							loopdata['detune'] = xv_Detune
						regionparams[dictname] = loopdata
	
						if dictname == 'loop':
							regionparams['start'] = int(MultiSamplePart['MultiSamplePart/SampleStart'][1])
							regionparams['end'] = int(MultiSamplePart['MultiSamplePart/SampleEnd'][1])
	
					plugin_obj.regions.add(key_r[0]-60, key_r[1]-60, regionparams)

			elif numzones == 1:
				for n, p in SampleParts[1].items():
					MultiSamplePart = p[0]

					middlenote = int(MultiSamplePart['MultiSamplePart/RootKey'][1])
					track_obj.datavals.add('middlenote', middlenote-60)

					file_path = get_sampleref(convproj_obj, MultiSamplePart['MultiSamplePart/SampleRef'][1])
					sampleref_obj = convproj_obj.add_sampleref(file_path, file_path)
					plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'single')
					plugin_obj.role = 'synth'
					plugin_obj.samplerefs['sample'] = file_path

					plugin_obj.datavals.add('point_value_type', "samples")

					for xmlname, dictname in [['MultiSamplePart/SustainLoop/', 'loop_sustain'], ['MultiSamplePart/ReleaseLoop/', 'loop']]:
						xv_Start = int(MultiSamplePart[xmlname+'Start'][1])
						xv_End = int(MultiSamplePart[xmlname+'End'][1])
						xv_Mode = int(MultiSamplePart[xmlname+'Mode'][1])
						xv_Crossfade = int(MultiSamplePart[xmlname+'Crossfade'][1])
						xv_Detune = int(MultiSamplePart[xmlname+'Detune'][1])
						loopdata = {}

						if xv_Mode == 0: loopdata['enabled'] = 0
						else:
							loopdata['enabled'] = 1
							loopdata['mode'] = 'normal'
							loopdata['points'] = [xv_Start, xv_End]
							loopdata['crossfade'] = xv_Crossfade
							loopdata['detune'] = xv_Detune
						plugin_obj.datavals.add(dictname, loopdata)

						if dictname == 'loop':
							plugin_obj.datavals.add('start', int(MultiSamplePart['MultiSamplePart/SampleStart'][1]))
							plugin_obj.datavals.add('end', int(MultiSamplePart['MultiSamplePart/SampleEnd'][1]))

		elif device.name == 'PluginDevice':
			track_obj.inst_pluginid = pluginid

			PluginDesc = device.params['PluginDesc'][1][0][0]

			pluginvsttype = 0
			if 'VstPluginInfo/UniqueId' in PluginDesc:
				pluginvsttype = 0

				vst_WinPosX = int(PluginDesc['VstPluginInfo/WinPosX'][1])
				vst_WinPosY = int(PluginDesc['VstPluginInfo/WinPosY'][1])
				vst_Path = PluginDesc['VstPluginInfo/Path'][1].replace('/','\\')
				vst_PlugName = PluginDesc['VstPluginInfo/PlugName']
				vst_UniqueId = int(PluginDesc['VstPluginInfo/UniqueId'][1])
				vst_NumberOfParameters = int(PluginDesc['VstPluginInfo/NumberOfParameters'][1])
				vst_NumberOfPrograms = int(PluginDesc['VstPluginInfo/NumberOfPrograms'][1])
				pluginvsttype = int(PluginDesc['VstPluginInfo/Category'][1])
				vst_flags = int(PluginDesc['VstPluginInfo/Flags'][1])
				binflags = data_bytes.to_bin(vst_flags, 32)
				useschunk = binflags[21]

				plugin_obj = convproj_obj.add_plugin(pluginid, 'vst2', 'win')
				windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
				windata_obj.pos_x = vst_WinPosX
				windata_obj.pos_y = vst_WinPosY

				convproj_obj.add_fileref(vst_Path, vst_Path)
				plugin_obj.filerefs['plugin'] = vst_Path

				plugin_obj.datavals.add('fourid', vst_UniqueId)
				plugin_obj.datavals.add('numparams', vst_NumberOfParameters)

				vst_version = int(PluginDesc['VstPluginInfo/Version'][1])
				plugin_obj.datavals.add('version_bytes', list(struct.unpack('BBBB', struct.pack('i', vst_version))) )

				Preset = PluginDesc['VstPluginInfo/Preset'][1]
				Preset = PluginDesc['VstPluginInfo/Preset'][1][list(Preset)[0]][0]

				plugin_obj.datavals.add('current_program', int(Preset['VstPreset/ProgramNumber'][1]))

				Buffer = Preset['VstPreset/Buffer'][1]
				if Buffer:
					if useschunk: 
						plugin_obj.datavals.add('datatype', 'chunk')
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, vst_UniqueId, 'chunk', Buffer, None)
					else:
						rawstream = BytesIO(Buffer)
						plugin_obj.datavals.add('datatype', 'params')
						cvpj_programs = []
						for num in range(vst_NumberOfPrograms):
							cvpj_program = {}
							cvpj_program['datatype'] = 'params'
							cvpj_program['numparams'] = vst_NumberOfParameters
							cvpj_program['params'] = {}
							cvpj_program['program_name'] = data_bytes.readstring_fixedlen(rawstream, 28, None)
							for paramnum in range(vst_NumberOfParameters): cvpj_program['params'][str(paramnum)] = {'value': struct.unpack('f', rawstream.read(4))[0]}
							cvpj_programs.append(cvpj_program)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id' ,None, vst_UniqueId, 'bank', cvpj_programs, None)

			if 'Vst3PluginInfo/Preset' in PluginDesc:
				vst_DeviceType = int(PluginDesc['Vst3PluginInfo/DeviceType'][1])
				vst_WinPosX = int(PluginDesc['Vst3PluginInfo/WinPosX'][1])
				vst_WinPosY = int(PluginDesc['Vst3PluginInfo/WinPosY'][1])

				plugin_obj = convproj_obj.add_plugin(pluginid, 'vst3', 'win')
				windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
				windata_obj.pos_x = vst_WinPosX
				windata_obj.pos_y = vst_WinPosY

				Preset = PluginDesc['Vst3PluginInfo/Preset'][1]
				Preset = PluginDesc['Vst3PluginInfo/Preset'][1][list(Preset)[0]][0]

				Fields_0 = int(Preset['Vst3Preset/Uid/Fields.0'][1])
				Fields_1 = int(Preset['Vst3Preset/Uid/Fields.1'][1])
				Fields_2 = int(Preset['Vst3Preset/Uid/Fields.2'][1])
				Fields_3 = int(Preset['Vst3Preset/Uid/Fields.3'][1])

				hexuuid = struct.pack('>iiii', Fields_0, Fields_1, Fields_2, Fields_3).hex().upper()
				
				ProcessorState = Preset['Vst3Preset/ProcessorState'][1]

				plugin_obj.datavals.add('id', hexuuid)
				plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, hexuuid, ProcessorState)

			if pluginvsttype == 2:
				plugin_obj.role = 'inst'
				track_obj.inst_pluginid = pluginid
			elif pluginvsttype == 1:
				plugin_obj.role = 'effect'
				track_obj.fxslots_audio.append(pluginid)

		else:
			plugin_obj = convproj_obj.add_plugin(pluginid, 'native-ableton', device.name)
			plugin_obj.role = 'effect'

			paramlist = dataset.params_list('plugin', device.name)
			device_type = dataset.object_var_get('group', 'plugin', device.name)
			if device_type[1] == 'inst': track_obj.inst_pluginid = pluginid

			if paramlist:
				for paramfullname in paramlist:
					defparams = dataset.params_i_get('plugin', device.name, paramfullname)
					
					if defparams[1] != 'list': 
						if paramfullname in device.params:
							if not defparams[0]:
								outval = get_param(device.params[paramfullname][1], defparams[5], defparams[1], 0, ['plugin', pluginid], None)
							else:
								outval = device.params[paramfullname][1]
								if defparams[1] == 'int': outval = int(outval)
								if defparams[1] == 'float': outval = float(outval)
								if defparams[1] == 'bool': outval = (outval == 'true')
							plugin_obj.add_from_dset(paramfullname, outval, dataset, 'plugin', device.name)
					#else:
					#	print(defparams)

			if plugin_obj.role == 'effect':
				track_obj.fxslots_audio.append(pluginid)

class input_ableton(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'ableton'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.name = 'Ableton Live 11'
		dawinfo_obj.file_ext = 'als'
		dawinfo_obj.placement_cut = True
		dawinfo_obj.placement_loop = ['loop', 'loop_off', 'loop_adv']
		dawinfo_obj.audio_stretch = ['warp']
		dawinfo_obj.auto_types = ['nopl_points']
		dawinfo_obj.plugin_included = ['sampler:single','synth-nonfree:europa','native-soundation']

	def parse(self, convproj_obj, input_file, dv_config):
		global abletondatadef_params
		global abletondatadef_data
		global dataset
		global autoid_assoc
		global vector_shapesdata
		
		vector_shapesdata = None

		xmlstring = ""

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)
		autoid_assoc = auto_id.convproj2autoid(4, True)

		dataset = dv_dataset.dataset('./data_dset/ableton.dset')

		project_obj = proj_ableton.ableton_liveset()
		project_obj.load_from_file(input_file)

		abletondatadef_params = ableton_values.devicesparam()
		abletondatadef_data = ableton_values.devicesdata()

		mastermixer = project_obj.MasterTrack.DeviceChain.Mixer

		mas_track_vol = get_param(mastermixer.Volume, 'Volume', 'float', 0, ['master', 'vol'], None)
		mas_track_pan = get_param(mastermixer.Pan, 'Pan', 'float', 0, ['master', 'pan'], None)
		tempo = get_param(mastermixer.Tempo, 'Tempo', 'float', 120, ['main', 'bpm'], None)
		tempomul = tempo/120

		convproj_obj.track_master.visual.name = project_obj.MasterTrack.Name.EffectiveName
		convproj_obj.track_master.visual.color = colorlist_one[int(project_obj.MasterTrack.Color)]
		convproj_obj.track_master.params.add('vol', mas_track_vol, 'float')
		convproj_obj.track_master.params.add('pan', mas_track_pan, 'float')
		convproj_obj.params.add('bpm', tempo, 'float')
		do_devices(project_obj.MasterTrack.DeviceChain.devices, None, convproj_obj.track_master, convproj_obj)

		returnid = 1

		for tracktype, als_track in project_obj.Tracks:
			track_mixer = als_track.DeviceChain.Mixer

			track_id = str(als_track.Id)
			track_name = als_track.Name.EffectiveName
			track_color = colorlist_one[als_track.Color]
			track_inside_group = als_track.TrackGroupId
			track_sendholders = track_mixer.Sends

			fxloc = None

			if tracktype == 'midi':
				fxloc = ['track', track_id]
				track_vol = get_param(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = get_param(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)

				track_obj = convproj_obj.add_track(track_id, 'instrument', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

				for clipid, cliptype, clipobj in als_track.DeviceChain.MainSequencer.ClipTimeable.Events:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.position = clipobj.CurrentStart*4
					placement_obj.duration = clipobj.CurrentEnd*4 - placement_obj.position
					placement_obj.visual.name = clipobj.Name
					placement_obj.visual.color = colorlist_one[clipobj.Color]
					placement_obj.muted = clipobj.Disabled

					if clipobj.Loop.LoopOn == 1:
						placement_obj.cut_loop_data(clipobj.Loop.StartRelative*4, clipobj.Loop.LoopStart*4, clipobj.Loop.LoopEnd*4)
					else:
						placement_obj.cut_type = 'cut'
						placement_obj.cut_data['start'] = clipobj.Loop.LoopStart

					t_notes_auto = {}
					for nid, nes in clipobj.Notes.PerNoteEventStore.items():
						points = []
						for e in nes.Events: points.append([e.TimeOffset*4, e.Value])
						if nes.NoteId not in t_notes_auto: t_notes_auto[nes.NoteId] = {}
						t_notes_auto[nes.NoteId][nes.CC] = points

					for nid, kt in clipobj.Notes.KeyTrack.items():
						for event in kt.NoteEvents:
							t_note_id = event.NoteId
							t_note_extra = {}
							t_note_extra['off_vol'] = event.OffVelocity/100
							t_note_extra['probability'] = event.Probability
							t_note_extra['enabled'] = event.IsEnabled
							placement_obj.notelist.add_r(event.Time*4, event.Duration*4, kt.MidiKey-60, event.Velocity/100, t_note_extra)
							if t_note_id in t_notes_auto:
								for atype, adata in t_notes_auto[t_note_id].items():
									for autopoints in adata:
										autopoint_obj = placement_obj.notelist.last_add_auto('pitch')
										autopoint_obj.pos = autopoints[0]
										autopoint_obj.value = autopoints[1]/170 if atype == -2 else autopoints[1]

			elif tracktype == 'audio':
				fxloc = ['track', track_id]
				track_vol = get_param(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = get_param(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)

				track_obj = convproj_obj.add_track(track_id, 'audio', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)
				
				for clipid, cliptype, clipobj in als_track.DeviceChain.MainSequencer.ClipTimeable.Events:
					placement_obj = track_obj.placements.add_audio()
					placement_obj.position = clipobj.CurrentStart*4
					placement_obj.duration = clipobj.CurrentEnd*4 - placement_obj.position
					placement_obj.visual.name = clipobj.Name
					placement_obj.visual.color = colorlist_one[clipobj.Color]
					placement_obj.muted = clipobj.Disabled
					placement_obj.vol = clipobj.SampleVolume
					placement_obj.sampleref = get_sampleref(convproj_obj, clipobj.SampleRef)

					if clipobj.Loop.LoopOn:
						placement_obj.cut_loop_data(clipobj.Loop.StartRelative*4, clipobj.Loop.LoopStart*4, clipobj.Loop.LoopEnd*4)
					else:
						placement_obj.cut_type = 'cut'
						placement_obj.cut_data['start'] = clipobj.Loop.LoopStart

					audio_placement_PitchCoarse = clipobj.PitchCoarse
					audio_placement_PitchFine = clipobj.PitchFine
					placement_obj.pitch = audio_placement_PitchCoarse + audio_placement_PitchFine/100

					if clipobj.Fade:
						placement_obj.fade_in['duration'] = clipobj.Fades.FadeInLength*8
						placement_obj.fade_in['skew'] = clipobj.Fades.FadeInCurveSkew
						placement_obj.fade_in['slope'] = clipobj.Fades.FadeInCurveSlope
						placement_obj.fade_out['duration'] = clipobj.Fades.FadeOutLength*8
						placement_obj.fade_out['skew'] = clipobj.Fades.FadeOutCurveSkew
						placement_obj.fade_out['slope'] = clipobj.Fades.FadeOutCurveSlope

					if clipobj.IsWarped:
						placement_obj.stretch.is_warped = True
						placement_obj.stretch.params = {}
						if clipobj.WarpMode == 0:
							placement_obj.stretch.algorithm = 'beats'
							placement_obj.stretch.params['TransientResolution'] = clipobj.TransientResolution
							placement_obj.stretch.params['TransientLoopMode'] = clipobj.TransientLoopMode
							placement_obj.stretch.params['TransientEnvelope'] = clipobj.TransientEnvelope
						if clipobj.WarpMode == 1:
							placement_obj.stretch.algorithm = 'ableton_tones'
							placement_obj.stretch.params['GranularityTones'] = clipobj.GranularityTones
						if clipobj.WarpMode == 2:
							placement_obj.stretch.algorithm = 'ableton_texture'
							placement_obj.stretch.params['GranularityTexture'] = clipobj.GranularityTexture
							placement_obj.stretch.params['FluctuationTexture'] = clipobj.FluctuationTexture
						if clipobj.WarpMode == 3:
							placement_obj.stretch.algorithm = 'resample'
						if clipobj.WarpMode == 4:
							placement_obj.stretch.algorithm = 'ableton_complex'
						if clipobj.WarpMode == 6:
							placement_obj.stretch.algorithm = 'stretch_complexpro'
							placement_obj.stretch.params['ComplexProFormants'] = clipobj.ComplexProFormants
							placement_obj.stretch.params['ComplexProEnvelope'] = clipobj.ComplexProEnvelope

						for _, WarpMarker in clipobj.WarpMarkers.items():
							warp_pos = WarpMarker.BeatTime*4
							warp_pos_real = WarpMarker.SecTime
							placement_obj.stretch.warp.append([warp_pos, warp_pos_real])
					else:
						pitchcalc = math.pow(2, placement_obj.pitch/12)
						placement_obj.stretch.is_warped = False
						placement_obj.stretch.set_rate_speed(tempo, pitchcalc, True)
						placement_obj.stretch.uses_tempo = False

					if not clipobj.IsWarped:
						if clipobj.Loop.LoopOn == 0:
							placement_obj.cut_type = 'cut'
							pitchcalc = math.pow(2, placement_obj.pitch/12)
							placement_obj.cut_data['start'] = (clipobj.Loop.LoopStart*8/pitchcalc)*tempomul
							placement_obj.duration *= pitchcalc
							placement_obj.duration /= tempomul
							placement_obj.duration /= placement_obj.stretch.calc_tempo_speed
					else:
						if clipobj.Loop.LoopOn == 0:
							placement_obj.cut_type = 'cut'
							placement_obj.cut_data['start'] = clipobj.Loop.LoopStart*4
						else:
							placement_obj.cut_type = 'loop'
							placement_obj.cut_data['start'] = clipobj.Loop.StartRelative*4
							placement_obj.cut_data['loopstart'] = clipobj.Loop.LoopStart*4
							placement_obj.cut_data['loopend'] = clipobj.Loop.LoopEnd*4

			elif tracktype == 'return':
				cvpj_returntrackid = 'return_'+str(returnid)
				fxloc = ['return', cvpj_returntrackid]
				track_vol = get_param(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = get_param(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)
				track_obj = convproj_obj.track_master.add_return(cvpj_returntrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				returnid += 1

			elif tracktype == 'group':
				cvpj_grouptrackid = 'group_'+str(track_id)
				fxloc = ['group', cvpj_grouptrackid]
				track_vol = get_param(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = get_param(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)

				track_obj = convproj_obj.add_group(cvpj_grouptrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

			sendcount = 1
			if fxloc != None:
				for _, track_sendholder in track_sendholders.items():
					sendid = sendcount
					sendautoid = 'send_'+track_id+'_'+str(sendid)
					sendlevel = get_param(track_sendholder.Send, 'Send', 'float', 0, ['send', sendautoid, 'amount'], None)
					#track_obj.sends.add('return_'+str(sendid), sendautoid, sendlevel)
					sendcount += 1

			do_devices(als_track.DeviceChain.devices, track_id, track_obj, convproj_obj)

		#exit()
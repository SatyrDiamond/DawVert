# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from objects import globalstore

from io import BytesIO
import numpy as np
import struct
import plugins
import gzip
import os

DEBUG_DISABLE_PLACEMENTS = False
DEBUG_DISABLE_SAMPLER = False
	
def get_sampleref(convproj_obj, alssampleref_obj):
	filename = alssampleref_obj.FileRef.Path
	sampleref_obj = convproj_obj.add_sampleref(filename, filename, 'win')
	sampleref_obj.dur_samples = alssampleref_obj.DefaultDuration
	sampleref_obj.hz = alssampleref_obj.DefaultSampleRate
	sampleref_obj.timebase = sampleref_obj.hz
	sampleref_obj.dur_sec = sampleref_obj.dur_samples / sampleref_obj.hz
	return filename

def doparam(alsparam, varname, vartype, i_fallback, i_loc, i_addmul): 
	global autoid_assoc
	out_value = alsparam.Manual if alsparam.exists else i_fallback
	if alsparam.AutomationTarget.exists: autoid_assoc.define(alsparam.AutomationTarget.id, i_loc, vartype, i_addmul)
	return out_value

def alsparam(dictdata, name):
	return [int(dictdata[name+x][1]) for x in ['Min','Max']]

def findlists(parampaths):
	outpaths = {}
	for p, v in parampaths.items():
		if '.' in p:
			orgparamname = p.rsplit('.', 1)
			if orgparamname[-1].isnumeric():
				if orgparamname[0] not in outpaths: outpaths[orgparamname[0]] = {}
				outpaths[orgparamname[0]][int(orgparamname[-1])] = v

	parsedout = {}
	for p, v in outpaths.items():
		v = dict(sorted(v.items()))
		allnums = list(v)
		alltypes = [x.type for n, x in v.items()]
		allvals = [x.value for n, x in v.items()]

		isvalid = not False in [n==x for n, x in enumerate(allnums)]
		typesame = all(t == alltypes[0] for t in alltypes)

		if isvalid and typesame:
			if alltypes[0] == 'param': parsedout[p] = [float(x) for n, x in v.items()]
			if alltypes[0] == 'value': 
				allisnum = [x.replace('.', '').isnumeric() for x in allvals]
				if not False in allisnum: parsedout[p] = [float(x) for n, x in v.items()]
			if alltypes[0] == 'bool': parsedout[p] = [bool(x) for n, x in v.items()]

	return parsedout

def do_samplepart(convproj_obj, sp_obj, SamplePart):
	samplerefid = get_sampleref(convproj_obj, SamplePart.SampleRef)
	sp_obj.sampleref = samplerefid
	sp_obj.point_value_type = "samples"
	sp_obj.start = float(SamplePart.SampleStart)
	sp_obj.end = float(SamplePart.SampleEnd)
	sp_obj.loop_start = float(SamplePart.SustainLoop.Start)
	sp_obj.loop_end = float(SamplePart.SustainLoop.End)
	sp_obj.loop_active = int(SamplePart.SustainLoop.Mode)!=0
	if SamplePart.SustainLoop.Mode == 2: sp_obj.loop_mode = 'pingpong'
	sp_obj.loop_data['crossfade'] = float(SamplePart.SustainLoop.Crossfade)
	sp_obj.loop_data['detune'] = float(SamplePart.SustainLoop.Detune)
	sp_obj.pan = float(SamplePart.Panorama)
	sp_obj.vol = float(SamplePart.Volume)
	return samplerefid

def do_automation(convproj_obj, AutomationEnvelopes):
	for _, env in AutomationEnvelopes.Envelopes.items():
		if env.Automation.Events:
			cvpj_autotype = None
			als_autotype = env.Automation.Events[0][1]
			if als_autotype == 'FloatEvent': cvpj_autotype = 'float'
			if als_autotype == 'BoolEvent': cvpj_autotype = 'bool'
			if cvpj_autotype:
				for _,_,alsevent in env.Automation.Events:
					convproj_obj.automation.add_autopoint(['id',str(env.PointeeId)], cvpj_autotype, alsevent.Time*4, alsevent.Value, 'normal' if cvpj_autotype != 'bool' else 'instant')

			if env.PointeeId == timesigid and als_autotype == 'EnumEvent':
				for _,_,alsevent in env.Automation.Events:
					if alsevent.Time > 0:
						convproj_obj.timesig_auto.add_point(alsevent.Time*4, [(alsevent.Value%99)+1, 2**(alsevent.Value//99)])
					else:
						convproj_obj.timesig = [(alsevent.Value%99)+1, 2**(alsevent.Value//99)]

def do_devices(x_trackdevices, track_id, track_obj, convproj_obj):
	from functions_plugin_ext import plugin_vst2
	from functions_plugin_ext import plugin_vst3

	global vector_shapesdata

	middlenote = 0
	issampler = False

	for device in x_trackdevices:
		is_instrument = False

		able_plug_id = str(device.id)
		if track_id != None: pluginid = track_id+'_'+able_plug_id
		else: pluginid = 'master_'+able_plug_id

		doparam(device.On, 'On', 'bool', 1, ['slot', pluginid, 'enabled'], None)

		parampaths = device.params.get_all_keys([])

		if device.name == 'MidiPitcher':
			Pitch = parampaths['Pitch']
			middlenote -= int(Pitch)

		if device.name in ['OriginalSimpler', 'MultiSampler'] and not DEBUG_DISABLE_SAMPLER:
			issampler = True
			track_obj.inst_pluginid = pluginid
			SampleParts = parampaths['Player/MultiSampleMap/SampleParts']

			plugin_obj = None
			numzones = len(SampleParts.value)

			if numzones == 1:
				SamplePart = SampleParts.value[next(iter(SampleParts.value))]
				middlenote = int(SamplePart.RootKey)-60
				track_obj.datavals.add('middlenote', middlenote-60)
				plugin_obj, sampleref_obj, sp_obj = convproj_obj.add_plugin_sampler(pluginid, None, None)
				do_samplepart(convproj_obj, sp_obj, SamplePart)
				sp_obj.reverse = int(parampaths['Player/Reverse'])
				sp_obj.vol = float(SamplePart.Volume)
				sp_obj.pan = float(SamplePart.Panorama)

			elif numzones>1:
				plugin_obj = convproj_obj.add_plugin(pluginid, 'universal', 'sampler', 'multi')
				plugin_obj.role = 'synth'
				for num, SamplePart in SampleParts.value.items():
					key_r = [int(SamplePart.KeyRange.Min), int(SamplePart.KeyRange.Max)]
					key_cf = [int(SamplePart.KeyRange.CrossfadeMin), int(SamplePart.KeyRange.CrossfadeMax)]
					vel_r = [int(SamplePart.VelocityRange.Min), int(SamplePart.VelocityRange.Max)]
					vel_cf = [int(SamplePart.VelocityRange.CrossfadeMin), SamplePart.VelocityRange.CrossfadeMax]
					middlenote = int(SamplePart.RootKey)
					sp_obj = plugin_obj.sampleregion_add(key_r[0]-60, key_r[1]-60, middlenote-60, None)
					do_samplepart(convproj_obj, sp_obj, SamplePart)
					sp_obj.reverse = float(parampaths['Player/Reverse'])
					sp_obj.data['key_fade'] = [key_cf[0]-key_r[0], key_r[1]-key_cf[1]]
					sp_obj.data['r_vel_fade'] = [x/127 for x in vel_cf]
					sp_obj.vel_min = vel_r[0]/127
					sp_obj.vel_max = vel_r[1]/127
					sp_obj.vol = float(SamplePart.Volume)
					sp_obj.pan = float(SamplePart.Panorama)

			if plugin_obj:
				envstarttxt = 'VolumeAndPan/Envelope/'
				AttackTime = float(parampaths[envstarttxt+'AttackTime']) if envstarttxt+'AttackTime' in parampaths else 0
				DecayTime = float(parampaths[envstarttxt+'DecayTime']) if envstarttxt+'DecayTime' in parampaths else 0
				SustainLevel = float(parampaths[envstarttxt+'SustainLevel']) if envstarttxt+'SustainLevel' in parampaths else 1
				ReleaseTime = float(parampaths[envstarttxt+'ReleaseTime']) if envstarttxt+'ReleaseTime' in parampaths else 0
				plugin_obj.env_asdr_add('vol', 0, AttackTime/1000, 0, DecayTime/1000, SustainLevel, ReleaseTime/1000, 1)

		elif device.name == 'PluginDevice':

			PluginDesc = parampaths['PluginDesc']

			pluginvsttype = 0
			if '0/VstPluginInfo' in PluginDesc:
				VstPluginInfo = PluginDesc['0/VstPluginInfo']
				pluginvsttype = 0

				vst_PlugName = str(VstPluginInfo['PlugName'])
				vst_UniqueId = int(VstPluginInfo['UniqueId'])
				vst_NumberOfParameters = int(VstPluginInfo['NumberOfParameters'])
				vst_NumberOfPrograms = int(VstPluginInfo['NumberOfPrograms'])
				pluginvsttype = int(VstPluginInfo['Category'])
				vst_flags = int(VstPluginInfo['Flags'])
				binflags = data_bytes.get_bitnums_int(vst_flags)

				plugin_obj = convproj_obj.add_plugin(pluginid, 'external', 'vst2', 'win')
				windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
				windata_obj.pos_x = int(VstPluginInfo['WinPosX'])
				windata_obj.pos_y = int(VstPluginInfo['WinPosY'])

				if 'Path' in VstPluginInfo:
					vst_Path = str(VstPluginInfo['Path']).replace('/','\\')
					convproj_obj.add_fileref(vst_Path, vst_Path, 'win')
					plugin_obj.filerefs['plugin'] = vst_Path

				plugin_obj.datavals_global.add('fourid', vst_UniqueId)
				plugin_obj.datavals_global.add('numparams', vst_NumberOfParameters)

				vst_version = int(VstPluginInfo['Version'])
				plugin_obj.datavals_global.add('version_bytes', vst_version)

				Preset = VstPluginInfo['Preset']
				Preset = VstPluginInfo['Preset'][list(Preset)[0]]

				prognum = int(Preset['ProgramNumber'])
				
				dtype_vstnames = np.zeros(vst_NumberOfParameters, np.dtype([('name', '<U32')]))
				for n, param_data in parampaths['ParameterList'].items():
					param_id = int(param_data['ParameterId'])
					if param_id != -1: dtype_vstnames[param_id] = param_data['ParameterName']

				Buffer = Preset['Buffer'].value

				if Buffer:
					if 10 in binflags: 
						plugin_obj.datavals_global.add('datatype', 'chunk')
						plugin_obj.clear_prog_keep(prognum)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', None, vst_UniqueId, 'chunk', Buffer, None)
						used_params = len([v for x, v in parampaths['ParameterList'].items() if int(v['ParameterId'])!=-1])
						plugin_obj.datavals_global.add('all_params_used', vst_NumberOfParameters == used_params)
					else:
						plugin_obj.datavals_global.add('datatype', 'param')
						plugin_obj.clear_prog_keep(0)
						plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id' ,None, vst_UniqueId, 'param', None, vst_NumberOfParameters)
						dtype_vstprog = np.dtype([('name', '<S28'),('params', np.float32, vst_NumberOfParameters)]) 
						programs = np.frombuffer(Buffer, dtype=dtype_vstprog)
						for num, presetdata in enumerate(programs):
							plugin_obj.set_program(num)
							plugin_obj.preset.name = presetdata['name'].decode()
							for paramnum, paramval in enumerate(presetdata['params']): 
								plugin_obj.params.add_named('ext_param_'+str(paramnum), paramval, 'float', dtype_vstnames[paramnum])
						plugin_obj.set_program(prognum)
						plugin_obj.datavals_global.add('all_params_used', True)

				for n, p in parampaths['ParameterList'].items():
					paramnum, paramtype = n.split('/')
					param_data = p
					param_name = param_data['ParameterName']
					param_id = int(param_data['ParameterId'])
					param_value = param_data['ParameterValue']
					if param_id != -1: 
						dtype_vstnames[param_id] = param_name
						cvpj_param_name = 'ext_param_'+str(param_id)
						param_val = doparam(param_value.value, cvpj_param_name, 'float', 0, ['plugin', pluginid, cvpj_param_name], None)
						plugin_obj.params.add_named(cvpj_param_name, param_val, 'float', str(param_name))

				if 2 in binflags:
					plugin_obj.role = 'inst'
					track_obj.inst_pluginid = pluginid
				else:
					plugin_obj.role = 'effect'
					track_obj.fxslots_audio.append(pluginid)

			if '0/Vst3PluginInfo' in PluginDesc:
				VstPluginInfo = PluginDesc['0/Vst3PluginInfo']

				vst_DeviceType = int(VstPluginInfo['DeviceType'])
				vst_WinPosX = int(VstPluginInfo['WinPosX'])
				vst_WinPosY = int(VstPluginInfo['WinPosY'])

				plugin_obj = convproj_obj.add_plugin(pluginid, 'external', 'vst3', 'win')
				windata_obj = convproj_obj.window_data_add(['plugin',pluginid])
				windata_obj.pos_x = vst_WinPosX
				windata_obj.pos_y = vst_WinPosY

				Preset = VstPluginInfo['Preset']
				Preset = VstPluginInfo['Preset'][list(Preset)[0]]

				Fields_0 = int(Preset['Uid/Fields.0'])
				Fields_1 = int(Preset['Uid/Fields.1'])
				Fields_2 = int(Preset['Uid/Fields.2'])
				Fields_3 = int(Preset['Uid/Fields.3'])

				hexuuid = struct.pack('>iiii', Fields_0, Fields_1, Fields_2, Fields_3).hex().upper()

				ProcessorState = Preset['ProcessorState'].value

				plugin_obj.datavals.add('id', hexuuid)
				plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', None, hexuuid, ProcessorState)

				if plugin_obj.role == 'synth': plugin_obj.role = 'inst'

				if plugin_obj.role == 'effect': track_obj.fxslots_audio.append(pluginid)
				elif plugin_obj.role == 'inst': track_obj.inst_pluginid = pluginid

				paramorder = []
				for n, p in parampaths['ParameterList'].items():
					paramnum, paramtype = n.split('/')
					param_data = p
					param_name = param_data['ParameterName']
					param_id = int(param_data['ParameterId'])
					param_value = param_data['ParameterValue']
					if param_id != -1: 
						cvpj_param_name = 'ext_param_'+str(param_id)
						param_val = doparam(param_value.value, cvpj_param_name, 'float', 0, ['plugin', pluginid, cvpj_param_name], None)
						track_obj.params.add(cvpj_param_name, param_val, 'float')
						paramorder.append(param_id)

				plugin_obj.datavals.add('paramorder', paramorder)
				plugin_obj.datavals.add_if_missing('numparams', len(paramorder))
 
		else:
			fldso = globalstore.dataset.get_obj('ableton', 'plugin', device.name)

			plugin_obj = convproj_obj.add_plugin(pluginid, 'native', 'ableton', device.name)
			plugin_obj.role = 'fx'

			if fldso:
				device_type = fldso.data['group'] if 'group' in fldso.data else 'fx'
				if device_type == 'inst': track_obj.inst_pluginid = pluginid
				if device_type: plugin_obj.role = device_type

				foundlists = findlists(parampaths)

				for param_id, dset_param in fldso.params.iter():
					if param_id in parampaths:
						alsparam = parampaths[param_id]
						if alsparam.type == 'param': outval = doparam(alsparam.value, param_id, dset_param.type, 0, ['plugin', pluginid, param_id], None)
						else: outval = alsparam.value
					else: outval = None
					if dset_param.type == 'list':
						if param_id in foundlists: outval = foundlists[param_id]

					plugin_obj.dset_param__add(param_id, outval, dset_param)

				if plugin_obj.role == 'fx':
					track_obj.fxslots_audio.append(pluginid)

			#if device.name == 'InstrumentVector':
			#	modcons = []
			#	for n, x in parampaths['ModulationConnections'].items():
			#		paramnum, paramtype = n.split('/')
			#		print(paramnum, paramtype, findlists(x))
			#		modcon = {}
			#		modcon['target'] = x
			#		modcon['name'] = x['TargetName'].value
			#		modcon['amounts'] = findlists(x)['ModulationAmounts']
#
			#		print(x)

				#	modcons.append(modcon)
				#	plugin_obj.datavals.add('ModulationConnections', modcons)
				#	SpriteName1 = parampaths['SpriteName1']
				#	SpriteName2 = parampaths['SpriteName2']
				#	UserSprite1 = parampaths['UserSprite1/Value']
				#	UserSprite2 = parampaths['UserSprite2/Value']
				#	UserSprite1 = get_sampleref(convproj_obj, UserSprite1[0][0]['SampleRef']) if 0 in UserSprite1 else None
				#	UserSprite2 = get_sampleref(convproj_obj, UserSprite2[0][0]['SampleRef']) if 0 in UserSprite2 else None
				#	if UserSprite1: plugin_obj.samplerefs['sample1'] = UserSprite1
				#	if UserSprite2: plugin_obj.samplerefs['sample2'] = UserSprite2
			#	exit()

	return middlenote, issampler

AUDCLIPVERBOSE = True

AUDWARPVERBOSE = False

class input_ableton(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def get_shortname(self): return 'ableton'
	def get_name(self): return 'Ableton Live 11'
	def get_priority(self): return 0
	def supported_autodetect(self): return False
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['als']
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['audio_stretch'] = ['warp']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:sampler:multi','universal:sampler:slicer','native:ableton']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['plugin_ext'] = ['vst2', 'vst3']

	def parse(self, convproj_obj, input_file, dv_config):
		from objects import colors
		from objects.file_proj import proj_ableton
		from objects import auto_id

		global autoid_assoc
		global timesigid
		global vector_shapesdata
		
		vector_shapesdata = None

		xmlstring = ""

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)
		autoid_assoc = auto_id.convproj2autoid(4, True)

		globalstore.dataset.load('ableton', './data_main/dataset/ableton.dset')
		colordata = colors.colorset.from_dataset('ableton', 'track', 'main')

		project_obj = proj_ableton.ableton_liveset()
		if not project_obj.load_from_file(input_file): exit()

		mastermixer = project_obj.MasterTrack.DeviceChain.Mixer

		mas_track_vol = doparam(mastermixer.Volume, 'Volume', 'float', 0, ['master', 'vol'], None)
		mas_track_pan = doparam(mastermixer.Pan, 'Pan', 'float', 0, ['master', 'pan'], None)
		tempo = doparam(mastermixer.Tempo, 'Tempo', 'float', 120, ['main', 'bpm'], None)
		tempomul = tempo/120

		timesigid = int(project_obj.MasterTrack.DeviceChain.Mixer.TimeSignature.AutomationTarget.id)

		for _, loc in project_obj.Locators.items():
			timemarker_obj = convproj_obj.add_timemarker()
			timemarker_obj.visual.name = loc.Name
			timemarker_obj.position = loc.Time

		do_automation(convproj_obj, project_obj.MasterTrack.AutomationEnvelopes)

		convproj_obj.track_master.visual.name = project_obj.MasterTrack.Name.EffectiveName
		convproj_obj.track_master.visual.color.from_colorset_num(colordata, int(project_obj.MasterTrack.Color))
		convproj_obj.track_master.params.add('vol', mas_track_vol, 'float')
		convproj_obj.track_master.params.add('pan', mas_track_pan, 'float')
		convproj_obj.params.add('bpm', tempo, 'float')
		do_devices(project_obj.MasterTrack.DeviceChain.devices, None, convproj_obj.track_master, convproj_obj)

		returnid = 1

		if AUDCLIPVERBOSE:
			for x in ['cut_type', 'cut_type', 'IsWarped', "Duration",
				"StartRelative", "LoopStart",
				"LoopEnd", "LoopOn", 
				"HidLoopStart", "HidLoopEnd"]:
				print(  str(x)[0:11].ljust(12), end=' ' )
			print()

							
		for tracktype, als_track in project_obj.Tracks:
			track_mixer = als_track.DeviceChain.Mixer

			track_id = str(als_track.Id)
			track_name = als_track.Name.EffectiveName
			track_color = int(als_track.Color)
			track_inside_group = als_track.TrackGroupId
			track_sendholders = track_mixer.Sends

			fxloc = None

			do_automation(convproj_obj, als_track.AutomationEnvelopes)

			if tracktype == 'midi':
				fxloc = ['track', track_id]
				track_vol = doparam(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = doparam(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)
				track_on = doparam(track_mixer.Speaker, 'On', 'bool', 1, fxloc+['enabled'], None)

				track_obj = convproj_obj.add_track(track_id, 'instrument', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color.from_colorset_num(colordata, track_color)

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				track_obj.params.add('enabled', track_on, 'bool')

				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

			elif tracktype == 'audio':
				fxloc = ['track', track_id]
				track_vol = doparam(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = doparam(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)
				track_on = doparam(track_mixer.On, 'On', 'bool', 0, fxloc+['enabled'], None)

				track_obj = convproj_obj.add_track(track_id, 'audio', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color.from_colorset_num(colordata, track_color)

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)
				
				if not DEBUG_DISABLE_PLACEMENTS:
					mainseq = als_track.DeviceChain.MainSequencer
					
					for clipid, cliptype, clipobj in mainseq.ClipTimeable.Events:
						placement_obj = track_obj.placements.add_audio()
						placement_obj.time.set_startend(clipobj.CurrentStart*4, clipobj.CurrentEnd*4)
						placement_obj.visual.name = clipobj.Name
						placement_obj.visual.color.from_colorset_num(colordata, clipobj.Color)
						placement_obj.muted = clipobj.Disabled
						placement_obj.sample.vol = clipobj.SampleVolume
						placement_obj.sample.sampleref = get_sampleref(convproj_obj, clipobj.SampleRef)

						for _, e in clipobj.Envelopes.items():
							mpetype = None
							alsparam = track_mixer.Pan
							if alsparam.ModulationTarget.exists:
								if int(e.PointeeId) == int(alsparam.ModulationTarget.id): mpetype = 'pan'
							if int(e.PointeeId) == int(mainseq.VolumeModulationTarget.id): mpetype = 'gain'
							if int(e.PointeeId) == int(mainseq.TranspositionModulationTarget.id): mpetype = 'pitch'

							if mpetype:
								autopoints_obj = placement_obj.add_autopoints(mpetype, 4, True)
								for mid, mtype, mobj in e.Automation.Events:
									if mtype == 'FloatEvent':
										autopoint_obj = autopoints_obj.add_point()
										autopoint_obj.pos = mobj.Time
										autopoint_obj.value = mobj.Value

						if clipobj.Loop.LoopOn:
							placement_obj.time.set_loop_data((clipobj.Loop.StartRelative+clipobj.Loop.LoopStart)*4, clipobj.Loop.LoopStart*4, clipobj.Loop.LoopEnd*4)
						else:
							placement_obj.time.set_offset(clipobj.Loop.LoopStart)

						audio_placement_PitchCoarse = clipobj.PitchCoarse
						audio_placement_PitchFine = clipobj.PitchFine
						placement_obj.sample.pitch = audio_placement_PitchCoarse + audio_placement_PitchFine/100

						if clipobj.Fade:
							placement_obj.fade_in.set_dur(clipobj.Fades.FadeInLength, 'beats')
							placement_obj.fade_in.skew = clipobj.Fades.FadeInCurveSkew
							placement_obj.fade_in.slope = clipobj.Fades.FadeInCurveSlope
							placement_obj.fade_out.set_dur(clipobj.Fades.FadeOutLength, 'beats')
							placement_obj.fade_out.skew = clipobj.Fades.FadeOutCurveSkew
							placement_obj.fade_out.slope = clipobj.Fades.FadeOutCurveSlope

						stretch_obj = placement_obj.sample.stretch

						if clipobj.IsWarped:
							stretch_obj.is_warped = True
							stretch_obj.params = {}
							stretch_obj.preserve_pitch = clipobj.WarpMode != 3

							if clipobj.WarpMode == 0:
								stretch_obj.algorithm = 'transient'
								stretch_obj.params['resolution'] = clipobj.TransientResolution
								stretch_obj.params['loopmode'] = clipobj.TransientLoopMode
								stretch_obj.params['envelope'] = clipobj.TransientEnvelope
							if clipobj.WarpMode == 1:
								stretch_obj.algorithm = 'ableton_tones'
								stretch_obj.params['GranularityTones'] = clipobj.GranularityTones
							if clipobj.WarpMode == 2:
								stretch_obj.algorithm = 'ableton_texture'
								stretch_obj.params['GranularityTexture'] = clipobj.GranularityTexture
								stretch_obj.params['FluctuationTexture'] = clipobj.FluctuationTexture
							if clipobj.WarpMode == 4:
								stretch_obj.algorithm = 'ableton_complex'
							if clipobj.WarpMode == 6:
								stretch_obj.algorithm = 'ableton_complexpro'
								stretch_obj.params['formants'] = clipobj.ComplexProFormants
								stretch_obj.params['envelope'] = clipobj.ComplexProEnvelope

							if AUDWARPVERBOSE: print('i')
							for _, WarpMarker in clipobj.WarpMarkers.items():
								warp_point_obj = stretch_obj.add_warp_point()
								warp_point_obj.beat = WarpMarker.BeatTime
								warp_point_obj.second = WarpMarker.SecTime
								if AUDWARPVERBOSE: print(str(WarpMarker.BeatTime).ljust(18), WarpMarker.SecTime)

							stretch_obj.calc_warp_points()
							stretch_obj.rem_last_warp_point()

						else:
							pitchcalc = 2**(placement_obj.sample.pitch/12)
							stretch_obj.is_warped = False
							stretch_obj.set_rate_speed(tempo, pitchcalc, False)
							stretch_obj.uses_tempo = False

						if not clipobj.IsWarped:
							if clipobj.Loop.LoopOn == 0:
								placement_obj.time.cut_type = 'cut'
								pitchcalc = 2**(placement_obj.sample.pitch/12)
								placement_obj.time.cut_start = (clipobj.Loop.LoopStart*8/pitchcalc)*tempomul
								placement_obj.time.duration *= pitchcalc
								placement_obj.time.duration /= tempomul
								placement_obj.time.duration /= stretch_obj.calc_tempo_speed
						else:
							if clipobj.Loop.LoopOn == 0:
								placement_obj.time.set_offset(clipobj.Loop.LoopStart*4)
							else:
								placement_obj.time.set_loop_data((clipobj.Loop.StartRelative+clipobj.Loop.LoopStart)*4, clipobj.Loop.LoopStart*4, clipobj.Loop.LoopEnd*4)

						if AUDCLIPVERBOSE:
							for x in [
								placement_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off'], placement_obj.time.cut_type, clipobj.IsWarped,
								clipobj.CurrentEnd-clipobj.CurrentStart,
								clipobj.Loop.StartRelative, clipobj.Loop.LoopStart,
								clipobj.Loop.LoopEnd, clipobj.Loop.LoopOn,
								clipobj.Loop.HiddenLoopStart, clipobj.Loop.HiddenLoopEnd
								]:
								print(  str(x)[0:11].ljust(12), end=' ' )
							print()


			elif tracktype == 'return':
				cvpj_returntrackid = 'return_'+str(returnid)
				fxloc = ['return', cvpj_returntrackid]
				track_vol = doparam(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = doparam(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)
				track_on = doparam(track_mixer.On, 'On', 'bool', 0, fxloc+['enabled'], None)
				track_obj = convproj_obj.track_master.add_return(cvpj_returntrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color.from_colorset_num(colordata, track_color)
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				returnid += 1

			elif tracktype == 'group':
				cvpj_grouptrackid = 'group_'+str(track_id)
				fxloc = ['group', cvpj_grouptrackid]
				track_vol = doparam(track_mixer.Volume, 'Volume', 'float', 0, fxloc+['vol'], None)
				track_pan = doparam(track_mixer.Pan, 'Pan', 'float', 0, fxloc+['pan'], None)
				track_on = doparam(track_mixer.On, 'On', 'bool', 0, fxloc+['enabled'], None)

				track_obj = convproj_obj.add_group(cvpj_grouptrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color.from_colorset_num(colordata, track_color)
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

			if als_track.DeviceChain.AudioOutputRouting.UpperDisplayString == 'Sends Only':
				track_obj.sends.to_master_active = False

			sendcount = 1
			if fxloc != None:
				for _, track_sendholder in track_sendholders.items():
					sendid = sendcount
					sendautoid = 'send_'+track_id+'_'+str(sendid)
					sendlevel = doparam(track_sendholder.Send, 'Send', 'float', 0, ['send', sendautoid, 'amount'], None)
					track_obj.sends.add('return_'+str(sendid), sendautoid, sendlevel)
					sendcount += 1

			middlenote, issampler = do_devices(als_track.DeviceChain.devices, track_id, track_obj, convproj_obj)
			track_obj.datavals.add('middlenote', middlenote)

			if tracktype == 'midi':

				midictrls = {}
				mainseq = als_track.DeviceChain.MainSequencer
				for n, x in mainseq.MidiControllers.items():
					midictrls[int(x.id)] = int(n)-2

				if not DEBUG_DISABLE_PLACEMENTS:
					
					for clipid, cliptype, clipobj in als_track.DeviceChain.MainSequencer.ClipTimeable.Events:
						placement_obj = track_obj.placements.add_notes()
						placement_obj.time.set_startend(clipobj.CurrentStart*4, clipobj.CurrentEnd*4)
						placement_obj.visual.name = clipobj.Name
						placement_obj.visual.color.from_colorset_num(colordata, clipobj.Color)
						placement_obj.muted = clipobj.Disabled

						for _, t in clipobj.TimeSignatures.items():
							placement_obj.timesig_auto.add_point(t.Time, [t.Numerator, t.Denominator])

						for _, e in clipobj.Envelopes.items():
							if int(e.PointeeId) in midictrls: 
								ccnum = midictrls[int(e.PointeeId)]

								if ccnum == -2: mpetype = 'midi_pitch'
								elif ccnum == -1: mpetype = 'midi_pressure'
								else: mpetype = 'midi_cc_'+str(ccnum)

							if mpetype:
								autopoints_obj = placement_obj.add_autopoints(mpetype)
								for mid, mtype, mobj in e.Automation.Events:
									if mtype == 'FloatEvent':
										autopoint_obj = autopoints_obj.add_point()
										autopoint_obj.pos = mobj.Time
										autopoint_obj.value = mobj.Value

						if clipobj.Loop.LoopOn == 1:
							placement_obj.time.set_loop_data((clipobj.Loop.StartRelative+clipobj.Loop.LoopStart)*4, clipobj.Loop.LoopStart*4, clipobj.Loop.LoopEnd*4)
						else:
							placement_obj.time.set_offset(clipobj.Loop.LoopStart)

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
								t_note_extra['velocity_range'] = event.VelocityDeviation
								t_note_extra['enabled'] = event.IsEnabled
								notevol = (event.Velocity/100)
								if issampler: notevol = notevol**3
								placement_obj.notelist.add_r(event.Time*4, event.Duration*4, kt.MidiKey-60, notevol, t_note_extra)
								if t_note_id in t_notes_auto:
									for atype, adata in t_notes_auto[t_note_id].items():
										mpetype = None
										autodiv = 1

										if atype == -2:
											mpetype = 'pitch'
											autodiv = 170

										if atype == 74: mpetype = 'slide'
										if atype == -1: mpetype = 'pressure'

										if mpetype:
											for autopoints in adata:
												autopoint_obj = placement_obj.notelist.last_add_auto(mpetype)
												autopoint_obj.pos = autopoints[0]
												autopoint_obj.value = autopoints[1]/autodiv


		autoid_assoc.output(convproj_obj)
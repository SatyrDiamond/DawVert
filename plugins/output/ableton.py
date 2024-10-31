# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import json
import lxml.etree as ET
from functions import xtramath
from objects import colors
from functions import data_values
from objects.data_bytes import bytewriter
from objects.file_proj import proj_ableton
from objects.file_proj._ableton.param import ableton_parampart
from objects.file_proj._ableton.samplepart import ableton_MultiSamplePart
from objects.file_proj._ableton.automation import ableton_AutomationEnvelope
from objects.file_proj._ableton.automation import ableton_ReceiveTarget
from objects import counter
from objects import globalstore
import numpy as np
import math
import os
import copy
import struct

import logging
logger_output = logging.getLogger('output')

DEBUG_IGNORE_INST = False
DEBUG_IGNORE_FX = False
DEBUG_IGNORE_PLACEMENTS = False
NOCOLORNUM = 13
LFO_SHAPE = {
	'sine': 0,
	'square': 1,
	'triangle': 2,
	'saw': 3,
	'saw_down': 4,
	'random': 5,
}

def fixtxt(inp):
	inp = inp.encode("ascii", "replace").decode(encoding="utf-8", errors="ignore")
	inp = "".join(t for t in inp if t.isprintable())
	return inp

def do_sampleref(convproj_obj, als_sampleref, cvpj_sampleref):
	als_fileref = als_sampleref.FileRef
	if cvpj_sampleref != None:
		als_fileref.RelativePathType = 0
		outpath = cvpj_sampleref.fileref.get_path('win', False)
		#print(outpath)
		als_fileref.Path = outpath.replace('\\','/')
		als_fileref.Type = 1
		als_sampleref.DefaultDuration = cvpj_sampleref.dur_samples
		als_sampleref.DefaultSampleRate = cvpj_sampleref.hz

def do_param(convproj_obj, cvpj_params, cvpj_name, cvpj_fallback, cvpj_type, cvpj_autoloc, als_param, als_auto):
	outval = cvpj_params.get(cvpj_name, cvpj_fallback).value
	if cvpj_type == 'bool': outval = bool(outval)
	if cvpj_type == 'float': outval = float(outval)
	if cvpj_type == 'int': outval = int(outval)

	als_param.setvalue(outval)

	if cvpj_autoloc:
		if_found, autopoints = convproj_obj.automation.get_autopoints(cvpj_autoloc)
		if if_found:
			autopoints.sort()
			if autopoints.check():
				als_param.AutomationTarget.set_unused()
				AutomationEnvelope_obj = als_auto.add(als_param.AutomationTarget.id)
				autopoints.remove_instant()
				firstpoint = autopoints.points[0]
				firstval = firstpoint.value
				if cvpj_type == 'float':
					alsevent = proj_ableton.ableton_FloatEvent(None)
					alsevent.Time = -63072000
					alsevent.Value = firstval
					AutomationEnvelope_obj.Automation.Events.append([0, 'FloatEvent', alsevent])
					for num, autopoint in enumerate(autopoints):
						alsevent = proj_ableton.ableton_FloatEvent(None)
						alsevent.Time = autopoint.pos
						alsevent.Value = autopoint.value
						AutomationEnvelope_obj.Automation.Events.append([num+1, 'FloatEvent', alsevent])
				if cvpj_type == 'bool':
					alsevent = proj_ableton.ableton_BoolEvent(None)
					alsevent.Time = -63072000
					alsevent.Value = firstval
					AutomationEnvelope_obj.Automation.Events.append([0, 'BoolEvent', alsevent])
					for num, autopoint in enumerate(autopoints):
						alsevent = proj_ableton.ableton_BoolEvent(None)
						alsevent.Time = autopoint.pos
						alsevent.Value = autopoint.value
						AutomationEnvelope_obj.Automation.Events.append([num+1, 'BoolEvent', alsevent])

def do_warpmarkers(convproj_obj, WarpMarkers, stretch_obj, dur_sec, pitch):
	warpenabled = False

	ratespeed = stretch_obj.calc_tempo_size

	if ratespeed != 1: warpenabled = True

	dsr = (dur_sec*2)*ratespeed

	warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
	warpmarker_obj.SecTime = 0
	warpmarker_obj.BeatTime = 0
	WarpMarkers[2] = warpmarker_obj

	warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
	warpmarker_obj.SecTime = dur_sec
	aftersec = warpmarker_obj.BeatTime = dsr if stretch_obj.uses_tempo else dsr/(2**(pitch/12))
	WarpMarkers[3] = warpmarker_obj

	#warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
	#warpmarker_obj.SecTime = dur_sec+((0.03125/2)/stretch_obj.calc_real_size)
	#warpmarker_obj.BeatTime = aftersec+0.03125
	#WarpMarkers[4] = warpmarker_obj

	return warpenabled, 1 if stretch_obj.uses_tempo else 1/(2**(pitch/12))

def do_samplepart(convproj_obj, als_samplepart, cvpj_samplepart, ignoreresample, warpprop):
	iffound, sampleref_obj = convproj_obj.get_sampleref(cvpj_samplepart.sampleref)

	if iffound:
		cvpj_samplepart.convpoints_samples(sampleref_obj)
		do_sampleref(convproj_obj, als_samplepart.SampleRef, sampleref_obj)
	
		#print(cvpj_samplepart.start, cvpj_samplepart.end, cvpj_samplepart.loop_start, cvpj_samplepart.loop_end, sampleref_obj.fileref.get_path(convproj_obj, 'win'))
		if cvpj_samplepart.visual.name: als_samplepart.Name = cvpj_samplepart.visual.name

		als_samplepart.SampleStart = cvpj_samplepart.start
		als_samplepart.SampleEnd = cvpj_samplepart.end
		als_samplepart.SustainLoop.Start = cvpj_samplepart.loop_start
		als_samplepart.SustainLoop.End = cvpj_samplepart.loop_end
	
		if als_samplepart.SampleEnd < 2: als_samplepart.SampleEnd = sampleref_obj.dur_sec
		if als_samplepart.SustainLoop.End < 2: als_samplepart.SustainLoop.End = sampleref_obj.dur_sec
	
		if 'crossfade' in cvpj_samplepart.loop_data: als_samplepart.SustainLoop.Crossfade = cvpj_samplepart.loop_data['crossfade']
		if 'detune' in cvpj_samplepart.loop_data: als_samplepart.SustainLoop.Detune = cvpj_samplepart.loop_data['detune']
		als_samplepart.Panorama = cvpj_samplepart.pan
		als_samplepart.Volume = cvpj_samplepart.vol
		if cvpj_samplepart.loop_active:
			als_samplepart.SustainLoop.Mode = 2 if cvpj_samplepart.loop_mode=='pingpong' else 1
			als_samplepart.ReleaseLoop.Mode = 3
		else:
			als_samplepart.SustainLoop.Mode = 0
			als_samplepart.ReleaseLoop.Mode = 0
	
		warp_obj = als_samplepart.SampleWarpProperties
	
		stretch_obj = cvpj_samplepart.stretch
	
		if not stretch_obj.preserve_pitch and not ignoreresample: 
			warp_obj.WarpMode = 3
		else:
			if stretch_obj.algorithm == 'beats':
				warp_obj.WarpMode = 0
				if 'resolution' in stretch_obj.params: warp_obj.TransientResolution = stretch_obj.params['resolution']
				if 'loopmode' in stretch_obj.params: warp_obj.TransientLoopMode = stretch_obj.params['loopmode']
				if 'envelope' in stretch_obj.params: warp_obj.TransientEnvelope = stretch_obj.params['envelope']
			elif stretch_obj.algorithm == 'ableton_tones':
				warp_obj.WarpMode = 1
				if 'GranularityTones' in stretch_obj.params: warp_obj.GranularityTones = stretch_obj.params['GranularityTones']
			elif stretch_obj.algorithm == 'ableton_texture':
				warp_obj.WarpMode = 2
				if 'GranularityTexture' in stretch_obj.params: warp_obj.GranularityTexture = stretch_obj.params['GranularityTexture']
				if 'FluctuationTexture' in stretch_obj.params: warp_obj.FluctuationTexture = stretch_obj.params['FluctuationTexture']
			elif stretch_obj.algorithm == 'ableton_complex':
				warp_obj.WarpMode = 4
			elif stretch_obj.algorithm == 'stretch_complexpro':
				warp_obj.WarpMode = 6
				if 'formants' in stretch_obj.params: warp_obj.ComplexProFormants = stretch_obj.params['formants']
				if 'envelope' in stretch_obj.params: warp_obj.ComplexProEnvelope = stretch_obj.params['envelope']
			else:
				warp_obj.WarpMode = 4
		
		if not warpprop and stretch_obj.calc_real_size != 1:
			warp_obj.IsWarped, ratespeed = do_warpmarkers(convproj_obj, warp_obj.WarpMarkers, stretch_obj, sampleref_obj.dur_sec, 0)
		else:
			do_warpmarkers(convproj_obj, warp_obj.WarpMarkers, stretch_obj, sampleref_obj.dur_sec, 0)

		for sample_slice in cvpj_samplepart.slicer_slices:
			als_slice = als_samplepart.add_slice()
			als_slice.TimeInSeconds = sample_slice.start/sampleref_obj.hz
			als_slice.Rank = 0
			als_slice.NormalizedEnergy = 1

	return sampleref_obj

def add_plugindevice_vst2(als_track, convproj_obj, plugin_obj, pluginid):
	vstid = plugin_obj.datavals_global.get('fourid', 0)
	vstnumparams = plugin_obj.datavals_global.get('numparams', None)
	vstdatatype = plugin_obj.datavals_global.get('datatype', 'chunk')

	visname = plugin_obj.datavals_global.get('name', '')

	if ((vstdatatype=='param' and vstnumparams) or vstdatatype=='chunk') and vstid:
		wobj = convproj_obj.window_data_get(['plugin', pluginid])
		vstpath = plugin_obj.getpath_fileref(convproj_obj, 'plugin', 'win', True)
		vstname = os.path.basename(vstpath).split('.')[0]
		vstversion = plugin_obj.datavals_global.get('version_bytes', 0)
		is_instrument = plugin_obj.role == 'inst'

		fx_on, fx_wet = plugin_obj.fxdata_get()
		als_device = als_track.DeviceChain.add_device('PluginDevice')
		do_param(convproj_obj, plugin_obj.params, 'enabled', 1, 'bool', ['slot', pluginid, 'enabled'], als_device.On, als_track.AutomationEnvelopes)
		als_device.On.Manual = fx_on

		paramkeys = {}
	
		paramkeys['PluginDesc'] = ableton_parampart.as_numset('VstPluginInfo')
		pluginfo = paramkeys['PluginDesc']['0/VstPluginInfo'] = {}
	
		if vstdatatype == 'chunk': outflags = 67110149 if is_instrument else 67110144
		else: outflags = 67108869 if is_instrument else 67109120
	
		pluginfo['WinPosX'] = ableton_parampart.as_value('WinPosX', wobj.pos_x)
		pluginfo['WinPosY'] = ableton_parampart.as_value('WinPosY', wobj.pos_y)
		pluginfo['Path'] = ableton_parampart.as_value('Path', vstpath)
		pluginfo['PlugName'] = ableton_parampart.as_value('PlugName', vstname)
		pluginfo['UniqueId'] = ableton_parampart.as_value('UniqueId', vstid)
		pluginfo['Inputs'] = ableton_parampart.as_value('Inputs', 0)
		pluginfo['Outputs'] = ableton_parampart.as_value('Outputs', 0)
		if vstnumparams: pluginfo['NumberOfParameters'] = ableton_parampart.as_value('NumberOfParameters', vstnumparams)
		pluginfo['NumberOfPrograms'] = ableton_parampart.as_value('NumberOfPrograms', 1)
		pluginfo['Flags'] = ableton_parampart.as_value('Flags', outflags)
		pluginfo['Preset'] = ableton_parampart.as_numset('VstPreset')
		pluginfo['Version'] = ableton_parampart.as_value('Version', vstversion)
		pluginfo['VstVersion'] = ableton_parampart.as_value('VstVersion', 2400)
		pluginfo['IsShellClient'] = ableton_parampart.as_bool('IsShellClient', False)
		pluginfo['Category'] = ableton_parampart.as_value('Category', 2 if is_instrument else 1)
		pluginfo['LastPresetFolder'] = ableton_parampart.as_value('LastPresetFolder', "")
	
		vstpreset = pluginfo['Preset']['0/VstPreset'] = {}
		vstpreset['IsOn'] = ableton_parampart.as_bool('IsOn', True)
		vstpreset['ParameterSettings'] = ableton_parampart.as_numset('ParameterSettings')
		vstpreset['PowerMacroControlIndex'] = ableton_parampart.as_value('PowerMacroControlIndex', -1)
		vstpreset['PowerMacroMappingRange/Min'] = ableton_parampart.as_value('Min', 64)
		vstpreset['PowerMacroMappingRange/Max'] = ableton_parampart.as_value('Max', 127)
		vstpreset['IsFolded'] = ableton_parampart.as_bool('IsFolded', True)
		vstpreset['StoredAllParameters'] = ableton_parampart.as_bool('StoredAllParameters', False)
		vstpreset['DeviceLomId'] = ableton_parampart.as_value('DeviceLomId', 0)
		vstpreset['DeviceViewLomId'] = ableton_parampart.as_value('DeviceViewLomId', 0)
		vstpreset['IsOnLomId'] = ableton_parampart.as_value('IsOnLomId', 0)
		vstpreset['ParametersListWrapperLomId'] = ableton_parampart.as_value('ParametersListWrapperLomId', 0)
		vstpreset['Type'] = ableton_parampart.as_value('Type', 1182286443 if vstdatatype == 'param' else 1178747752)
		vstpreset['ProgramCount'] = ableton_parampart.as_value('ProgramCount', 1)
		if vstnumparams != None: vstpreset['ParameterCount'] = ableton_parampart.as_value('ParameterCount', vstnumparams)
		if vstdatatype == 'chunk': 
			vstpreset['Buffer'] = ableton_parampart.as_buffer('Buffer', plugin_obj.rawdata_get('chunk'))
			vstpreset['ProgramNumber'] = ableton_parampart.as_value('ProgramNumber', plugin_obj.current_program)
		if vstdatatype == 'param': 
			pluginfo['NumberOfPrograms'] = ableton_parampart.as_value('NumberOfPrograms', len(plugin_obj.programs))
			prognums = list(plugin_obj.programs)
			prognum = prognums.index(plugin_obj.current_program)
			vstpreset['ProgramNumber'] = ableton_parampart.as_value('ProgramNumber', prognum)
			dtype_vstprog = np.dtype([('name', '<S28'),('params', np.float32, vstnumparams)]) 
			programs = np.zeros(len(plugin_obj.programs), dtype=dtype_vstprog)
			for n, v in enumerate(plugin_obj.programs.items()):
				_, progstate = v
				programs[n]['name'] = progstate.preset.name
				programs[n]['params'] = [progstate.params.get('ext_param_'+str(pn), 0).value for pn in range(vstnumparams)]
			vstpreset['Buffer'] = ableton_parampart.as_buffer('Buffer', programs.tobytes())
		vstpreset['Name'] = ableton_parampart.as_value('Name', '')
		vstpreset['PluginVersion'] = ableton_parampart.as_value('PluginVersion', vstversion)
		vstpreset['UniqueId'] = ableton_parampart.as_value('UniqueId', vstid)
		vstpreset['ByteOrder'] = ableton_parampart.as_value('ByteOrder', 2)
		#paramkeys['MpeEnabled'] = ableton_parampart.as_bool('MpeEnabled', True)
		paramkeys['ParameterList'] = ableton_parampart.as_numset('PluginFloatParameter')
		visualnum = 0
		for cvpj_paramid in plugin_obj.params.list():
			if cvpj_paramid.startswith('ext_param_'):
				plugparam = paramkeys['ParameterList'][str(visualnum)+'/PluginFloatParameter'] = {}
				paramnum = int(cvpj_paramid[10:])
				param_obj = plugin_obj.params.get(cvpj_paramid, 0)
				plugparam['ParameterName'] = ableton_parampart.as_value('ParameterName', param_obj.visual.name)
				plugparam['ParameterId'] = ableton_parampart.as_value('ParameterId', paramnum)
				plugparam['VisualIndex'] = ableton_parampart.as_value('VisualIndex', visualnum)
				plugparam['ParameterValue'] = ableton_parampart.as_param('ParameterValue', 'float', int(param_obj.value))
				do_param(convproj_obj, plugin_obj.params, cvpj_paramid, param_obj.value, 'float', ['plugin', pluginid, cvpj_paramid], plugparam['ParameterValue'].value, als_track.AutomationEnvelopes)
				visualnum += 1
		als_device.params.import_keys(paramkeys)
		return als_device
	else:
		if not vstid: errmsg = 'no ID '+('for "'+visname+'" found.' if visname else "found.")
		elif vstdatatype=='param' and not vstnumparams: errmsg = 'num_params not found'
		logger_output.warning('VST2 plugin not placed: '+errmsg)


def add_plugindevice_vst3(als_track, convproj_obj, plugin_obj, pluginid):

	vstid = plugin_obj.datavals_global.get('id', 0)

	if vstid:
		fx_on, fx_wet = plugin_obj.fxdata_get()
		als_device = als_track.DeviceChain.add_device('PluginDevice')
		do_param(convproj_obj, plugin_obj.params, 'enabled', 1, 'bool', ['slot', pluginid, 'enabled'], als_device.On, als_track.AutomationEnvelopes)
		als_device.On.Manual = fx_on

		paramkeys = {}
		paramkeys['PluginDesc'] = ableton_parampart.as_numset('Vst3PluginInfo')
		pluginfo = paramkeys['PluginDesc']['0/Vst3PluginInfo'] = {}
		wobj = convproj_obj.window_data_get(['plugin', pluginid])
		vstpath = plugin_obj.getpath_fileref(convproj_obj, 'plugin', 'win', True)
		vstname = plugin_obj.datavals_global.get('name', 0)
		is_instrument = plugin_obj.role == 'inst'

		Fields = [int(vstid[0:8], 16), int(vstid[8:16], 16), int(vstid[16:24], 16), int(vstid[24:32], 16)]
		devicetype = 1 if is_instrument else 2

		pluginfo['Preset'] = ableton_parampart.as_numset('VstPreset')
		pluginfo['WinPosX'] = ableton_parampart.as_value('WinPosX', wobj.pos_x)
		pluginfo['WinPosY'] = ableton_parampart.as_value('WinPosY', wobj.pos_y)

		vstpreset = pluginfo['Preset']['0/Vst3Preset'] = {}
		vstpreset['IsOn'] = ableton_parampart.as_bool('IsOn', True)
		vstpreset['ParameterSettings'] = ableton_parampart.as_numset('ParameterSettings')
		vstpreset['PowerMacroControlIndex'] = ableton_parampart.as_value('PowerMacroControlIndex', -1)
		vstpreset['PowerMacroMappingRange/Min'] = ableton_parampart.as_value('Min', 64)
		vstpreset['PowerMacroMappingRange/Max'] = ableton_parampart.as_value('Max', 127)
		vstpreset['IsFolded'] = ableton_parampart.as_bool('IsFolded', True)
		vstpreset['StoredAllParameters'] = ableton_parampart.as_bool('StoredAllParameters', False)
		vstpreset['DeviceLomId'] = ableton_parampart.as_value('DeviceLomId', 0)
		vstpreset['DeviceViewLomId'] = ableton_parampart.as_value('DeviceViewLomId', 0)
		vstpreset['IsOnLomId'] = ableton_parampart.as_value('IsOnLomId', 0)
		vstpreset['ParametersListWrapperLomId'] = ableton_parampart.as_value('ParametersListWrapperLomId', 0)
		vstpreset['Uid/Fields.0'] = ableton_parampart.as_value('Fields.0', Fields[0])
		vstpreset['Uid/Fields.1'] = ableton_parampart.as_value('Fields.1', Fields[1])
		vstpreset['Uid/Fields.2'] = ableton_parampart.as_value('Fields.2', Fields[2])
		vstpreset['Uid/Fields.3'] = ableton_parampart.as_value('Fields.3', Fields[3])
		vstpreset['DeviceType'] = ableton_parampart.as_value('DeviceType', devicetype)

		vstpreset['ProcessorState'] = ableton_parampart.as_buffer('ProcessorState', plugin_obj.rawdata_get('chunk'))
		pluginfo['Name'] = ableton_parampart.as_value('Name', vstname)
		pluginfo['Uid/Fields.0'] = ableton_parampart.as_value('Fields.0', Fields[0])
		pluginfo['Uid/Fields.1'] = ableton_parampart.as_value('Fields.1', Fields[1])
		pluginfo['Uid/Fields.2'] = ableton_parampart.as_value('Fields.2', Fields[2])
		pluginfo['Uid/Fields.3'] = ableton_parampart.as_value('Fields.3', Fields[3])
		pluginfo['DeviceType'] = ableton_parampart.as_value('DeviceType', devicetype)
	
		paramkeys['ParameterList'] = ableton_parampart.as_numset('PluginFloatParameter')
		visualnum = 0
		for cvpj_paramid in plugin_obj.params.list():
			if cvpj_paramid.startswith('ext_param_'):
				plugparam = paramkeys['ParameterList'][str(visualnum)+'/PluginFloatParameter'] = {}
				paramnum = int(cvpj_paramid[10:])
				param_obj = plugin_obj.params.get(cvpj_paramid, 0)
				plugparam['ParameterName'] = ableton_parampart.as_value('ParameterName', param_obj.visual.name)
				plugparam['ParameterId'] = ableton_parampart.as_value('ParameterId', paramnum)
				plugparam['VisualIndex'] = ableton_parampart.as_value('VisualIndex', visualnum)
				plugparam['ParameterValue'] = ableton_parampart.as_param('ParameterValue', 'float', int(param_obj.value))
				do_param(convproj_obj, plugin_obj.params, cvpj_paramid, param_obj.value, 'float', ['plugin', pluginid, cvpj_paramid], plugparam['ParameterValue'].value, als_track.AutomationEnvelopes)
				visualnum += 1
		als_device.params.import_keys(paramkeys)
		return als_device
	else:
		logger_output.warning('VST3 plugin not placed: no ID found.')

def add_plugindevice_native(als_track, convproj_obj, plugin_obj, pluginid):
	fx_on, fx_wet = plugin_obj.fxdata_get()
	als_device = als_track.DeviceChain.add_device(plugin_obj.type.subtype)
	do_param(convproj_obj, plugin_obj.params, 'enabled', 1, 'bool', ['slot', pluginid, 'enabled'], als_device.On, als_track.AutomationEnvelopes)
	als_device.On.Manual = fx_on

	if plugin_obj.type.subtype in ['Eq8']:
		als_device.IsExpanded = False

	parampaths = {}
	fldso = globalstore.dataset.get_obj('ableton', 'plugin', plugin_obj.type.subtype)
	if fldso:
		for param_id, dset_param in fldso.params.iter():
			paramname = param_id.split('/')[-1]
			if dset_param.noauto == False:
				param_obj = plugin_obj.params.get(param_id, dset_param.defv)
				ppart_obj = ableton_parampart.as_param(paramname, dset_param.type, param_obj.value)
				do_param(convproj_obj, plugin_obj.params, param_id, param_obj.value, dset_param.type, ['plugin', pluginid, param_id], ppart_obj.value, als_track.AutomationEnvelopes)
				parampaths[param_id] = ppart_obj
			else:
				if dset_param.type != 'list':
					param_obj = plugin_obj.datavals.get(param_id, dset_param.defv)
					if dset_param.type == 'bool': 
						ppart_obj = ableton_parampart.as_bool(paramname, bool(param_obj))
						parampaths[param_id] = ppart_obj
					else: 
						if param_obj == 'int': param_obj = int(param_obj)
						ppart_obj = ableton_parampart.as_value(paramname, param_obj)
						parampaths[param_id] = ppart_obj
				else:
					array_data = plugin_obj.array_get_vl(param_id)
					for n, v in enumerate(array_data):
						param_id_list = param_id+'.'+str(n)
						param_name_list = paramname+'.'+str(n)
						if isinstance(v, bool):
							parampaths[param_id_list] = ableton_parampart.as_bool(param_name_list, v)
						else:
							parampaths[param_id_list] = ableton_parampart.as_value(param_name_list, v)
	else:
		for param_id in plugin_obj.params.list():
			paramname = param_id.split('/')[-1]
			param_obj = plugin_obj.params.get(param_id, 0)
			ppart_obj = ableton_parampart.as_param(paramname, param_obj.type, param_obj.value)
			do_param(convproj_obj, plugin_obj.params, param_id, param_obj.value, param_obj.type, ['plugin', pluginid, param_id], ppart_obj.value, als_track.AutomationEnvelopes)
			parampaths[param_id] = ppart_obj

	als_device.params.import_keys(parampaths)
	return als_device


#def do_note_effects(convproj_obj, als_track, fxslots_notes):
#	if not DEBUG_IGNORE_FX:
#		for pluginid in fxslots_notes:
#
#			plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
#			if plugin_found:
#
#				#print(plugin_obj.type)
#
#				als_device = None
#
#				#if plugin_obj.check_match('universal', 'arpeggiator'):
#				#	fx_on, fx_wet = plugin_obj.fxdata_get()
#				#	als_device = als_track.DeviceChain.add_device('MidiArpeggiator')
#				#	#do_param(convproj_obj, plugin_obj.params, 'enabled', 1, 'bool', ['slot', pluginid, 'enabled'], als_device.On, als_track.AutomationEnvelopes)
#				#	als_device.On.Manual = fx_on
#				#	parampaths = {}
#				#	timing_obj = plugin_obj.timing_get('main')
#				#	#print(timing_obj.type)
#				#	als_device.params.import_keys(parampaths)

def do_effects(convproj_obj, als_track, fxslots_audio):
	if not DEBUG_IGNORE_FX:
		for plugid in fxslots_audio:

			plugin_found, plugin_obj = convproj_obj.get_plugin(plugid)
			if plugin_found:

				als_device = None

				if plugin_obj.check_wildmatch('native', 'ableton', None):
					als_device = add_plugindevice_native(als_track, convproj_obj, plugin_obj, plugid)

				if plugin_obj.check_match('external', 'vst2', 'win'):
					als_device = add_plugindevice_vst2(als_track, convproj_obj, plugin_obj, plugid)
	
				if plugin_obj.check_match('external', 'vst3', 'win'):
					als_device = add_plugindevice_vst3(als_track, convproj_obj, plugin_obj, plugid)

TIMESIGVALS = [1,2,4,8,16]

def get_timesig(timesig):
	timesig_numerator = timesig[0]-3
	timesig_denominator = (TIMESIGVALS.index(timesig[1]) if timesig[1] in TIMESIGVALS else 1)
	outval = timesig_denominator*100 + timesig_numerator+(2-timesig_denominator)
	return outval

def add_group(convproj_obj, project_obj, groupid):
	global counter_track
	global colordata
	global ids_group_cvpj_als

	ingroupid = None
	if groupid not in ids_group_cvpj_als:
		group_obj = convproj_obj.groups[groupid]
		groupnumid = counter_track.get()
		als_gtrack = project_obj.add_group_track(groupnumid)
		do_effects(convproj_obj, als_gtrack, group_obj.fxslots_audio)
		als_gtrack.Color = group_obj.visual.color.closest_color_index(colordata, NOCOLORNUM)
		if group_obj.visual.name: als_gtrack.Name.UserName = fixtxt(group_obj.visual.name)
		do_param(convproj_obj, group_obj.params, 'vol', 1, 'float', ['group', groupid, 'vol'], als_gtrack.DeviceChain.Mixer.Volume, als_gtrack.AutomationEnvelopes)
		do_param(convproj_obj, group_obj.params, 'pan', 0, 'float', ['group', groupid, 'pan'], als_gtrack.DeviceChain.Mixer.Pan, als_gtrack.AutomationEnvelopes)
		ids_group_cvpj_als[groupid] = groupnumid
		if group_obj.group:
			als_gtrack.TrackGroupId = add_group(convproj_obj, project_obj, group_obj.group)
			als_gtrack.DeviceChain.AudioOutputRouting.set('AudioOut/GroupTrack', 'Group', '')
		#print('NEW GROUP', groupid, groupnumid)
	else:
		groupnumid = ids_group_cvpj_als[groupid]


	return groupnumid

def do_audio_mpe(audiopl_obj, als_track):
	track_mixer = als_track.DeviceChain.Mixer
	mainseq = als_track.DeviceChain.MainSequencer

	for i, d in enumerate(audiopl_obj.auto.items()):
		n, x = d
		clipenv = ableton_AutomationEnvelope(None)

		mpeid = None

		if n == 'pan': mpeid = track_mixer.Pan.ModulationTarget.id
		if n == 'gain': mpeid = mainseq.VolumeModulationTarget.id
		if n == 'pitch': mpeid = mainseq.TranspositionModulationTarget.id

		if mpeid:
			clipenv.PointeeId = mpeid
			for num, autopoint in enumerate(x):
				alsevent = proj_ableton.ableton_FloatEvent(None)
				alsevent.Time = autopoint.pos
				alsevent.Value = autopoint.value
				clipenv.Automation.Events.append([num+1, 'FloatEvent', alsevent])

			als_audioclip.Envelopes[i] = clipenv

def do_audio_stretch(als_audioclip, stretch_obj):
	if not stretch_obj.preserve_pitch: 
		als_audioclip.WarpMode = 3
	else:
		if stretch_obj.algorithm == 'transient':
			als_audioclip.WarpMode = 0
			if 'TransientResolution' in stretch_obj.params: als_audioclip.TransientResolution = stretch_obj.params['TransientResolution']
			if 'TransientLoopMode' in stretch_obj.params: als_audioclip.TransientLoopMode = stretch_obj.params['TransientLoopMode']
			if 'TransientEnvelope' in stretch_obj.params: als_audioclip.TransientEnvelope = stretch_obj.params['TransientEnvelope']
		elif stretch_obj.algorithm == 'ableton_tones':
			als_audioclip.WarpMode = 1
			if 'GranularityTones' in stretch_obj.params: als_audioclip.GranularityTones = stretch_obj.params['GranularityTones']
		elif stretch_obj.algorithm == 'ableton_texture':
			als_audioclip.WarpMode = 2
			if 'GranularityTexture' in stretch_obj.params: als_audioclip.GranularityTexture = stretch_obj.params['GranularityTexture']
			if 'FluctuationTexture' in stretch_obj.params: als_audioclip.FluctuationTexture = stretch_obj.params['FluctuationTexture']
		elif stretch_obj.algorithm == 'ableton_complex':
			als_audioclip.WarpMode = 4
		elif stretch_obj.algorithm == 'ableton_complexpro':
			als_audioclip.WarpMode = 6
			if 'ComplexProFormants' in stretch_obj.params: als_audioclip.ComplexProFormants = stretch_obj.params['ComplexProFormants']
			if 'ComplexProEnvelope' in stretch_obj.params: als_audioclip.ComplexProEnvelope = stretch_obj.params['ComplexProEnvelope']
		else:
			als_audioclip.WarpMode = 4

class timestate():
	def __init__(self, audiopl_obj):
		self.position = audiopl_obj.time.position
		self.duration = audiopl_obj.time.duration
		self.startrel = 0
		self.loop_start = 0
		self.loop_end = audiopl_obj.time.duration
		self.loop_on = False

AUDCLIPVERBOSE = True
AUDWARPVERBOSE = False

def do_audioclips(convproj_obj, pls_audio, track_color, als_track):
	for clipid, audiopl_obj in enumerate(pls_audio):
		als_audioclip = als_track.add_audioclip(clipid)
		als_audioclip.Disabled = audiopl_obj.muted

		als_audioclip.Fades.FadeInLength = audiopl_obj.fade_in.get_dur_beat(bpm)
		als_audioclip.Fades.FadeInCurveSkew = audiopl_obj.fade_in.skew
		als_audioclip.Fades.FadeInCurveSlope = audiopl_obj.fade_in.slope
		als_audioclip.Fades.FadeOutLength = audiopl_obj.fade_out.get_dur_beat(bpm)
		als_audioclip.Fades.FadeOutCurveSkew = audiopl_obj.fade_out.skew
		als_audioclip.Fades.FadeOutCurveSlope = audiopl_obj.fade_out.slope
	
		sample_obj = audiopl_obj.sample
		stretch_obj = copy.deepcopy(sample_obj.stretch)

		do_audio_stretch(als_audioclip, stretch_obj)

		als_audioclip.PitchCoarse = round(sample_obj.pitch)
		als_audioclip.PitchFine = (sample_obj.pitch-round(sample_obj.pitch))*100
		als_audioclip.SampleVolume = sample_obj.vol
	
		ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sample.sampleref)

		do_sampleref(convproj_obj, als_audioclip.SampleRef, sampleref_obj)


		do_audio_mpe(audiopl_obj, als_track)

		ats = timestate(audiopl_obj)
		ats.position = audiopl_obj.time.position
		ats.duration = audiopl_obj.time.duration
		ats.startrel = 0
		ats.loop_start = 0
		ats.loop_end = audiopl_obj.time.duration
		ats.loop_on = False
	
		second_dur = sampleref_obj.dur_sec

		if audiopl_obj.time.cut_type == 'cut':
			ats.startrel = 0
			ats.loop_start = audiopl_obj.time.cut_start
			ats.loop_end = ats.duration+(audiopl_obj.time.cut_start*1.5)
			als_audioclip.Loop.HiddenLoopStart = 0
			als_audioclip.Loop.HiddenLoopEnd = ats.duration+ats.loop_start
		elif audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']:
			ats.loop_on = True
			ats.startrel, ats.loop_start, ats.loop_end = audiopl_obj.time.get_loop_data()
			als_audioclip.Loop.HiddenLoopStart = 0
			als_audioclip.Loop.HiddenLoopEnd = ats.loop_end
		else:
			ats.loop_start = 0
			ats.loop_end = audiopl_obj.time.duration
			if stretch_obj.is_warped:
				s = second_dur*2
				speed = stretch_obj.calc_warp_speed()
				s *= speed
				als_audioclip.Loop.HiddenLoopStart = ats.loop_end - s
			else: als_audioclip.Loop.HiddenLoopStart = 0
			als_audioclip.Loop.HiddenLoopEnd = ats.duration+ats.loop_start
	
		if not stretch_obj.is_warped:
			if ref_found: 
				second_dur = sampleref_obj.dur_sec

				if stretch_obj.uses_tempo:
					als_audioclip.IsWarped, ratespeed = do_warpmarkers(convproj_obj, als_audioclip.WarpMarkers, stretch_obj, second_dur if second_dur else 1, sample_obj.pitch)
					ats.loop_end += ats.startrel/2
					if ats.loop_on: 
						stretch_obj.set_rate_speed(bpm, 1, False)
						als_audioclip.IsWarped = True
					else:
						ats.startrel = 0
				else:
					if not ats.loop_on:
						als_audioclip.IsWarped, ratespeed = do_warpmarkers(convproj_obj, als_audioclip.WarpMarkers, stretch_obj, second_dur if second_dur else 1, sample_obj.pitch)
						if stretch_obj.calc_tempo_size == 1:
							ats.duration = min(ats.duration, (second_dur*2*stretch_obj.calc_tempo_size))
							ats.loop_start /= 2
							ats.loop_end = (ats.startrel+(ats.duration/2))
						else:
							ats.startrel = 0
					else:
						als_audioclip.IsWarped, ratespeed = do_warpmarkers(convproj_obj, als_audioclip.WarpMarkers, stretch_obj, second_dur if second_dur else 1, sample_obj.pitch)
						ats.loop_end += ats.startrel
						if ats.loop_on: 
							stretch_obj.set_rate_speed(bpm, 1, False)
							als_audioclip.IsWarped = True

			else:
				warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
				warpmarker_obj.BeatTime = 0
				warpmarker_obj.SecTime = 0
				als_audioclip.WarpMarkers[1] = warpmarker_obj

				warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
				warpmarker_obj.BeatTime = 0.03125
				warpmarker_obj.SecTime = 0.03125
				als_audioclip.WarpMarkers[2] = warpmarker_obj

		else:
			als_audioclip.IsWarped = True

			if AUDWARPVERBOSE: print('o')
			for num, warp_point_obj in enumerate(stretch_obj.iter_warp_points()):
				warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
				warpmarker_obj.BeatTime = warp_point_obj.beat
				warpmarker_obj.SecTime = warp_point_obj.second

				if AUDWARPVERBOSE: print(str(warpmarker_obj.BeatTime).ljust(18), warpmarker_obj.SecTime)

				als_audioclip.WarpMarkers[num+1] = warpmarker_obj

			lastpoint = stretch_obj.warppoints[-1]

			warpmarker_obj = proj_ableton.ableton_WarpMarker(None)
			warpmarker_obj.BeatTime = lastpoint.beat+0.03125
			warpmarker_obj.SecTime = lastpoint.second+((0.03125/2)/lastpoint.speed)
			als_audioclip.WarpMarkers[len(stretch_obj.warppoints)+1] = warpmarker_obj

			if AUDWARPVERBOSE: print(str(warpmarker_obj.BeatTime).ljust(18), warpmarker_obj.SecTime)



		als_audioclip.Time = ats.position
		als_audioclip.CurrentStart = ats.position
		als_audioclip.CurrentEnd = ats.position+ats.duration
		als_audioclip.Loop.StartRelative = ats.startrel-ats.loop_start
		als_audioclip.Loop.LoopStart = ats.loop_start
		als_audioclip.Loop.LoopEnd = ats.loop_end
		als_audioclip.Loop.LoopOn = ats.loop_on

		if audiopl_obj.time.cut_type == 'cut':
			als_audioclip.Loop.LoopEnd -= ats.loop_start/2
			pass
		elif audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']:
			pass
		else:
			pass

		if AUDCLIPVERBOSE:
			for x in [
				audiopl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off'], audiopl_obj.time.cut_type, int(als_audioclip.IsWarped),
				als_audioclip.CurrentEnd-als_audioclip.CurrentStart,
				als_audioclip.Loop.StartRelative, als_audioclip.Loop.LoopStart,
				als_audioclip.Loop.LoopEnd, int(als_audioclip.Loop.LoopOn),
				als_audioclip.Loop.HiddenLoopStart, als_audioclip.Loop.HiddenLoopEnd
				]:
				print(  str(x)[0:11].ljust(12), end=' ' )
			print()

def add_track(convproj_obj, project_obj, trackid, track_obj):
	track_obj.placements.pl_notes.sort()
	track_color = track_obj.visual.color.closest_color_index(colordata, NOCOLORNUM)

	groupnumid = None
	if track_obj.group:
		if track_obj.group in convproj_obj.groups:
			groupnumid = add_group(convproj_obj, project_obj, track_obj.group)
			
	if track_obj.type == 'instrument':
		tracknumid = counter_track.get()
		als_track = project_obj.add_midi_track(tracknumid)
		#do_note_effects(convproj_obj, als_track, track_obj.fxslots_notes)
		als_track.Color = track_color
		if track_obj.visual.name: als_track.Name.UserName = fixtxt(track_obj.visual.name)
		do_param(convproj_obj, track_obj.params, 'vol', 1, 'float', ['track', trackid, 'vol'], als_track.DeviceChain.Mixer.Volume, als_track.AutomationEnvelopes)
		do_param(convproj_obj, track_obj.params, 'pan', 0, 'float', ['track', trackid, 'pan'], als_track.DeviceChain.Mixer.Pan, als_track.AutomationEnvelopes)
		do_param(convproj_obj, track_obj.params, 'enabled', 1, 'bool', ['track', trackid, 'enabled'], als_track.DeviceChain.Mixer.Speaker, als_track.AutomationEnvelopes)

		if groupnumid: 
			als_track.TrackGroupId = groupnumid
			als_track.DeviceChain.AudioOutputRouting.set('AudioOut/GroupTrack', 'Group', '')

		#print('NEW TRACK', tracknumid, trackid, groupnumid)

		plugin_found, plugin_obj = convproj_obj.get_plugin(track_obj.inst_pluginid)
		if plugin_found:
			issampler = plugin_obj.check_wildmatch('universal', 'sampler', None)
		else:
			issampler = False

		mainseq = als_track.DeviceChain.MainSequencer

		midicc = {}

		for n in range(130):
			d = mainseq.MidiControllers[n] = ableton_ReceiveTarget(None, 'ControllerTargets.'+str(n))
			d.set_unused()
			if n == 0: mpetype = 'midi_pitch'
			elif n == 1: mpetype = 'midi_pressure'
			else: mpetype = 'midi_cc_'+str(n-2)
			midicc[mpetype] = d.id

		if not DEBUG_IGNORE_PLACEMENTS:
			track_obj.placements.pl_notes.remove_overlaps()
			for clipid, notespl_obj in enumerate(track_obj.placements.pl_notes):
				als_midiclip = als_track.add_midiclip(clipid)
				als_midiclip.Color = notespl_obj.visual.color.closest_color_index(colordata, track_color)
				if notespl_obj.visual.name: als_midiclip.Name = fixtxt(notespl_obj.visual.name)
				als_midiclip.Time = notespl_obj.time.position
				als_midiclip.Disabled = notespl_obj.muted
				als_midiclip.CurrentStart = notespl_obj.time.position
				als_midiclip.CurrentEnd = notespl_obj.time.position+notespl_obj.time.duration

				if 0 in notespl_obj.timesig_auto.points:
					timesigc = als_midiclip.TimeSignatures[0]
					timesigc.Numerator, timesigc.Denominator = notespl_obj.timesig_auto.points[0]
	
				notespl_obj.notelist.notemod_conv()
				notespl_obj.notelist.mod_limit(-60, 67)
				notespl_obj.notelist.remove_overlap()
	
				if notespl_obj.time.cut_type == 'cut':
					als_midiclip.Loop.LoopOn = False
					als_midiclip.Loop.LoopStart = notespl_obj.time.cut_start
					als_midiclip.Loop.LoopEnd = als_midiclip.Loop.LoopStart+notespl_obj.time.duration
				elif notespl_obj.time.cut_type in ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']:
					als_midiclip.Loop.LoopOn = True
					als_midiclip.Loop.StartRelative, als_midiclip.Loop.LoopStart, als_midiclip.Loop.LoopEnd = notespl_obj.time.get_loop_data()
				else:
					als_midiclip.Loop.LoopOn = False
					als_midiclip.Loop.LoopStart = 0
					als_midiclip.Loop.LoopEnd = notespl_obj.time.duration
	
				t_keydata = {}
				
				for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notespl_obj.notelist.iter():
					for t_key in t_keys:
						if t_key not in t_keydata: t_keydata[t_key] = []
						notevol = t_vol**(1/3) if issampler else t_vol
						t_keydata[t_key].append([counter_note.get(), t_pos, t_dur, notevol, t_inst, t_extra, t_auto, t_slide])
	
				t_keydata = dict(sorted(t_keydata.items(), key=lambda item: item[0]))
	
				PerNoteEventListID = 0
				for key, notedata in t_keydata.items():
					KeyTrack_obj = proj_ableton.ableton_KeyTrack(None)
	
					for t_id, t_pos, t_dur, t_vol, t_inst, t_extra, t_auto, t_slide in notedata:
						MidiNoteEvent_obj = proj_ableton.ableton_x_MidiNoteEvent(None)
						MidiNoteEvent_obj.NoteId = t_id
						MidiNoteEvent_obj.Time = t_pos
						MidiNoteEvent_obj.Duration = t_dur
						MidiNoteEvent_obj.Velocity = t_vol*100
						if t_extra:
							if 'off_vol' in t_extra: MidiNoteEvent_obj.OffVelocity = t_extra['off_vol']*100
							if 'probability' in t_extra: MidiNoteEvent_obj.Probability = t_extra['probability']
							if 'enabled' in t_extra: MidiNoteEvent_obj.IsEnabled = bool(t_extra['enabled'])
							if 'velocity_range' in t_extra: MidiNoteEvent_obj.VelocityDeviation = t_extra['velocity_range']
	
						if t_auto:
							for mpetype,d in t_auto.items():
								atype = None
								autodiv = 1
								if mpetype == 'pitch':
									atype = -2
									autodiv = 170
								if mpetype == 'slide': atype = 74
								if mpetype == 'pressure': atype = -1
								if atype:
									d.remove_instant()
									PerNoteEventList_obj = proj_ableton.ableton_PerNoteEventList(None)
									PerNoteEventList_obj.CC = atype
									PerNoteEventList_obj.NoteId = t_id
									for autopoint_obj in d:
										PerNoteEvent_obj = proj_ableton.ableton_x_PerNoteEvent(None)
										PerNoteEvent_obj.TimeOffset = autopoint_obj.pos
										PerNoteEvent_obj.Value = autopoint_obj.value*autodiv
										PerNoteEventList_obj.Events.append(PerNoteEvent_obj)
									als_midiclip.Notes.PerNoteEventStore[PerNoteEventListID] = PerNoteEventList_obj
									PerNoteEventListID += 1
	
						KeyTrack_obj.NoteEvents.append(MidiNoteEvent_obj)
	
					KeyTrack_obj.MidiKey = key+60
					als_midiclip.Notes.KeyTrack[counter_keytrack.get()] = KeyTrack_obj

				for i, d in enumerate(notespl_obj.auto.items()):
					n, x = d
					clipenv = ableton_AutomationEnvelope(None)

					mpeid = None

					if n in midicc: mpeid = midicc[n]

					if mpeid:
						clipenv.PointeeId = mpeid
						for num, autopoint in enumerate(x):
							alsevent = proj_ableton.ableton_FloatEvent(None)
							alsevent.Time = autopoint.pos
							alsevent.Value = autopoint.value
							clipenv.Automation.Events.append([num+1, 'FloatEvent', alsevent])

						als_midiclip.Envelopes[i] = clipenv

		middlenote = track_obj.datavals.get('middlenote', 0)

		pitchparamkeys = {}
		als_device_pitch = None

		if plugin_found and not DEBUG_IGNORE_INST:
			middlenote += plugin_obj.datavals_global.get('middlenotefix', 0)

			#print(str(plugin_obj.type), plugin_obj.datavals_global.get('name', ''))
			is_sampler = False

			if plugin_obj.check_wildmatch('native', 'ableton', None):
				if middlenote != 0:
					als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
					pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', -middlenote)
				add_plugindevice_native(als_track, convproj_obj, plugin_obj, track_obj.inst_pluginid)

			if plugin_obj.check_match('external', 'vst2', 'win'):
				if middlenote != 0:
					als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
					pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', -middlenote)
				add_plugindevice_vst2(als_track, convproj_obj, plugin_obj, track_obj.inst_pluginid)

			if plugin_obj.check_match('external', 'vst3', 'win'):
				if middlenote != 0:
					als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
					pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', -middlenote)
				add_plugindevice_vst3(als_track, convproj_obj, plugin_obj, track_obj.inst_pluginid)

			if plugin_obj.check_match('universal', 'sampler', 'multi'):
				is_sampler = True
				if middlenote != 0:
					als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
					pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', -middlenote)

				paramkeys = {}
				als_device = als_track.DeviceChain.add_device('MultiSampler')
				spd = paramkeys['Player/MultiSampleMap/SampleParts'] = ableton_parampart.as_sampleparts('SampleParts')

				for spn, sampleregion in enumerate(plugin_obj.sampleregions):
					key_l, key_h, key_r, samplerefid, extradata = sampleregion
					als_samplepart = spd.value[spn] = ableton_MultiSamplePart(None)
					als_samplepart.Selection = True
					samplepart_obj = plugin_obj.samplepart_get(samplerefid)
					sampleref_obj = do_samplepart(convproj_obj, als_samplepart, samplepart_obj, False, False)

					als_samplepart.KeyRange.Min = key_l+60
					als_samplepart.KeyRange.Max = key_h+60
					als_samplepart.KeyRange.CrossfadeMin = key_l+60
					als_samplepart.KeyRange.CrossfadeMax = key_h+60
					als_samplepart.RootKey = key_r+60
					als_samplepart.VelocityRange.Min = int(samplepart_obj.vel_min*127)
					als_samplepart.VelocityRange.Max = int(samplepart_obj.vel_max*127)
					als_samplepart.VelocityRange.CrossfadeMin = als_samplepart.VelocityRange.Min
					als_samplepart.VelocityRange.CrossfadeMax = als_samplepart.VelocityRange.Max

					pitchd = samplepart_obj.pitch
					TransposeKey = round(pitchd)
					TransposeFine = (pitchd-round(pitchd))*100

					als_samplepart.RootKey -= TransposeKey
					als_samplepart.Detune = TransposeFine

				adsr_obj = plugin_obj.env_asdr_get('vol')
				paramkeys['VolumeAndPan/Envelope/AttackTime'] = ableton_parampart.as_param('AttackTime', 'float', adsr_obj.attack*1000)
				paramkeys['VolumeAndPan/Envelope/DecayTime'] = ableton_parampart.as_param('DecayTime', 'float', adsr_obj.decay*1000)
				paramkeys['VolumeAndPan/Envelope/SustainLevel'] = ableton_parampart.as_param('SustainLevel', 'float', adsr_obj.sustain)
				paramkeys['VolumeAndPan/Envelope/ReleaseTime'] = ableton_parampart.as_param('ReleaseTime', 'float', adsr_obj.release*1000)

				paramkeys['VolumeAndPan/Envelope/AttackSlope'] = ableton_parampart.as_param('AttackSlope', 'float', -adsr_obj.attack_tension)
				paramkeys['VolumeAndPan/Envelope/DecaySlope'] = ableton_parampart.as_param('DecaySlope', 'float', -adsr_obj.decay_tension)
				paramkeys['VolumeAndPan/Envelope/ReleaseSlope'] = ableton_parampart.as_param('ReleaseSlope', 'float', -adsr_obj.release_tension)

				paramkeys['VolumeAndPan/VolumeVelScale'] = ableton_parampart.as_param('VolumeVelScale', 'float', 1)
			
				paramkeys['Globals/NumVoices'] = ableton_parampart.as_value('NumVoices', 14)

			if plugin_obj.check_match('universal', 'sampler', 'single'):
				is_sampler = True

				if middlenote != 0:
					als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
					pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', -middlenote)

				samplepart_obj = plugin_obj.samplepart_get('sample')
				paramkeys = {}

				pitchin = samplepart_obj.pitch

				loop_active = samplepart_obj.loop_active

				if (samplepart_obj.stretch.calc_real_speed == 1 and samplepart_obj.trigger != 'oneshot' and pitchin == 0) or loop_active:
					als_device = als_track.DeviceChain.add_device('MultiSampler')
					spd = paramkeys['Player/MultiSampleMap/SampleParts'] = ableton_parampart.as_sampleparts('SampleParts')
					paramkeys['Player/Reverse'] = ableton_parampart.as_param('Reverse', 'bool', samplepart_obj.reverse)
					als_samplepart = spd.value[0] = ableton_MultiSamplePart(None)
					als_samplepart.Selection = True
					sampleref_obj = do_samplepart(convproj_obj, als_samplepart, samplepart_obj, False, False)

					trkpitch = track_obj.params.get('pitch', 0).value
					pitchd = trkpitch+pitchin

					TransposeKey = round(pitchd)
					TransposeFine = (pitchd-round(pitchd))*100

					als_samplepart.RootKey = 60-TransposeKey
					als_samplepart.Detune = TransposeFine

					adsr_obj = plugin_obj.env_asdr_get('vol')
					paramkeys['VolumeAndPan/Envelope/AttackTime'] = ableton_parampart.as_param('AttackTime', 'float', adsr_obj.attack*1000)
					paramkeys['VolumeAndPan/Envelope/DecayTime'] = ableton_parampart.as_param('DecayTime', 'float', adsr_obj.decay*1000)
					paramkeys['VolumeAndPan/Envelope/SustainLevel'] = ableton_parampart.as_param('SustainLevel', 'float', adsr_obj.sustain)
					paramkeys['VolumeAndPan/Envelope/ReleaseTime'] = ableton_parampart.as_param('ReleaseTime', 'float', adsr_obj.release*1000)

					paramkeys['VolumeAndPan/Envelope/AttackSlope'] = ableton_parampart.as_param('AttackSlope', 'float', -adsr_obj.attack_tension)
					paramkeys['VolumeAndPan/Envelope/DecaySlope'] = ableton_parampart.as_param('DecaySlope', 'float', -adsr_obj.decay_tension)
					paramkeys['VolumeAndPan/Envelope/ReleaseSlope'] = ableton_parampart.as_param('ReleaseSlope', 'float', -adsr_obj.release_tension)

					paramkeys['VolumeAndPan/VolumeVelScale'] = ableton_parampart.as_param('VolumeVelScale', 'float', 1)
			
					#lfo_vol_obj = plugin_obj.lfo_get('vol')
					#lfo_pitch_obj = plugin_obj.lfo_get('pitch')
					#lfo_filter_obj = plugin_obj.lfo_get('cutoff')
					#print(lfo_vol_obj)
					#print(lfo_pitch_obj)
					#print(lfo_filter_obj)

					paramkeys['Globals/NumVoices'] = ableton_parampart.as_value('NumVoices', 14)

				else:
					als_device = als_track.DeviceChain.add_device('OriginalSimpler')
					spd = paramkeys['Player/MultiSampleMap/SampleParts'] = ableton_parampart.as_sampleparts('SampleParts')
					#paramkeys['Player/Reverse'] = ableton_parampart.as_param('Reverse', 'bool', samplepart_obj.reverse)
					als_samplepart = spd.value[0] = ableton_MultiSamplePart(None)
					als_samplepart.Selection = True
					sampleref_obj = do_samplepart(convproj_obj, als_samplepart, samplepart_obj, False, False)

					paramkeys['Globals/NumVoices'] = ableton_parampart.as_value('NumVoices', 14)
					paramkeys['Globals/PlaybackMode'] = ableton_parampart.as_value('PlaybackMode', 1 if samplepart_obj.trigger == 'oneshot' else 0)

					paramkeys['Pitch/TransposeKey'] = ableton_parampart.as_param('TransposeKey', 'float', round(pitchin))
					paramkeys['Pitch/TransposeFine'] = ableton_parampart.as_param('TransposeFine', 'float', (pitchin-round(pitchin))*100)

			if plugin_obj.check_match('universal', 'sampler', 'slicer'):
				is_sampler = True
				samplepart_obj = plugin_obj.samplepart_get('sample')

				als_device_pitch = als_track.DeviceChain.add_device('MidiPitcher')
				pitchparamkeys['Pitch'] = ableton_parampart.as_param('Pitch', 'int', (-24)+samplepart_obj.slicer_start_key)

				paramkeys = {}
				als_device = als_track.DeviceChain.add_device('OriginalSimpler')
				spd = paramkeys['Player/MultiSampleMap/SampleParts'] = ableton_parampart.as_sampleparts('SampleParts')
				als_samplepart = spd.value[0] = ableton_MultiSamplePart(None)
				als_samplepart.Selection = True
				sampleref_obj = do_samplepart(convproj_obj, als_samplepart, samplepart_obj, True, True)
				paramkeys['Globals/NumVoices'] = ableton_parampart.as_value('NumVoices', 14)
				paramkeys['Globals/PlaybackMode'] = ableton_parampart.as_value('PlaybackMode', 2)
				paramkeys['SimplerSlicing/PlaybackMode'] = ableton_parampart.as_value('PlaybackMode', 1)
				paramkeys['VolumeAndPan/OneShotEnvelope/SustainMode'] = ableton_parampart.as_param('SustainMode', 'int', int(samplepart_obj.trigger != 'oneshot'))

			if is_sampler:
				filter_obj = plugin_obj.filter

				paramkeys['Filter/IsOn'] = ableton_parampart.as_param('IsOn', 'bool', filter_obj.on)
				paramkeys['Filter/Slot/Value'] = ableton_parampart.as_numset('SimplerFilter')
				alsfilter = paramkeys['Filter/Slot/Value']['0/SimplerFilter'] = {}
				alsfilter['Freq'] = ableton_parampart.as_param('Freq', 'float', filter_obj.freq)
				alsfilter['Res'] = ableton_parampart.as_param('Res', 'float', (filter_obj.q**0.7)/3.5)
				alsfilter['Slope'] = ableton_parampart.as_param('Slope', 'bool', filter_obj.slope>18)
				alsfilter['ModByPitch'] = ableton_parampart.as_param('ModByPitch', 'float', 0)

				if filter_obj.type.type == 'low_pass': 
					alsfilter['Type'] = ableton_parampart.as_param('Type', 'int', 0)

				if filter_obj.type.type == 'high_pass': 
					alsfilter['Type'] = ableton_parampart.as_param('Type', 'int', 1)

				if filter_obj.type.type == 'band_pass': 
					alsfilter['Type'] = ableton_parampart.as_param('Type', 'int', 2)

				if filter_obj.type.type == 'notch': 
					alsfilter['Type'] = ableton_parampart.as_param('Type', 'int', 3)

				if als_device.name == 'MultiSampler':
					lfo_pan_obj = plugin_obj.lfo_get('pan')
					paramkeys['Lfo/IsOn'] = ableton_parampart.as_param('IsOn', 'bool', True)
					paramkeys['VolumeAndPan/PanoramaLfoAmount'] = ableton_parampart.as_param('PanoramaLfoAmount', 'float', abs(lfo_pan_obj.amount))
					paramkeys['Lfo/Slot/Value'] = ableton_parampart.as_numset('SimplerLfo')
					alslfo = paramkeys['Lfo/Slot/Value']['0/SimplerLfo'] = {}
					if lfo_pan_obj.prop.shape in LFO_SHAPE:
						alslfo['Type'] = ableton_parampart.as_param('Type', 'int', LFO_SHAPE[lfo_pan_obj.prop.shape])
					alslfo['Frequency'] = ableton_parampart.as_param('Frequency', 'float', 1/lfo_pan_obj.time.speed_seconds)
					alslfo['Attack'] = ableton_parampart.as_param('Attack', 'float', lfo_pan_obj.attack*1000)
					alslfo['Retrigger'] = ableton_parampart.as_param('Retrigger', 'bool', lfo_pan_obj.retrigger)

					lfo_vol_obj = plugin_obj.lfo_get('vol')
					paramkeys['AuxLfos.0/IsOn'] = ableton_parampart.as_param('IsOn', 'bool', True)
					paramkeys['AuxLfos.0/Slot/Value'] = ableton_parampart.as_numset('SimplerAuxLfo')
					alslfo = paramkeys['AuxLfos.0/Slot/Value']['0/SimplerAuxLfo'] = {}
					if lfo_vol_obj.prop.shape in LFO_SHAPE:
						alslfo['Type'] = ableton_parampart.as_param('Type', 'int', LFO_SHAPE[lfo_vol_obj.prop.shape])
					alslfo['Frequency'] = ableton_parampart.as_param('Frequency', 'float', 1/lfo_vol_obj.time.speed_seconds)
					alslfo['Attack'] = ableton_parampart.as_param('Attack', 'float', lfo_vol_obj.attack*1000)
					alslfo['ModDst/ModConnections.0/Amount'] = ableton_parampart.as_value('Amount', lfo_vol_obj.amount*100)
					alslfo['ModDst/ModConnections.0/Connection'] = ableton_parampart.as_value('Connection', 18)
					alslfo['Retrigger'] = ableton_parampart.as_param('Retrigger', 'bool', lfo_vol_obj.retrigger)
					
					lfo_pitch_obj = plugin_obj.lfo_get('pitch')
					paramkeys['AuxLfos.1/IsOn'] = ableton_parampart.as_param('IsOn', 'bool', True)
					paramkeys['AuxLfos.1/Slot/Value'] = ableton_parampart.as_numset('SimplerAuxLfo')
					alslfo = paramkeys['AuxLfos.1/Slot/Value']['0/SimplerAuxLfo'] = {}
					if lfo_pitch_obj.prop.shape in LFO_SHAPE:
						alslfo['Type'] = ableton_parampart.as_param('Type', 'int', LFO_SHAPE[lfo_pitch_obj.prop.shape])
					alslfo['Frequency'] = ableton_parampart.as_param('Frequency', 'float', 1/lfo_pitch_obj.time.speed_seconds)
					alslfo['Attack'] = ableton_parampart.as_param('Attack', 'float', lfo_pitch_obj.attack*1000)
					alslfo['ModDst/ModConnections.0/Amount'] = ableton_parampart.as_value('Amount', (lfo_pitch_obj.amount/24)*100)
					alslfo['ModDst/ModConnections.0/Connection'] = ableton_parampart.as_value('Connection', 6)
					alslfo['Retrigger'] = ableton_parampart.as_param('Retrigger', 'bool', lfo_pitch_obj.retrigger)
				
				als_device.params.import_keys(paramkeys)

		if als_device_pitch: als_device_pitch.params.import_keys(pitchparamkeys)

	if track_obj.type == 'audio':
		tracknumid = counter_track.get()
		als_track = project_obj.add_audio_track(tracknumid)
		als_track.Color = track_color
		if track_obj.visual.name: als_track.Name.UserName = fixtxt(track_obj.visual.name)
		do_param(convproj_obj, track_obj.params, 'vol', 1, 'float', ['track', trackid, 'vol'], als_track.DeviceChain.Mixer.Volume, als_track.AutomationEnvelopes)
		do_param(convproj_obj, track_obj.params, 'pan', 0, 'float', ['track', trackid, 'pan'], als_track.DeviceChain.Mixer.Pan, als_track.AutomationEnvelopes)

		if groupnumid: 
			als_track.TrackGroupId = groupnumid
			als_track.DeviceChain.AudioOutputRouting.set('AudioOut/GroupTrack', 'Group', '')

		#print('NEW TRACK', tracknumid, trackid, groupnumid)

		if not DEBUG_IGNORE_PLACEMENTS:
			track_obj.placements.pl_audio.sort()
			do_audioclips(convproj_obj, track_obj.placements.pl_audio, track_color, als_track)

	if track_obj.type in ['instrument', 'audio']:
		do_effects(convproj_obj, als_track, track_obj.fxslots_audio)
		track_sendholders = als_track.DeviceChain.Mixer.Sends
		numsend = 0
		for returnid, x in master_returns.items():
			TrackSendHolder_obj = proj_ableton.ableton_TrackSendHolder(None)
			if returnid in track_obj.sends.data:
				send_obj = track_obj.sends.data[returnid]
				do_param(convproj_obj, send_obj.params, 'amount', 0, 'float', ['send', send_obj.sendautoid, 'amount'] if send_obj.sendautoid else None, TrackSendHolder_obj.Send, als_track.AutomationEnvelopes)
			else:
				TrackSendHolder_obj.Send.setvalue(0)
			track_sendholders[numsend] = TrackSendHolder_obj
			numsend += 1

def do_tracks(convproj_obj, project_obj, current_grouptab, track_group, groups_used, debugtxt):
	for tracktype, tid in current_grouptab:
		if tracktype == 'GROUP' and tid not in groups_used and tid in track_group:
			add_group(convproj_obj, project_obj, tid)
			groups_used.append(tid)
			do_tracks(convproj_obj, project_obj, track_group[tid], track_group, groups_used, 'GROUP: '+tid)
		if tracktype == 'TRACK':
			track_obj = convproj_obj.track_data[tid]
			if track_obj.group:
				if track_obj.group not in groups_used:
					add_group(convproj_obj, project_obj, track_obj.group)
					groups_used.append(track_obj.group)
			add_track(convproj_obj, project_obj, tid, track_obj)
		#print(debugtxt.ljust(20), tracktype, tid)

class output_ableton(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'output'
	def get_name(self): return 'Ableton Live 11'
	def get_shortname(self): return 'ableton'
	def gettype(self): return 'r'
	def get_prop(self, in_dict): 
		in_dict['plugin_arch'] = [64]
		in_dict['file_ext'] = 'als'
		in_dict['placement_cut'] = True
		in_dict['placement_loop'] = ['loop', 'loop_off', 'loop_adv', 'loop_adv_off']
		in_dict['audio_stretch'] = ['warp', 'rate']
		in_dict['plugin_included'] = ['universal:sampler:single','universal:sampler:multi','universal:sampler:slicer','native:ableton']
		in_dict['plugin_ext'] = ['vst2', 'vst3']
		in_dict['auto_types'] = ['nopl_points']
		in_dict['audio_filetypes'] = ['wav','flac','ogg','mp3']
		in_dict['fxtype'] = 'groupreturn'
		
	def parse(self, convproj_obj, output_file):
		global counter_track
		global counter_note
		global counter_keytrack
		global colordata
		global ids_group_cvpj_als
		global master_returns
		global bpm

		if AUDCLIPVERBOSE:
			for x in ['cut_type', 'cut_type', 'IsWarped', "Duration",
				"StartRelative", "LoopStart",
				"LoopEnd", "LoopOn", 
				"HidLoopStart", "HidLoopEnd"]:
				print(  str(x)[0:11].ljust(12), end=' ' )
			print()

		convproj_obj.change_timings(1, True)
		project_obj = proj_ableton.ableton_liveset()
		project_obj.make_from_scratch()

		globalstore.dataset.load('ableton', './data_main/dataset/ableton.dset')
		colordata = colors.colorset.from_dataset('ableton', 'track', 'main')

		counter_note = data_values.counter(0)
		counter_keytrack = data_values.counter(-1)

		counter_track = data_values.counter(5)

		bpm = convproj_obj.params.get('bpm', 120).value

		project_obj.add_settempotimeig(bpm, get_timesig(convproj_obj.timesig))

		als_mastertrack = project_obj.MasterTrack
		als_mastermixer = als_mastertrack.DeviceChain.Mixer
		als_masterauto = als_mastertrack.AutomationEnvelopes
		cvpj_master_params = convproj_obj.track_master.params
		als_mastertrack.Color = convproj_obj.track_master.visual.color.closest_color_index(colordata, NOCOLORNUM)
		if convproj_obj.track_master.visual.name: als_mastertrack.Name.UserName = fixtxt(convproj_obj.track_master.visual.name)
		do_param(convproj_obj, cvpj_master_params, 'vol', 1, 'float', ['master', 'vol'], als_mastermixer.Volume, als_masterauto)
		do_param(convproj_obj, cvpj_master_params, 'pan', 0, 'float', ['master', 'pan'], als_mastermixer.Pan, als_masterauto)

		tempoauto = als_mastertrack.AutomationEnvelopes.Envelopes[1]
		timesigauto = als_mastertrack.AutomationEnvelopes.Envelopes[0]

		ta_found, ta_points = convproj_obj.automation.get_autopoints(['main', 'bpm'])
		if ta_found:
			if ta_points.check():
				ta_points.remove_instant()
				firstpoint = ta_points.points[0]
				firstval = firstpoint.value
				tempoauto.Automation.Events[0][2].Value = firstval
				for num, autopoint in enumerate(ta_points):
					alsevent = proj_ableton.ableton_FloatEvent(None)
					alsevent.Time = autopoint.pos
					alsevent.Value = autopoint.value
					tempoauto.Automation.Events.append([num+1, 'FloatEvent', alsevent])

		for num, tsd in enumerate(convproj_obj.timesig_auto):
			pos, value = tsd
			alsevent = proj_ableton.ableton_EnumEvent(None)
			alsevent.Time = pos
			alsevent.Value = get_timesig(value)
			timesigauto.Automation.Events.append([num+1, 'EnumEvent', alsevent])

		master_returns = convproj_obj.track_master.returns

		do_effects(convproj_obj, als_mastertrack, convproj_obj.track_master.fxslots_audio)

		ids_group_cvpj_als = {}

		track_group = {}
		track_nongroup = []
		groups_used = []

		convproj_obj.remove_unused_groups()

		for groupid, group_obj in convproj_obj.groups.items():
			if group_obj.group:
				if group_obj.group not in track_group: track_group[group_obj.group] = []
				track_group[group_obj.group].append(['GROUP', groupid])
			else: track_nongroup.append(['GROUP', groupid])

		for trackid, track_obj in convproj_obj.iter_track():
			if track_obj.group: 
				if track_obj.group not in track_group: track_group[track_obj.group] = []
				track_group[track_obj.group].append(['TRACK', trackid])
			else: track_nongroup.append(['TRACK', trackid])

		do_tracks(convproj_obj, project_obj, track_nongroup, track_group, groups_used,'    MAIN')

		for returnid, return_obj in convproj_obj.track_master.iter_return():
			tracknumid = counter_track.get()
			als_track = project_obj.add_return_track(tracknumid)
			do_effects(convproj_obj, als_track, return_obj.fxslots_audio)
			do_param(convproj_obj, return_obj.params, 'vol', 1, 'float', ['return', returnid, 'vol'], als_track.DeviceChain.Mixer.Volume, als_track.AutomationEnvelopes)
			do_param(convproj_obj, return_obj.params, 'pan', 0, 'float', ['return', returnid, 'pan'], als_track.DeviceChain.Mixer.Pan, als_track.AutomationEnvelopes)
			als_track.Color = return_obj.visual.color.closest_color_index(colordata, NOCOLORNUM)
			if return_obj.visual.name: als_track.Name.UserName = fixtxt(return_obj.visual.name)
			track_sendholders = als_track.DeviceChain.Mixer.Sends
			numsend = 0
			for returnid, x in master_returns.items():
				TrackSendHolder_obj = proj_ableton.ableton_TrackSendHolder(None)
				if returnid in return_obj.sends.data:
					send_obj = return_obj.sends.data[returnid]
					do_param(convproj_obj, send_obj.params, 'amount', 0, 'float', ['send', send_obj.sendautoid, 'amount'] if send_obj.sendautoid else None, TrackSendHolder_obj.Send, als_track.AutomationEnvelopes)
				else:
					TrackSendHolder_obj.Send.setvalue(0)
				track_sendholders[numsend] = TrackSendHolder_obj
				numsend += 1

		for num, timemarker_obj in enumerate(convproj_obj.timemarkers):
			locator_obj = proj_ableton.ableton_Locator(None)
			locator_obj.Name = timemarker_obj.visual.name
			locator_obj.Time = timemarker_obj.position
			project_obj.Locators[num] = locator_obj

		for num, alsdata in enumerate(convproj_obj.track_master.iter_return()):
			returnid, return_obj = alsdata
			project_obj.SendsPre[num] = False

		project_obj.Transport.LoopOn = convproj_obj.loop_active
		project_obj.Transport.LoopStart = convproj_obj.loop_start
		project_obj.Transport.LoopLength = convproj_obj.loop_end-convproj_obj.loop_start

		project_obj.save_to_file(output_file)
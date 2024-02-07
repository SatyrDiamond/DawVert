# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import data_values
from objects import dv_dataset
#from functions_plugin_ext import plugin_vst2
#from functions_plugin_ext import plugin_vst3
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

colorlist = ['FF94A6','FFA529','CC9927','F7F47C','BFFB00','1AFF2F','25FFA8','5CFFE8','8BC5FF','5480E4','92A7FF','D86CE4','E553A0','FFFFFF','FF3636','F66C03','99724B','FFF034','87FF67','3DC300','00BFAF','19E9FF','10A4EE','007DC0','886CE4','B677C6','FF39D4','D0D0D0','E2675A','FFA374','D3AD71','EDFFAE','D2E498','BAD074','9BC48D','D4FDE1','CDF1F8','B9C1E3','CDBBE4','AE98E5','E5DCE1','A9A9A9','C6928B','B78256','99836A','BFBA69','A6BE00','7DB04D','88C2BA','9BB3C4','85A5C2','8393CC','A595B5','BF9FBE','BC7196','7B7B7B','AF3333','A95131','724F41','DBC300','85961F','539F31','0A9C8E','236384','1A2F96','2F52A2','624BAD','A34BAD','CC2E6E','3C3C3C']
colorlist_one = [colors.hex_to_rgb_float(color) for color in colorlist]

def get_value(xmldata, varname, fallback): 
	if len(xmldata.findall(varname)) != 0:
		xml_e = xmldata.findall(varname)[0]
		return xml_e.get('Value')
	else:
		return fallback

def get_id(xmldata, varname, fallback): 
	if len(xmldata.findall(varname)) != 0:
		xml_e = xmldata.findall(varname)[0]
		return xml_e.get('Id')

def get_nested_xml(xmldata, nestpath):
	if len(nestpath) == 0:
		return xmldata
	elif len(nestpath) >= 1:
		findxml = xmldata.findall(nestpath[0])
		if findxml: return get_nested_xml(findxml[0], nestpath[1:])
		else: return None


def use_valuetype(i_valtype, i_value): 
	if i_valtype == 'string': return str(i_value)
	if i_valtype == 'float': return float(i_value)
	if i_valtype == 'int': return int(i_value)
	if i_valtype == 'bool': return ['false','true'].index(i_value) if i_value in ['false','true'] else i_value

def get_param(xmldata, varname, vartype, fallback, i_loc, i_addmul): 
	global autoid_assoc
	if len(xmldata.findall(varname)) != 0:
		param_data = xmldata.findall(varname)[0]
		out_value = get_value(param_data, 'Manual', fallback)
		outdata = use_valuetype(vartype, out_value)
		autotarget = get_id(param_data, 'AutomationTarget', None)
		if autotarget != None: autoid_assoc.define(int(autotarget), i_loc, vartype, i_addmul)
		return outdata
	else:
		return fallback

def get_auto(x_track_data): 
	global autoid_assoc
	track_AutomationEnvelopes = x_track_data.findall('AutomationEnvelopes')[0]
	track_Envelopes = track_AutomationEnvelopes.findall('Envelopes')[0]
	for AutomationEnvelope in track_Envelopes.findall('AutomationEnvelope'):
		env_EnvelopeTarget = AutomationEnvelope.findall('EnvelopeTarget')[0]
		env_Automation = AutomationEnvelope.findall('Automation')[0]
		env_AutoEvents = env_Automation.findall('Events')[0]
		autotarget = int(get_value(env_EnvelopeTarget, 'PointeeId', None))

		autopl_obj = autoid_assoc.add_pl(autotarget, 'float')
		for env_AutoEvent in env_AutoEvents:
			if env_AutoEvent.tag == 'FloatEvent':
				autopoint_obj = autopl_obj.data.add_point()
				autopoint_obj.pos = float(env_AutoEvent.get('Time'))*4
				autopoint_obj.value = float(env_AutoEvent.get('Value'))

def get_sampleref(convproj_obj, xmldata):
	x_sampleref = xmldata.findall('SampleRef')[0]
	x_fileref = x_sampleref.findall('FileRef')[0]
	out_data = {}
	filename = get_value(x_fileref, 'Path', '')
	sampleref_obj = convproj_obj.add_sampleref(filename, filename)
	sampleref_obj.dur_samples = float(get_value(x_sampleref, 'DefaultDuration', 1))
	sampleref_obj.hz = float(get_value(x_sampleref, 'DefaultSampleRate', 1))
	sampleref_obj.timebase = sampleref_obj.hz
	sampleref_obj.dur_sec = sampleref_obj.dur_samples / sampleref_obj.hz
	return filename

def get_Range_cross(x_xml, rangename):
	x_range = x_xml.findall(rangename)[0]
	output = []
	output.append(int(get_value(x_range, 'Min', 0)))
	output.append(int(get_value(x_range, 'Max', 127)))
	output.append(int(get_value(x_range, 'CrossfadeMin', 0)))
	output.append(int(get_value(x_range, 'CrossfadeMax', 127)))
	return output

def get_Range(x_xml, rangename):
	rangevalfind = x_xml.findall(rangename)

	if len(rangevalfind) != 0:
		x_range = rangevalfind[0]
		output = []
		output.append(float(get_value(x_range, 'Min', None)))
		output.append(float(get_value(x_range, 'Max', None)))
		return output

def isfloatboolstring(valuedata): 
	if valuedata.replace('.','',1).replace('-','',1).isdigit():
		return 'float'
	elif valuedata in ['true', 'false']:
		return 'bool'
	else:
		return 'string'

lfo_beatsteps = []
for lfo_beatstep in [1/64, 1/48, 1/32, 1/24, 1/16, 1/12, 1/8, 
	1/6, 3/16, 1/4, 5/16, 1/3, 3/8, 1/2, 3/4, 1, 1.5, 2, 3, 4, 6, 8]:
	lfo_beatsteps.append( math.log2(lfo_beatstep) )


# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------


def get_MultiSampleMap(x_MultiSampleMap):
	outdata = []
	x_sampleparts = x_MultiSampleMap.findall('SampleParts')[0]
	xs_sampleparts = x_sampleparts.findall('MultiSamplePart')
	for xs_samplepart in xs_sampleparts:
		t_samppart = {}
		t_samppart['sampleref'] = get_sampleref(convproj_obj, xs_samplepart)
		t_samppart['Name'] = get_value(xs_samplepart, 'Name', '')
		t_samppart['KeyRange'] = get_Range_cross(xs_samplepart, 'KeyRange')
		t_samppart['VelocityRange'] = get_Range_cross(xs_samplepart, 'VelocityRange')
		t_samppart['SelectorRange'] = get_Range_cross(xs_samplepart, 'SelectorRange')
		t_samppart['CrossfadeMin'] = get_value(xs_samplepart, 'CrossfadeMin', 0)
		t_samppart['Detune'] = float(get_value(xs_samplepart, 'Detune', 0))/100
		t_samppart['TuneScale'] = float(get_value(xs_samplepart, 'TuneScale', 0))/100
		t_samppart['Volume'] = float(get_value(xs_samplepart, 'Volume', 1))
		t_samppart['SampleStart'] = float(get_value(xs_samplepart, 'SampleStart', 1))
		t_samppart['SampleEnd'] = float(get_value(xs_samplepart, 'SampleEnd', 1))
		for xmlname, tname in [['SustainLoop', 'loop_sustain'],['ReleaseLoop', 'loop_release']]:
			x_loop = xs_samplepart.findall(xmlname)[0]
			t_samppart[tname] = {}
			t_samppart[tname]['Start'] = int(get_value(x_loop, 'Start', 0))
			t_samppart[tname]['End'] = int(get_value(x_loop, 'End', 0))
			t_samppart[tname]['Mode'] = int(get_value(x_loop, 'Mode', 0))
			t_samppart[tname]['Crossfade'] = float(get_value(x_loop, 'Crossfade', 0))
			t_samppart[tname]['Detune'] = float(get_value(x_loop, 'Detune', 0))/100

		t_samppart_slice = {}
		t_samppart_slice['Threshold'] = int(get_value(xs_samplepart, 'SlicingThreshold', 0))
		t_samppart_slice['BeatGrid'] = int(get_value(xs_samplepart, 'SlicingBeatGrid', 0))
		t_samppart_slice['Regions'] = int(get_value(xs_samplepart, 'SlicingRegions', 0))
		t_samppart_slice['Style'] = int(get_value(xs_samplepart, 'SlicingStyle', 0))
		t_samppart_slice['UseDynamicBeatSlices'] = use_valuetype('bool', get_value(xs_samplepart, 'UseDynamicBeatSlices', 'true'))
		t_samppart_slice['UseDynamicRegionSlices'] = use_valuetype('bool', get_value(xs_samplepart, 'UseDynamicRegionSlices', 'true'))
		t_samppart_slice['Points'] = []

		x_SlicePoints = xs_samplepart.findall('SlicePoints')[0]
		for xs_SlicePoint in x_SlicePoints.findall('SlicePoint'):
			t_slice = {}
			t_slice['TimeInSeconds'] = float(xs_SlicePoint.get('TimeInSeconds'))
			t_slice['Rank'] = float(xs_SlicePoint.get('Rank'))
			t_slice['NormalizedEnergy'] = float(xs_SlicePoint.get('NormalizedEnergy'))
			t_samppart_slice['Points'].append(t_slice)

		outdata.append(t_samppart)
		
		return outdata

# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------


def do_devices(x_trackdevices, track_id, track_obj, convproj_obj):
	for x_trackdevice in x_trackdevices:
		able_plug_id = x_trackdevice.get('Id')
		if track_id != None: pluginid = track_id+'_'+able_plug_id
		else: pluginid = 'master_'+able_plug_id
		devicename = str(x_trackdevice.tag)
		is_instrument = False
		devfx_enabled = int(get_param(x_trackdevice, 'On', 'bool', True, ['slot', able_plug_id, 'enabled'], None))

		if devicename in ['OriginalSimpler', 'MultiSampler']:
			plugin_obj = convproj_obj.add_plugin(pluginid, 'sampler', 'multi')
			track_obj.inst_pluginid = pluginid

			x_samp_Player = x_trackdevice.findall('Player')[0]
			x_samp_MultiSampleMap = x_samp_Player.findall('MultiSampleMap')[0]
			x_samp_SampleParts = x_samp_MultiSampleMap.findall('SampleParts')[0]
			x_samp_MultiSampleParts = x_samp_SampleParts.findall('MultiSamplePart')

			for x_samp_MultiSamplePart in x_samp_MultiSampleParts:
				regionparams = {}
				regionparams['name'] = get_value(x_samp_MultiSamplePart, 'Name', '')

				min_max = [0,0]

				if x_samp_MultiSamplePart.findall('KeyRange')[0]:
					x_KeyRange = x_samp_MultiSamplePart.findall('KeyRange')[0]
					xv_Min = int(get_value(x_KeyRange, 'Min', '0'))-60
					xv_Max = int(get_value(x_KeyRange, 'Max', '127'))-60
					xv_CrossfadeMin = int(get_value(x_KeyRange, 'CrossfadeMin', '0'))-60
					xv_CrossfadeMax = int(get_value(x_KeyRange, 'CrossfadeMax', '127'))-60
					min_max = [xv_Min, xv_Max]
					regionparams['r_key_fade'] = [xv_CrossfadeMin, xv_CrossfadeMax]

				if x_samp_MultiSamplePart.findall('VelocityRange')[0]:
					x_VelocityRange = x_samp_MultiSamplePart.findall('VelocityRange')[0]
					xv_Min = int(get_value(x_VelocityRange, 'Min', '1'))
					xv_Max = int(get_value(x_VelocityRange, 'Max', '127'))
					xv_CrossfadeMin = int(get_value(x_VelocityRange, 'CrossfadeMin', '1'))
					xv_CrossfadeMax = int(get_value(x_VelocityRange, 'CrossfadeMax', '127'))
					regionparams['r_vel'] = [xv_Min, xv_Max]
					regionparams['r_vel_fade'] = [xv_CrossfadeMin, xv_CrossfadeMax]

				regionparams['middlenote'] = int(get_value(x_samp_MultiSamplePart, 'RootKey', '60'))-60
				regionparams['volume'] = float(get_value(x_samp_MultiSamplePart, 'volume', '1'))
				regionparams['pan'] = float(get_value(x_samp_MultiSamplePart, 'pan', '0'))

				for xmlname, dictname in [['SustainLoop', 'loop_sustain'], ['ReleaseLoop', 'loop']]:
					if x_samp_MultiSamplePart.findall(xmlname)[0]:
						x_Loop = x_samp_MultiSamplePart.findall(xmlname)[0]
						xv_Start = int(get_value(x_Loop, 'Start', '0'))
						xv_End = int(get_value(x_Loop, 'End', '1'))
						xv_Mode = int(get_value(x_Loop, 'Mode', '0'))
						xv_Crossfade = int(get_value(x_Loop, 'Crossfade', '0'))
						xv_Detune = int(get_value(x_Loop, 'Detune', '0'))
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
							regionparams['start'] = int(get_value(x_Loop, 'SampleStart', '0'))
							regionparams['end'] = int(get_value(x_Loop, 'SampleEnd', '1'))

				regionparams['sampleref'] = get_sampleref(convproj_obj, x_samp_MultiSamplePart)
				plugin_obj.regions.add(min_max[0], min_max[1], regionparams)

		else:
			plugin_obj = convproj_obj.add_plugin(pluginid, 'native-ableton', devicename)

			paramlist = dataset.params_list('plugin', devicename)
			device_type = dataset.object_var_get('group', 'plugin', devicename)

			if paramlist:
				for paramfullname in paramlist:
					parampath = paramfullname.split('/')
					paramfolder = parampath[:-1]
					paramname = parampath[-1]
					xmltag = get_nested_xml(x_trackdevice, paramfolder)
					defparams = dataset.params_i_get('plugin', devicename, paramfullname)
					
					if defparams != None and xmltag != None:
						isdata = defparams[0]
						if not defparams[0]:
							outval = get_param(xmltag, paramname, defparams[1], defparams[2], ['plugin', pluginid, paramfullname], None)
							plugin_obj.add_from_dset(paramfullname, outval, dataset, 'plugin', devicename)
						else:
							if defparams[1] != 'list': 
								outval = get_value(xmltag, paramname, defparams[2])
								if defparams[1] == 'int': outval = int(outval)
								if defparams[1] == 'float': outval = float(outval)
								if defparams[1] == 'bool': outval = (outval == 'true')
								plugin_obj.add_from_dset(paramfullname, outval, dataset, 'plugin', devicename)
							else:
								outlist = []
								iscomplete = False
								listnum = 0
								while iscomplete == False:
									outval = get_value(xmltag, paramname+'.'+str(listnum), None)
									if outval == None: iscomplete = True
									else: outlist.append(float(outval))
									listnum += 1
								plugin_obj.add_from_dset(paramfullname, outlist, dataset, 'plugin', devicename)

				if devicename == 'Looper':
					hextext = x_trackdevice.findall('SavedBuffer')[0].text
					if hextext != None: 
						plugin_obj.rawdata_add('SavedBuffer', bytes.fromhex(hextext))
				
				if devicename == 'Hybrid':
					x_Hybrid = x_trackdevice.findall('ImpulseResponseHandler')[0]
					x_SampleSlot = x_Hybrid.findall('SampleSlot')[0]
					x_Value = x_SampleSlot.findall('Value')[0]

					plugin_obj.samplerefs['sample'] = get_sampleref(convproj_obj, x_Value)

				if devicename == 'InstrumentVector':
					modcons = []
					x_ModulationConnections = x_trackdevice.findall('ModulationConnections')[0]
					x_ModulationConnectionsForInstrumentVectors = x_ModulationConnections.findall('ModulationConnectionsForInstrumentVector')
					for x_ModulationConnectionsForInstrumentVector in x_ModulationConnectionsForInstrumentVectors:
						s_modcon = {}
						s_modcon_target = x_ModulationConnectionsForInstrumentVector.get('TargetId')
						s_modcon['target'] = x_ModulationConnectionsForInstrumentVector.get('TargetId')
						s_modcon['name'] = get_value(x_ModulationConnectionsForInstrumentVector, 'TargetName', '')
						s_modcon['amounts'] = []
						for num in range(13):
							s_modcon['amounts'].append( float(get_value(x_ModulationConnectionsForInstrumentVector, 'ModulationAmounts.'+str(num), 0)) )
						modcons.append(s_modcon)
					plugin_obj.datavals.add('ModulationConnections', modcons)

					for num in range(2):
						UserSpriteNum = 'UserSprite'+str(num+1)
						x_UserSprite = x_trackdevice.findall(UserSpriteNum)
						if x_UserSprite:
							x_UserSpriteVal = x_UserSprite[0].findall('Value')
							if x_UserSpriteVal:
								if x_UserSpriteVal[0].findall('SampleRef'):
									plugin_obj.samplerefs['sample'] = get_sampleref(convproj_obj, x_UserSpriteVal[0])['file']

				if device_type == (True, 'fx'):
					plugin_obj.fxdata_add(devfx_enabled, None)
					track_obj.fxslots_audio.append(pluginid)

				if device_type == (True, 'inst'):
					track_obj.inst_pluginid = pluginid

			#else:
			#	if devicename == 'PluginDevice':
			#		x_plugdisc = x_trackdevice.findall('PluginDesc')
			#		pluginfound = False

			#		pluginvsttype = 0

			#		if x_plugdisc:
			#			xp_VstPluginInfo = x_plugdisc[0].findall('VstPluginInfo')
			#			xp_Vst3PluginInfo = x_plugdisc[0].findall('Vst3PluginInfo')

			#			if xp_VstPluginInfo:
			#				x_VstPluginInfo = xp_VstPluginInfo[0]

			#				pluginfound = True
			#				vst_WinPosX = int(get_value(x_VstPluginInfo, 'WinPosX', '0'))
			#				vst_WinPosY = int(get_value(x_VstPluginInfo, 'WinPosY', '0'))
			#				vst_Path = get_value(x_VstPluginInfo, 'Path', '')
			#				vst_PlugName = get_value(x_VstPluginInfo, 'PlugName', '')
			#				vst_UniqueId = int(get_value(x_VstPluginInfo, 'UniqueId', 0))
			#				vst_NumberOfParameters = int(get_value(x_VstPluginInfo, 'NumberOfParameters', '0'))
			#				vst_NumberOfPrograms = int(get_value(x_VstPluginInfo, 'NumberOfPrograms', '0'))
			#				pluginvsttype = int(get_value(x_VstPluginInfo, 'Category', '0'))
			#				vst_flags = int(get_value(x_VstPluginInfo, 'Flags', '0'))
			#				binflags = data_bytes.to_bin(vst_flags, 32)

			#				cvpj_plugindata = plugins.cvpj_plugin('deftype', 'vst2', 'win')
			#				song.add_visual_window(cvpj_l, 'plugin', pluginid, [vst_WinPosX, vst_WinPosY], None, False, False)

			#				plugin_obj.datavals.add('path', vst_Path)
			#				plugin_obj.datavals.add('fourid', vst_UniqueId)
			#				plugin_obj.datavals.add('numparams', vst_NumberOfParameters)

			#				vst_version = int(get_value(x_VstPluginInfo, 'Version', '0'))
			#				plugin_obj.datavals.add('version_bytes', list(struct.unpack('BBBB', struct.pack('i', vst_version))) )

			#				useschunk = binflags[21]

			#				xp_Preset = x_VstPluginInfo.findall('Preset')
			#				if xp_Preset:
			#					xp_VstPreset = xp_Preset[0].findall('VstPreset')
			#					if xp_VstPreset:
			#						x_VstPreset = xp_VstPreset[0]
			#						vst_ProgramNumber = int(get_value(x_VstPreset, 'ProgramNumber', '0'))

			#						plugin_obj.datavals.add('current_program', vst_ProgramNumber)
			#						hextext = x_VstPreset.findall('Buffer')[0].text
			#						rawbytes = bytes.fromhex(hextext) if hextext != None else b''
			#						if useschunk: 
			#							plugin_obj.datavals.add('datatype', 'chunk')
			#							plugin_vst2.replace_data(cvpj_plugindata, 'id' ,'win', vst_UniqueId, 'chunk', rawbytes, None)
			#						else:
			#							if rawbytes:
			#								rawstream = BytesIO(rawbytes)
			#								plugin_obj.datavals.add('datatype', 'params')
			#								cvpj_programs = []
			#								for num in range(vst_NumberOfPrograms):
			#									cvpj_program = {}
			#									cvpj_program['datatype'] = 'params'
			#									cvpj_program['numparams'] = vst_NumberOfParameters
			#									cvpj_program['params'] = {}
			#									cvpj_program['program_name'] = data_bytes.readstring_fixedlen(rawstream, 28, None)
			#									for paramnum in range(vst_NumberOfParameters): 
			#										cvpj_program['params'][str(paramnum)] = {'value': struct.unpack('f', rawstream.read(4))[0]}
			#									cvpj_programs.append(cvpj_program)

			#							plugin_vst2.replace_data(cvpj_plugindata, 'id' ,'win', vst_UniqueId, 'params', cvpj_programs, None)

			#			if xp_Vst3PluginInfo:
			#				x_Vst3PluginInfo = xp_Vst3PluginInfo[0]
			#				vst_WinPosX = int(get_value(x_Vst3PluginInfo, 'WinPosX', '0'))
			#				vst_WinPosY = int(get_value(x_Vst3PluginInfo, 'WinPosY', '0'))
			#				song.add_visual_window(cvpj_l, 'plugin', pluginid, [vst_WinPosX, vst_WinPosY], None, False, False)
			#				vst_Name = get_value(x_Vst3PluginInfo, 'Name', '')

			#				xp_Preset = x_Vst3PluginInfo.findall('Preset')
			#				if xp_Preset:
			#					xp_Vst3Preset = xp_Preset[0].findall('Vst3Preset')
			#					if xp_Vst3Preset:
			#						x_Vst3Preset = xp_Vst3Preset[0]

			#						pluginvsttype = int(get_value(x_Vst3PluginInfo, 'DeviceType', '0'))

			#						x_Uid = x_Vst3Preset.findall('Uid')[0]
			#						Fields_0 = int(get_value(x_Uid, 'Fields.0', '0'))
			#						Fields_1 = int(get_value(x_Uid, 'Fields.1', '0'))
			#						Fields_2 = int(get_value(x_Uid, 'Fields.2', '0'))
			#						Fields_3 = int(get_value(x_Uid, 'Fields.3', '0'))

			#						hexuuid = struct.pack('>iiii', Fields_0, Fields_1, Fields_2, Fields_3).hex().upper()

			#						hextext = x_Vst3Preset.findall('ProcessorState')[0].text
			#						rawbytes = bytes.fromhex(hextext) if hextext != None else b''

			#						pluginfound = True
			#						cvpj_plugindata = plugins.cvpj_plugin('deftype', 'vst3', 'win')
			#						plugin_obj.datavals.add('name', vst_Name)
			#						plugin_obj.datavals.add('guid', hexuuid)
			#						plugin_vst3.replace_data(cvpj_plugindata, 'id', 'win', hexuuid, rawbytes)

			#		if pluginfound:
			#			xp_ParameterList = x_trackdevice.findall('ParameterList')

			#			if xp_ParameterList:
			#				x_ParameterList = xp_ParameterList[0]

			#				pluginfloats = x_ParameterList.findall('PluginFloatParameter')
							
			#				for pluginfloat in pluginfloats:
			#					ParameterName = get_value(pluginfloat, 'ParameterName', 'noname')
			#					ParameterId = int(get_value(pluginfloat, 'ParameterId', '0'))

			#					if ParameterId != -1:
			#						cvpj_paramid = 'ext_param_'+str(ParameterId)
			#						ParameterValue = get_param(pluginfloat, 'ParameterValue', 'float', 0, ['plugin', pluginid, cvpj_paramid], None)
			#						cvpj_plugindata.param_add_minmax(cvpj_paramid, ParameterValue, 'float', ParameterName, [0,1]) 

			#		if pluginvsttype == 2:
			#			tracks_r.track_inst_pluginid(cvpj_l, track_id, pluginid)
			#			cvpj_plugindata.to_cvpj(cvpj_l, pluginid)
			#		elif pluginvsttype == 1:
			#			cvpj_plugindata.fxdata_add(devfx_enabled, None)
			#			if fxloc != None: fxslot.insert(cvpj_l, fxloc, 'audio', pluginid)
			#			cvpj_plugindata.to_cvpj(cvpj_l, pluginid)

		#if is_instrument == True:
		#	tracks_r.track_inst_pluginid(cvpj_l, track_id, pluginid)
		#else:
		#	if fxloc != None: fxslot.insert(cvpj_l, fxloc, 'audio', pluginid)
		#	plugins.add_plug_fxdata(cvpj_l, pluginid, able_plug_id, devfx_wet)

		#_______paramfinder_data[devicename] = {}
		#_______paramfinder_param[devicename] = {}
	#	if False:
	#		for x_trackdevice_name in x_trackdevice:
	#			tagname = x_trackdevice_name.tag
	#			manualval = x_trackdevice_name.findall('Manual')
	#			if tagname not in ['On', 'LomId', 'LomIdView', 'IsExpanded', 'ModulationSourceCount',
	#			'ParametersListWrapper', 'Pointee', 'LastSelectedTimeableIndex', 'LastSelectedClipEnvelopeIndex',
	#			'LastPresetRef', 'LockedScripts', 'IsFolded', 'ShouldShowPresetName', 'UserName', 'Annotation', 
	#			'SourceContext', 'OverwriteProtectionNumber']:
	#				if manualval != []:
	#					findmanval = manualval[0].get('Value')
	#					valuetype = isfloatboolstring(findmanval)
	#					#print('--PARAM--', tagname, valuetype, findmanval)

	#					#_______paramfinder_param[devicename][tagname] = [valuetype, findmanval, 
	#					#get_Range(x_trackdevice_name, 'MidiControllerRange'), 
	#					#get_Range(x_trackdevice_name, 'MidiCCOnOffThresholds')]
	#				elif x_trackdevice_name.get('Value') != None :
	#					findmanval = x_trackdevice_name.get('Value')
	#					valuetype = isfloatboolstring(findmanval)
	#					print('--DATA---', tagname, valuetype, findmanval)
	#					_______paramfinder_data[devicename][tagname] = [valuetype, findmanval]
	#				else:
	#					print('---------', tagname)


# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------------------------------







class input_ableton(plugin_input.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'ableton'
	def getname(self): return 'Ableton Live 11'
	def gettype(self): return 'r'
	def supported_autodetect(self): return False
	def getdawcapabilities(self): 
		return {
		'placement_cut': True,
		'placement_loop': ['loop', 'loop_off', 'loop_adv'],
		'placement_audio_stretch': ['warp'],
		'auto_nopl': True,
		}
	def parse(self, convproj_obj, input_file, extra_param):
		global abletondatadef_params
		global abletondatadef_data
		global dataset
		global autoid_assoc
		global tempomul

		xmlstring = ""

		convproj_obj.type = 'r'
		convproj_obj.set_timings(4, True)
		autoid_assoc = auto_id.convproj2autoid(4, True)

		dataset = dv_dataset.dataset('./data_dset/ableton.dset')

		with open(input_file, 'rb') as alsbytes:
			if alsbytes.read(2) == b'\x1f\x8b': 
				alsbytes.seek(0)
				xmlstring = gzip.decompress(alsbytes.read())
			else:
				alsbytes.seek(0)
				xmlstring = alsbytes.read().decode()

		root = ET.fromstring(xmlstring)

		abletondatadef_params = ableton_values.devicesparam()
		abletondatadef_data = ableton_values.devicesdata()

		abletonversion = root.get('MinorVersion').split('.')[0]
		if abletonversion != '11':
			print('[error] Ableton version '+abletonversion+' is not supported.')
			exit()

		x_LiveSet = root.findall('LiveSet')[0]
		x_Tracks = x_LiveSet.findall('Tracks')[0]
		x_MasterTrack = x_LiveSet.findall('MasterTrack')[0]
		x_MasterTrack_DeviceChain = x_MasterTrack.findall('DeviceChain')[0]
		x_MasterTrack_Mixer = x_MasterTrack_DeviceChain.findall('Mixer')[0]
		x_MasterTrack_DeviceChain_inside = x_MasterTrack_DeviceChain.findall('DeviceChain')[0]
		x_MasterTrack_trackdevices = x_MasterTrack_DeviceChain_inside.findall('Devices')[0]

		x_mastertrack_Name = x_MasterTrack.findall('Name')[0]
		mastertrack_name = get_value(x_mastertrack_Name, 'EffectiveName', '')
		mastertrack_color = colorlist_one[int(get_value(x_MasterTrack, 'Color', 'test'))]
		x_mastertrack_DeviceChain = x_MasterTrack.findall('DeviceChain')[0]
		x_mastertrack_Mixer = x_mastertrack_DeviceChain.findall('Mixer')[0]
		mas_track_vol = get_param(x_mastertrack_Mixer, 'Volume', 'float', 0, ['master', 'vol'], None)
		mas_track_pan = get_param(x_mastertrack_Mixer, 'Pan', 'float', 0, ['master', 'pan'], None)
		tempo = get_param(x_mastertrack_Mixer, 'Tempo', 'float', 140, ['main', 'bpm'], None)
	
		tempomul = tempo/120

		convproj_obj.track_master.visual.name = mastertrack_name
		convproj_obj.track_master.visual.color = mastertrack_color
		convproj_obj.track_master.params.add('vol', mas_track_vol, 'float')
		convproj_obj.track_master.params.add('pan', mas_track_pan, 'float')
		convproj_obj.params.add('bpm', tempo, 'float')
		do_devices(x_MasterTrack_trackdevices, None, convproj_obj.track_master, convproj_obj)



		sendnum = 1
		returnid = 1

		for x_track_data in list(x_Tracks):
			tracktype = x_track_data.tag

			x_track_DeviceChain = x_track_data.findall('DeviceChain')[0]
			x_track_Mixer = x_track_DeviceChain.findall('Mixer')[0]

			x_track_Name = x_track_data.findall('Name')[0]

			fxloc = None

			track_id = x_track_data.get('Id')
			track_name = get_value(x_track_Name, 'EffectiveName', '')
			track_color = colorlist_one[int(get_value(x_track_data, 'Color', ''))]
			track_inside_group = int(get_value(x_track_data, 'TrackGroupId', '-1'))
			track_sends = x_track_Mixer.findall('Sends')[0]
			track_sendholders = track_sends.findall('TrackSendHolder')

			if tracktype == 'MidiTrack':
				fxloc = ['track', track_id]
				print('[input-ableton] MIDI: '+track_name+' ['+track_id+']')
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['track', track_id, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['track', track_id, 'pan'], None)

				track_obj = convproj_obj.add_track(track_id, 'instrument', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

				x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
				x_track_ClipTimeable = x_track_MainSequencer.findall('ClipTimeable')[0]
				x_track_ArrangerAutomation = x_track_ClipTimeable.findall('ArrangerAutomation')[0]
				x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
				x_track_MidiClips = x_track_Events.findall('MidiClip')
				for x_track_MidiClip in x_track_MidiClips:
					placement_obj = track_obj.placements.add_notes()
					placement_obj.position = float(get_value(x_track_MidiClip, 'CurrentStart', 0))*4
					placement_obj.duration = float(get_value(x_track_MidiClip, 'CurrentEnd', 0))*4 - placement_obj.position
					placement_obj.visual.name = get_value(x_track_MidiClip, 'Name', '')
					placement_obj.visual.color = colorlist_one[int(get_value(x_track_MidiClip, 'Color', 0))]
					placement_obj.muted = ['false','true'].index(get_value(x_track_MidiClip, 'Disabled', 'false'))

					x_track_MidiClip_loop = x_track_MidiClip.findall('Loop')[0]
					note_placement_loop_l_start = float(get_value(x_track_MidiClip_loop, 'LoopStart', 0))*4
					note_placement_loop_l_end = float(get_value(x_track_MidiClip_loop, 'LoopEnd', 1))*4
					note_placement_loop_start = float(get_value(x_track_MidiClip_loop, 'StartRelative', 0))*4
					note_placement_loop_on = ['false','true'].index(get_value(x_track_MidiClip_loop, 'LoopOn', 'false'))

					if note_placement_loop_on == 1:
						placement_obj.cut_loop_data(note_placement_loop_start, note_placement_loop_l_start, note_placement_loop_l_end)
					else:
						placement_obj.cut_type = 'cut'
						placement_obj.cut_data['start'] = note_placement_loop_l_start

					x_track_MidiClip_Notes = x_track_MidiClip.findall('Notes')[0]

					t_notes_auto = {}
					x_track_MidiClip_NES = x_track_MidiClip_Notes.findall('PerNoteEventStore')[0]
					x_track_MidiClip_NES_EL = x_track_MidiClip_NES.findall('EventLists')[0]
					for x_note_nevent in x_track_MidiClip_NES_EL.findall('PerNoteEventList'):
						auto_note_id = int(x_note_nevent.get('NoteId'))
						auto_note_cc = int(x_note_nevent.get('CC'))
						t_notes_auto[auto_note_id] = []
						if auto_note_cc == -2:
							x_note_nevent_ev = x_note_nevent.findall('Events')[0]
							for ableton_point in x_note_nevent_ev.findall('PerNoteEvent'):
								ap_pos = float(ableton_point.get('TimeOffset'))*4
								ap_val = float(ableton_point.get('Value'))/170
								t_notes_auto[auto_note_id].append([ap_pos, ap_val])

					x_track_MidiClip_KT = x_track_MidiClip_Notes.findall('KeyTracks')[0]
					for x_track_MidiClip_KT_KT_s in x_track_MidiClip_KT.findall('KeyTrack'):
						t_note_key = int(get_value(x_track_MidiClip_KT_KT_s, 'MidiKey', 60))-60
						x_track_MidiClip_KT_KT_Notes = x_track_MidiClip_KT_KT_s.findall('Notes')[0]
						for x_track_MidiClip_MNE in x_track_MidiClip_KT_KT_Notes.findall('MidiNoteEvent'):
							t_note_id = int(x_track_MidiClip_MNE.get('NoteId'))
							t_note_position = float(x_track_MidiClip_MNE.get('Time'))*4
							t_note_duration = float(x_track_MidiClip_MNE.get('Duration'))*4
							t_note_vol = float(x_track_MidiClip_MNE.get('Velocity'))/100
							t_note_extra = {}
							t_note_extra['off_vol'] = float(x_track_MidiClip_MNE.get('OffVelocity'))/100
							t_note_extra['probability'] = float(x_track_MidiClip_MNE.get('Probability'))
							t_note_extra['enabled'] = ['false','true'].index(x_track_MidiClip_MNE.get('IsEnabled'))
							placement_obj.notelist.add_r(t_note_position, t_note_duration, t_note_key, t_note_vol, t_note_extra)
							if t_note_id in t_notes_auto:
								for autopoints in t_notes_auto[t_note_id]:
									autopoint_obj = placement_obj.notelist.last_add_auto('pitch')
									autopoint_obj.pos = autopoints[0]
									autopoint_obj.value = autopoints[1]

			if tracktype == 'AudioTrack':
				fxloc = ['track', track_id]
				print('[input-ableton] Audio: '+track_name+' ['+track_id+']')
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['track', track_id, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['track', track_id, 'pan'], None)

				track_obj = convproj_obj.add_track(track_id, 'audio', 1, False)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color

				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')

				x_track_MainSequencer = x_track_DeviceChain.findall('MainSequencer')[0]
				x_track_Sample = x_track_MainSequencer.findall('Sample')[0]
				x_track_ArrangerAutomation = x_track_Sample.findall('ArrangerAutomation')[0]
				x_track_Events = x_track_ArrangerAutomation.findall('Events')[0]
				x_track_AudioClips = x_track_Events.findall('AudioClip')
				for x_track_AudioClip in x_track_AudioClips:

					t_CurrentStart = float(get_value(x_track_AudioClip, 'CurrentStart', 0))
					t_CurrentEnd = float(get_value(x_track_AudioClip, 'CurrentEnd', 0))

					audio_placement_warp_on = ['false','true'].index(get_value(x_track_AudioClip, 'IsWarped', 'false'))
					audio_placement_warp_mode = int(get_value(x_track_AudioClip, 'WarpMode', 0))

					placement_obj = track_obj.placements.add_audio()
					placement_obj.position = t_CurrentStart*4
					placement_obj.duration = (t_CurrentEnd-t_CurrentStart)*4
					placement_obj.visual.name = get_value(x_track_AudioClip, 'Name', '')
					placement_obj.visual.color = colorlist_one[int(get_value(x_track_AudioClip, 'Color', 0))]
					placement_obj.muted = ['false','true'].index(get_value(x_track_AudioClip, 'Disabled', 'false'))
					placement_obj.vol = float(get_value(x_track_AudioClip, 'SampleVolume', 0))
					placement_obj.sampleref = get_sampleref(convproj_obj, x_track_AudioClip)

					x_track_AudioClip_loop = x_track_AudioClip.findall('Loop')[0]

					t_LoopStart = float(get_value(x_track_AudioClip_loop, 'LoopStart', 0))
					t_LoopEnd = float(get_value(x_track_AudioClip_loop, 'LoopEnd', 0))
					t_StartRelative = float(get_value(x_track_AudioClip_loop, 'StartRelative', 0))

					audio_placement_loop_l_start = t_LoopStart*4
					audio_placement_loop_l_end = t_LoopEnd*4
					audio_placement_loop_start = t_StartRelative*4
					audio_placement_loop_on = ['false','true'].index(get_value(x_track_AudioClip_loop, 'LoopOn', 'test'))

					audio_placement_Fade = ['false','true'].index(get_value(x_track_AudioClip, 'Fade', 'false'))
					x_track_AudioClip_fades = x_track_AudioClip.findall('Fades')[0]

					if audio_placement_Fade == 1:
						placement_obj.fade_in['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeInLength', 0))*8
						placement_obj.fade_in['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSkew', 0))
						placement_obj.fade_in['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeInCurveSlope', 0))
						placement_obj.fade_out['duration'] = float(get_value(x_track_AudioClip_fades, 'FadeOutLength', 0))*8
						placement_obj.fade_out['skew'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSkew', 0))
						placement_obj.fade_out['slope'] = float(get_value(x_track_AudioClip_fades, 'FadeOutCurveSlope', 0))

					if audio_placement_warp_on == 1:
						placement_obj.stretch.is_warped = True
						placement_obj.stretch.params = {}
						if audio_placement_warp_mode == 0:
							placement_obj.stretch.algorithm = 'beats'
							placement_obj.stretch.params['TransientResolution'] = int(get_value(x_track_AudioClip, 'TransientResolution', 6))
							placement_obj.stretch.params['TransientLoopMode'] = int(get_value(x_track_AudioClip, 'TransientLoopMode', 2))
							placement_obj.stretch.params['TransientEnvelope'] = int(get_value(x_track_AudioClip, 'TransientEnvelope', 100))
						if audio_placement_warp_mode == 1:
							placement_obj.stretch.algorithm = 'ableton_tones'
							placement_obj.stretch.params['GranularityTones'] = float(get_value(x_track_AudioClip, 'GranularityTones', 30))
						if audio_placement_warp_mode == 2:
							placement_obj.stretch.algorithm = 'ableton_texture'
							placement_obj.stretch.params['GranularityTexture'] = float(get_value(x_track_AudioClip, 'GranularityTexture', 71.328125))
							placement_obj.stretch.params['FluctuationTexture'] = float(get_value(x_track_AudioClip, 'FluctuationTexture', 27.34375))
						if audio_placement_warp_mode == 3:
							placement_obj.stretch.algorithm = 'resample'
						if audio_placement_warp_mode == 4:
							placement_obj.stretch.algorithm = 'ableton_complex'
						if audio_placement_warp_mode == 6:
							placement_obj.stretch.algorithm = 'stretch_complexpro'
							placement_obj.stretch.params['ComplexProFormants'] = float(get_value(x_track_AudioClip, 'ComplexProFormants', 100))
							placement_obj.stretch.params['ComplexProEnvelope'] = int(get_value(x_track_AudioClip, 'ComplexProEnvelope', 120))

						x_track_AudioClip_WarpMarkers_bef = x_track_AudioClip.findall('WarpMarkers')[0]
						x_track_AudioClip_WarpMarkers = x_track_AudioClip_WarpMarkers_bef.findall('WarpMarker')
						for x_track_AudioClip_WarpMarker in x_track_AudioClip_WarpMarkers:
							warp_pos = float(x_track_AudioClip_WarpMarker.get('BeatTime'))*4
							warp_pos_real = float(x_track_AudioClip_WarpMarker.get('SecTime'))
							placement_obj.stretch.warp.append([warp_pos, warp_pos_real])
					else:
						placement_obj.stretch.is_warped = False
						placement_obj.stretch.rate = (tempo/120)

					audio_placement_PitchCoarse = float(get_value(x_track_AudioClip, 'PitchCoarse', 0))
					audio_placement_PitchFine = float(get_value(x_track_AudioClip, 'PitchFine', 0))
					placement_obj.pitch = audio_placement_PitchCoarse + audio_placement_PitchFine/100

					#for value in ["CurrentStart", "CurrentEnd", "StartRelative", "LoopStart", "LoopEnd"]:
					#	print(str(get_value(x_track_AudioClip, value, 0)).ljust(20), end=' ')
					#print()

					#print(audio_placement_loop_start, audio_placement_loop_l_start, audio_placement_loop_l_end)

					if audio_placement_warp_on == False:
						if audio_placement_loop_on == 0:
							out_is_speed, out_rate = placement_obj.stretch.get(tempo, False)
							print(out_is_speed, out_rate)

							placement_obj.cut_type = 'cut'
							placement_obj.cut_data['start'] = audio_placement_loop_l_start*2
							placement_obj.duration /= out_rate
					else:
						if audio_placement_loop_on == 0:
							placement_obj.cut_type = 'cut'
							placement_obj.cut_data['start'] = audio_placement_loop_l_start
						else:
							placement_obj.cut_type = 'loop'
							placement_obj.cut_data['start'] = audio_placement_loop_start
							placement_obj.cut_data['loopstart'] = audio_placement_loop_l_start
							placement_obj.cut_data['loopend'] = audio_placement_loop_l_end

			if tracktype == 'ReturnTrack':
				get_auto(x_track_data)
				cvpj_returntrackid = 'return_'+str(returnid)
				fxloc = ['return', None, cvpj_returntrackid]
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['return', cvpj_returntrackid, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['return', cvpj_returntrackid, 'pan'], None)
				track_obj = convproj_obj.track_master.add_return(cvpj_returntrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				returnid += 1

			if tracktype == 'GroupTrack':
				get_auto(x_track_data)
				cvpj_grouptrackid = 'group_'+str(track_id)
				fxloc = ['group', cvpj_grouptrackid]
				track_vol = get_param(x_track_Mixer, 'Volume', 'float', 0, ['group', cvpj_grouptrackid, 'vol'], None)
				track_pan = get_param(x_track_Mixer, 'Pan', 'float', 0, ['group', cvpj_grouptrackid, 'pan'], None)

				track_obj = convproj_obj.add_group(cvpj_grouptrackid)
				track_obj.visual.name = track_name
				track_obj.visual.color = track_color
				track_obj.params.add('vol', track_vol, 'float')
				track_obj.params.add('pan', track_pan, 'float')
				if track_inside_group != -1: track_obj.group = 'group_'+str(track_inside_group)

			sendcount = 1
			if fxloc != None:
				get_auto(x_track_data)
				for track_sendholder in track_sendholders:
					sendid = sendcount
					sendautoid = 'send_'+track_id+'_'+str(sendid)
					sendlevel = get_param(track_sendholder, 'Send', 'float', 0, ['send', sendautoid, 'amount'], None)
					track_obj.sends.add('return_'+str(sendid), sendautoid, sendlevel)
					sendcount += 1

			x_track_DeviceChain_inside = x_track_DeviceChain.findall('DeviceChain')[0]
			x_trackdevices = x_track_DeviceChain_inside.findall('Devices')[0]
			do_devices(x_trackdevices, track_id, track_obj, convproj_obj)

		#for devicename in _______paramfinder_param:
		#	print('"'+devicename+'":', _______paramfinder_param[devicename],',')

		get_auto(x_MasterTrack)

		autoid_assoc.output(convproj_obj)

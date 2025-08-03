# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.data_bytes import bytereader
import logging
import numpy as np

def valprint(tabv, txt, val, **k):
	print(('\t'*tabv)+txt.rjust(8), val, **k)

VERBOSE = True

def decode_value_debug(byr_stream, tabnum):
	vtype = byr_stream.uint8()
	if vtype == 2: 
		value = byr_stream.int32()
		if VERBOSE: valprint(tabnum, 'INT32', value)
	elif vtype == 3: 
		value = byr_stream.uint64()
		if VERBOSE: valprint(tabnum, 'UINT64', value)
	elif vtype == 4: 
		value = byr_stream.float()
		if VERBOSE: valprint(tabnum, 'FLOAT', value)
	elif vtype == 5: 
		value = byr_stream.double()
		if VERBOSE: valprint(tabnum, 'DOUBLE', value)
	elif vtype == 6: 
		value = byr_stream.uint16()
		if VERBOSE: valprint(tabnum, 'UINT16', value)
	elif vtype == 7: 
		value = byr_stream.string(byr_stream.uint32())
		if VERBOSE: valprint(tabnum, 'STRING', value)
	elif vtype == 8: 
		value = byr_stream.raw(byr_stream.uint32())
		if VERBOSE: valprint(tabnum, 'RAW', value)
	elif vtype == 9: 
		if VERBOSE: valprint(tabnum, '>>DICT>>', '')
		numparts = byr_stream.uint32()
		value = dict([
			[
			decode_value(byr_stream, tabnum+1)[1], 
			decode_value(byr_stream, tabnum+1)] for _ in range(numparts)
			])
	elif vtype == 10: 
		if VERBOSE: valprint(tabnum, '>>LIST>>', '')
		numparts = byr_stream.uint32()
		value = [decode_value(byr_stream, tabnum+1) for _ in range(numparts)]
	else: 
		print('unknown type', vtype)
		exit()
	return vtype, value

def decode_value_1way(byr_stream):
	vtype = byr_stream.uint8()
	if vtype == 2: return byr_stream.int32()
	elif vtype == 3: return byr_stream.uint64()
	elif vtype == 4: return byr_stream.float()
	elif vtype == 5: return byr_stream.double()
	elif vtype == 6: return byr_stream.uint16()
	elif vtype == 7: return byr_stream.string(byr_stream.uint32())
	elif vtype == 8: return byr_stream.raw(byr_stream.uint32())
	elif vtype == 9: return dict([[decode_value_1way(byr_stream), decode_value_1way(byr_stream)] for _ in range(byr_stream.uint32())])
	elif vtype == 10: return [decode_value_1way(byr_stream) for _ in range(byr_stream.uint32())]
	else: 
		print('unknown type', vtype)
		exit()

class soundop_clip:
	def __init__(self, indata):
		self.AutomationLanes = indata['AutomationLanes'] if 'AutomationLanes' in indata else None
		self.AutomationLaneSel = indata['AutomationLaneSel'] if 'AutomationLaneSel' in indata else None
		self.AutomationMode = indata['AutomationMode'] if 'AutomationMode' in indata else None
		self.DispMode = indata['DispMode'] if 'DispMode' in indata else None
		self.EffectData = indata['EffectData'] if 'EffectData' in indata else None
		self.EffSel = indata['EffSel'] if 'EffSel' in indata else None
		self.FadeIn = indata['FadeIn'] if 'FadeIn' in indata else None
		self.FadeOut = indata['FadeOut'] if 'FadeOut' in indata else None
		self.FileID = indata['FileID'] if 'FileID' in indata else None
		self.FilePos = indata['FilePos'] if 'FilePos' in indata else None
		self.FreezeData = indata['FreezeData'] if 'FreezeData' in indata else None
		self.Gain = indata['Gain'] if 'Gain' in indata else None
		self.GainEnvelop = indata['GainEnvelop'] if 'GainEnvelop' in indata else None
		self.Height = indata['Height'] if 'Height' in indata else None
		self.HeightOrg = indata['HeightOrg'] if 'HeightOrg' in indata else None
		self.Hue = indata['Hue'] if 'Hue' in indata else None
		self.ID = indata['ID'] if 'ID' in indata else None
		self.Length = indata['Length'] if 'Length' in indata else None
		self.LockInTime = indata['LockInTime'] if 'LockInTime' in indata else None
		self.Loop = indata['Loop'] if 'Loop' in indata else None
		self.Minimized = indata['Minimized'] if 'Minimized' in indata else None
		self.Mute = indata['Mute'] if 'Mute' in indata else None
		self.ParamSel = indata['ParamSel'] if 'ParamSel' in indata else None
		self.Selected = indata['Selected'] if 'Selected' in indata else None
		self.StretchData = indata['StretchData'] if 'StretchData' in indata else None
		self.TakesInfo = indata['TakesInfo'] if 'TakesInfo' in indata else None
		self.Title = indata['Title'].decode('utf16') if 'Title' in indata else None
		self.TrackPos = indata['TrackPos'] if 'TrackPos' in indata else None
		self.Transparent = indata['Transparent'] if 'Transparent' in indata else None
		self.UseHue = indata['UseHue'] if 'UseHue' in indata else None
		self.zOrder = indata['zOrder'] if 'zOrder' in indata else None

class soundop_file:
	def __init__(self, indata):
		self.Length = indata['Length'] if 'Length' in indata else None
		self.SampleType = indata['SampleType'] if 'SampleType' in indata else None
		self.FilePath = indata['FilePath'].decode('utf16') if 'FilePath' in indata else None
		self.Raw = indata['Raw'] if 'Raw' in indata else None
		self.SampleRate = indata['SampleRate'] if 'SampleRate' in indata else None
		self.Offset = indata['Offset'] if 'Offset' in indata else None
		self.Channel = indata['Channel'] if 'Channel' in indata else None
		self.FileID = indata['FileID'] if 'FileID' in indata else None
		self.PathType = indata['PathType'] if 'PathType' in indata else None

class soundop_effect:
	def __init__(self, indata):
		self.Active = indata['Active'] if 'Active' in indata else None
		self.Bypass = indata['Bypass'] if 'Bypass' in indata else None
		self.DeltaSolo = indata['DeltaSolo'] if 'DeltaSolo' in indata else None
		self.EditorBottom = indata['EditorBottom'] if 'EditorBottom' in indata else None
		self.EditorLeft = indata['EditorLeft'] if 'EditorLeft' in indata else None
		self.EditorRight = indata['EditorRight'] if 'EditorRight' in indata else None
		self.EditorTop = indata['EditorTop'] if 'EditorTop' in indata else None
		self.EditorVisible = indata['EditorVisible'] if 'EditorVisible' in indata else None
		self.Envelops = indata['Envelops'] if 'Envelops' in indata else None
		self.ID = indata['ID'] if 'ID' in indata else None
		self.IsPreset = indata['IsPreset'] if 'IsPreset' in indata else None
		self.LockedAutomation = indata['LockedAutomation'] if 'LockedAutomation' in indata else None
		self.Mix = indata['Mix'] if 'Mix' in indata else None
		self.MixRatio = indata['MixRatio'] if 'MixRatio' in indata else None
		self.Name = indata['Name'].decode('utf16') if 'Name' in indata else None
		self.ProgramAsChunk = indata['ProgramAsChunk'] if 'ProgramAsChunk' in indata else None
		self.ProgramDirty = indata['ProgramDirty'] if 'ProgramDirty' in indata else None
		self.ProgramID = indata['ProgramID'] if 'ProgramID' in indata else None
		self.ProgramName = indata['ProgramName'].decode('utf16') if 'ProgramName' in indata else None
		self.SideChainActive = indata['SideChainActive'] if 'SideChainActive' in indata else None
		self.SplineState = indata['SplineState'] if 'SplineState' in indata else None
		self.StateParams = indata['StateParams'] if 'StateParams' in indata else None
		self.StateChunk = indata['StateChunk'] if 'StateChunk' in indata else None
		self.TypeID = indata['TypeID'].decode('utf16') if 'TypeID' in indata else None

class soundop_effectdata:
	def __init__(self, indata):
		self.EffectChain = indata['EffectChain'] if 'EffectChain' in indata else None
		self.Sends = indata['Sends'] if 'Sends' in indata else None
		self.Active = indata['Active'] if 'Active' in indata else None
		self.Effects = [soundop_effect(x) for x in indata['Effects']] if 'Effects' in indata else None
		self.FixedEffects = [soundop_effect(x) for x in indata['FixedEffects']] if 'FixedEffects' in indata else None
		self.PostFade = indata['PostFade'] if 'PostFade' in indata else None

class soundop_track:
	def __init__(self, indata):
		self.data_clips = []
		self.data_length = 0

		self.Active = indata['Active'] if 'Active' in indata else None
		self.AutomationLanes = indata['AutomationLanes'] if 'AutomationLanes' in indata else None
		self.AutomationLaneSel = indata['AutomationLaneSel'] if 'AutomationLaneSel' in indata else None
		self.AutomationMode = indata['AutomationMode'] if 'AutomationMode' in indata else None
		self.ChannelType = indata['ChannelType'] if 'ChannelType' in indata else None
		self.Data = indata['Data'] if 'Data' in indata else None
		self.EffectData = soundop_effectdata(indata['EffectData']) if 'EffectData' in indata else None
		self.EffectDataInput = indata['EffectDataInput'] if 'EffectDataInput' in indata else None
		self.FreezeData = indata['FreezeData'] if 'FreezeData' in indata else None
		self.Height = indata['Height'] if 'Height' in indata else None
		self.HeightOrg = indata['HeightOrg'] if 'HeightOrg' in indata else None
		self.Hue = indata['Hue'] if 'Hue' in indata else None
		self.ID = indata['ID'] if 'ID' in indata else None
		self.InputDev = indata['InputDev'] if 'InputDev' in indata else None
		self.LayersInfo = indata['LayersInfo'] if 'LayersInfo' in indata else None
		self.Minimized = indata['Minimized'] if 'Minimized' in indata else None
		self.Monitor = indata['Monitor'] if 'Monitor' in indata else None
		self.OutputDev = indata['OutputDev'] if 'OutputDev' in indata else None
		self.Record = indata['Record'] if 'Record' in indata else None
		self.ShowAutomation = indata['ShowAutomation'] if 'ShowAutomation' in indata else None
		self.ShowAutomationSave = indata['ShowAutomationSave'] if 'ShowAutomationSave' in indata else None
		self.Solo = indata['Solo'] if 'Solo' in indata else None
		self.SoloSafe = indata['SoloSafe'] if 'SoloSafe' in indata else None
		self.TabIndex = indata['TabIndex'] if 'TabIndex' in indata else None
		self.Title = indata['Title'].decode('utf16') if 'Title' in indata else None
		self.Type = indata['Type'] if 'Type' in indata else None

		if self.Data: 
			if 'Clips' in self.Data: self.data_clips = [soundop_clip(x) for x in self.Data['Clips']]
			if 'Length' in self.Data: self.data_length = self.Data['Length']

class soundop_proj:
	def __init__(self):
		self.maindata = {}

	def load_data(self, indata):
		self.StretchCaches = indata['StretchCaches'] if 'StretchCaches' in indata else None
		self.Format = indata['Format'] if 'Format' in indata else None
		self.Misc = indata['Misc'] if 'Misc' in indata else None
		self.VideoInfo = indata['VideoInfo'] if 'VideoInfo' in indata else None
		self.Metadata = indata['Metadata'] if 'Metadata' in indata else None
		self.TracksInfo = indata['TracksInfo'] if 'TracksInfo' in indata else None
		self.MarkersInfo = indata['MarkersInfo'] if 'MarkersInfo' in indata else None
		self.Tracks = [soundop_track(x) for x in indata['Tracks']] if 'Tracks' in indata else None
		self.ExportFormat = indata['ExportFormat'] if 'ExportFormat' in indata else None
		self.Version = indata['Version'] if 'Version' in indata else None
		self.Groups = indata['Groups'] if 'Groups' in indata else None
		self.FreezeCaches = indata['FreezeCaches'] if 'FreezeCaches' in indata else None
		self.Files = [soundop_file(x) for x in indata['Files']] if 'Files' in indata else None

	def load_from_file(self, input_file):
		byr_stream = bytereader.bytereader()
		byr_stream.load_file(input_file)

		byr_stream.magic_check(b'$$mcrootv0000$$')
		indata = decode_value_1way(byr_stream)

		#from pprint import pprint
		#pprint(indata)

		self.load_data(indata)
		return True
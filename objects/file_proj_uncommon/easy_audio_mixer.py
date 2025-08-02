# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import xml.etree.ElementTree as ET

def getbool(v): return v=='true'

class easyamixr_EAM1_AutomationPointClass:
	def __init__(self):
		self.BeatN = 0
		self.Value = 0
		self.ID = 0
		self.Selected = False

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'BeatN': self.BeatN = float(xpart.text)
			if tagname == 'Value': self.Value = float(xpart.text)
			if tagname == 'ID': self.ID = int(xpart.text)
			if tagname == 'Selected': self.Selected = getbool(xpart.text)

class easyamixr_EAM1_AutomationClass:
	def __init__(self):
		self.ID = 0
		self.DestinationID = 0
		self.AutomationType = 'Volume'
		self.OwnerISAudioChannel = True
		self.ParameterIndex = 0
		self.MidiControllerNumber = 0
		self.HTMLColor = ''
		self.Visible = True
		self.DisplayMode = 'Lineal'
		self.Points = []

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			if tagname == 'DestinationID': self.DestinationID = int(xpart.text)
			if tagname == 'AutomationType': self.AutomationType = xpart.text
			if tagname == 'OwnerISAudioChannel': self.OwnerISAudioChannel = getbool(xpart.text)
			if tagname == 'ParameterIndex': self.ParameterIndex = int(xpart.text)
			if tagname == 'MidiControllerNumber': self.MidiControllerNumber = int(xpart.text)
			if tagname == 'HTMLColor': self.HTMLColor = xpart.text
			if tagname == 'Visible': self.Visible = getbool(xpart.text)
			if tagname == 'DisplayMode': self.DisplayMode = xpart.text
			if tagname == 'Points':
				for t in xpart:
					if t.tag == 'AutomationPointClass':
						pointc = easyamixr_EAM1_AutomationPointClass()
						pointc.read(t)
						self.Points.append(pointc)

class easyamixr_EAM1_WaveEventClass:
	def __init__(self):
		self.ID = 0
		self.FilePath = ''
		self.StartSampleMS = 0
		self.EndSampleMS = 0
		self.Title = ''
		self.BeatPos = 0
		self.FadeIN_LengthBeats = 0
		self.FadeOUT_LengthBeats = 0
		self.Muted = False
		self.Gain = 0

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			if tagname == 'FilePath': self.FilePath = xpart.text
			if tagname == 'StartSampleMS': self.StartSampleMS = float(xpart.text)
			if tagname == 'EndSampleMS': self.EndSampleMS = float(xpart.text)
			if tagname == 'Title': self.Title = xpart.text
			if tagname == 'BeatPos': self.BeatPos = float(xpart.text)
			if tagname == 'FadeIN_LengthBeats': self.FadeIN_LengthBeats = float(xpart.text)
			if tagname == 'FadeOUT_LengthBeats': self.FadeOUT_LengthBeats = float(xpart.text)
			if tagname == 'Muted': self.Muted = getbool(xpart.text)
			if tagname == 'Gain': self.Gain = float(xpart.text)

class easyamixr_EAM1_FxInfo:
	def __init__(self):
		self.bypass = False
		self.dllPath = ''
		self.displayName = ''
		self.effectVersion = 1
		self.effectType = 0
		self.ID = 0

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'bypass': self.bypass = getbool(xpart.text)
			if tagname == 'dllPath': self.dllPath = xpart.text
			if tagname == 'displayName': self.displayName = xpart.text
			if tagname == 'effectVersion': self.effectVersion = int(xpart.text)
			if tagname == 'effectType': self.effectType = int(xpart.text)
			if tagname == 'ID': self.ID = int(xpart.text)

class easyamixr_EAM1_AudioChannel:
	def __init__(self):
		self.ID = 0
		self.Name = ''
		self.OutputID = 0
		self.InputID = -1
		self.OutputName = ''
		self.InputName = ''
		self.Type = ''
		self.Pan = 0.0
		self.Trim = 0.0
		self.Volume = 0.0
		self.VoiceRemoval = 0
		self.ChannelHeight = 100
		self.EventsColorRGB = -15234422
		self.TitleColorIndex = 1
		self.Muted = False
		self.Solo = False
		self.Record = False
		self.MonitorInput = False
		self.IsMusicChannel = True
		self.IsVideoAudio = False
		self.FXList = []
		self.EventsList = []
		self.AutomationList = []

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'ID': self.ID = int(xpart.text)
			if tagname == 'Name': self.Name = xpart.text
			if tagname == 'OutputID': self.OutputID = int(xpart.text)
			if tagname == 'InputID': self.InputID = int(xpart.text)
			if tagname == 'OutputName': self.OutputName = xpart.text
			if tagname == 'InputName': self.InputName = xpart.text
			if tagname == 'Type': self.Type = xpart.text
			if tagname == 'Pan': self.Pan = float(xpart.text)
			if tagname == 'Trim': self.Trim = float(xpart.text)
			if tagname == 'Volume': self.Volume = float(xpart.text)
			if tagname == 'VoiceRemoval': self.VoiceRemoval = int(xpart.text)
			if tagname == 'ChannelHeight': self.ChannelHeight = int(xpart.text)
			if tagname == 'EventsColorRGB': self.EventsColorRGB = int(xpart.text)
			if tagname == 'TitleColorIndex': self.TitleColorIndex = int(xpart.text)
			if tagname == 'Muted': self.Muted = getbool(xpart.text)
			if tagname == 'Solo': self.Solo = getbool(xpart.text)
			if tagname == 'Record': self.Record = getbool(xpart.text)
			if tagname == 'MonitorInput': self.MonitorInput = getbool(xpart.text)
			if tagname == 'IsMusicChannel': self.IsMusicChannel = getbool(xpart.text)
			if tagname == 'IsVideoAudio': self.IsVideoAudio = getbool(xpart.text)
			if tagname == 'FXList':
				for t in xpart:
					if t.tag == 'FxInfo':
						fxi = easyamixr_EAM1_FxInfo()
						fxi.read(t)
						self.FXList.append(fxi)
			if tagname == 'EventsList':
				for t in xpart:
					if t.tag == 'WaveEventClass':
						wavee = easyamixr_EAM1_WaveEventClass()
						wavee.read(t)
						self.EventsList.append(wavee)
			if tagname == 'AutomationList':
				for t in xpart:
					if t.tag == 'AutomationClass':
						autoc = easyamixr_EAM1_AutomationClass()
						autoc.read(t)
						self.AutomationList.append(autoc)

class easyamixr_EAMFormat1:
	def __init__(self):
		self.VideoInfo = None
		self.MinorVersion = 2
		self.ChannelsOrder = []
		self.IDCounter = 112
		self.BPM = 60
		self.TimeSignature = 5
		self.AudioChannelsList = []
		self.ProjectSettings = None
		self.SavePath = ''
		self.ExportTagSettings = None
		self.TrackEditorAlign = 1
		self.SaveFileDPI = 96

	def read(self, x_data):
		for xpart in x_data:
			tagname = xpart.tag
			if tagname == 'MinorVersion': self.MinorVersion = int(xpart.text)
			if tagname == 'IDCounter': self.IDCounter = int(xpart.text)
			if tagname == 'BPM': self.BPM = int(xpart.text)
			if tagname == 'TimeSignature': self.TimeSignature = int(xpart.text)
			if tagname == 'SavePath': self.SavePath = xpart.text
			if tagname == 'TrackEditorAlign': self.TrackEditorAlign = int(xpart.text)
			if tagname == 'SaveFileDPI': self.SaveFileDPI = int(xpart.text)
			if tagname == 'ChannelsOrder': self.ChannelsOrder = [int(x.text) for x in xpart if x.tag == 'long']
			if tagname == 'AudioChannelsList':
				for t in xpart:
					if t.tag == 'AudioChannel':
						chan = easyamixr_EAM1_AudioChannel()
						chan.read(t)
						self.AudioChannelsList.append(chan)

class easyamixr_proj:
	def __init__(self):
		self.Format = None
		self.EAMFormat1 = None

	def load_from_file(self, input_file):
		x_root = ET.parse(input_file).getroot()
		for xpart in x_root:
			if xpart.tag == 'Format': self.Format = xpart.text
			if xpart.tag == 'EAMFormat1': 
				self.EAMFormat1 = easyamixr_EAMFormat1()
				self.EAMFormat1.read(xpart)
		return True

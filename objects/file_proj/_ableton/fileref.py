# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj._ableton.func import *

class ableton_SourceContext:
	__slots__ = ['OriginalFileRef','BrowserContentPath']
	def __init__(self, xmltag):
		self.OriginalFileRef = get_list(xmltag, 'OriginalFileRef', 'FileRef', ableton_FileRef)
		self.BrowserContentPath = get_value(xmltag, 'BrowserContentPath', '')

	def write(self, xmltag):
		set_list(xmltag, self.OriginalFileRef, "OriginalFileRef", "FileRef")
		add_value(xmltag, 'BrowserContentPath', self.BrowserContentPath)

class ableton_SampleRef:
	def __init__(self, xmltag):
		if xmltag:
			x_SampleRef = xmltag.findall('SampleRef')[0]
			self.FileRef = ableton_FileRef(x_SampleRef.findall('FileRef')[0])
			self.LastModDate = int(get_value(x_SampleRef, 'LastModDate', 0))
			self.SourceContext = get_list(x_SampleRef, 'SourceContext', 'SourceContext', ableton_SourceContext)
			self.SampleUsageHint = int(get_value(x_SampleRef, 'SampleUsageHint', 0))
			self.DefaultDuration = int(get_value(x_SampleRef, 'DefaultDuration', 0))
			self.DefaultSampleRate = int(get_value(x_SampleRef, 'DefaultSampleRate', 0))
		else:
			self.FileRef = ableton_FileRef(None)
			self.LastModDate = 0
			self.SourceContext = {}
			self.SampleUsageHint = 0
			self.DefaultDuration = 0
			self.DefaultSampleRate = 0

	def write(self, xmltag):
		x_SampleRef = ET.SubElement(xmltag, "SampleRef")
		x_FileRef = ET.SubElement(x_SampleRef, "FileRef")
		self.FileRef.write(x_FileRef)
		add_value(x_SampleRef, 'LastModDate', self.LastModDate)
		set_list(x_SampleRef, self.SourceContext, "SourceContext", "SourceContext")
		add_value(x_SampleRef, 'SampleUsageHint', self.SampleUsageHint)
		add_value(x_SampleRef, 'DefaultDuration', self.DefaultDuration)
		add_value(x_SampleRef, 'DefaultSampleRate', self.DefaultSampleRate)

class ableton_FileRef:
	__slots__ = ['RelativePathType','RelativePath','Path','Type','LivePackName','LivePackId','OriginalFileSize','OriginalCrc']
	def __init__(self, xmltag):
		self.RelativePathType = int(get_value(xmltag, 'RelativePathType', 5))
		self.RelativePath = get_value(xmltag, 'RelativePath', '')
		self.Path = get_value(xmltag, 'Path', '')
		self.Type = int(get_value(xmltag, 'Type', 0))
		self.LivePackName = get_value(xmltag, 'LivePackName', '')
		self.LivePackId = get_value(xmltag, 'LivePackId', '')
		self.OriginalFileSize = int(get_value(xmltag, 'OriginalFileSize', 0))
		self.OriginalCrc = int(get_value(xmltag, 'OriginalCrc', 0))

	def write(self, xmltag):
		add_value(xmltag, 'RelativePathType', self.RelativePathType)
		add_value(xmltag, 'RelativePath', self.RelativePath)
		add_value(xmltag, 'Path', self.Path)
		add_value(xmltag, 'Type', self.Type)
		add_value(xmltag, 'LivePackName', self.LivePackName)
		add_value(xmltag, 'LivePackId', self.LivePackId)
		add_value(xmltag, 'OriginalFileSize', self.OriginalFileSize)
		add_value(xmltag, 'OriginalCrc', self.OriginalCrc)

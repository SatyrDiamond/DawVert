# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getpass

from plugins import base as dv_plugins
from functions import data_values
from objects.convproj import visual
from objects.file import audio_wav
import logging

logger_project = logging.getLogger('project')

username = getpass.getuser()

os_path = 'unix' if sys.platform != 'win32' else 'win'

class cvpj_fileref:
	__slots__ = ['os_type','filepath','relative','basename','filename','extension','win_drive','is_file']

	searchpaths = {}

	def add_searchpath_file(searchseries, in_path):
		if searchseries not in cvpj_fileref.searchpaths: cvpj_fileref.searchpaths[searchseries] = []
		outdata = [0, in_path]
		if outdata not in cvpj_fileref.searchpaths[searchseries]:
			cvpj_fileref.searchpaths[searchseries].append(outdata)

	def add_searchpath_abs(searchseries, in_path):
		if searchseries not in cvpj_fileref.searchpaths: cvpj_fileref.searchpaths[searchseries] = []
		outdata = [1, in_path]
		if outdata not in cvpj_fileref.searchpaths[searchseries]:
			cvpj_fileref.searchpaths[searchseries].append(outdata)

	def __init__(self):
		self.os_type = None
		self.win_drive = None
		self.filepath = []
		self.is_file = False
		self.basename = None
		self.filename = None
		self.extension = ''
		self.relative = False

	def change_path(self, in_path, always_folder):
		splitpath = in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

		iswindowspath = False
		if len(splitpath[0]) == 2:
			if splitpath[0][1] == ':': iswindowspath = True

		self.relative = False
		if iswindowspath:
			self.os_type = 'win'
			self.win_drive = splitpath[0][0]
			self.filepath = splitpath[1:]
		elif splitpath[0] == '': 
			self.os_type = 'unix'
			if len(splitpath)>1:
				if splitpath[1] in ['home','usr','home','mnt','media']:
					self.relative = False
					self.os_type = 'unix'
					self.filepath = splitpath[1:] if len(splitpath) != 1 else []
				else:
					self.relative = True
					self.filepath = splitpath
		else:
			self.relative = True
			self.filepath = splitpath

		self.basename = splitpath[-1]
		filenamesplit = self.basename.split('.', 1)
		self.filename = filenamesplit[0]

		if self.filepath:
			if self.filepath[0] == '.': del self.filepath[0]

		self.is_file = False

		if not always_folder:
			if len(filenamesplit) > 1:
				self.extension = filenamesplit[1]
				self.is_file = True
				self.filepath = self.filepath[0:-1]

	def changefolder(self, in_path):
		old_is_file = self.is_file
		old_filename = self.filename
		old_extension = self.extension
		self.change_path(in_path, False)
		self.is_file = old_is_file
		self.filename = old_filename
		self.extension = old_extension

	def search(self, searchseries, os_type):
		old_os_type = self.os_type
		old_win_drive = self.win_drive
		old_filepath = self.filepath.copy()
		old_is_file = self.is_file
		old_relative = self.relative
		
		old_basename = self.basename
		old_filename = self.filename
		old_extension = self.extension
		old_is_file = self.is_file

		iffound = False
		if searchseries in cvpj_fileref.searchpaths:
			for searchtype, in_path in cvpj_fileref.searchpaths[searchseries]:

				self.filepath = old_filepath.copy()

				if searchtype == 1: 
					self.change_path(in_path, True)
					self.filepath += old_filepath[1:]
					self.basename = old_basename
					self.filename = old_filename
					self.extension = old_extension
					self.is_file = old_is_file
				if searchtype == 0: 
					self.change_path(in_path, True)
					self.basename = old_basename
					self.filename = old_filename
					self.extension = old_extension
					self.is_file = old_is_file

				#print(  '-----------------------------------'  )
				#self.debugtxt()

				if self.exists(os_type): 
					iffound = True
					logger_project.info('fileref: relative found: '+self.get_path(os_type, True))
					break

		if not iffound:
			self.os_type = old_os_type
			self.win_drive = old_win_drive
			self.filepath = old_filepath
			self.is_file = old_is_file
			self.basename = old_basename
			self.filename = old_filename
			self.extension = old_extension
			self.relative = old_relative

		return iffound

	def get_filename(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.is_file else ''

	def get_basefolder(self, os_type, absolute):
		if os_type not in ['unix', 'win']: os_type = os_path
		filename = self.get_filename()
		if self.relative == False:
			if self.filepath:
				if self.os_type == 'win':
					if os_type == 'win': return self.win_drive+':\\'+'\\'.join(self.filepath+[''])
					if os_type == 'unix': return '/home/'+username+'/.wine/drive_'+self.win_drive.lower()+'/'+'/'.join(self.filepath+[''])
				if self.os_type == 'unix':
					if os_type == 'win': return 'Z:\\'+'\\'.join(self.filepath+[''])
					if os_type == 'unix': return '/'+'/'.join(self.filepath+[''])
			else:
				return ''
		else:
			if os_type == 'win': return '.'+'\\'.join(self.filepath+[''])
			elif os_type == 'unix': return '.'+'/'.join(self.filepath+[''])

	def get_path(self, os_type, absolute):
		basetxt = self.get_basefolder(os_type, absolute)
		filename = self.get_filename()
		return basetxt+filename if self.is_file else basetxt

	def exists(self, os_type):
		filepath = self.get_path(os_type, True)
		if os.path.exists(filepath): return os.path.isfile(filepath)
		else: return False

	def debugtxt(self):
		print('os_type', self.os_type)
		print('win_drive', self.win_drive)
		print('filepath', self.filepath)
		print('basename', self.basename)
		print('filename', self.filename)
		print('extension', self.extension)
		print('relative', self.relative)
		print('is_file', self.is_file)

		print('exists:win', self.exists('win'))
		print('exists:unix', self.exists('unix'))

		print('get_path:win', self.get_path('win', False))
		print('get_path:unix', self.get_path('unix', False))

VERBOSE = False

class cvpj_sampleref:
	__slots__ = ['fileref','dur_samples','dur_sec','timebase','hz','channels','found','file_size','file_date', 'visual','fileformat','loop_found','loop_start','loop_end','slices']

	def __init__(self, in_path):
		self.fileref = cvpj_fileref()
		self.found = False
		self.dur_samples = 0
		self.dur_sec = 0
		self.timebase = 44100
		self.hz = 44100
		self.channels = 1
		self.file_size = 0
		self.file_date = 0
		self.fileformat = ''
		self.loop_found = False
		self.loop_start = 0
		self.loop_end = 0
		self.slices = []
		self.visual = visual.cvpj_visual()
		self.fileref.change_path(in_path, False)
		self.get_info()
		
	def find_relative(self, searchseries):
		if not self.found:
			orgpath = self.fileref.get_path(None, False)

			iffound = False
			if not os.path.exists(orgpath):
				iffound = self.fileref.search(searchseries, 'win')

			if iffound: self.get_info()
			return iffound
		return True

	def get_info(self):
		wav_realpath = self.fileref.get_path(os_path, None)

		if os.path.exists(wav_realpath):

			self.file_size = os.path.getsize(wav_realpath)
			self.file_date = int(os.path.getmtime(wav_realpath))

			fileextlow = self.fileref.extension.lower()

			if fileextlow == 'wav':
				try:
					wav_obj = audio_wav.wav_main()
					wav_obj.readinfo(wav_realpath)
					if wav_obj.smpl.loops:
						first_loop = wav_obj.smpl.loops[0]
						self.loop_found = True
						self.loop_start = first_loop.start
						self.loop_end = first_loop.end

				except:
					pass

			for shortname, audiofileplug_obj in dv_plugins.plugins_audio_file.items():
				self.found = True
				self.visual.name = self.fileref.filename
				try:
					if fileextlow in audiofileplug_obj.file_formats:
						isvalid = audiofileplug_obj.object.getinfo(wav_realpath, self, fileextlow)
						audiofileplug_obj.file_formats
						if isvalid: break
				except: 
					if VERBOSE:
						import traceback
						print(traceback.format_exc())
					logger_project.warning('fileref: error using: '+shortname)

	def convert(self, dawaudiofiles, outpath):
		for shortname, audioconvplug_obj in dv_plugins.plugins_audio_convert.items():
			if (self.fileformat in audioconvplug_obj.in_file_formats):
				filesupported = data_values.in_both_lists(dawaudiofiles, audioconvplug_obj.out_file_formats)
				if filesupported:
					isconverted = False
					try: isconverted = audioconvplug_obj.object.convert_file(self, filesupported[0], outpath)
					except: pass
					if isconverted: 
						output_file = self.fileref.get_path(None, False)
						logger_project.info('fileref: converted "'+output_file+'" to '+filesupported[0])
						break
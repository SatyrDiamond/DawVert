# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getpass

from plugins import base as dv_plugins
from functions import data_values
from objects.convproj import visual
from objects.file import audio_wav
import copy
import logging

logger_project = logging.getLogger('project')

username = getpass.getuser()
os_path = 'unix' if sys.platform != 'win32' else 'win'
unix_folders = ['home','usr','home','mnt','media']

def splitpath_txt(in_path):
	return in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

def pathmod(folderpath, otherfolderpath):
	folderpath = folderpath.copy()
	for x in otherfolderpath:
		if x == '..': folderpath = folderpath[0:-1]
		elif x == '.': pass
		elif x == '': pass
		else: folderpath.append(x)
	return folderpath

class filesearcher_entry:
	def __init__(self):
		self.search_type = None
		self.basepath = None
		self.os_type = None
		self.mainpath = cvpj_fileref()

	def __repr__(self):
		return 'Filesearcher '+str(self.search_type)+': MainPath '+self.mainpath.get_path(None, False)

	def apply(self, fileref_obj, basepaths):
		if fileref_obj.exists(None): return True

		if self.search_type == 'partial_file' and fileref_obj.partial and self.basepath in basepaths:
			state_obj = fileref_obj.create_state()
			basefileref_obj = basepaths[self.basepath]

			fileref_obj.folderpath = pathmod(basefileref_obj.folderpath+fileref_obj.folderpath, self.mainpath.get_all())
			fileref_obj.os_type = basefileref_obj.os_type
			fileref_obj.win_drive = basefileref_obj.win_drive
			fileref_obj.partial = False

			iffound = fileref_obj.exists(None)
			if iffound: logger_project.info('fileref: file found: '+fileref_obj.get_path(None, False))
			else: fileref_obj.restore_state(state_obj)
			return iffound

		if self.search_type == 'full_append' and fileref_obj.is_file:
			state_obj = fileref_obj.create_state()
			fileref_obj.complete(self.mainpath)
			iffound = fileref_obj.exists(None)
			if iffound: logger_project.info('fileref: file found: '+fileref_obj.get_path(None, False))
			else: fileref_obj.restore_state(state_obj)
			return iffound

		return False

class filesearcher:
	basepaths = {}
	searchparts = {}

	def add_basepath(searchseries, in_path):
		pathdata = cvpj_fileref()
		pathdata.set_path(None, in_path, 0)
		if not pathdata.partial:
			filesearcher.basepaths[searchseries] = pathdata

	def add_searchpath_full_append(searchseries, in_path, os_type):
		pathdata = cvpj_fileref()
		pathdata.set_path(os_type, in_path, 0)
		if not pathdata.partial:
			searchparts = filesearcher.searchparts
			if searchseries not in searchparts: searchparts[searchseries] = []
			searchentry_obj = filesearcher_entry()
			searchentry_obj.search_type = 'full_append'
			searchentry_obj.os_type = os_type
			searchentry_obj.mainpath = pathdata
			searchparts[searchseries].append(searchentry_obj)

	def add_searchpath_full_filereplace(searchseries, in_path, os_type):
		pathdata = cvpj_fileref()
		pathdata.set_path(os_type, in_path, 0)
		if not pathdata.partial:
			searchparts = filesearcher.searchparts
			if searchseries not in searchparts: searchparts[searchseries] = []
			searchentry_obj = filesearcher_entry()
			searchentry_obj.search_type = 'full_filereplace'
			searchentry_obj.os_type = os_type
			searchentry_obj.mainpath = pathdata
			searchparts[searchseries].append(searchentry_obj)

	def add_searchpath_partial(searchseries, in_path, basepath):
		pathdata = cvpj_fileref()
		pathdata.set_path(None, in_path, 0)
		searchparts = filesearcher.searchparts
		if searchseries not in searchparts: searchparts[searchseries] = []
		searchentry_obj = filesearcher_entry()
		searchentry_obj.search_type = 'partial_file'
		searchentry_obj.mainpath = pathdata
		searchentry_obj.basepath = basepath
		searchparts[searchseries].append(searchentry_obj)

class cvpj_filename:
	def __init__(self):
		self.used = False
		self.basename = None
		self.extension = ''
		self.filename = None

	def reset(self):
		self.used = False
		self.basename = None
		self.extension = ''
		self.filename = None

	def debugtxt(self):
		print('file_basename', self.basename)
		print('file_extension', self.extension)
		print('file_filename', self.filename)

	def set(self, basename):
		self.used = True
		self.basename = basename
		filenamesplit = self.basename.split('.', 1)
		self.filename = filenamesplit[0]
		if len(filenamesplit) > 1: 
			self.extension = filenamesplit[1]
			return True
		return False

	def __str__(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.used else ''

class cvpj_fileref:
	def __init__(self):
		self.reset()

	def __repr__(self):
		return ('FILE ' if self.is_file else 'FOLDER ')+self.get_path(None, False)

	def search(self, searchseries):
		iffound = False
		if searchseries in filesearcher.searchparts:
			for spe in filesearcher.searchparts[searchseries]:
				iffound = spe.apply(self, filesearcher.basepaths)
				if iffound: break
		return iffound

	def reset(self):
		self.file = cvpj_filename()
		self.is_file = False
		self.folderpath = []
		self.os_type = None
		self.partial = True
		self.win_drive = None

	def get_all(self):
		return self.folderpath+([str(self.file)] if self.is_file else [])

	def debugtxt(self):
		self.file.debugtxt()
		print('folderpath', self.folderpath)
		print('is_file', self.is_file)
		print('os_type', self.os_type)
		print('partial', self.partial)
		print('win_drive', self.win_drive)

	def internal_basename(self, splitpath, alwaysfile):
		if splitpath:
			basename = splitpath[-1]
			if alwaysfile == 1: 
				self.is_file = True
				self.file.set(splitpath[-1])
				self.folderpath = self.folderpath[0:-1]
			elif alwaysfile == -1: 
				self.is_file = False
				self.folderpath = self.folderpath
			elif alwaysfile == 0: 
				if '.' in basename:
					self.is_file = self.file.set(basename)
					self.folderpath = self.folderpath[0:-1]
				else: self.folderpath = self.folderpath

	def internal_unix_in_win(self, splitpath):
		if not self.partial:
			if len(splitpath)>2:
				if splitpath[0] == 'cygdrive':
					self.os_type = 'win'
					self.win_drive = splitpath[1].upper()
					splitpath = splitpath[2:]

			if len(splitpath)>4:
				if splitpath[0] == 'home' and splitpath[2] == '.wine' and splitpath[3].startswith('drive_'):
					self.os_type = 'win'
					self.win_drive = splitpath[3][6:].upper()
					splitpath = splitpath[4:]
		return splitpath

	def internal_setpath_win(self, in_path, alwaysfile):
		self.reset()
		self.os_type = 'win'
		splitpath = splitpath_txt(in_path)
		if splitpath:
			if len(splitpath[0])==2 and ':' in splitpath[0]:
				self.win_drive = splitpath[0][0].upper()
				self.partial = False
				splitpath = splitpath[1:]
			elif splitpath[0] == '': splitpath = splitpath[1:]
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
			self.folderpath = splitpath
			self.internal_basename(splitpath, alwaysfile)

	def internal_setpath_unix(self, in_path, alwaysfile):
		self.reset()
		self.os_type = 'unix'
		splitpath = splitpath_txt(in_path)
		if splitpath:
			if splitpath[0] == '':
				self.partial = False
				splitpath = splitpath[1:]
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
			splitpath = self.internal_unix_in_win(splitpath)
			self.folderpath = splitpath
			self.internal_basename(splitpath, alwaysfile)

	def internal_setpath_any(self, in_path, alwaysfile):
		self.reset()
		splitpath = splitpath_txt(in_path)
		if splitpath and splitpath != ['']:
			if splitpath[0] == '':
				self.partial = False
				splitpath = splitpath[1:]
				self.os_type = 'unix'
			if len(splitpath[0])==2 and ':' in splitpath[0]:
				self.win_drive = splitpath[0][0].upper()
				self.partial = False
				splitpath = splitpath[1:]
				self.os_type = 'win'
			if not self.partial and self.os_type == 'unix':
				splitpath = self.internal_unix_in_win(splitpath)
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
			self.folderpath = splitpath
			self.internal_basename(splitpath, alwaysfile)

	def set_path(self, in_os_type, in_path, alwaysfile):
		if in_os_type == 'win': self.internal_setpath_win(in_path, alwaysfile)
		elif in_os_type == 'unix': self.internal_setpath_unix(in_path, alwaysfile)
		else: self.internal_setpath_any(in_path, alwaysfile)

	def set_folder(self, in_os_type, in_path, alwaysfile):
		old_file = copy.deepcopy(self.file)
		old_is_file = self.is_file
		self.set_path(in_os_type, in_path, alwaysfile)
		self.file = old_file
		self.is_file = old_is_file

	def get_path(self, in_os_type, nofile):
		if in_os_type not in ['unix', 'win']: in_os_type = os_path
		if not self.partial: 
			if in_os_type == 'win':
				if self.os_type == 'win': outpath = [self.win_drive+':']+self.folderpath.copy()
				else: outpath = ['Z:']+self.folderpath.copy()
			else:
				if self.os_type == 'win': outpath = ['','home',username,'.wine','drive_'+self.win_drive.lower()]+self.folderpath.copy()
				else: outpath = ['']+self.folderpath.copy()
		else: outpath = self.folderpath.copy()

		if self.is_file and not nofile: outpath.append(str(self.file))

		if in_os_type == 'win': return '\\'.join(outpath)
		else: return '/'.join(outpath)

	def exists(self, os_type):
		if os_type not in ['unix', 'win']: os_type = os_path
		filepath = self.get_path(os_type, False)
		logger_project.debug('fileref: check exist: '+filepath)
		if os.path.exists(filepath): return os.path.isfile(filepath)
		else: return False

	def get_filename(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.is_file else ''

	def complete(self, other_fileref):
		if self.partial == False and other_fileref.partial == True:
			self.folderpath = pathmod(self.folderpath, other_fileref.folderpath)
			self.partial = False
			self.file = copy.deepcopy(other_fileref.file)
			self.is_file = other_fileref.is_file

		if self.partial == True and other_fileref.partial == False:
			self.folderpath = pathmod(other_fileref.folderpath, self.folderpath)
			self.partial = False
			self.os_type = other_fileref.os_type
			self.win_drive = other_fileref.win_drive

	def create_state(self):
		state_obj = cvpj_fileref_state()
		state_obj.folderpath = self.folderpath.copy()
		state_obj.file = copy.deepcopy(self.file)
		state_obj.is_file = self.is_file
		state_obj.os_type = self.os_type
		state_obj.partial = self.partial
		state_obj.win_drive = self.win_drive
		return state_obj

	def restore_state(self, state_obj):
		self.folderpath = state_obj.folderpath.copy()
		self.file = state_obj.file
		self.is_file = state_obj.is_file
		self.os_type = state_obj.os_type
		self.partial = state_obj.partial
		self.win_drive = state_obj.win_drive

class cvpj_fileref_state:
	def __init__(self):
		self.folderpath = []
		self.file = None
		self.is_file = False
		self.os_type = None
		self.partial = True
		self.win_drive = None



VERBOSE = False

class cvpj_sampleref:
	__slots__ = ['fileref','dur_samples','dur_sec','timebase','hz','channels','found','file_size','file_date', 'visual','fileformat','loop_found','loop_start','loop_end','slices']

	def __init__(self):
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

	def set_path(self, in_os_type, in_path):
		self.fileref.set_path(in_os_type, in_path, 0)
		self.get_info()

	def find_relative(self, searchseries):

		if not self.found:
			orgpath = self.fileref.get_path(None, False)

			iffound = False
			if not os.path.exists(orgpath):
				iffound = self.fileref.search(searchseries)

			if iffound: self.get_info()

			return iffound



		return False

	def get_info(self):
		wav_realpath = self.fileref.get_path(os_path, False)

		if os.path.exists(wav_realpath):

			self.file_size = os.path.getsize(wav_realpath)
			self.file_date = int(os.path.getmtime(wav_realpath))

			fileextlow = self.fileref.file.extension.lower()

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
				self.visual.name = self.fileref.file.filename
				try:
					if fileextlow in audiofileplug_obj.file_formats:
						isvalid = audiofileplug_obj.object.getinfo(wav_realpath, self, fileextlow)
						if isvalid: break
				except: 
					if VERBOSE:
						import traceback
						print(traceback.format_exc())
					logger_project.warning('fileref: audioinfo: error using: '+shortname)

	def convert(self, dawaudiofiles, outpath):
		for shortname, audioconvplug_obj in dv_plugins.plugins_audio_convert.items():
			if (self.fileformat in audioconvplug_obj.in_file_formats):
				filesupported = data_values.list__in_both(dawaudiofiles, audioconvplug_obj.out_file_formats)
				if filesupported:
					isconverted = False
					try: isconverted = audioconvplug_obj.object.convert_file(self, filesupported[0], outpath)
					except: 
						if True:
							import traceback
							print(traceback.format_exc())
						logger_project.warning('fileref: audioconv: error using: '+shortname)
					if isconverted: 
						output_file = self.fileref.get_path(None, False)
						logger_project.info('fileref: converted "'+output_file+'" to '+filesupported[0])
						break

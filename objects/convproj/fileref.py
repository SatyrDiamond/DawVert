# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import getpass
import glob
import shutil

from plugins import base as dv_plugins
import copy
import logging

logger_project = logging.getLogger('project')
logger_filesearch = logging.getLogger('filesearch')

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

		if self.search_type == 'full_filereplace':
			state_obj = fileref_obj.create_state()
			fileref_obj.set_folder_obj(self.mainpath)
			iffound = fileref_obj.exists(None)
			if iffound: 
				logger_filesearch.debug('    >>| file found: full_filereplace >'+fileref_obj.get_path(None, False))
				logger_filesearch.debug('')
			else: 
				fileref_obj.restore_state(state_obj)
				logger_filesearch.debug('    ..| file not found: full_filereplace > '+str(self))
				logger_filesearch.debug('')
			return iffound

		if self.search_type == 'partial_file' and self.basepath in basepaths:
			state_obj = fileref_obj.create_state()
			fileref_obj.set_folder_obj(basepaths[self.basepath])
			iffound = fileref_obj.exists(None)
			if iffound:
				logger_filesearch.debug('    >>| file found: partial_file >'+fileref_obj.get_path(None, False))
				logger_filesearch.debug('')
			else:
				fileref_obj.restore_state(state_obj)
				logger_filesearch.debug('    ..| file not found: partial_file > '+str(self))
				logger_filesearch.debug('')
			return iffound

		if self.search_type == 'full_append' and fileref_obj.is_file:
			state_obj = fileref_obj.create_state()
			if_proc = fileref_obj.complete(self.mainpath)
			if if_proc:
				iffound = fileref_obj.exists(None)
				if iffound:
					logger_filesearch.debug('    >>| file found: full_append >'+fileref_obj.get_path(None, False))
					logger_filesearch.debug('')
				else:
					fileref_obj.restore_state(state_obj)
					logger_filesearch.debug('    ..| file not found: full_append > '+str(self))
					logger_filesearch.debug('')
				return iffound
			else:
				fileref_obj.restore_state(state_obj)

		return False

sampleref__searchmissing_limit = 1000

class filesearcher:
	basepaths = {}
	searchparts = {}
	searchcache = None

	def scan_local_files(dirpath):
		filesearcher.searchcache = filesearcher.searchcache
		if filesearcher.searchcache == None:
			filesearcher.searchcache = {}
			numfile = 0

			for n, file in enumerate(glob.glob(os.path.join(dirpath, "**/*"), recursive=True)):
				if os.path.isfile(file):
					fileref_obj = cvpj_fileref()
					fileref_obj.set_path(None, file, True)
					filename = str(fileref_obj.file)
					if filename not in filesearcher.searchcache:
						filesearcher.searchcache[filename] = fileref_obj
						numfile += 1
						if numfile > sampleref__searchmissing_limit: break

	def add_basepath(searchseries, in_path):
		pathdata = cvpj_fileref()
		pathdata.set_path(None, in_path, 0)
		if not pathdata.folder.partial:
			filesearcher.basepaths[searchseries] = pathdata

	def add_searchpath_full_append(searchseries, in_path, os_type):
		pathdata = cvpj_fileref()
		pathdata.set_path(os_type, in_path, 0)
		if not pathdata.folder.partial:
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
		if not pathdata.folder.partial:
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

	def reset():
		searchparts = {}

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
		print('file___basename', self.basename)
		print('file___extension', self.extension)
		print('file___filename', self.filename)

	def set(self, basename):
		self.used = True
		self.basename = basename
		filenamesplit = self.basename.rsplit('.', 1)
		self.filename = filenamesplit[0]
		if len(filenamesplit) > 1: 
			self.extension = filenamesplit[1]
			return True
		return False

	def __str__(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.used else ''

class cvpj_folderpath:
	def __init__(self):
		self.folderloc = []
		self.os_type = None
		self.partial = True
		self.win_drive = None

	def reset(self):
		self.folderloc = []
		self.os_type = None
		self.partial = True
		self.win_drive = None

	def debugtxt(self):
		print('path___folderloc', self.folderloc)
		print('path___os_type', self.os_type)
		print('path___partial', self.partial)
		print('path___win_drive', self.win_drive)

	def set(self, splitpath, is_file):
		self.folderloc = splitpath[0:-1] if is_file else splitpath

	def get_path(self, in_os_type):
		if in_os_type not in ['unix', 'win']: in_os_type = os_path
		if not self.partial: 
			if in_os_type == 'win':
				if self.os_type == 'win': outpath = [self.win_drive+':']+self.folderloc.copy()
				else: outpath = ['Z:']+self.folderloc.copy()
			else:
				if self.os_type == 'win': outpath = ['','home',username,'.wine','drive_'+self.win_drive.lower()]+self.folderloc.copy()
				else: outpath = ['']+self.folderloc.copy()
		else: outpath = self.folderloc.copy()
		return outpath

class cvpj_fileref:
	__slots__ = ['file','folder','is_file']

	def __init__(self):
		self.reset()

	def __repr__(self):
		return ('FILE ' if self.is_file else 'FOLDER ')+self.get_path(None, False)

	def copy(self):
		return copy.deepcopy(self)

	def search_local(self, dirpath):
		if self.folder.partial:
			if self.exists(None):
				orgpath = self.get_path(None, False)
				self.internal_setpath_any(os.path.abspath(orgpath), False)
				logger_filesearch.debug('    >>| abs file found: searchmissing >'+self.get_path(None, False))
				return True

		filesearcher.scan_local_files(dirpath)
		files = filesearcher.searchcache
		filename = str(self.file)

		if not self.exists(None):
			orgloc = self.folder.folderloc.copy()
			tempcopy = self.copy()
			tempcopy.set_folder(None, dirpath, False)
			newloc = tempcopy.folder.folderloc.copy()
			lenl = len(orgloc)
			found = False
			for f in range(lenl):
				tempcopy.folder.folderloc = newloc+orgloc[lenl-f-1:lenl]
				if tempcopy.exists(None): 
					found = True
					logger_filesearch.debug('    >>| path file found: searchmissing >'+self.get_path(None, False))
					self.set_folder_obj(tempcopy)
					return True

		if not self.exists(None):
			if filename in files: 
				logger_filesearch.debug('    >>| file found: searchmissing >'+self.get_path(None, False))
				fileref = files[filename]
				self.file = fileref.file
				self.folder = fileref.folder
				self.is_file = fileref.is_file
				return True
			else:
				logger_filesearch.debug('    ..| file not found: searchmissing > '+str(self.get_path(None, False)))
				return False

	def search(self, searchseries):
		iffound = False

		if searchseries in filesearcher.searchparts:
			logger_filesearch.debug('>>    | search start: '+searchseries)
			for spe in filesearcher.searchparts[searchseries]:
				iffound = spe.apply(self, filesearcher.basepaths)
				if iffound: break
		return iffound

	def reset(self):
		self.file = cvpj_filename()
		self.folder = cvpj_folderpath()
		self.is_file = False

	def get_all(self):
		return self.folder.folderloc+([str(self.file)] if self.is_file else [])

	def debugtxt(self):
		self.file.debugtxt()
		self.folder.debugtxt()
		print('is_file', self.is_file)

	def internal_basename(self, splitpath, alwaysfile):
		if splitpath:
			basename = splitpath[-1]
			if alwaysfile == 1: 
				self.is_file = True
				self.file.set(basename)
			elif alwaysfile == -1: self.is_file = False
			elif alwaysfile == 0: 
				if '.' in basename: 
					self.is_file = self.file.set(basename)
			self.folder.set(splitpath, self.is_file)

	def internal_unix_in_win(self, splitpath):
		if not self.folder.partial:
			if len(splitpath)>2:
				if splitpath[0] == 'cygdrive':
					self.folder.os_type = 'win'
					self.folder.win_drive = splitpath[1].upper()
					splitpath = splitpath[2:]

			if len(splitpath)>4:
				if splitpath[0] == 'home' and splitpath[2] == '.wine' and splitpath[3].startswith('drive_'):
					self.folder.os_type = 'win'
					self.folder.win_drive = splitpath[3][6:].upper()
					splitpath = splitpath[4:]

			if len(splitpath)>3:
				if splitpath[0] == 'mnt' and len(splitpath[1])==1:
					self.folder.os_type = 'win'
					self.folder.win_drive = splitpath[1].upper()
					splitpath = splitpath[2:]

		return splitpath

	def internal_setpath_win(self, in_path, alwaysfile):
		self.reset()
		self.folder.os_type = 'win'
		splitpath = splitpath_txt(in_path)

		if splitpath:
			if len(splitpath[0])==2 and ':' in splitpath[0]:
				self.folder.win_drive = splitpath[0][0].upper()
				self.folder.partial = False
				splitpath = splitpath[1:]
			elif splitpath[0] == '': splitpath = splitpath[1:]
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
			self.folder.folderloc = splitpath
			self.internal_basename(splitpath, alwaysfile)


	def internal_setpath_unix(self, in_path, alwaysfile):
		self.reset()
		self.folder.os_type = 'unix'
		splitpath = splitpath_txt(in_path)
		if splitpath:
			if splitpath[0] == '':
				self.folder.partial = False
				splitpath = splitpath[1:]
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
			splitpath = self.internal_unix_in_win(splitpath)
			self.internal_basename(splitpath, alwaysfile)

	def internal_setpath_any(self, in_path, alwaysfile):
		self.reset()
		splitpath = splitpath_txt(in_path)
		if splitpath and splitpath != ['']:
			if splitpath[0] == '':
				self.folder.partial = False
				splitpath = splitpath[1:]
				self.folder.os_type = 'unix'
			if len(splitpath[0])==2 and ':' in splitpath[0]:
				self.folder.win_drive = splitpath[0][0].upper()
				self.folder.partial = False
				splitpath = splitpath[1:]
				self.folder.os_type = 'win'
			if not self.folder.partial and self.folder.os_type == 'unix':
				splitpath = self.internal_unix_in_win(splitpath)
			if splitpath:
				if splitpath[-1] == '': splitpath = splitpath[:-1]
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
		outpath = self.folder.get_path(in_os_type)
		if self.is_file and not nofile: outpath.append(str(self.file))
		if in_os_type == 'win': return '\\'.join(outpath)
		else: return '/'.join(outpath)

	def exists(self, os_type):
		if os_type not in ['unix', 'win']: os_type = os_path
		filepath = self.get_path(os_type, False)
		logger_filesearch.debug('  ??  | check exist: '+filepath)
		if os.path.exists(filepath): return os.path.isfile(filepath)
		else: return False

	def get_filename(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.is_file else ''

	def complete(self, other_fileref):
		if self.folder.partial == False and other_fileref.folder.partial == True:
			self.folder.folderloc = pathmod(self.folder.folderloc, other_fileref.folder.folderloc)
			self.partial = False
			self.file = copy.deepcopy(other_fileref.file)
			self.is_file = other_fileref.is_file
			return True

		if self.folder.partial == True and other_fileref.folder.partial == False:
			self.folder.folderloc = pathmod(other_fileref.folder.folderloc, self.folder.folderloc)
			self.folder.partial = False
			self.folder.os_type = other_fileref.folder.os_type
			self.folder.win_drive = other_fileref.folder.win_drive
			return True

		return False

	def set_folder_obj(self, other_fileref):
		self.folder = copy.deepcopy(other_fileref.folder)

	def create_state(self):
		state_obj = cvpj_fileref_state()
		state_obj.folder = copy.deepcopy(self.folder)
		state_obj.file = copy.deepcopy(self.file)
		state_obj.is_file = self.is_file
		return state_obj

	def restore_state(self, state_obj):
		self.folder = copy.deepcopy(state_obj.folder)
		self.file = state_obj.file
		self.is_file = state_obj.is_file

class cvpj_fileref_state:
	def __init__(self):
		self.folder = None
		self.file = None
		self.is_file = False

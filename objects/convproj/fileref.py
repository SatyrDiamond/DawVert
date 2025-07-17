# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import getpass
import glob
import copy
from objects import globalstore

username = getpass.getuser()
unix_folders = ['home','usr','home','mnt','media']
get_path_type = globalstore.os_info_target.get_path_type

def splitpath_txt(in_path):
	return in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

def folderfile(in_path, isfile):
	pathd = splitpath_txt(in_path)
	while pathd:
		if pathd[0] == '.': pathd = pathd[1:]
		else: break
	if pathd:
		if isfile>=0:
			if '.' in pathd[-1]: return pathd[0:-1], pathd[-1]
			else: pathd[0:-1], None
		elif isfile==1:
			return pathd[0:-1], pathd[-1]
		return pathd, None
	return [], None

def pathmod(folderpath, otherfolderpath):
	folderpath = folderpath.copy()
	for x in otherfolderpath:
		if x == '..': folderpath = folderpath[0:-1]
		elif x == '.': pass
		elif x == '': pass
		else: folderpath.append(x)
	return folderpath

class cvpj_filename:
	def __init__(self):
		self.reset()

	def reset(self):
		self.used = False
		self.basename = None
		self.extension = ''
		self.filename = None

	def set(self, basename):
		if basename is not None:
			self.used = True
			self.basename = basename
			filenamesplit = self.basename.rsplit('.', 1)
			self.filename = filenamesplit[0]
			if len(filenamesplit) > 1: 
				self.extension = filenamesplit[1]
				return True
			return False
		else:
			self.reset()
			return False

	def __str__(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.used else ''

class cvpj_folderpath:
	def __init__(self):
		self.reset()

	def reset(self):
		self.folderloc = []
		self.os_type = None
		self.full = False
		self.win_drive = None

	def internal__path_win_from_unix(self):
		splitpath = self.folderloc
		if self.full:
			if len(splitpath)>2:
				if splitpath[0] == 'cygdrive': #Cygwin
					win_drive = splitpath[1].upper()
					splitpath = splitpath[2:]
					return win_drive, splitpath

			if len(splitpath)>3:
				if splitpath[0] == 'mnt' and len(splitpath[1])==1: #WSL
					win_drive = splitpath[1].upper()
					splitpath = splitpath[2:]
					return win_drive, splitpath
				if splitpath[0] == 'home' and splitpath[2] == '.wine' and splitpath[3].startswith('drive_') and len(splitpath[3])>6:
					win_drive = splitpath[3][6:].upper()[0]
					splitpath = splitpath[4:]
					return win_drive, splitpath

		return None, []

	def internal__path_unix_from_win(self):
		splitpath = self.folderloc

		if self.full and self.win_drive:
			outpath = ['','home',username,'.wine','drive_'+self.win_drive.lower()]+splitpath.copy()
			return outpath
		return ['']

	def internal__get_remove_trailing(self, splitpath):
		if splitpath:
			if splitpath[-1] == '': splitpath = splitpath[:-1]
		self.folderloc = splitpath

	def internal__setpath__win(self, splitpath):
		self.os_type = 'win'
		if len(splitpath[0])==2 and ':' in splitpath[0]:
			self.win_drive = splitpath[0][0].upper()
			self.full = True
			splitpath = splitpath[1:]
		elif splitpath[0] == '': splitpath = splitpath[1:]
		self.internal__get_remove_trailing(splitpath)

	def internal__setpath__unix(self, splitpath):
		self.os_type = 'unix'
		if splitpath[0] == '':
			self.full = True
			splitpath = splitpath[1:]
		self.internal__get_remove_trailing(splitpath)

	def internal__setpath__any(self, splitpath):
		if splitpath[0] == '':
			self.os_type = 'unix'
			self.full = True
			splitpath = splitpath[1:]
		if splitpath:
			if len(splitpath[0])==2 and ':' in splitpath[0]:
				self.os_type = 'win'
				self.win_drive = splitpath[0][0].upper()
				self.full = True
				splitpath = splitpath[1:]
			self.internal__get_remove_trailing(splitpath)
		else:
			self.reset()

	def setpath(self, o_folder, in_os_type):
		if o_folder:
			if in_os_type == 'win': self.internal__setpath__win(o_folder)
			elif in_os_type == 'unix': self.internal__setpath__unix(o_folder)
			else: self.internal__setpath__any(o_folder)
		else: self.reset()

	def internal__getpath__win(self):
		if self.os_type == 'win':
			return [self.win_drive+':']+self.folderloc.copy()
		else: 
			win_drive, splitpath = self.internal__path_win_from_unix()
			if win_drive: return [win_drive+':']+splitpath
			else: return ['Z:']+self.folderloc.copy()

	def internal__getpath__unix(self):
		if self.os_type == 'unix': return ['']+self.folderloc.copy()
		else: return self.internal__path_unix_from_win()

	def getpath(self, in_os_type):
		in_os_type = get_path_type(in_os_type)
		if in_os_type == 'org': in_os_type = self.os_type if self.os_type else 'unix'
		if self.full: 
			if in_os_type == 'win': outpath = self.internal__getpath__win()
			else: outpath = self.internal__getpath__unix()
		else: outpath = self.folderloc.copy()
		return outpath

class filesearcher:
	basepaths = {}
	searchparts = {}
	searchcache = None
	sampleref__searchmissing_limit = 1000

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
						if numfile > filesearcher.sampleref__searchmissing_limit: break

class cvpj_fileref_state:
	def __init__(self, fileref):
		self.file = copy.deepcopy(fileref.file)
		self.folder = copy.deepcopy(fileref.folder)
		self.is_file = fileref.is_file

	def restore(self, fileref):
		fileref.file = self.file
		fileref.folder = self.folder
		fileref.is_file = self.is_file

class cvpj_fileref_global:
	prefixes = {}
	prefix_groups = {}

	def reset():
		cvpj_fileref_global.prefixes = {}
		cvpj_fileref_global.prefix_groups = {}

	def internal_addgroup(name):
		prefix_groups = cvpj_fileref_global.prefix_groups
		if name:
			splitname = name.split(':')

			if len(splitname)==1:
				if splitname[0] not in prefix_groups:
					prefix_groups[splitname[0]] = [splitname[0]]

			if len(splitname)>1:
				if splitname[0] not in prefix_groups:
					prefix_groups[splitname[0]] = []
				if name not in prefix_groups[splitname[0]]: 
					prefix_groups[splitname[0]].append(name)

	def add_prefix(name, os_type, in_path):
		pathobj = cvpj_fileref()
		pathobj.set_path(os_type, in_path, -1)
		if not os_type: os_type = 'native'
		if name not in cvpj_fileref_global.prefixes:
			cvpj_fileref_global.prefixes[name] = {}
		cvpj_fileref_global.internal_addgroup(name)
		cvpj_fileref_global.prefixes[name][os_type] = pathobj.folder

	def add_prefix_extend(org_name, name, in_path):
		if org_name in cvpj_fileref_global.prefixes:
			orgprefix = cvpj_fileref_global.prefixes[org_name]
			outfold = {}
			for os_type, folder_obj in orgprefix.items():
				folder_obj = copy.deepcopy(folder_obj)
				folder_obj.folderloc += in_path
				outfold[os_type] = folder_obj
			cvpj_fileref_global.prefixes[name] = outfold
			cvpj_fileref_global.internal_addgroup(name)

class cvpj_fileref:
	__slots__ = ['file','folder','is_file','prefix','optional_prefixes']

	def __init__(self):
		self.reset()

	def reset(self):
		self.file = cvpj_filename()
		self.folder = cvpj_folderpath()
		self.is_file = False
		self.prefix = None
		self.optional_prefixes = []

	def copy(self):
		return copy.deepcopy(self)

	def prefix_apply_folder_obj(self, prefix_data):
		in_os_type = get_path_type(None)
		other_folder_obj = None
		if in_os_type in prefix_data: other_folder_obj = prefix_data[in_os_type]
		elif 'native' in prefix_data: other_folder_obj = prefix_data['native']
		if other_folder_obj: 
			other_folder_obj = copy.deepcopy(other_folder_obj)
			main_folder_obj = self.folder
			main_folder_obj.folderloc = other_folder_obj.folderloc+main_folder_obj.folderloc
			main_folder_obj.os_type = other_folder_obj.os_type
			main_folder_obj.full = other_folder_obj.full
			main_folder_obj.win_drive = other_folder_obj.win_drive
			return True
		else:
			return False

	def resolve_prefix(self):
		prefix_groups = cvpj_fileref_global.prefix_groups
		prefixes = cvpj_fileref_global.prefixes

		is_found = False
		if self.prefix in prefix_groups:
			s_prefixes = prefix_groups[self.prefix]
			if len(s_prefixes)==1:
				state = cvpj_fileref_state(self)
				self.prefix_apply_folder_obj(prefixes[s_prefixes[0]])
				if not self.exists(None): 
					state.restore(self)
				else: 
					is_found = True
					self.prefix = None
					self.optional_prefixes = []
			if len(s_prefixes)>2:
				for s_prefix in s_prefixes:
					state = cvpj_fileref_state(self)
					self.prefix_apply_folder_obj(prefixes[s_prefix])
					#print(self.exists(None), self.get_path(None, 0))
					if not self.exists(None): 
						state.restore(self)
					else: 
						is_found = True
						self.prefix = None
						self.optional_prefixes = []
						break



		return is_found
		#if not is_found:
		#	print( self.prefix, self.get_path(None, False) )

	def search_local(self, dirpath):
		prefixes = cvpj_fileref_global.prefixes

		if not self.exists(None):
			if self.optional_prefixes:
				for prefix in self.optional_prefixes:
					orgloc = self.folder.folderloc.copy()
					state = cvpj_fileref_state(self)
					self.folder.reset()
					self.prefix_apply_folder_obj(prefixes[prefix])
					if not self.exists(None): state.restore(self)
					else: return 'in_prefix'

		# partial current dir
		if not self.folder.full:
			if self.exists(None):
				is_file = self.is_file
				orgpath = self.get_path(None, False)
				outpath = os.path.abspath(orgpath)
				state = cvpj_fileref_state(self)
				self.set_path(self.folder.os_type, outpath, 1 if is_file else -1)
				if not self.exists(None): state.restore(self)
				else: return 'current_dir'

		if not self.exists(None):
			state = cvpj_fileref_state(self)
			orgloc = self.folder.folderloc.copy()
			lenl = len(orgloc)
			isfound = False
			for f in range(lenl):
				self.folder.folderloc = orgloc[0:lenl-f]
				isfound = self.exists(None)
				if isfound: break
			if not isfound: state.restore(self)
			else: return 'under_dir'

		# prev dir
		if not self.exists(None):
			filesearcher.scan_local_files(dirpath)
			files = filesearcher.searchcache
			filename = str(self.file)
			if filename in files: 
				fileref = files[filename]
				self.file = fileref.file
				self.folder = fileref.folder
				self.is_file = fileref.is_file
				return 'filesearcher'

	def get_all(self):
		return self.folder.folderloc+([str(self.file)] if self.is_file else [])

	def set_path_prefix(self, prefixname, in_path, alwaysfile):
		o_folder, o_file = folderfile(in_path, alwaysfile)
		self.prefix = prefixname
		self.folder.setpath(o_folder, None)
		self.is_file = self.file.set(o_file)

	def set_path(self, in_os_type, in_path, alwaysfile):
		o_folder, o_file = folderfile(in_path, alwaysfile)
		self.folder.setpath(o_folder, in_os_type)
		self.is_file = self.file.set(o_file)

	def set_folder(self, in_os_type, in_path, alwaysfile):
		old_file = copy.deepcopy(self.file)
		old_is_file = self.is_file
		self.set_path(in_os_type, in_path, alwaysfile)
		self.file = old_file
		self.is_file = old_is_file

	def get_path(self, in_os_type, nofile):
		outpath = self.folder.getpath(in_os_type)
		if self.is_file and not nofile: outpath.append(str(self.file))
		if in_os_type == 'win': return '\\'.join(outpath)
		else: return ('/' if not self.folder.os_type == 'win' else '\\').join(outpath)

	def exists(self, os_type):
		os_type = get_path_type(os_type)
		filepath = self.get_path(os_type, False)
		if os.path.exists(filepath): return os.path.isfile(filepath)
		else: return False

	def get_filename(self):
		return (self.filename+'.'+self.extension if self.extension else self.filename) if self.is_file else ''

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

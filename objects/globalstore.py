# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import platform
import os
import traceback
import logging
from ctypes import *
from contextlib import contextmanager
from objects.data_bytes import dv_datadef
from objects.datastorage import extplug_db as ep_class
from objects.datastorage import dataset as ds_class
from objects.datastorage import idvals as iv_class
from objects.datastorage import paramremap as pr_class
from objects.datastorage import plugts as pts_class
import sys

logger_globalstore = logging.getLogger('globalstore')

home_folder = os.path.expanduser("~")
dawvert_script_path = os.getcwd()

platform_architecture = platform.architecture()
if platform_architecture[1] == 'WindowsPE': os_platform = 'win'
else: os_platform = 'lin'

class extplug:
	def load():
		try:
			if ep_class.extplug_db.load_db(): logger_globalstore.info('extplug: Loaded database')
			return 1
		except: 
			logger_globalstore.error('extplug: Error loading database')
			return 0

	def write():
		ep_class.extplug_db.write_db()

	def get(plugtype, bycat, in_val, in_platformtxt, cpu_arch_list):
		extplug.load()
		if plugtype == 'vst2': return ep_class.vst2.get(bycat, in_val, in_platformtxt, cpu_arch_list)
		if plugtype == 'vst3': return ep_class.vst3.get(bycat, in_val, in_platformtxt, cpu_arch_list)
		if plugtype == 'clap': return ep_class.clap.get(bycat, in_val, in_platformtxt, cpu_arch_list)

	def check(plugtype, bycat, in_val):
		extplug.load()
		if plugtype == 'vst2': return ep_class.vst2.check(bycat, in_val)
		if plugtype == 'vst3': return ep_class.vst3.check(bycat, in_val)
		if plugtype == 'clap': return ep_class.clap.check(bycat, in_val)

	@contextmanager
	def add(plugtype, platformtxt):
		extplug.load()
		pluginfo_obj = ep_class.pluginfo()
		try:
			yield pluginfo_obj
		finally:
			if plugtype == 'vst2': ep_class.vst2.add(pluginfo_obj, platformtxt)
			if plugtype == 'vst3': ep_class.vst3.add(pluginfo_obj, platformtxt)
			if plugtype == 'clap': ep_class.clap.add(pluginfo_obj, platformtxt)
			if plugtype == 'ladspa': ep_class.ladspa.add(pluginfo_obj, platformtxt)

	def count(plugtype):
		if plugtype == 'vst2': return ep_class.vst2.count()
		if plugtype == 'vst3': return ep_class.vst3.count()
		if plugtype == 'clap': return ep_class.clap.count()
		if plugtype == 'ladspa': return ep_class.ladspa.count()
		if plugtype == 'all': return ep_class.vst2.count()+ep_class.vst3.count()+ep_class.clap.count()

class os_type_info:
	def __init__(self, *args):
		self.os_type = None
		self.dll_fileext = None
		self.path_type = None
		self.bits = 64 if sys.maxsize > 2**32 else 32
		self.from_platformtxt(sys.platform)

	def from_platformtxt(self, platname):
		if platname == 'win32': self.os_type = 'win'
		elif platname == 'cygwin': self.os_type = 'cygwin'
		elif platname == 'linux': self.os_type = 'linux'
		elif platname == 'linux2': self.os_type = 'linux'
		elif platname == 'msys': self.os_type = 'win'
		elif platname == 'darwin': self.os_type = 'mac'
		elif platname == 'freebsd7': self.os_type = 'freebsd7'
		elif platname == 'freebsd8': self.os_type = 'freebsd8'
		elif platname == 'freebsdN': self.os_type = 'freebsdn'
		elif platname == 'openbsd6': self.os_type = 'openbsd6'
		else: self.os_type = 'unix'

		if platname == 'win32': self.dll_fileext = '.dll'
		elif platname == 'cygwin': self.dll_fileext = '.dll'
		elif platname == 'msys': self.dll_fileext = '.dll'
		elif platname == 'darwin': self.dll_fileext = '.dylib'
		else: self.dll_fileext = '.so'

		if platname == 'win32': self.path_type = 'win'
		else: self.path_type = 'unix'

	def from_ostype(self, os_type):
		self.os_type = os_type

		if os_type == 'win': self.dll_fileext = '.dll'
		elif os_type == 'cygwin': self.dll_fileext = '.dll'
		elif os_type == 'darwin': self.dll_fileext = '.dylib'
		else: self.dll_fileext = '.so'

	def get_ext_ostype(self, platform_txt):
		if self.os_type == 'win': platform_txt = 'win'
		else: platform_txt = 'lin'
		return platform_txt

	def get_path_type(self, platform_txt):
		return platform_txt if platform_txt else self.path_type

os_info_native = os_type_info()
os_info_target = os_type_info()

class extlib:
	loaded_parts = {}

	def load_native(nameid, dllname):
		osbits = str(os_info_native.bits)
		filepath = os.path.join('.', 'libs', os_info_native.os_type+'_'+osbits, dllname+os_info_native.dll_fileext)
		return extlib.load(nameid, filepath)

	def load(nameid, filepath):
		if nameid not in extlib.loaded_parts:
			try:
				if os.path.exists(filepath):
					extlib.loaded_parts[nameid] = cdll.LoadLibrary(filepath)
					logger_globalstore.info('extlib: Loaded "'+filepath+'" as '+nameid)
					return 1
				else:
					logger_globalstore.warning('extlib: file "'+filepath+"\" dosen't exist.")
					return -1
			except: 
				#print(traceback.format_exc())
				return -1
		else: return 0

	def get(nameid):
		return extlib.loaded_parts[nameid] if nameid in extlib.loaded_parts else None

class dataset:
	loaded_parts = {}
	def load(dset_name, filepath):
		if dset_name not in dataset.loaded_parts:
			if os.path.exists(filepath):
				dataset.loaded_parts[dset_name] = ds_class.dataset(filepath)
				logger_globalstore.info('dataset: Loaded "'+filepath+'" as '+dset_name)
				return 1
			else: return -1
		else: return 0

	def get(d_id):
		return dataset.loaded_parts[d_id] if d_id in dataset.loaded_parts else None

	def get_obj(d_id, d_cat, d_item):
		o_dset = dataset.loaded_parts[d_id] if d_id in dataset.loaded_parts else None
		if o_dset:
			if d_cat in o_dset.categorys:
				return o_dset.categorys[d_cat].objects.get(d_item)

	def get_cat(d_id, d_cat):
		o_dset = dataset.loaded_parts[d_id] if d_id in dataset.loaded_parts else None
		if o_dset:
			return o_dset.categorys[d_cat] if d_cat in o_dset.categorys else None

	def get_params(d_id, d_cat, d_item):
		fldso = dataset.get_obj(d_id, d_cat, d_item)
		if fldso:
			return fldso.params.iter()
		else:
			return []

class datadef:
	loaded_parts = {}
	def load(libname, filepath):
		if libname not in datadef.loaded_parts:
			if os.path.exists(filepath):
				datadef.loaded_parts[libname] = dv_datadef.datadef(filepath)
				logger_globalstore.info('datadef: Loaded "'+filepath+'" as '+libname)
				return 1
			else: return -1
		else: return 0

	def get(libname):
		return datadef.loaded_parts[libname] if libname in datadef.loaded_parts else None
		
class idvals:
	loaded_parts = {}
	def load(libname, filepath):
		if libname not in idvals.loaded_parts:
			if os.path.exists(filepath):
				idvals.loaded_parts[libname] = iv_class.idvals(filepath)
				logger_globalstore.info('idvals: Loaded "'+filepath+'" as '+libname)
				return 1
			else: return -1
		else: return 0

	def get(libname):
		return idvals.loaded_parts[libname] if libname in idvals.loaded_parts else None

class paramremap:
	loaded_parts = {}
	def load(libname, filepath):
		if libname not in paramremap.loaded_parts:
			if os.path.exists(filepath):
				paramremap.loaded_parts[libname] = pr_class.paramremap(filepath)
				logger_globalstore.info('paramremap: Loaded "'+filepath+'" as '+libname)
				return 1
			else: return -1
		else: return 0

	def get(libname):
		return paramremap.loaded_parts[libname] if libname in paramremap.loaded_parts else None

class plugts:
	loaded_parts = {}
	def load(libname, filepath):
		if libname not in plugts.loaded_parts:
			if os.path.exists(filepath):
				plugts.loaded_parts[libname] = pts_class.plugts(filepath)
				logger_globalstore.info('plugtransform: Loaded "'+filepath+'" as '+libname)
				return 1
			else: return -1
		else: return 0

	def get(libname):
		return plugts.loaded_parts[libname] if libname in plugts.loaded_parts else None

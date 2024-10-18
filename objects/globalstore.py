# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import platform
import os
import logging
from ctypes import *
from contextlib import contextmanager
from objects.data_bytes import dv_datadef
from objects.datastorage import extplug_db as ep_class
from objects.datastorage import dataset as ds_class
from objects.datastorage import idvals as iv_class
from objects.datastorage import paramremap as pr_class
from objects.datastorage import plugts as pts_class

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

class extlib:
	loaded_parts = {}
	def load(nameid, filepath):
		if nameid not in extlib.loaded_parts:
			try:
				extlib.loaded_parts[nameid] = cdll.LoadLibrary(filepath)
				logger_globalstore.info('extlib: Loaded "'+filepath+'" as '+nameid)
				return 1
			except: return -1
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

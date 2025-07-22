# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from objects import audio_data
from objects.convproj import fileref
from plugins import base as dv_plugins
from objects.file import audio_wav
from objects.convproj import visual
from objects import globalstore
import os
import logging
import shutil
logger_project = logging.getLogger('project')
get_path_type = globalstore.os_info_target.get_path_type

VERBOSE = False

class cvpj_sampleref:

	audiofile_selector = dv_plugins.create_selector('audiofile')
	audioconv_selector = dv_plugins.create_selector('audioconv')

	def __init__(self):
		self.fileref = fileref.cvpj_fileref()
		self.found = False
		self.dur_samples = -1
		self.dur_sec = -1
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
		self.defined_meta = []




	def to_dict(self):
		out = {}
		if 'dur_samples' in self.defined_meta: out['dur_samples'] = self.dur_samples
		if 'dur_sec' in self.defined_meta: out['dur_sec'] = self.dur_sec
		if 'channels' in self.defined_meta: out['channels'] = self.channels
		if 'fileformat' in self.defined_meta: out['fileformat'] = self.fileformat
		if 'hz' in self.defined_meta: out['hz'] = self.hz
		return out

	def set_hz(self, val):
		if 'hz' not in self.defined_meta:
			self.defined_meta.append('hz')
		self.hz = val
		self.timebase = val

	def set_dur_samples(self, val):
		if 'dur_samples' not in self.defined_meta: self.defined_meta.append('dur_samples')
		self.dur_samples = val

	def set_dur_sec(self, val):
		if 'dur_sec' not in self.defined_meta: self.defined_meta.append('dur_sec')
		self.dur_sec = val

	def set_channels(self, val):
		if 'channels' not in self.defined_meta: self.defined_meta.append('channels')
		self.channels = val

	def set_fileformat(self, val):
		if 'fileformat' not in self.defined_meta: self.defined_meta.append('fileformat')
		self.fileformat = val





	def convert__dur_sec__dur_samples(self, overwrite):
		cond_samp = ('dur_samples' not in self.defined_meta) or overwrite
		if ('dur_sec' in self.defined_meta) or cond_samp:
			if ('hz' in self.defined_meta): 
				#logger_project.warning('Guessing dur_samples from dur_sec')
				self.set_dur_samples(int(self.dur_sec*self.timebase))
				return 1
			else: return -1
		else: return 0

	def convert__dur_samples__dur_sec(self, overwrite):
		cond_samp = ('dur_sec' not in self.defined_meta) or overwrite
		if ('dur_samples' in self.defined_meta) or cond_samp:
			if ('hz' in self.defined_meta): 
				#logger_project.warning('Guessing dur_sec from dur_samples')
				self.set_dur_sec(self.dur_samples/self.timebase)
				return 1
			else: return -1
		else: return 0

	def convert__path__fileformat(self):
		if ('fileformat' not in self.defined_meta):
			self.set_fileformat(self.fileref.file.extension.lower())



	def get_hz(self):
		if 'hz' not in self.defined_meta: self.get_info('get_hz')
		if 'hz' in self.defined_meta: return self.hz

	def get_hz_opt(self):
		if 'hz' in self.defined_meta: return self.hz

	def get_dur_samples(self):
		resd = self.convert__dur_sec__dur_samples(False)
		if resd == -1:
			if self.get_info('get_dur_samples'): self.convert__dur_sec__dur_samples(False)

		if 'dur_samples' in self.defined_meta:
			return self.dur_samples

	def get_dur_sec(self):
		resd = self.convert__dur_samples__dur_sec(False)
		if resd == -1:
			if self.get_info('get_dur_sec'): self.convert__dur_samples__dur_sec(False)

		if 'dur_sec' in self.defined_meta:
			return self.dur_sec

	def get_channels(self):
		if 'channels' not in self.defined_meta: self.get_info('get_channels')
		if 'channels' in self.defined_meta: return self.channels

	def get_channels_opt(self):
		if 'channels' in self.defined_meta: return self.channels

	def get_fileformat(self):
		if 'fileformat' not in self.defined_meta: self.get_info('get_fileformat')
		if 'fileformat' in self.defined_meta: return self.fileformat

	def get_exists(self):
		orgpath = self.fileref.get_path(None, False)
		return os.path.exists(orgpath)




	def set_path(self, in_os_type, in_path):
		self.fileref.set_path(in_os_type, in_path, 0)

	def set_path_prefix(self, prefixname, in_path):
		self.fileref.set_path_prefix(prefixname, in_path, 0)

	def copy_file(self, os_type, outfilename):
		filename = self.fileref.get_path(None, False)
		if os.path.exists(filename):
			shutil.copy(filename, outfilename)
			self.set_path(os_type, outfilename)
			return True

	def copy_resample(self, os_type, outfilename):
		try:
			filename = self.fileref.get_path(None, False)
			if not os.path.exists(outfilename):
				audiof_obj = audio_data.audio_obj()
				audiof_obj.from_file_wav(filename)
				logger_project.warning('sampleref: Started Resampling '+str(self.fileref.file))
				audiof_obj.resample(44100)
				audiof_obj.to_file_wav(outfilename)
				self.set_path(os_type, outfilename)
			self.hz = 44100
			return True
		except:
			filename = self.fileref.get_path(None, False)
			logger_project.warning('sampleref: Failed to Resample '+str(self.fileref.file)+'. Copying instead.')
			try:
				shutil.copy(filename, outfilename)
				self.set_path(os_type, outfilename)
			except: pass
			return False

	def search_local(self, dirpath):
		return self.fileref.search_local(dirpath)

	def get_info(self, *args):
		wav_realpath = self.fileref.get_path(get_path_type(None), False)

		if os.path.exists(wav_realpath):

			# logger_project.warning('sampleref: Getting Info from "%s"' % str(self.fileref.file) + (' because of '+args[0] if args else ''))

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

			isvalid = False
			iserror = False
			for shortname, plug_obj, prop_obj in cvpj_sampleref.audiofile_selector.iter():
				self.found = True
				self.visual.name = self.fileref.file.filename
				try:
					if fileextlow in prop_obj.file_formats:
						isvalid = plug_obj.getinfo(wav_realpath, self, fileextlow)
						if isvalid: break
				except: 
					if VERBOSE:
						import traceback
						print(traceback.format_exc())
						iserror = True
			if not isvalid and iserror:
				logger_project.warning('sampleref: audioinfo: error getting info from '+shortname)

			return True

		else:
			logger_project.warning('sampleref: Sample Not Found "%s"' % str(self.fileref.file))

			return False

	def convert(self, dawaudiofiles, outpath):

		os.makedirs(outpath, exist_ok=True)

		for shortname, plug_obj, prop_obj in cvpj_sampleref.audioconv_selector.iter():
			usable, usable_meg = plug_obj.usable()
			fileformat = self.get_fileformat()

			if (fileformat in prop_obj.in_file_formats):
				if usable:
					filesupported = data_values.list__in_both(dawaudiofiles, prop_obj.out_file_formats)
					if filesupported:
						isconverted = False
						oldpath = self.fileref.get_path(None, False)

						try: isconverted = plug_obj.convert_file(self, filesupported[0], outpath)
						except PermissionError:
							pass
						except: 
							if False:
								import traceback
								print(traceback.format_exc())
							logger_project.warning('sampleref: audioconv: error using: '+shortname)
						if isconverted: 
							logger_project.info('fileref: converted "'+oldpath+'" to '+filesupported[0])
							self.set_fileformat(filesupported[0])
							break
				else:
					logger_project.error('fileref: audiofile plugin "'+shortname+'" is not usable: '+usable_meg)

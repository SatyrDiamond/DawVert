# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import os
from objects import globalstore
import uuid

class plugsearch(plugins.base):
	def __init__(self): pass
	def get_shortname(self): return 'bidule'
	def get_name(self): return 'Bidule'
	def is_dawvert_plugin(self): return 'externalsearch'
	def get_prop(self, in_dict): in_dict['supported_os'] = ['win']
	def import_plugins(self):

		path_ploguebidule = os.path.join(globalstore.home_folder, "AppData", "Roaming", "Plogue", "Bidule")
		path_ploguebidule_vst3_64 = os.path.join(globalstore.home_folder, "AppData", "Roaming", "Plogue", "Bidule", "vst3_x64.cache")
		path_ploguebidule_vst2_64 = os.path.join(globalstore.home_folder, "AppData", "Roaming", "Plogue", "Bidule", "vst_x64.cache")
		path_ploguebidule_clap_64 = os.path.join(globalstore.home_folder, "AppData", "Roaming", "Plogue", "Bidule", "clap_x64.cache")

		vst2count = 0
		vst3count = 0
		clapcount = 0

		if os.path.exists(path_ploguebidule_vst2_64) == True:
			bio_data = open(path_ploguebidule_vst2_64, "r")
			for vstline in bio_data.readlines():
				vstsplit = vstline.strip().split(';')
				if '_' not in vstsplit[5]:
					if os.path.exists(vstsplit[0]) == True:
						vst_uniqueId = vstsplit[5]
						with globalstore.extplug.add('vst2', 'win') as pluginfo_obj:
							pluginfo_obj.id = vst_uniqueId
							pluginfo_obj.path_64bit = vstsplit[0]
							pluginfo_obj.name = vstsplit[2]
							pluginfo_obj.creator = vstsplit[3]
						vst2count += 1

		if os.path.exists(path_ploguebidule_vst3_64) == True:
			bio_data = open(path_ploguebidule_vst3_64, "r")
			for vstline in bio_data.readlines():
				vstsplit = vstline.strip().split(';')
				if '_' not in vstsplit[3]:
					if os.path.exists(vstsplit[0]) == True:
						vst_uniqueId = uuid.UUID(vstsplit[3]).hex.upper()
						with globalstore.extplug.add('vst3', 'win') as pluginfo_obj:
							pluginfo_obj.id = vst_uniqueId
							pluginfo_obj.path_64bit = vstsplit[0]
							pluginfo_obj.name = vstsplit[1]
							pluginfo_obj.creator = vstsplit[2]
						vst3count += 1

		if os.path.exists(path_ploguebidule_clap_64) == True:
			bio_data = open(path_ploguebidule_clap_64, "r")
			for vstline in bio_data.readlines():
				clapsplit = vstline.strip().split(';')
				if os.path.exists(vstsplit[0]) == True:
					vst_uniqueId = clapsplit[3]
					with globalstore.extplug.add('clap', 'win') as pluginfo_obj:
						pluginfo_obj.id = vst_uniqueId
						pluginfo_obj.path_64bit = clapsplit[0]
						pluginfo_obj.name = clapsplit[1]
						pluginfo_obj.creator = clapsplit[2]
					clapcount += 1

		print('[bidule] VST2: '+str(vst2count)+', VST3: '+str(vst3count)+', CLAP: '+str(clapcount))
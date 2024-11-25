# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects import globalstore
import os
import plugins
import configparser

class plugsearch(plugins.base):
	def get_shortname(self):
		return 'reaper'
	
	def get_name(self):
		return 'Reaper'
	
	def is_dawvert_plugin(self):
		return 'externalsearch'
	
	def get_prop(self, in_dict):
		in_dict['supported_os'] = ['win', 'lin']
	
	def import_plugins(self):
		if globalstore.os_platform == 'win': searchpath = os.path.join(globalstore.home_folder, "AppData", "Roaming", "REAPER")
		else: searchpath = os.path.join(globalstore.home_folder, ".config", "REAPER")

		vstplugins64 = configparser.RawConfigParser()
		config = configparser.RawConfigParser()

		vst2count = 0
		vst3count = 0

		r_vst_path = os.path.join(searchpath, 'reaper-vstplugins64.ini')
		if globalstore.os_platform == 'win': r_config_path = os.path.join(searchpath, 'REAPER.ini')
		else: r_config_path = os.path.join(searchpath, 'reaper.ini')

		if os.path.exists(r_vst_path) and os.path.exists(r_config_path):
			vstplugins64.read(r_vst_path)
			config.read(r_config_path)

			if globalstore.os_platform == 'win': vstpath = config['reaper']['vstpath64'].split(';')
			else: vstpath = config['REAPER']['vstpath'].split(';')

			for filename, vstpart in vstplugins64['vstcache'].items():
				splitparts = vstpart.split(',')
				if len(splitparts) > 2:
					vstid = splitparts[1]
					vstname = splitparts[2]
					is_vst3 = '{' in vstid
					is_inst = '!!!VSTi' in vstname
					is_32 = False
					vst_id = vstid.split('{')[1] if is_vst3 else vstid
					vst_name = vstname.replace('!!!VSTi', '')
					vst_mani = None
					namesplit = [p.split(')')[0] for p in vst_name.split(' (') if ')' in p][::-1]

					audioinports = 2
					audiooutports = 2

					if namesplit:
						starttxt = namesplit[0]
						if ' out' in starttxt: 
							audiooutports = int(starttxt.split(' out')[0])
							namesplit = namesplit[1:]
							vst_name = vst_name.replace(' ('+starttxt+')', '')
						if 'mono' in starttxt: 
							audioinports = 1
							audiooutports = 1
							namesplit = namesplit[1:]
							vst_name = vst_name.replace(' ('+starttxt+')', '')
						if starttxt.endswith('ch') and starttxt[0].isdigit(): 
							chsplit = starttxt.split('ch')[0]
							if '->' in starttxt:
								sepsplit = chsplit.split('->')
								audioinports = int(sepsplit[0])
								audiooutports = int(sepsplit[1])
							else:
								audiooutports = int(chsplit)
							namesplit = namesplit[1:]
							vst_name = vst_name.replace(' ('+starttxt+')', '')

						if len(namesplit) > 1:
							if 'x86' == namesplit[1]:
								is_32 = True
								vst_name = vst_name.replace(' (x86)', '')
								del namesplit[1]

						vst_mani = namesplit[0]
						vst_name = vst_name.replace(' ('+vst_mani+')', '')

						for p in vstpath:
							fullfilename = os.path.join(p, filename)
							if os.path.exists(fullfilename): break
							fullfilename = None

						if not is_vst3:
							with globalstore.extplug.add('vst2', globalstore.os_platform) as pluginfo_obj:
								pluginfo_obj.id = int(vst_id)
								pluginfo_obj.type = 'synth' if is_inst else 'effect'
								pluginfo_obj.creator = vst_mani
								pluginfo_obj.audio_num_inputs = audioinports
								pluginfo_obj.audio_num_outputs = audiooutports
							vst2count += 1
						else:
							with globalstore.extplug.add('vst3', globalstore.os_platform) as pluginfo_obj:
								pluginfo_obj.id = vst_id
								pluginfo_obj.type = 'synth' if is_inst else 'effect'
								pluginfo_obj.creator = vst_mani
								pluginfo_obj.audio_num_inputs = audioinports
								pluginfo_obj.audio_num_outputs = audiooutports
								pluginfo_obj.name = vst_name
							vst3count += 1

			print('[reaper] VST2: '+str(vst2count)+', VST3: '+str(vst3count))
			return True
		else:
			return False

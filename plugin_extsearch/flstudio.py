# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_extsearch
import os
from os.path import exists
from objects import manager_extplug
import uuid

class plugsearch(plugin_extsearch.base):
    def __init__(self): pass
    def getname(self): return 'FL Studio'
    def is_dawvert_plugin(self): return 'externalsearch'
    def issupported(self, platformtxt): return platformtxt == 'win'
    def import_plugins(self, platformtxt, homepath):

        flpath = [
        os.path.join(homepath, "Documents\\Image-Line\\FL Studio\\Presets\\Plugin database\\Installed"),
        'C:\\Program Files (x86)\\Image-Line\\Shared\\Data\\FL Studio\\Presets\\Plugin database\\Installed'
        ]

        path_flstudio = ''

        for p in flpath:
            if os.path.exists(p): 
                path_flstudio = p

        path_flstudio_vst2_inst = os.path.join(path_flstudio, "Generators", "VST")
        path_flstudio_vst2_fx = os.path.join(path_flstudio, "Effects", "VST")
        path_flstudio_vst3_inst = os.path.join(path_flstudio, "Generators", "VST3")
        path_flstudio_vst3_fx = os.path.join(path_flstudio, "Effects", "VST3")

        vst2count = 0
        vst3count = 0
        for pathtype in [ ['vst2',path_flstudio_vst2_inst],['vst2',path_flstudio_vst2_fx],['vst3',path_flstudio_vst3_inst],['vst3',path_flstudio_vst3_fx] ]:
            if os.path.exists(pathtype[1]): 
                for filename in os.listdir(pathtype[1]):
                    if '.nfo' in filename:
                        bio_data = open(pathtype[1]+'\\'+filename, "r")
                        flp_nfo_plugdata = bio_data.readlines()

                        dict_vstinfo = {}
                        for s_flp_nfo_plugdata in flp_nfo_plugdata:
                            splittedtxt = s_flp_nfo_plugdata.strip().split('=')
                            dict_vstinfo[splittedtxt[0]] = splittedtxt[1]

                        for filenum in range(int(dict_vstinfo['ps_files'])):
                            if pathtype[0] == 'vst2':
                                if 'ps_file_magic_'+str(filenum) in dict_vstinfo:
                                    if os.path.exists(dict_vstinfo['ps_file_filename_'+str(filenum)]):
                                        pluginfo_obj = manager_extplug.pluginfo()
                                        pluginfo_obj.id = dict_vstinfo['ps_file_magic_'+str(filenum)]
                                        pluginfo_obj.name = dict_vstinfo['ps_file_name_'+str(filenum)]
                                        if 'ps_file_vendorname_'+str(filenum) in dict_vstinfo: pluginfo_obj.creator = dict_vstinfo['ps_file_vendorname_'+str(filenum)]
                                        if 'ps_file_category_'+str(filenum) in dict_vstinfo: pluginfo_obj.type = dict_vstinfo['ps_file_category_'+str(filenum)].lower()
                                        if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '32': pluginfo_obj.path_32bit = dict_vstinfo['ps_file_filename_'+str(filenum)]
                                        if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '64': pluginfo_obj.path_64bit = dict_vstinfo['ps_file_filename_'+str(filenum)]
                                        manager_extplug.vst2_add(pluginfo_obj, 'win')
                                        vst2count += 1

                            if pathtype[0] == 'vst3':
                                if 'ps_file_guid_'+str(filenum) in dict_vstinfo:
                                    if os.path.exists(dict_vstinfo['ps_file_filename_'+str(filenum)]):
                                        pluginfo_obj = manager_extplug.pluginfo()
                                        pluginfo_obj.id = uuid.UUID(dict_vstinfo['ps_file_guid_'+str(filenum)]).hex.upper()
                                        pluginfo_obj.name = dict_vstinfo['ps_file_name_'+str(filenum)]
                                        if 'ps_file_vendorname_'+str(filenum) in dict_vstinfo: pluginfo_obj.creator = dict_vstinfo['ps_file_vendorname_'+str(filenum)]
                                        if 'ps_file_category_'+str(filenum) in dict_vstinfo: pluginfo_obj.category = dict_vstinfo['ps_file_category_'+str(filenum)]
                                        if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '32': pluginfo_obj.path_32bit = dict_vstinfo['ps_file_filename_'+str(filenum)]
                                        if dict_vstinfo['ps_file_bitsize_'+str(filenum)] == '64': pluginfo_obj.path_64bit = dict_vstinfo['ps_file_filename_'+str(filenum)]
                                        manager_extplug.vst3_add(pluginfo_obj, 'win')
                                        vst3count += 1

        print('[fl_studio] VST2: '+str(vst2count)+', VST3: '+str(vst3count))
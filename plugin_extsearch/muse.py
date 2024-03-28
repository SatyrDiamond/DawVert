# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import plugin_extsearch
from os.path import exists
from pathlib import Path
import xml.etree.ElementTree as ET
from objects import manager_extplug

def muse_getvalue(fallback, xmldata, name):
        outval = xmldata.findall(name)
        if outval == []: return fallback
        else: return outval[0].text

class plugsearch(plugin_extsearch.base):
    def __init__(self): pass
    def getname(self): return 'MusE'
    def is_dawvert_plugin(self): return 'externalsearch'
    def issupported(self, platformtxt): return platformtxt == 'lin'
    def import_plugins(self, platformtxt, homepath):

        l_path_muse = os.path.join(homepath,".cache", "MusE", "MusE", "scanner")
        vst2count = 0
        ladspacount = 0

        muse_g_path_vst = l_path_muse+'/linux_vst_plugins.scan'
        muse_g_path_ladspa = l_path_muse+'/ladspa_plugins.scan'
        muse_g_path_dssi = l_path_muse+'/dssi_plugins.scan'

        if os.path.exists(muse_g_path_vst):
            path_vst_linux = muse_g_path_vst
            vstxmldata = ET.parse(path_vst_linux)
            vstxmlroot = vstxmldata.getroot()
            for x_vst_plug_cache in vstxmlroot:
                muse_file = x_vst_plug_cache.get('file')
                if os.path.exists(muse_file):
                    pluginfo_obj = manager_extplug.pluginfo()
                    pluginfo_obj.id = muse_getvalue(None, x_vst_plug_cache, 'uniqueID')
                    pluginfo_obj.name = muse_getvalue(None, x_vst_plug_cache, 'name')
                    pluginfo_obj.creator = muse_getvalue(None, x_vst_plug_cache, 'maker')
                    pluginfo_obj.audio_num_inputs = muse_getvalue(0, x_vst_plug_cache, 'inports')
                    pluginfo_obj.audio_num_outputs = muse_getvalue(0, x_vst_plug_cache, 'outports')
                    pluginfo_obj.num_params = muse_getvalue(0, x_vst_plug_cache, 'ctlInports')
                    manager_extplug.vst2_add(pluginfo_obj, platformtxt)
                    vst2count += 1

        if os.path.exists(muse_g_path_ladspa):
            path_ladspa_linux = muse_g_path_ladspa
            ladspaxmldata = ET.parse(path_ladspa_linux)
            ladspaxmlroot = ladspaxmldata.getroot()
            for x_ladspa_plug_cache in ladspaxmlroot:
                muse_file = x_ladspa_plug_cache.get('file')
                muse_label = x_ladspa_plug_cache.get('label')
                if os.path.exists(muse_file):
                    pluginfo_obj = manager_extplug.pluginfo()
                    pluginfo_obj.id = muse_getvalue(None, x_ladspa_plug_cache, 'uniqueID')
                    pluginfo_obj.name = muse_getvalue(None, x_ladspa_plug_cache, 'name')
                    pluginfo_obj.inside_id = muse_label
                    pluginfo_obj.creator = muse_getvalue(None, x_ladspa_plug_cache, 'maker')
                    pluginfo_obj.audio_num_inputs = muse_getvalue(0, x_ladspa_plug_cache, 'inports')
                    pluginfo_obj.audio_num_outputs = muse_getvalue(0, x_ladspa_plug_cache, 'outports')
                    pluginfo_obj.num_params = muse_getvalue(0, x_ladspa_plug_cache, 'ctlInports')
                    pluginfo_obj.num_params_out = muse_getvalue(0, x_ladspa_plug_cache, 'ctlOutports')
                    pluginfo_obj.path_unix = muse_file
                    manager_extplug.vst2_add(pluginfo_obj, platformtxt)
                    ladspacount += 1

        print('[muse] VST2: '+str(vst2count)+', LADSPA: '+str(ladspacount))

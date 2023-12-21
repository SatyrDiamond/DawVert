# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import note_data
from functions import placement_data
from functions import plugins
from functions import song
from functions import colors
from functions import data_dataset
from functions_tracks import tracks_r
import plugin_input
import io
import struct
import json

def getval(i_val):
    if i_val == 91: i_val = 11
    elif i_val == 11: i_val = 91
    elif i_val == -3: i_val = 92
    elif i_val == -2: i_val = 93
    return i_val

midi_inst = {
    'paint': [5,0,3,4,9,14,11,13,1,12]
}

class input_petaporon(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'petaporon'
    def getname(self): return 'Petaporon'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'track_nopl': True
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)
        cvpj_l = {}
        peta_notedata = sndstat_data['n'].encode('ascii')
        peta_noteints = struct.unpack("B"*len(peta_notedata), peta_notedata)
        peta_instset = sndstat_data['i']
        bio_peta_notebytes = data_bytes.to_bytesio(bytes(peta_noteints))

        cvpj_notelists = {}

        dataset = data_dataset.dataset('./data_dset/petaporon.dset')
        colordata = colors.colorset(dataset.colorset_e_list('inst', 'main'))

        for instnum in range(10):
            cvpj_notelists[instnum] = []
            pluginid = plugins.get_id()
            instid = 'petaporon'+str(instnum)

            tracks_r.track_create(cvpj_l, instid, 'instrument')
            tracks_r.track_visual(cvpj_l, instid, name='Inst #'+str(instnum+1), color=colordata.getcolornum(instnum))
            tracks_r.track_inst_pluginid(cvpj_l, instid, pluginid)

            inst_plugindata = plugins.cvpj_plugin('deftype', 'universal', 'synth-osc')
            inst_plugindata.osc_num_oscs(1)
            if instnum in [0,1,2,3,4,7]: inst_plugindata.osc_opparam_set(0, 'shape', 'square')
            if instnum in [5,6]: inst_plugindata.osc_opparam_set(0, 'shape', 'triangle')
            if instnum in [8]: inst_plugindata.osc_opparam_set(0, 'shape', 'noise')
            if instnum in [0,1]: inst_plugindata.osc_opparam_set(0, 'pulse_width', 1/8)
            if instnum in [2,7]: inst_plugindata.osc_opparam_set(0, 'pulse_width', 1/4)
            if instnum in [3,4,5,6]: inst_plugindata.osc_opparam_set(0, 'pulse_width', 1/2)

            if instnum == 0: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.1, 0, 0, 1)
            if instnum == 1: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.1, 0.7, 0, 1)
            if instnum == 2: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.25, 0, 0, 1)
            if instnum == 3: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.2, 0, 0, 1)
            if instnum == 4: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0, 1, 0, 1)
            if instnum == 5: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0, 1, 0, 1)
            if instnum == 6: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.2, 0, 0, 1)
            if instnum == 7: inst_plugindata.asdr_env_add('vol', 0, 0.3, 0, 0.3, 0.2, 0.3, 1)
            if instnum == 8: inst_plugindata.asdr_env_add('vol', 0, 0, 0, 0.4, 0, 0, 1)
            inst_plugindata.to_cvpj(cvpj_l, pluginid)

        for _ in range(len(peta_noteints)//5):
            partdata = bio_peta_notebytes.read(5)
            peta_note = getval(partdata[0]-35)
            peta_inst = getval(partdata[1]-35)
            peta_len = getval(partdata[2]-35)
            peta_poshigh = getval(partdata[3]-35)
            peta_poslow = getval(partdata[4]-35)
            peta_pos = peta_poslow+(peta_poshigh*94)
            cvpj_notelists[peta_inst].append(note_data.rx_makenote(peta_pos, peta_len, peta_note-12, None, None))

        for instnum in range(10):
            tracks_r.add_pl(cvpj_l, 'petaporon'+str(instnum), 'notes', placement_data.nl2pl(cvpj_notelists[instnum]))

        cvpj_l['do_singlenotelistcut'] = True

        song.add_timesig(cvpj_l, sndstat_data['c'], 4)
        song.add_param(cvpj_l, 'bpm', sndstat_data['t'])

        return json.dumps(cvpj_l)

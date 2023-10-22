# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from functions import xtramath

import json

def rx_track_iter(cvpj_track_placements, cvpj_track_order, cvpj_track_data):
    for trackid in cvpj_track_order:
        track_placements_pre = cvpj_track_placements[trackid] if trackid in cvpj_track_placements else {}
        track_placements_notes = track_placements_pre['notes'] if 'notes' in track_placements_pre else []
        track_placements_audio = track_placements_pre['audio'] if 'audio' in track_placements_pre else []
        track_data = cvpj_track_data[trackid] if trackid in cvpj_track_data else {}
        yield trackid, track_data, track_placements_notes, track_placements_audio

def convert(song):
    print('[song-convert] Converting from RegularMultiple > Regular')
    cvpj_proj = json.loads(song)
    if 'track_order' not in cvpj_proj:
        print('[error] track_order not found')

    cvpj_instruments_data = cvpj_proj['instruments_data'] if 'instruments_data' in cvpj_proj else {}
    cvpj_track_order = cvpj_proj['track_order'] if 'track_order' in cvpj_proj else []
    cvpj_track_data = cvpj_proj['track_data'] if 'track_data' in cvpj_proj else {}
    cvpj_plugins = {}
    if 'plugins' in cvpj_proj:
        cvpj_plugins = cvpj_proj['plugins']
        del cvpj_proj['plugins']
    if 'instruments_data' in cvpj_proj: del cvpj_proj['instruments_data']
    if 'track_order' in cvpj_proj: del cvpj_proj['track_order']
    if 'track_data' in cvpj_proj: del cvpj_proj['track_data']

    if 'track_placements' in cvpj_proj: 
        cvpj_track_placements = cvpj_proj['track_placements']
        del cvpj_proj['track_placements']
    else: cvpj_track_placements = {}

    cvpj_proj['track_placements'] = {}
    cvpj_proj['track_order'] = []
    cvpj_proj['track_data'] = {}
    cvpj_proj['plugins'] = {}

    usedinst = {}

    for trackid, track_data, track_placements_notes, track_placements_audio in rx_track_iter(cvpj_track_placements, cvpj_track_order, cvpj_track_data):

        if track_data['type'] == 'instruments':
            track_data['type'] = 'instrument'

            used_insts = []
            for c_track_placement in track_placements_notes:
                c_track_placement_base = c_track_placement.copy()
                del c_track_placement_base['notelist']
                m_notelist = {}
                if 'notelist' in c_track_placement:
                    for cvpj_note in c_track_placement['notelist']:
                        noteinst = cvpj_note['instrument']
                        if noteinst not in m_notelist: m_notelist[noteinst] = []
                        cvpj_note['instrument'] += '_'+trackid
                        m_notelist[noteinst].append(cvpj_note)
                        if noteinst not in used_insts: used_insts.append(noteinst)

                for m_inst in m_notelist:
                    r_trackid = m_inst+'_'+trackid
                    c_track_placement_single = c_track_placement_base.copy()
                    c_track_placement_single['notelist'] = m_notelist[m_inst]
                    data_values.nested_dict_add_to_list(
                        cvpj_proj, 
                        ['track_placements', r_trackid, 'notes'], 
                        c_track_placement_single)

            for used_inst in used_insts:
                cvpj_instrument = cvpj_instruments_data[used_inst].copy() if used_inst in cvpj_instruments_data else {}
                pluginid = data_values.nested_dict_get_value(cvpj_instrument, ['instdata', 'pluginid'])
                if pluginid != None and pluginid not in cvpj_proj['plugins']:
                    cvpj_proj['plugins'][pluginid] = cvpj_plugins[pluginid]

                #cvpj_plugins
                temp_track_data = track_data.copy()

                if 'name' in cvpj_instrument: 
                    instname = cvpj_instrument['name']
                    del cvpj_instrument['name']
                else: instname = used_inst

                instcolor = None
                if 'color' in cvpj_instrument: 
                    instcolor = cvpj_instrument['color']
                    del cvpj_instrument['color']

                trackcolor = None
                if 'color' in temp_track_data: 
                    trackcolor = temp_track_data['color']
                    del temp_track_data['color']

                if 'name' in temp_track_data: temp_track_data['name'] = instname+' ('+temp_track_data['name']+')' if temp_track_data['name'] != '' else instname
                else: temp_track_data['name'] = instname

                temp_track_data |= cvpj_instrument

                if trackcolor != None: temp_track_data['color'] = trackcolor
                elif instcolor != None: temp_track_data['color'] = instcolor

                r_trackid = used_inst+'_'+trackid
                cvpj_proj['track_order'].append(r_trackid)
                cvpj_proj['track_data'][r_trackid] = temp_track_data

        if track_data['type'] == 'audio':
            cvpj_proj['track_order'].append(trackid)
            cvpj_proj['track_data'][trackid] = track_data
            data_values.nested_dict_add_to_list(
                cvpj_proj, 
                ['track_placements', trackid, 'audio'], 
                track_placements_audio)

    if 'fxrack' in cvpj_proj:
        for fxnum in cvpj_proj['fxrack']:
            fxdata = cvpj_proj['fxrack'][fxnum]
            if 'chain_fx_audio' in fxdata:
                for plugid in fxdata['chain_fx_audio']:
                    cvpj_proj['plugins'][plugid] = cvpj_plugins[plugid]
        

    return json.dumps(cvpj_proj)

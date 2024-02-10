# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later  

import plugin_output
import json
import math
import base64
import struct
from bs4 import BeautifulSoup
from functions_plugin import format_flp_enc
from functions_plugin import flp_enc_plugins
from functions import data_values
from functions import xtramath

from objects import dv_datadef
from objects import dv_dataset

filename_len = {}

def decode_color(color):
    return int.from_bytes(bytes([int(color[0]*255), int(color[1]*255), int(color[2]*255)]), "little")

class output_cvpjs(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'flp'
    def getname(self): return 'FL Studio'
    def gettype(self): return 'mi'
    def plugin_archs(self): return ['amd64', 'i386']
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'fxrack_params': ['enabled','vol','pan'],
        'track_lanes': True,
        'placement_cut': True,
        'placement_audio_stretch': ['rate', 'rate_ignoretempo'],
        'track_hybrid': True
        }
    def getsupportedplugformats(self): return ['vst2', 'vst3']
    def getsupportedplugins(self): return ['sampler:single', 'soundfont2']
    def getfileextension(self): return 'flp'
    def parse(self, convproj_obj, output_file):

        ppq = 960
        convproj_obj.change_timings(ppq, False)

        datadef = dv_datadef.datadef('./data_ddef/fl_studio.ddef')
        dataset = dv_dataset.dataset('./data_dset/fl_studio.dset')

        FLP_Data = {}
        FL_Main = FLP_Data['FL_Main'] = {}
        FL_Channels = FLP_Data['FL_Channels'] = {}
        FL_Patterns = FLP_Data['FL_Patterns'] = {}
        FL_Arrangements = FLP_Data['FL_Arrangements'] = {}
        FL_TimeMarkers = FLP_Data['FL_TimeMarkers'] = {}
        FL_Tracks = FLP_Data['FL_Tracks'] = {}
        FL_Mixer = FLP_Data['FL_Mixer'] = {}

        FL_Main['ppq'] = ppq
        
        FL_Main['ShowInfo'] = 0

        samplestretch = {}

        FL_Main['ShowInfo'] = 1
        FL_Main['Title'] = convproj_obj.metadata.name
        FL_Main['Author'] = convproj_obj.metadata.author
        FL_Main['URL'] = convproj_obj.metadata.genre
        FL_Main['Genre'] = convproj_obj.metadata.url
        if convproj_obj.metadata.comment_datatype == 'html':
            bst = BeautifulSoup(convproj_obj.metadata.comment_text, "html.parser")
            FL_Main['Comment'] = bst.get_text()
        if convproj_obj.metadata.comment_datatype == 'text': FL_Main['Comment'] = convproj_obj.metadata.comment_text
        FL_Main['Comment'] = convproj_obj.metadata.comment_text.replace("\r\n", "\r").replace("\n", "\r")

        FL_Main['ProjectDataPath'] = ''

        bpm = convproj_obj.params.get('bpm',120).value

        FL_Main['Numerator'], FL_Main['Denominator'] = convproj_obj.timesig
        FL_Main['Tempo'] = bpm
        FL_Main['MainPitch'] = struct.unpack('H', struct.pack('h', int(convproj_obj.params.get('pitch',0).value)))[0]
        FL_Main['Shuffle'] = convproj_obj.params.get('shuffle',0).value

        samples_id = {}
        g_inst_id = {}
        g_inst_id_count = 0

        for instentry in convproj_obj.instruments_order:
            g_inst_id[instentry] = str(g_inst_id_count)
            g_inst_id_count += 1

        for sampleentry in convproj_obj.sample_index:
            g_inst_id[sampleentry] = str(g_inst_id_count)
            samples_id[sampleentry] = str(g_inst_id_count)
            g_inst_id_count += 1

        for inst_id, inst_obj in convproj_obj.iter_instrument():
            T_Main = {}
            T_Main['volume'] = inst_obj.params.get('vol',1).value
            T_Main['pan'] = inst_obj.params.get('pan',0).value
            T_Main['enabled'] = int(inst_obj.params.get('enabled',True).value)
            T_Main['pitch'] = inst_obj.params.get('pitch',0).value
            T_Main['main_pitch'] = int(inst_obj.params.get('usemasterpitch',True).value)
            T_Main['middlenote'] = inst_obj.datavals.get('middlenote', 0)+60
            if inst_obj.visual.name: T_Main['name'] = inst_obj.visual.name
            T_Main['fxchannel'] = max(inst_obj.fxrack_channel, 0)

            T_Main['type'] = 0
            T_Main['plugin'] = ''

            plugin_found, plugin_obj = convproj_obj.get_plugin(inst_obj.pluginid)
            if plugin_found:
                if plugin_obj.check_match('sampler', 'single'):
                    T_Main['type'] = 0
                    T_Main['plugin'] = ''
                    ref_found, sampleref_obj = plugin_obj.sampleref_fileref('sample', convproj_obj)
                    if ref_found: T_Main['samplefilename'] = sampleref_obj.fileref.get_path('win', True)

                fl_plugin, fl_pluginparams = flp_enc_plugins.setparams(convproj_obj, plugin_obj, datadef, dataset)
                if fl_plugin != None:
                    plug_opened = False
                    pos_x, pos_y = [0,0]
                    size_x, size_y = [0,0]

                    windowdata_obj = convproj_obj.window_data_get(['plugin', inst_obj.pluginid])

                    if windowdata_obj.pos_x != -1: pos_x = windowdata_obj.pos_x
                    if windowdata_obj.pos_y != -1: pos_y = windowdata_obj.pos_y
                    if windowdata_obj.size_x != -1: size_x = windowdata_obj.size_x
                    if windowdata_obj.size_y != -1: size_y = windowdata_obj.size_y
                    if windowdata_obj.open != -1: plug_opened = windowdata_obj.open

                    fl_plugindata = b'\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00'
                    fl_plugindata += b'Q' if plug_opened else b'P'
                    fl_plugindata += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

                    fl_plugindata += struct.pack('iiii', pos_x, pos_y, size_x, size_y)

                    T_Main['plugindata'] = fl_plugindata
                    T_Main['type'] = 2
                    T_Main['plugin'] = fl_plugin
                    T_Main['pluginparams'] = fl_pluginparams

            T_Main['polymax'] = inst_obj.datavals.get('poly_max', 0)
            if inst_obj.visual.color: T_Main['color'] = decode_color(inst_obj.visual.color)

            FL_Channels[g_inst_id[inst_id]] = T_Main

        for samp_id, sre_obj in convproj_obj.iter_sampleindex():
            T_Main = {}
            T_Main['type'] = 4

            ref_found, sampleref_obj = convproj_obj.get_sampleref(sre_obj.sampleref)
            samplefilename = sampleref_obj.fileref.get_path('win', True) if ref_found else ""

            T_Main['volume'] = sre_obj.vol
            T_Main['pan'] = sre_obj.pan
            T_Main['enabled'] = sre_obj.enabled
            T_Main['fxchannel'] = max(sre_obj.fxrack_channel, 0)
            T_Main['samplefilename'] = samplefilename

            if sre_obj.visual.name: T_Main['name'] = sre_obj.visual.name
            if sre_obj.visual.color: T_Main['color'] = decode_color(sre_obj.visual.color)

            samplestretch[samp_id] = ['normal', 1]
            audiorate = 1

            if sre_obj.stretch.algorithm == 'resample': T_Main['stretchingmode'] = 0
            elif sre_obj.stretch.algorithm == 'elastique_v3': T_Main['stretchingmode'] = 1
            elif sre_obj.stretch.algorithm == 'elastique_v3_mono': T_Main['stretchingmode'] = 2
            elif sre_obj.stretch.algorithm == 'slice_stretch': T_Main['stretchingmode'] = 3
            elif sre_obj.stretch.algorithm == 'auto': T_Main['stretchingmode'] = 4
            elif sre_obj.stretch.algorithm == 'slice_map': T_Main['stretchingmode'] = 5
            elif sre_obj.stretch.algorithm == 'elastique_v2': T_Main['stretchingmode'] = 6
            elif sre_obj.stretch.algorithm == 'elastique_v2_transient': T_Main['stretchingmode'] = 7
            elif sre_obj.stretch.algorithm == 'elastique_v2_mono': T_Main['stretchingmode'] = 8
            elif sre_obj.stretch.algorithm == 'elastique_v2_speech': T_Main['stretchingmode'] = 9
            else: T_Main['stretchingmode'] = -1

            T_Main['stretchingpitch'] = int(sre_obj.pitch*100)

            out_is_speed, out_rate = sre_obj.stretch.get(bpm, True)

            if out_is_speed: T_Main['stretchingmultiplier'] = int(  math.log2(1/sre_obj.stretch.rate)*10000  )
            else: T_Main['stretchingtime'] = int(  (sampleref_obj.dur_sec*384)/sre_obj.stretch.rate     )

            samplestretch[samp_id] = sre_obj.stretch

            FL_Channels[g_inst_id[samp_id]] = T_Main

        pat_id = {}
        pat_id_count = 1
        for nle_id, nle_obj in convproj_obj.iter_notelistindex():
            pat_id[nle_id] = pat_id_count
            pat_id_count += 1

        for pat_entry in pat_id:
            FL_Patterns[str(pat_id[pat_entry])] = {}
            FL_Pattern = FL_Patterns[str(pat_id[pat_entry])]

            nle_obj = convproj_obj.notelist_index[pat_entry]

            if nle_obj.visual.name: FL_Pattern['name'] = nle_obj.visual.name
            if nle_obj.visual.color: FL_Pattern['color'] = decode_color(nle_obj.visual.color)

            FL_Pattern['notes'] = []
            nle_obj.notelist.sort()
            for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in nle_obj.notelist.iter():
                for t_key in t_keys:
                    FL_Note = {}
                    FL_Note['rack'] = int(g_inst_id[t_inst])
                    M_FL_Note_Key = int(t_key)+60
                    M_FL_Note_Pos = int(t_pos)
                    M_FL_Note_Dur = int(t_dur)
                    if 'finepitch' in t_extra: FL_Note['finep'] = int((t_extra['finepitch']/10)+120)
                    if 'release' in t_extra: FL_Note['rel'] = int(xtramath.clamp(t_extra['release'],0,1)*128)
                    if 'cutoff' in t_extra: FL_Note['mod_x'] = int(xtramath.clamp(t_extra['cutoff'],0,1)*255)
                    if 'reso' in t_extra: FL_Note['mod_y'] = int(xtramath.clamp(t_extra['reso'],0,1)*255)
                    if 'pan' in t_extra: FL_Note['pan'] = int((xtramath.clamp(float(t_extra['pan']),-1,1)*64)+64)
                    FL_Note['velocity'] = int(xtramath.clamp(t_vol,0,1)*100)
                    FL_Note['pos'] = M_FL_Note_Pos
                    FL_Note['dur'] = M_FL_Note_Dur
                    FL_Note['key'] = M_FL_Note_Key
                    FL_Pattern['notes'].append(FL_Note)

                    if t_slide:
                        for s_pos, s_dur, s_key, s_vol, s_extra in t_slide:
                            FL_Note = {}
                            FL_Note['rack'] = int(g_inst_id[t_inst])
                            FL_Note['key'] = int(s_key + t_key)+60
                            FL_Note['pos'] = M_FL_Note_Pos + int(s_pos)
                            FL_Note['dur'] = int(s_dur)
                            FL_Note['flags'] = 16392
                            if 'finepitch' in s_extra: FL_Note['finep'] = int((s_extra['finepitch']/10)+120)
                            if 'release' in s_extra: FL_Note['rel'] = int(xtramath.clamp(s_extra['release'],0,1)*128)
                            if s_vol: FL_Note['velocity'] = int(xtramath.clamp(s_vol,0,1)*100)
                            elif 'vol' in note: FL_Note['velocity'] = int(xtramath.clamp(t_vol,0,1)*100)
                            if 'cutoff' in s_extra: FL_Note['mod_x'] = int(xtramath.clamp(s_extra['cutoff'],0,1)*255)
                            if 'reso' in s_extra: FL_Note['mod_y'] = int(xtramath.clamp(s_extra['reso'],0,1)*255)
                            if 'pan' in s_extra: FL_Note['pan'] = int((xtramath.clamp(float(s_extra['pan']),-1,1)*64)+64)
                            FL_Pattern['notes'].append(FL_Note)
                            
        if len(FL_Patterns) > 999:
            print('[error] FLP patterns over 999 is unsupported.')
            exit()

        if len(FL_Channels) > 256:
            print('[error] FLP channels over 256 is unsupported.')
            exit()

        FL_Playlist_BeforeSort = {}
        FL_Playlist_Sorted = {}
        FL_Playlist = []

        for idnum, playlist_obj in convproj_obj.iter_playlist():

            idnum = int(idnum)+1

            for pl_obj in playlist_obj.placements.iter_notes():
                if pl_obj.fromindex in pat_id:
                    FL_playlistitem = {}
                    FL_playlistitem['position'] = int(pl_obj.position)
                    FL_playlistitem['patternbase'] = 20480
                    FL_playlistitem['itemindex'] = int(pat_id[pl_obj.fromindex] + FL_playlistitem['patternbase'])
                    FL_playlistitem['length'] = int(pl_obj.duration)
                    FL_playlistitem['startoffset'] = 0
                    FL_playlistitem['endoffset'] = int(pl_obj.duration)
                    FL_playlistitem['unknown1'] = 120
                    FL_playlistitem['unknown2'] = 25664
                    FL_playlistitem['unknown3'] = 32896
                    FL_playlistitem['flags'] = 64
                    FL_playlistitem['trackindex'] = (-500 + int(idnum))*-1
                    if pl_obj.muted == True: FL_playlistitem['flags'] = 12352
                    if pl_obj.cut_type == 'cut':
                        if 'start' in pl_obj.cut_data: 
                            FL_playlistitem['startoffset'] = int(pl_obj.cut_data['start'])
                            FL_playlistitem['endoffset'] += int(pl_obj.cut_data['start'])
                    if FL_playlistitem['position'] not in FL_Playlist_BeforeSort: FL_Playlist_BeforeSort[FL_playlistitem['position']] = []
                    FL_Playlist_BeforeSort[FL_playlistitem['position']].append(FL_playlistitem)


            for pl_obj in playlist_obj.placements.iter_audio():
                if pl_obj.fromindex in samples_id:
                    FL_playlistitem = {}
                    FL_playlistitem['position'] = int(pl_obj.position)
                    FL_playlistitem['patternbase'] = 20480
                    FL_playlistitem['itemindex'] = samples_id[pl_obj.fromindex]
                    FL_playlistitem['length'] = max(0, int(pl_obj.duration))
                    FL_playlistitem['startoffset'] = 0
                    FL_playlistitem['endoffset'] = int(pl_obj.duration)/ppq
                    FL_playlistitem['unknown1'] = 120
                    FL_playlistitem['unknown2'] = 25664
                    FL_playlistitem['unknown3'] = 32896
                    FL_playlistitem['flags'] = 64
                    FL_playlistitem['trackindex'] = (-500 + int(idnum))*-1
                    if pl_obj.muted == True: FL_playlistitem['flags'] = 12352

                    #if pl_obj.fromindex in samplestretch:

                    startat = 0
                    if pl_obj.cut_type == 'cut': startat = pl_obj.cut_data['start']

                    if pl_obj.fromindex in samplestretch:
                        startat = startat/ppq
                        endat = startat+(pl_obj.duration/ppq)

                        stretch_obj = samplestretch[pl_obj.fromindex]
                        out_is_speed, out_rate = stretch_obj.get(bpm, True)
                        #print(out_is_speed, out_rate, end=' | ')
                        #print(pl_obj.duration/ppq, end=' | ')
                        #print(startat*out_rate, end=' -S- ')
                        #print(startat, end=' | ')
                        #print(endat*out_rate, end=' -E- ')
                        #print(endat, end=' | ')
                        #print(placement_obj.duration/ppq, end=' | ')
                        #print()
                        FL_playlistitem['startoffset'] = (startat*out_rate)*4
                        FL_playlistitem['endoffset'] = (endat*out_rate)*4

                    #print(FL_playlistitem['startoffset'])
                    #print(FL_playlistitem['endoffset'])

                    #    if pl_stretch[0] == 'rate_tempo':
                    #        if 'start' in pl_obj.cut_data: 
                    #            FL_playlistitem['startoffset'] = pl_obj.cut_data['start']*pl_stretch[1]
                    #            FL_playlistitem['endoffset'] = pl_obj.duration*pl_stretch[1] + FL_playlistitem['startoffset']
                    #    elif pl_stretch[0] == 'rate_ignoretempo':
                    #        if 'start' in pl_obj.cut_data: 
                    #            FL_playlistitem['startoffset'] = pl_obj.cut_data['start']
                    #            FL_playlistitem['endoffset'] = pl_obj.duration + FL_playlistitem['startoffset']
                    #    elif pl_stretch[0] == 'rate_speed':
                    #        if 'start' in pl_obj.cut_data: 
                    #            FL_playlistitem['startoffset'] = (pl_obj.cut_data['start'])*pl_stretch[1]
                    #            FL_playlistitem['endoffset'] = (pl_obj.duration)*pl_stretch[1] + FL_playlistitem['startoffset']

                    #FL_playlistitem['startoffset'] /= (ppq/4)
                    #FL_playlistitem['endoffset'] /= (ppq/4)

                    if FL_playlistitem['position'] not in FL_Playlist_BeforeSort: FL_Playlist_BeforeSort[FL_playlistitem['position']] = []
                    FL_Playlist_BeforeSort[FL_playlistitem['position']].append(FL_playlistitem)


            if str(idnum) not in FL_Tracks: FL_Tracks[str(idnum)] = {}
            if playlist_obj.visual.name: FL_Tracks[str(idnum)]['name'] = playlist_obj.visual.name
            if playlist_obj.visual.color: FL_Tracks[str(idnum)]['color'] = decode_color(playlist_obj.visual.color)
            FL_Tracks[str(idnum)]['height'] = playlist_obj.visual_ui.height
            FL_Tracks[str(idnum)]['enabled'] = int(playlist_obj.params.get('enabled',True).value)
        FL_Playlist_Sorted = dict(sorted(FL_Playlist_BeforeSort.items(), key=lambda item: item[0]))

        for itemposition in FL_Playlist_Sorted:
            playlistposvalues = FL_Playlist_Sorted[itemposition]
            for itemrow in playlistposvalues: FL_Playlist.append(itemrow)

        markernum = 0

        if convproj_obj.loop_active:
            markernum += 1
            FL_TimeMarker = {}
            FL_TimeMarkers[str(markernum)] = {'name': "", 'type':2, 'pos':convproj_obj.loop_start}

        for pos, value in convproj_obj.timesig_auto.iter():
            markernum += 1
            FL_TimeMarker = {}
            FL_TimeMarker['pos'] = pos
            FL_TimeMarker['type'] = 8
            FL_TimeMarker['numerator'] = value[0]
            FL_TimeMarker['denominator'] = value[1]
            FL_TimeMarkers[str(markernum)] = FL_TimeMarker

        for timemarker_obj in convproj_obj.timemarkers:
            markernum += 1
            FL_TimeMarker = {}
            FL_TimeMarker['pos'] = timemarker_obj.position
            FL_TimeMarker['type'] = 0
            FL_TimeMarker['name'] = timemarker_obj.visual.name if timemarker_obj.visual.name else ""
            if timemarker_obj.type == 'start': FL_TimeMarker['type'] = 5
            elif timemarker_obj.type == 'loop': FL_TimeMarker['type'] = 4
            elif timemarker_obj.type == 'markerloop': FL_TimeMarker['type'] = 1
            elif timemarker_obj.type == 'markerskip': FL_TimeMarker['type'] = 2
            elif timemarker_obj.type == 'pause': FL_TimeMarker['type'] = 3
            elif timemarker_obj.type == 'punchin': FL_TimeMarker['type'] = 9
            elif timemarker_obj.type == 'punchout': FL_TimeMarker['type'] = 10
            FL_TimeMarkers[str(markernum)] = FL_TimeMarker


        for fx_num, fxchannel_obj in convproj_obj.fxrack.items():
            fx_num = str(fx_num)
            FL_Mixer[fx_num] = {}
            FL_Mixer[fx_num]['slots'] = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}

            if fxchannel_obj.visual.name: FL_Mixer[fx_num]['name'] = fxchannel_obj.visual.name
            if fxchannel_obj.visual.color: FL_Mixer[fx_num]['color'] = decode_color(fxchannel_obj.visual.color)
 
            slotnum = 0
            for pluginid in fxchannel_obj.fxslots_audio:
                plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
                if plugin_found: 
                    fl_plugin, fl_pluginparams = flp_enc_plugins.setparams(convproj_obj, plugin_obj, datadef, dataset)
                    if fl_plugin != None:
                        FL_Mixer[fx_num]['slots'][slotnum] = {}
                        slotdata = FL_Mixer[fx_num]['slots'][slotnum]
                        slotdata['plugin'] = fl_plugin
                        slotdata['pluginparams'] = fl_pluginparams
                        if plugin_obj.visual.name: slotdata['name'] = plugin_obj.visual.name
                        if plugin_obj.visual.color: slotdata['color'] = decode_color(plugin_obj.visual.color)
                        slotnum += 1
                        if slotnum == 10: break

        FL_Arrangements['0'] = {}
        FL_Arrangements['0']['items'] = FL_Playlist
        FL_Arrangements['0']['name'] = 'Arrangement'
        FL_Arrangements['0']['tracks'] = FL_Tracks
        FL_Arrangements['0']['timemarkers'] = FL_TimeMarkers

            

        format_flp_enc.make(FLP_Data, output_file)
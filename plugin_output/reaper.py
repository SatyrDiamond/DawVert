# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import uuid
import rpp
from rpp import Element
from functions import colors
from functions import notelist_data
from functions import xtramath

def rpp_obj(i_name, i_vals): return Element(tag=i_name, attrib=i_vals, children=[])
def rpp_obj_data(i_name, i_vals, i_data): return Element(tag=i_name, attrib=i_vals, children=i_data)

def cvpj_color_to_reaper_color(i_color): 
    cvpj_trackcolor = bytes(colors.rgb_float_2_rgb_int(i_color))+b'\x01'
    return int.from_bytes(cvpj_trackcolor, 'little')

def cvpj_color_to_reaper_color_clip(i_color): 
    cvpj_trackcolor = bytes(colors.rgb_float_2_rgb_int([i_color[2],i_color[1],i_color[0]]))+b'\x01'
    return int.from_bytes(cvpj_trackcolor, 'little')

def calc_pos(i_value, i_bpm):
    return (i_value/8)*(120/i_bpm)

def midi_add_cmd(i_list, i_pos, i_cmd):
    if i_pos not in i_list: i_list[i_pos] = []
    i_list[i_pos].append(i_cmd)

def convert_midi(notelist, tempo, num, dem, enddur):
    clip_GUID = '{'+str(uuid.uuid4())+'}'
    clip_POOLEDEVTS = '{'+str(uuid.uuid4())+'}'

    midiclipdata = rpp_obj('SOURCE', ['MIDI'])
    midiclipdata.children.append(['HASDATA',1,960,'QN'])
    midiclipdata.children.append(['CCINTERP',32])
    midiclipdata.children.append(['POOLEDEVTS',clip_POOLEDEVTS])

    i_list = {}
    notelist = notelist_data.sort(notelist)

    midi_add_cmd(i_list, (enddur*4)*60, ['end'])

    for cvpj_tr_pl_n in notelist:
        cvmi_n_pos = int(cvpj_tr_pl_n['position']*4)*60
        cvmi_n_dur = int(cvpj_tr_pl_n['duration']*4)*60
        cvmi_n_key = int(cvpj_tr_pl_n['key'])+60
        cvmi_n_vol = 127
        if 'vol' in cvpj_tr_pl_n: cvmi_n_vol = xtramath.clamp(int(cvpj_tr_pl_n['vol']*127), 0, 127)
        midi_add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
        midi_add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

    i_list = dict(sorted(i_list.items(), key=lambda item: item[0]))

    prevpos = 0
    for i_list_e in i_list:
        for midi_notedata in i_list[i_list_e]:
            if midi_notedata[0] == 'note_on': midiclipdata.children.append(['E',i_list_e-prevpos, 90, hex(midi_notedata[1])[2:], hex(midi_notedata[2])[2:]])
            if midi_notedata[0] == 'note_off': midiclipdata.children.append(['E',i_list_e-prevpos, 80, hex(midi_notedata[1])[2:], '00'])
            if midi_notedata[0] == 'end': midiclipdata.children.append(['E',i_list_e-prevpos, 'b0', '7b', '00'])
            prevpos = i_list_e

    midiclipdata.children.append(['CCINTERP',32])
    midiclipdata.children.append(['CHASE_CC_TAKEOFFS',1])
    midiclipdata.children.append(['GUID',clip_GUID])
    midiclipdata.children.append(['IGNTEMPO',0,tempo,num,dem])
    midiclipdata.children.append(['SRCCOLOR',0])
    midiclipdata.children.append(['VELLANE',-1,100,0])
    midiclipdata.children.append(['KEYSNAP',0])
    midiclipdata.children.append(['TRACKSEL',0])
    return midiclipdata

class output_reaper(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'reaper'
    def getshortname(self): return 'reaper'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_loop': False,
        'no_placements': False,
        'pl_audio_events': False
        }
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)

        reaper_tempo = 140
        reaper_numerator = 4
        reaper_denominator = 4

        if 'timesig_numerator' in projJ: reaper_numerator = int(projJ['timesig_numerator'])
        if 'timesig_denominator' in projJ: reaper_denominator = int(projJ['timesig_denominator'])
        if 'bpm' in projJ: reaper_tempo = projJ['bpm']

        rppdata = rpp_obj('REAPER_PROJECT', [0.1, 6.78, 1681239515])
        rppdata.children.append(['RIPPLE','0'])
        rppdata.children.append(['GROUPOVERRIDE','0','0','0'])
        rppdata.children.append(['AUTOXFADE','129'])
        rppdata.children.append(['ENVATTACH','3'])
        rppdata.children.append(['POOLEDENVATTACH','0'])
        rppdata.children.append(['MIXERUIFLAGS','11','48'])
        rppdata.children.append(['PEAKGAIN','1'])
        rppdata.children.append(['FEEDBACK','0'])
        rppdata.children.append(['PANLAW','1'])
        rppdata.children.append(['PROJOFFS','0','0','0'])
        rppdata.children.append(['MAXPROJLEN','0','600'])
        rppdata.children.append(['GRID','3199','8','1','8','1','0','0','0'])
        rppdata.children.append(['TIMEMODE','1','5','-1','30','0','0','-1'])
        rppdata.children.append(['VIDEO_CONFIG','0','0','256'])
        rppdata.children.append(['PANMODE','3'])
        rppdata.children.append(['CURSOR','0'])
        rppdata.children.append(['ZOOM','100','0','0'])
        rppdata.children.append(['VZOOMEX','6','0'])
        rppdata.children.append(['USE_REC_CFG','0'])
        rppdata.children.append(['RECMODE','1'])
        rppdata.children.append(['SMPTESYNC','0','30','100','40','1000','300','0','0','1','0','0'])
        rppdata.children.append(['LOOP','0'])
        rppdata.children.append(['LOOPGRAN','0','4'])
        rppdata.children.append(['RECORD_PATH'," "" "," "" "])
        rppdata.children.append(rpp_obj_data('RECORD_CFG', [], ['ZXZhdxgAAA=']))
        rppdata.children.append(rpp_obj_data('APPLYFX_CFG', [], []))
        rppdata.children.append(['RENDER_FILE'," "" "])
        rppdata.children.append(['RENDER_PATTERN'," "" "])
        rppdata.children.append(['RENDER_FMT','0','2','0'])
        rppdata.children.append(['RENDER_1X','0'])
        rppdata.children.append(['RENDER_RANGE','1','0','0','18','1000'])
        rppdata.children.append(['RENDER_RESAMPLE','3','0','1'])
        rppdata.children.append(['RENDER_ADDTOPROJ','0'])
        rppdata.children.append(['RENDER_STEMS','0'])
        rppdata.children.append(['RENDER_DITHER','0'])
        rppdata.children.append(['TIMELOCKMODE','1'])
        rppdata.children.append(['TEMPOENVLOCKMODE','1'])
        rppdata.children.append(['ITEMMIX','1'])
        rppdata.children.append(['DEFPITCHMODE','589824','0'])
        rppdata.children.append(['TAKELANE','1'])
        rppdata.children.append(['SAMPLERATE','44100','0','0'])
        rppdata.children.append(rpp_obj_data('RENDER_CFG', [], ['ZXZhdxgAAA=']))
        rppdata.children.append(['LOCK','1'])
        metronomedata = rpp_obj('METRONOME', [6, 2])
        metronomedata.children.append(['VOL','0.25','0.125'])
        metronomedata.children.append(['FREQ','800','1600','1'])
        metronomedata.children.append(['BEATLEN','4'])
        metronomedata.children.append(['SAMPLES'," "" "," "" "])
        metronomedata.children.append(['PATTERN','2863311530','2863311529'])
        metronomedata.children.append(['MULT','1'])
        rppdata.children.append(rpp_obj_data('METRONOME', [6, 2], metronomedata))
        rppdata.children.append(['GLOBAL_AUTO','-1'])
        rppdata.children.append(['TEMPO',reaper_tempo,'4','4'])
        rppdata.children.append(['PLAYRATE','1','0','0.25','4'])
        rppdata.children.append(['SELECTION','1.5','1.5'])
        rppdata.children.append(['SELECTION2','1.5','1.5'])
        rppdata.children.append(['MASTERAUTOMODE','0'])
        rppdata.children.append(['MASTERTRACKHEIGHT','0','0'])
        rppdata.children.append(['MASTERPEAKCOL','16576'])
        rppdata.children.append(['MASTERMUTESOLO','0'])
        rppdata.children.append(['MASTERTRACKVIEW','0','0.6667','0.5','0.5','-1','-1','-1','0','0','0','0','0','0'])
        rppdata.children.append(['MASTERHWOUT','0','0','1','0','0','0','0','-1'])
        rppdata.children.append(['MASTER_NCH','2','2'])
        rppdata.children.append(['MASTER_VOLUME','1','0','-1','-1','1'])
        rppdata.children.append(['MASTER_PANMODE','3'])
        rppdata.children.append(['MASTER_FX','1'])
        rppdata.children.append(['MASTER_SEL','0'])

        if 'track_data' in projJ and 'track_order' in projJ:
            for trackid in projJ['track_order']:
                if trackid in projJ['track_data']:
                    trackdata = projJ['track_data'][trackid]

                    cvpj_trackname = "noname"
                    cvpj_trackcolor = "0"
                    cvpj_trackvol = 1.0

                    if 'name' in trackdata: cvpj_trackname = trackdata['name']
                    if 'vol' in trackdata: cvpj_trackvol = trackdata['vol']
                    if 'color' in trackdata: cvpj_trackcolor = cvpj_color_to_reaper_color(trackdata['color'])

                    track_uuid = '{'+str(uuid.uuid4())+'}'

                    rpp_trackdata = rpp_obj('TRACK',[track_uuid])
                    rpp_trackdata.children.append(['NAME',cvpj_trackname])
                    rpp_trackdata.children.append(['PEAKCOL',cvpj_trackcolor])
                    rpp_trackdata.children.append(['BEAT','-1'])
                    rpp_trackdata.children.append(['AUTOMODE','0'])
                    rpp_trackdata.children.append(['VOLPAN',cvpj_trackvol,'0','-1','-1','1'])
                    rpp_trackdata.children.append(['MUTESOLO','0','0','0'])
                    rpp_trackdata.children.append(['IPHASE','0'])
                    rpp_trackdata.children.append(['PLAYOFFS','0','1'])
                    rpp_trackdata.children.append(['ISBUS','0','0'])
                    rpp_trackdata.children.append(['BUSCOMP','0','0','0','0','0'])
                    rpp_trackdata.children.append(['SHOWINMIX','1','0.6667','0.5','1','0.5','-1','-1','-1'])
                    rpp_trackdata.children.append(['SEL','0'])
                    rpp_trackdata.children.append(['REC','0','0','1','0','0','0','0','0'])
                    rpp_trackdata.children.append(['VU','2'])
                    rpp_trackdata.children.append(['TRACKHEIGHT','0','0','0','0','0','0'])
                    rpp_trackdata.children.append(['INQ','0','0','0','0.5','100','0','0','100'])
                    rpp_trackdata.children.append(['NCHAN','2'])
                    rpp_trackdata.children.append(['FX','1'])
                    rpp_trackdata.children.append(['TRACKID',track_uuid])
                    rpp_trackdata.children.append(['PERF','0'])
                    rpp_trackdata.children.append(['MIDIOUT','-1'])
                    rpp_trackdata.children.append(['MAINSEND','1','0'])

                    if trackid in projJ['track_placements']:
                        trackplacements = projJ['track_placements'][trackid]

                        if 'notes' in trackplacements:
                            for trackplacement_notes in trackplacements['notes']:
                                clip_IGUID = '{'+str(uuid.uuid4())+'}'
                                clip_GUID = '{'+str(uuid.uuid4())+'}'

                                clip_name = ''
                                if 'name' in trackplacement_notes: clip_name = trackplacement_notes['name']

                                clip_notelist = []
                                if 'notelist' in trackplacement_notes: clip_notelist = trackplacement_notes['notelist']
                                clip_position = trackplacement_notes['position']
                                clip_duration = trackplacement_notes['duration']
                                clip_loop = 0
                                clip_startat = 0
                                clip_color = None
                                if 'color' in trackplacement_notes: clip_color = trackplacement_notes['color']

                                if 'cut' in trackplacement_notes:
                                    clip_cutdata = trackplacement_notes['cut']
                                    if clip_cutdata['type'] == 'cut': 
                                        clip_startat = clip_cutdata['start']

                                rpp_midiclipdata = rpp_obj('ITEM',track_uuid)
                                rpp_midiclipdata.children.append(['POSITION',calc_pos(clip_position, reaper_tempo)])
                                rpp_midiclipdata.children.append(['SNAPOFFS','0'])
                                rpp_midiclipdata.children.append(['LENGTH',calc_pos(clip_duration, reaper_tempo)])
                                rpp_midiclipdata.children.append(['LOOP',clip_loop])
                                rpp_midiclipdata.children.append(['ALLTAKES','0'])
                                rpp_midiclipdata.children.append(['FADEIN','1','0','0','1','0','0','0'])
                                rpp_midiclipdata.children.append(['FADEOUT','1','0','0','1','0','0','0'])
                                rpp_midiclipdata.children.append(['MUTE','0','0'])
                                if clip_color != None:
                                    rpp_midiclipdata.children.append(['COLOR',cvpj_color_to_reaper_color_clip(clip_color),'B'])
                                rpp_midiclipdata.children.append(['SEL','0'])
                                rpp_midiclipdata.children.append(['IGUID',clip_IGUID])
                                rpp_midiclipdata.children.append(['IID','1'])
                                rpp_midiclipdata.children.append(['NAME',clip_name])
                                rpp_midiclipdata.children.append(['VOLPAN','1','0','1','-1'])
                                rpp_midiclipdata.children.append(['SOFFS',calc_pos(clip_startat, reaper_tempo),'0'])
                                rpp_midiclipdata.children.append(['PLAYRATE','1','1','0','-1','0','0.0025'])
                                rpp_midiclipdata.children.append(['CHANMODE','0'])
                                rpp_midiclipdata.children.append(['GUID',clip_GUID])
                                rpp_midiclipdata.children.append(rpp_obj_data('SOURCE', ['MIDI'], convert_midi(clip_notelist,reaper_tempo,'4','4', clip_duration+clip_startat)))

                                rpp_trackdata.children.append(rpp_obj_data('ITEM', [], rpp_midiclipdata))


                    rppdata.children.append(rpp_obj_data('TRACK', track_uuid, rpp_trackdata))



        out_text = rpp.dumps(rppdata)
        
        with open(output_file, "w") as fileout:
            fileout.write(out_text)
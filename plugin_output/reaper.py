# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import uuid
import rpp
import struct
import base64
import os.path
from rpp import Element
from functions import data_bytes
from functions import data_values
from functions import colors
from functions import notelist_data
from functions import params
from functions import xtramath


def make_vst2(rpp_fxchain, cvpj_plugindata): 
    vst_fx_name = cvpj_plugindata['plugin']['name']
    vst_fx_path = cvpj_plugindata['plugin']['path']
    vst_fx_version = cvpj_plugindata['plugin']['version']
    vst_fx_fourid = cvpj_plugindata['plugin']['fourid']

    if cvpj_plugindata['datatype'] == 'chunk': vstparams = base64.b64decode(cvpj_plugindata['data'].encode())
    if cvpj_plugindata['datatype'] == 'param': 
        floatdata = []
        for num in range(cvpj_plugindata['numparams']):
            floatdata.append(float(cvpj_plugindata['params'][str(num)]['value']))
        vstparams = struct.pack('f'*cvpj_plugindata['numparams'], *floatdata)

    vstdata = []

    vstheader_ints = (vst_fx_fourid, 4276969198,0,2,1,0,2,0,len(vstparams),1,1048576)
    vstheader = base64.b64encode( struct.pack('IIIIIIIIIII', *vstheader_ints) ).decode()

    rpp_vstdata = rpp_obj('VST',[])
    rpp_vstdata.children.append([vstheader])

    for vstparampart in data_values.list_chunks(vstparams, 128):
        vstparampart_b64 = base64.b64encode(vstparampart).decode()
        rpp_vstdata.children.append([vstparampart_b64])

    rpp_fxchain.children.append(rpp_obj_data('VST', [vst_fx_name, os.path.basename(vst_fx_path), 0, "", vst_fx_fourid, ""], rpp_vstdata))


def rpp_obj(i_name, i_vals): return Element(tag=i_name, attrib=i_vals, children=[])
def rpp_obj_data(i_name, i_vals, i_data): return Element(tag=i_name, attrib=i_vals, children=i_data)

def cvpj_color_to_reaper_color(i_color): 
    cvpj_trackcolor = bytes(colors.rgb_float_to_rgb_int(i_color))+b'\x01'
    return int.from_bytes(cvpj_trackcolor, 'little')

def cvpj_color_to_reaper_color_clip(i_color): 
    cvpj_trackcolor = bytes(colors.rgb_float_to_rgb_int([i_color[2],i_color[1],i_color[0]]))+b'\x01'
    return int.from_bytes(cvpj_trackcolor, 'little')

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

    endmidi = (enddur*24)/tempomul

    i_list = {}
    notelist = notelist_data.sort(notelist)

    for cvpj_tr_pl_n in notelist:
        cvmi_n_pos = int(cvpj_tr_pl_n['position']*4)*60
        cvmi_n_dur = int(cvpj_tr_pl_n['duration']*4)*60
        cvmi_n_key = int(cvpj_tr_pl_n['key'])+60
        cvmi_n_vol = 127
        if 'vol' in cvpj_tr_pl_n: cvmi_n_vol = xtramath.clamp(int(cvpj_tr_pl_n['vol']*127), 0, 127)
        midi_add_cmd(i_list, cvmi_n_pos, ['note_on', cvmi_n_key, cvmi_n_vol])
        midi_add_cmd(i_list, cvmi_n_pos+cvmi_n_dur, ['note_off', cvmi_n_key])

    midi_add_cmd(i_list, int((endmidi)*60), ['end'])

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

def convert_placementdata(rpp_trackdata, trackplacements, cliptype, track_uuid):
    for trackplacement_data in trackplacements:
        clip_IGUID = '{'+str(uuid.uuid4())+'}'
        clip_GUID = '{'+str(uuid.uuid4())+'}'

        clip_name = data_values.get_value(trackplacement_data, 'name', '')
        clip_filename = data_values.get_value(trackplacement_data, 'file', '')
        clip_notelist = data_values.get_value(trackplacement_data, 'notelist', [])
        cvpj_pl_volume = data_values.get_value(trackplacement_data, 'vol', 1)
        cvpj_pl_pan = data_values.get_value(trackplacement_data, 'pan', 0)
        clip_color = data_values.get_value(trackplacement_data, 'color', None)
        clip_muted = data_values.get_value(trackplacement_data, 'muted', False)

        clip_position = trackplacement_data['position']
        clip_duration = trackplacement_data['duration']
        clip_startat = 0

        stretchinfo = [None, 1]
        pitch = 0
        preserve_pitch = 0

        if 'audiomod' in trackplacement_data:
            audiomoddata = trackplacement_data['audiomod']
            #print(audiomoddata)
            if 'pitch' in audiomoddata: pitch = audiomoddata['pitch']

            stretch_algorithm = audiomoddata['stretch_algorithm']

            if stretch_algorithm != 'resample': preserve_pitch = 1

            if audiomoddata['stretch_method'] == 'rate_speed': 
                stretchinfo = ['rate_tempo', (audiomoddata['stretch_data']['rate'])]
            if audiomoddata['stretch_method'] == 'rate_tempo': 
                stretchinfo = ['rate_tempo', (audiomoddata['stretch_data']['rate'])*tempomul]
            if audiomoddata['stretch_method'] == 'rate_ignoretempo': 
                stretchinfo = ['rate_ignoretempo', (audiomoddata['stretch_data']['rate'])]

            #print(stretchinfo, tempomul)

        endmidi = clip_duration

        if 'cut' in trackplacement_data:
                clip_cutdata = trackplacement_data['cut']

                if clip_cutdata['type'] == 'cut':
                    if cliptype == 'notes':  
                        if 'start' in clip_cutdata: clip_startat = clip_cutdata['start']/8/tempomul

                    if cliptype == 'audio': 
                        if 'start' in clip_cutdata: 
                            if stretchinfo[0] == 'rate_ignoretempo': clip_startat = (clip_cutdata['start']/8)
                            elif stretchinfo[0] == 'rate_ignoretempo': clip_startat = (clip_cutdata['start']/8)
                            else: clip_startat = ((clip_cutdata['start']/8)*stretchinfo[1])/tempomul

        rpp_clipdata = rpp_obj('ITEM',track_uuid)
        rpp_clipdata.children.append(['POSITION',clip_position])
        rpp_clipdata.children.append(['SNAPOFFS','0'])
        rpp_clipdata.children.append(['LENGTH',clip_duration])
        rpp_clipdata.children.append(['LOOP','0'])
        rpp_clipdata.children.append(['ALLTAKES','0'])
        rpp_clipdata.children.append(['FADEIN','1','0','0','1','0','0','0'])
        rpp_clipdata.children.append(['FADEOUT','1','0','0','1','0','0','0'])
        rpp_clipdata.children.append(['MUTE',int(clip_muted),'0'])
        if clip_color != None: rpp_clipdata.children.append(['COLOR',cvpj_color_to_reaper_color_clip(clip_color),'B'])
        rpp_clipdata.children.append(['SEL','0'])
        rpp_clipdata.children.append(['IGUID',clip_IGUID])
        rpp_clipdata.children.append(['IID','1'])
        rpp_clipdata.children.append(['NAME',clip_name])
        rpp_clipdata.children.append(['VOLPAN',str(cvpj_pl_volume),cvpj_pl_pan,'1','-1'])
        rpp_clipdata.children.append(['SOFFS',clip_startat,'0'])

        rpp_clipdata.children.append(['PLAYRATE',str(stretchinfo[1]),preserve_pitch,str(pitch),'-1','0','0.0025'])
        rpp_clipdata.children.append(['CHANMODE','0'])
        rpp_clipdata.children.append(['GUID',clip_GUID])
        if cliptype == 'notes': 
            rpp_clipdata.children.append(rpp_obj_data('SOURCE', ['MIDI'], convert_midi(clip_notelist,reaper_tempo,'4','4', endmidi)))
        if cliptype == 'audio': 
            audiotype = clip_filename.split('.')[-1]
            wavefiledata = rpp_obj('FILE',clip_filename)
            if audiotype == 'mp3': objaudiotype = 'MP3'
            elif audiotype == 'flac': objaudiotype = 'FLAC'
            elif audiotype == 'ogg': objaudiotype = 'VORBIS'
            else: objaudiotype = 'WAVE'
            rpp_wavefiledata = rpp_obj('SOURCE',[objaudiotype])
            rpp_wavefiledata.children.append(['FILE',clip_filename])
            rpp_clipdata.children.append(rpp_wavefiledata)

        rpp_trackdata.children.append(rpp_obj_data('ITEM', [], rpp_clipdata))
        
class output_reaper(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'reaper'
    def getshortname(self): return 'reaper'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': [],
        'time_seconds': True,
        'track_hybrid': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugins(self): return ['vst2']
    def parse(self, convproj_json, output_file):
        global reaper_tempo
        global tempomul
        projJ = json.loads(convproj_json)

        reaper_tempo = 140
        reaper_numerator = 4
        reaper_denominator = 4

        if 'timesig' in projJ: reaper_numerator, reaper_denominator = projJ['timesig']
        reaper_tempo = params.get(projJ, [], 'bpm', 120)[0]

        tempomul = reaper_tempo/120

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

                    cvpj_trackcolor = "0"
                    cvpj_trackname = data_values.get_value(trackdata, 'name', '')
                    cvpj_trackvol = params.get(trackdata, [], 'vol', 1)
                    cvpj_trackpan = params.get(trackdata, [], 'pan', 0)

                    if 'color' in trackdata: cvpj_trackcolor = cvpj_color_to_reaper_color(trackdata['color'])

                    track_uuid = '{'+str(uuid.uuid4())+'}'

                    rpp_trackdata = rpp_obj('TRACK',[track_uuid])
                    rpp_trackdata.children.append(['NAME',cvpj_trackname])
                    rpp_trackdata.children.append(['PEAKCOL',cvpj_trackcolor])
                    rpp_trackdata.children.append(['BEAT','-1'])
                    rpp_trackdata.children.append(['AUTOMODE','0'])
                    rpp_trackdata.children.append(['VOLPAN',cvpj_trackvol,cvpj_trackpan,'-1','-1','1'])
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

                    rpp_fxchain = rpp_obj('FXCHAIN',[])
                    rpp_fxchain.children.append(['SHOW','0'])
                    rpp_fxchain.children.append(['LASTSEL','0'])
                    rpp_fxchain.children.append(['DOCKED','0'])
                    rpp_fxchain.children.append(['BYPASS','0','0','0'])

                    if 'instdata' in trackdata:
                        cvpj_instdata = trackdata['instdata']
                        if 'plugin' in cvpj_instdata:
                            if cvpj_instdata['plugin'] in ['vst2-dll', 'vst2-so']:
                                cvpj_plugindata = cvpj_instdata['plugindata']
                                make_vst2(rpp_fxchain, cvpj_plugindata)


                    rpp_trackdata.children.append(rpp_obj_data('FXCHAIN', [], rpp_fxchain))


                    if trackid in projJ['track_placements']:
                        trackplacements = projJ['track_placements'][trackid]

                        if 'notes' in trackplacements:
                            convert_placementdata(rpp_trackdata, trackplacements['notes'], 'notes', track_uuid)
                        if 'audio' in trackplacements:
                            convert_placementdata(rpp_trackdata, trackplacements['audio'], 'audio', track_uuid)


                    rppdata.children.append(rpp_obj_data('TRACK', [track_uuid], rpp_trackdata))



        out_text = rpp.dumps(rppdata)
        
        with open(output_file, "w") as fileout:
            fileout.write(out_text)
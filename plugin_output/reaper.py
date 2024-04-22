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
from functions import xtramath

def make_vst3(rpp_fxchain, plugin_obj, convproj_obj): 
    vst_fx_name = plugin_obj.datavals.get('name', None)
    vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
    vst_fx_version = plugin_obj.datavals.get('version', None)
    vst_fx_id = plugin_obj.datavals.get('id', 0)
    chunkdata = plugin_obj.rawdata_get('chunk')
    vstparams = struct.pack('II', len(chunkdata), 1)+chunkdata+b'\x00\x00\x00\x00\x00\x00\x00\x00'
    vstheader = b':\xfbA+\xee^\xed\xfe'
    vstheader += struct.pack('II', 0, plugin_obj.audioports.num_outputs)
    for n in range(plugin_obj.audioports.num_outputs): 
        if n < len(plugin_obj.audioports.ports):
            vstheader += data_bytes.set_bitnums(plugin_obj.audioports.ports[n], 8)
        else:
            vstheader += b'\x00\x00\x00\x00\x00\x00\x00\x00'

    vstheader_end = b''
    vstheader_end += (len(chunkdata)+16).to_bytes(4, 'little')+b'\x01\x00\x00\x00\xff\xff\x10\x00'

    vstparams = base64.b64encode(vstparams).decode()
    vstheader = base64.b64encode(vstheader+vstheader_end).decode()
    vstend = base64.b64encode(b'\x01\x00\x00\x00').decode()

    rpp_vstdata = rpp_obj('VST',[])

    if vstheader:
        for vstheaderpart in data_values.list_chunks(vstheader, 128):
            rpp_vstdata.children.append([vstheaderpart])

    if vstparams:
        for vstparampart in data_values.list_chunks(vstparams, 128):
            rpp_vstdata.children.append([vstparampart])

    rpp_vstdata.children.append([vstend])
    rpp_fxchain.children.append(rpp_obj_data('VST', [vst_fx_name, os.path.basename(vst_fx_path), 0, "", '{'+vst_fx_id+'}', ""], rpp_vstdata))

def make_vst2(rpp_fxchain, plugin_obj, convproj_obj): 
    vst_fx_name = plugin_obj.datavals.get('name', None)
    vst_fx_path = plugin_obj.getpath_fileref(convproj_obj, 'file', None, True)
    vst_fx_version = plugin_obj.datavals.get('version', None)
    vst_fx_fourid = plugin_obj.datavals.get('fourid', 0)
    vst_fx_datatype = plugin_obj.datavals.get('datatype', None)
    vst_fx_numparams = plugin_obj.datavals.get('numparams', 0)

    vstparamsnum = 0
    vstparams = None

    if vst_fx_datatype == 'chunk': 
        vstparams = plugin_obj.rawdata_get('chunk')
        vstparamsnum = len(vstparams)
    if vst_fx_datatype == 'param': 
        floatdata = []
        for num in range(vst_fx_numparams):
            pval = plugin_obj.params.get('vst_param_'+str(num), 0).value
            floatdata.append(float(pval))
        vstparams = struct.pack('f'*vst_fx_numparams, *floatdata)
        vstparamsnum = len(vstparams)

    vstdata = []

    vstheader_ints = (vst_fx_fourid, 4276969198,0,2,1,0,2,0,vstparamsnum,1,1048576)
    vstheader = base64.b64encode( struct.pack('IIIIIIIIIII', *vstheader_ints) ).decode()

    rpp_vstdata = rpp_obj('VST',[])
    rpp_vstdata.children.append([vstheader])

    if vstparams:
        for vstparampart in data_values.list_chunks(vstparams, 128):
            vstparampart_b64 = base64.b64encode(vstparampart).decode()
            rpp_vstdata.children.append([vstparampart_b64])

    rpp_fxchain.children.append(rpp_obj_data('VST', [vst_fx_name, os.path.basename(vst_fx_path), 0, "", vst_fx_fourid, ""], rpp_vstdata))

def add_plugin(rpp_fxchain, pluginid, convproj_obj):
    plugin_found, plugin_obj = convproj_obj.get_plugin(pluginid)
    if plugin_found:
        is_vst2 = plugin_obj.check_wildmatch('vst2', None)
        is_vst3 = plugin_obj.check_wildmatch('vst3', None)
        fx_on, fx_wet = plugin_obj.fxdata_get()

        if (is_vst2 or is_vst3): rpp_fxchain.children.append(['BYPASS',int(not fx_on),'0','0'])
        if is_vst2: make_vst2(rpp_fxchain, plugin_obj, convproj_obj)
        if is_vst3: make_vst3(rpp_fxchain, plugin_obj, convproj_obj)
        if (is_vst2 or is_vst3) and fx_wet != 1: rpp_fxchain.children.append(['WET',str(fx_wet),'0'])

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

    i_list = {}
    notelist.sort()
    notelist.change_timings(960, False)

    for t_pos, t_dur, t_keys, t_vol, t_inst, t_extra, t_auto, t_slide in notelist.iter():
        for t_key in t_keys:
            cvmi_n_pos = int(t_pos)
            cvmi_n_dur = int(t_dur)
            cvmi_n_key = int(t_key)+60
            cvmi_n_vol = xtramath.clamp(int(t_vol*127), 0, 127)
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
    def getdawinfo(self, dawinfo_obj): 
        dawinfo_obj.name = 'REAPER'
        dawinfo_obj.file_ext = 'rpp'
        dawinfo_obj.placement_cut = True
        dawinfo_obj.placement_loop = []
        dawinfo_obj.fxtype = 'track'
        dawinfo_obj.time_seconds = True
        dawinfo_obj.track_hybrid = True
        dawinfo_obj.audio_stretch = ['rate']
        dawinfo_obj.plugin_ext = ['vst2', 'vst3']
    def parse(self, convproj_obj, output_file):
        global reaper_tempo
        global tempomul

        convproj_obj.change_timings(4, True)

        reaper_numerator, reaper_denominator = convproj_obj.timesig
        reaper_tempo = convproj_obj.params.get('bpm', 120).value

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

        track_uuids = []
        for _ in convproj_obj.iter_track():
            track_uuids.append('{'+str(uuid.uuid4())+'}')

        trackdata = []

        tracknum = 0
        for trackid, track_obj in convproj_obj.iter_track():

            track_uuid = track_uuids[tracknum]

            track_uuid_txt = '{'+str(track_uuid)+'}'

            cvpj_trackcolor = "0"
            cvpj_trackvol = track_obj.params.get('vol', 1.0).value
            cvpj_trackpan = track_obj.params.get('pan', 0).value

            rpp_trackdata = rpp_obj('TRACK',[track_uuid_txt])
            if track_obj.visual.name: 
                rpp_trackdata.children.append(['NAME',track_obj.visual.name])

            if track_obj.visual.color: 
                cvpj_trackcolor = cvpj_color_to_reaper_color(track_obj.visual.color)
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
            rpp_trackdata.children.append(['TRACKID',track_uuid_txt])
            rpp_trackdata.children.append(['PERF','0'])

            rpp_trackdata.children.append(['MIDIOUT','-1'])

            rpp_fxchain = rpp_obj('FXCHAIN',[])
            rpp_fxchain.children.append(['SHOW','0'])
            rpp_fxchain.children.append(['LASTSEL','0'])
            rpp_fxchain.children.append(['DOCKED','0'])
            rpp_fxchain.children.append(['BYPASS','0','0','0'])

            middlenote = track_obj.datavals.get('middlenote', 0)

            if middlenote != 0:
                rpp_vstdata = rpp_obj('VST',[])
                rpp_vstdata.children.append(['ZG1jcu5e7f4AAAAAAAAAAOYAAAABAAAAAAAQAA=='])
                midictrlstate1 = b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\xff?\x00\x00\x00 \x00\x00\x00 \x00\x00\x00\x00\x00\x005\x00\x00\x00C:\\Users\\colby\\AppData\\Roaming\\REAPER\\Data\\GM.reabank\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
                midictrlstate2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00Major\x00\r\x00\x00\x00102034050607\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\r\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00'
                midictrlstate3 = struct.pack('i', -middlenote)
                rpp_vstdata.children.append([base64.b64encode(midictrlstate1+midictrlstate3+midictrlstate2).decode()])
                rpp_fxchain.children.append(rpp_obj_data('VST', ['ReaControlMIDI (Cockos)','reacontrolmidi.dll','0',"",'1919118692<56535472636D64726561636F6E74726F>'], rpp_vstdata))

            add_plugin(rpp_fxchain, track_obj.inst_pluginid, convproj_obj)

            for notespl_obj in track_obj.placements.pl_notes:
                clip_IGUID = '{'+str(uuid.uuid4())+'}'
                clip_GUID = '{'+str(uuid.uuid4())+'}'
                clip_startat = 0
                if notespl_obj.cut_type == 'cut':
                    if 'start' in notespl_obj.cut_data: clip_startat = notespl_obj.cut_data['start']/8/tempomul
                rpp_clipdata = rpp_obj('ITEM',track_uuid_txt)
                rpp_clipdata.children.append(['POSITION',notespl_obj.position_real])
                rpp_clipdata.children.append(['SNAPOFFS','0'])
                rpp_clipdata.children.append(['LENGTH',notespl_obj.duration_real])
                rpp_clipdata.children.append(['LOOP','0'])
                rpp_clipdata.children.append(['ALLTAKES','0'])
                rpp_clipdata.children.append(['FADEIN','1','0','0','1','0','0','0'])
                rpp_clipdata.children.append(['FADEOUT','1','0','0','1','0','0','0'])
                rpp_clipdata.children.append(['MUTE',int(notespl_obj.muted),'0'])
                if notespl_obj.visual.color: rpp_clipdata.children.append(['COLOR',cvpj_color_to_reaper_color_clip(notespl_obj.visual.color),'B'])
                rpp_clipdata.children.append(['SEL','0'])
                rpp_clipdata.children.append(['IGUID',clip_IGUID])
                rpp_clipdata.children.append(['IID','1'])
                if notespl_obj.visual.name: rpp_clipdata.children.append(['NAME',notespl_obj.visual.name])
                #rpp_clipdata.children.append(['VOLPAN',str(cvpj_pl_volume),cvpj_pl_pan,'1','-1'])
                rpp_clipdata.children.append(['VOLPAN','1','0','1','-1'])
                rpp_clipdata.children.append(['SOFFS',clip_startat,'0'])
                rpp_clipdata.children.append(['CHANMODE','0'])
                rpp_clipdata.children.append(['GUID',clip_GUID])
                rpp_clipdata.children.append(rpp_obj_data('SOURCE', ['MIDI'], convert_midi(notespl_obj.notelist,reaper_tempo,'4','4', notespl_obj.duration_real)))
                rpp_trackdata.children.append(rpp_obj_data('ITEM', [], rpp_clipdata))

            for audiopl_obj in track_obj.placements.pl_audio:
                clip_IGUID = '{'+str(uuid.uuid4())+'}'
                clip_GUID = '{'+str(uuid.uuid4())+'}'
                clip_startat = 0
                #print(audiopl_obj.stretch.use_tempo)

                audiorate = audiopl_obj.stretch.calc_real_speed

                if audiopl_obj.cut_type == 'cut':
                    if 'start' in audiopl_obj.cut_data: clip_startat = audiopl_obj.cut_data['start']/8

                clip_startat *= audiopl_obj.stretch.calc_tempo_speed

                rpp_clipdata = rpp_obj('ITEM',track_uuid_txt)
                rpp_clipdata.children.append(['POSITION',audiopl_obj.position_real])
                rpp_clipdata.children.append(['SNAPOFFS','0'])
                rpp_clipdata.children.append(['LENGTH',audiopl_obj.duration_real])
                rpp_clipdata.children.append(['LOOP','0'])
                rpp_clipdata.children.append(['ALLTAKES','0'])
                rpp_clipdata.children.append(['FADEIN','1','0','0','1','0','0','0'])
                rpp_clipdata.children.append(['FADEOUT','1','0','0','1','0','0','0'])
                rpp_clipdata.children.append(['MUTE',int(audiopl_obj.muted),'0'])
                if audiopl_obj.visual.color: rpp_clipdata.children.append(['COLOR',cvpj_color_to_reaper_color_clip(audiopl_obj.visual.color),'B'])
                rpp_clipdata.children.append(['SEL','0'])
                rpp_clipdata.children.append(['IGUID',clip_IGUID])
                rpp_clipdata.children.append(['IID','1'])
                if audiopl_obj.visual.name: rpp_clipdata.children.append(['NAME',audiopl_obj.visual.name])
                rpp_clipdata.children.append(['VOLPAN',str(audiopl_obj.vol),audiopl_obj.pan,'1','-1'])
                rpp_clipdata.children.append(['SOFFS',clip_startat,'0'])

                preserve_pitch = int(audiopl_obj.stretch.algorithm != 'resample')

                rpp_clipdata.children.append(['PLAYRATE',audiorate,preserve_pitch,audiopl_obj.pitch,'-1','0','0.0025'])
                rpp_clipdata.children.append(['CHANMODE','0'])
                rpp_clipdata.children.append(['GUID',clip_GUID])

                ref_found, sampleref_obj = convproj_obj.get_sampleref(audiopl_obj.sampleref)
                if ref_found:
                    fileref_obj = sampleref_obj.fileref
                    filename = fileref_obj.get_path(None, True)
                    wavefiledata = rpp_obj('FILE',filename)
                    if fileref_obj.extension == 'mp3': objaudiotype = 'MP3'
                    elif fileref_obj.extension == 'flac': objaudiotype = 'FLAC'
                    elif fileref_obj.extension == 'ogg': objaudiotype = 'VORBIS'
                    else: objaudiotype = 'WAVE'
                    rpp_wavefiledata = rpp_obj('SOURCE',[objaudiotype])
                    rpp_wavefiledata.children.append(['FILE',filename])
                    rpp_clipdata.children.append(rpp_wavefiledata)

                rpp_trackdata.children.append(rpp_obj_data('ITEM', [], rpp_clipdata))

            for fxid in track_obj.fxslots_audio:
                add_plugin(rpp_fxchain, fxid, convproj_obj)

            rpp_trackdata.children.append(rpp_obj_data('FXCHAIN', [], rpp_fxchain))

            trackdata.append(rpp_trackdata)
            tracknum += 1

        if convproj_obj.trackroute:
            for tracknum, trackid in enumerate(convproj_obj.track_order):
                sends_obj = convproj_obj.trackroute[trackid]
                tracksendnum = convproj_obj.track_order.index(trackid)
                trackdata[tracknum].children.append(['MAINSEND',str(int(sends_obj.to_master_active)),'0'])
                for target, send_obj in sends_obj.iter():
                    amount = send_obj.params.get('amount', 1).value
                    pan = send_obj.params.get('pan', 0).value

                    trackrecnum = convproj_obj.track_order.index(target)
                    trackdata[trackrecnum].children.append(['AUXRECV',tracksendnum,'0',str(amount),str(pan),'0','0','0','0','0','-1:U','0','-1',''])
        else:
            for tracknum, trackid in enumerate(convproj_obj.track_order):
                trackdata[tracknum].children.append(['MAINSEND','1','0'])

        for n, t in enumerate(trackdata):
            track_uuid = track_uuids[n]
            rppdata.children.append(rpp_obj_data('TRACK', [track_uuid], t))

        out_text = rpp.dumps(rppdata)
        
        with open(output_file, "w") as fileout:
            fileout.write(out_text)
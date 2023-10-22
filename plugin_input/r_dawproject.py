# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import song
from functions import note_data
from functions import placement_data
import plugin_input
import json
import zipfile
import os
import xml.etree.ElementTree as ET
from functions_tracks import tracks_r

def getvalue(varx, name, fallbackval):
    if len(varx.findall(name)) != 0:
        varxi = varx.findall(name)[0]
        varvalue = varxi.get('value')
        varunit = varxi.get('unit')
        if varxi.get('unit') == 'normalized': varvalue = (float(varvalue)-0.5)*2
        return varvalue, varxi.get('name')
    else:
        return fallbackval, name



def parse_notelist(dpx_clip):
    dpx_notes = dpx_clip.findall('Notes')[0]
    dpx_notelist = dpx_notes.findall('Note')
    cvpj_notelist = []
    for dpx_note in dpx_notelist:
        cvpj_note = note_data.rx_makenote(float(dpx_note.get('time'))*4, float(dpx_note.get('duration'))*4, int(dpx_note.get('key'))-60, float(dpx_note.get('vel')), None)
        if dpx_note.get('release') != None: cvpj_note["release"] = float(dpx_note.get('release'))
        if dpx_note.get('channel') != None: cvpj_note["channel"] = int(dpx_note.get('channel'))

        cvpj_notemod = {}
        if dpx_note.findall('Points') != []: parse_note_points(cvpj_notemod, dpx_note.findall('Points')[0])
        if dpx_note.findall('Lanes') != []:
            xml_lanes = dpx_note.findall('Lanes')[0]
            if xml_lanes.findall('Points') != []:
                for pointxml in xml_lanes.findall('Points'):
                    parse_note_points(cvpj_notemod, pointxml)
        if cvpj_notemod != {}: cvpj_note["notemod"] = cvpj_notemod
        cvpj_notelist.append(cvpj_note)
    return cvpj_notelist

def calc_time(dpx_clip, dp_tempo):
    dpx_p_timetype = dpx_clip.get('contentTimeUnit')

    calctempo = (dp_tempo/120)

    dpx_p_time = dpx_clip.get('time')
    dpx_p_duration = dpx_clip.get('duration')
    dpx_p_playStart = dpx_clip.get('playStart')
    dpx_p_playStop = dpx_clip.get('playStop')

    if dpx_p_timetype == 'beats':
        if dpx_p_time != None: dpx_p_time = float(dpx_p_time)*4
        if dpx_p_duration != None: dpx_p_duration = float(dpx_p_duration)*4
        if dpx_p_playStop != None: dpx_p_playStop = float(dpx_p_playStop)*4
        if dpx_p_playStop != None: dpx_p_playStop = float(dpx_p_playStop)*4
    if dpx_p_timetype == 'seconds':
        if dpx_p_time != None: dpx_p_time = (float(dpx_p_time)*8)*calctempo
        if dpx_p_duration != None: dpx_p_duration = (float(dpx_p_duration)*16)*calctempo
        if dpx_p_playStart != None: dpx_p_playStart = (float(dpx_p_playStart)*16)*calctempo
        if dpx_p_playStop != None: dpx_p_playStop = (float(dpx_p_playStop)*16)*calctempo

    return dpx_p_time, dpx_p_duration, dpx_p_playStart, dpx_p_playStop


def dp_parse_trackinfo(dpx_track): 
    global cvpj_l
    global trackchanid

    cvpj_l_track = {}

    dpt_contentType = dpx_track.get('contentType')
    dpt_id = dpx_track.get('id')
    dpx_chan = dpx_track.findall('Channel')[0]
    dpt_destination = dpx_chan.get('destination')
    dpt_role = dpx_chan.get('role')
    dpt_cid = dpx_chan.get('id')
    dpt_color = dpx_track.get('color')

    if '#' in dpt_color: dpt_color = colors.hex_to_rgb_float(dpt_color[1:7])

    dpt_name = dpx_track.get('name')
    track_role = None

    trackchanid[dpt_id] = dpt_cid

    if dpt_contentType == 'notes' and dpt_role == 'regular': track_role = "instrument"
    if dpt_contentType == 'audio' and dpt_role == 'regular': track_role = "audio"
    #if dpt_contentType == 'audio' and dpt_role == 'effect': track_role = "return"
    #if dpt_contentType == 'audio notes' and dpt_role == 'master': track_role = "master"
    #if dpt_contentType == 'tracks' and dpt_role == 'master': track_role = "group"

    if track_role == "instrument": cvpj_l_track['type'] = "instrument"
    if track_role == "audio": cvpj_l_track['type'] = "audio"
    #if track_role == "return": cvpj_l_track['type'] = "return"
    #if track_role == "group": cvpj_l_track['type'] = "group"
    #if track_role == "master": cvpj_l_track['type'] = "master"

    cvpj_l_track_pan = getvalue(dpx_chan, 'Pan', 0)
    cvpj_l_track_vol = getvalue(dpx_chan, 'Volume', 1)

    if track_role == "instrument" or track_role == "audio":
        tracks_r.track_create(cvpj_l, dpt_cid, track_role)
        tracks_r.track_visual(cvpj_l, dpt_cid, name=dpt_name, color=dpt_color)
        tracks_r.track_param_add(cvpj_l, dpt_cid, 'vol', float(cvpj_l_track_vol[0]), 'float')
        tracks_r.track_param_add(cvpj_l, dpt_cid, 'pan', float(cvpj_l_track_pan[0]), 'float')

def parse_auto(pointsxml):
    cvpj_auto_out = []
    for xmlpoint in pointsxml.findall('RealPoint'):
        cvpj_auto_point = {}
        cvpj_auto_point['position'] = float(xmlpoint.get('time'))*4
        cvpj_auto_point['value'] = float(xmlpoint.get('value'))
        cvpj_auto_out.append(cvpj_auto_point)
    return cvpj_auto_out

def parse_note_points(cvpj_notemod, note_points_xml):
    if note_points_xml.findall('Target') != []:
        xml_target = note_points_xml.findall('Target')[0]
        expression = xml_target.get('expression')
        if expression == 'transpose': expression = 'pitch'
        if 'auto' not in cvpj_notemod: cvpj_notemod['auto'] = {}
        cvpj_notemod['auto'][expression] = parse_auto(note_points_xml)

class input_dawproject(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'dawproject'
    def getname(self): return 'dawproject'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'track_lanes': False,
        'placement_cut': True,
        'placement_loop': ['loop', 'loop_off', 'loop_adv'],
        'placement_audio_nested': True,
        'auto_nopl': True,
        'track_nopl': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        global trackchanid
        global samplefolder

        zip_data = zipfile.ZipFile(input_file, 'r')

        cvpj_l = {}
        trackchanid = {}

        dp_timesig = [4,4]
        dp_tempo = 140

        samplefolder = extra_param['samplefolder']

        if 'project.xml' in zip_data.namelist():
            dpx_project = ET.fromstring(zip_data.read('project.xml'))
            dpx_transport = dpx_project.findall('Transport')[0]
            dpx_structure = dpx_project.findall('Structure')[0]
            dpx_arrangement = dpx_project.findall('Arrangement')[0]

            # ----------------------------------------- Transport -----------------------------------------

            if len(dpx_transport.findall('Tempo')) != 0:
                dpx_tempo = dpx_transport.find('Tempo')
                dp_tempo = float(dpx_tempo.get('value'))
                dp_id_tempo = dpx_transport.find('id')

            if len(dpx_transport.findall('TimeSignature')) != 0:
                dpx_ts = dpx_transport.find('TimeSignature')
                dp_timesig[0] = int(dpx_ts.get('denominator'))
                dp_timesig[1] = int(dpx_ts.get('numerator'))
                dp_id_ts = dpx_transport.find('id')

            # ----------------------------------------- Structure -----------------------------------------

            mastertrack_id = None
            effecttrack_ids = []
            track_id_dest = {}

            t_tracks = []
            t_grouptracks = []

            for dpx_strack in dpx_structure.findall('Track'):
                dp_parse_trackinfo(dpx_strack)

            groupids = []
            masterid = None

            # ----------------------------------------- Arrangement -----------------------------------------

            dpx_lanes = dpx_arrangement.findall('Lanes')[0]
            dpx_trklanes = dpx_lanes.findall('Lanes')

            for dpx_trklane in dpx_trklanes:
                trackid = dpx_trklane.get('track')
                if trackid in trackchanid:
                    trackidchan = trackchanid[trackid]
                    if dpx_trklane.findall('Clips') != []:
                        dpx_clips = dpx_trklane.findall('Clips')[0]
                        for dpx_clip in dpx_clips.findall('Clip'):

                            dpx_p_loopStart = dpx_clip.get('loopStart')
                            dpx_p_loopEnd = dpx_clip.get('loopEnd')

                            dpx_p_time, dpx_p_duration, dpx_p_playStart, dpx_p_playStop = calc_time(dpx_clip, dp_tempo)

                            for dpx_clipnotes in dpx_clip.findall('Notes'):
                                cvpj_pldata = placement_data.makepl_n(dpx_p_time, dpx_p_duration, parse_notelist(dpx_clipnotes))
                                if dpx_p_loopStart == None and dpx_p_loopEnd == None: cvpj_pldata["cut"] = {'type': 'cut', 'start': float(dpx_p_playStart)*4}
                                elif dpx_p_loopStart != None and dpx_p_loopEnd != None: cvpj_pldata["cut"] = placement_data.cutloopdata(float(dpx_p_playStart)*4, float(dpx_p_loopStart)*4, float(dpx_p_loopEnd)*4)
                                tracks_r.add_pl(cvpj_l, trackidchan, 'notes', cvpj_pldata)

                            for dpx_lanes in dpx_clip.findall('Lanes'):
                                if dpx_lanes.findall('Notes') != []:
                                    cvpj_pldata = placement_data.makepl_n(dpx_p_time, dpx_p_duration, parse_notelist(dpx_lanes))
                                    if dpx_p_loopStart == None and dpx_p_loopEnd == None: cvpj_pldata["cut"] = {'type': 'cut', 'start': float(dpx_p_playStart)*4}
                                    elif dpx_p_loopStart != None and dpx_p_loopEnd != None: cvpj_pldata["cut"] = placement_data.cutloopdata(float(dpx_p_playStart)*4, float(dpx_p_loopStart)*4, float(dpx_p_loopEnd)*4)
                                    tracks_r.add_pl(cvpj_l, trackidchan, 'notes', cvpj_pldata)

                            for dpx_clipp in dpx_clip.findall('Clips'):

                                #print('audio', dpx_p_time,dpx_p_playStop)

                                clip_events = []

                                pl_data = {}
                                pl_data['position'] = dpx_p_time
                                pl_data['duration'] = dpx_p_playStop

                                for dpx_insideclipp in dpx_clipp.findall('Clip'):

                                    in_time, in_duration, in_playStart, in_playStop = calc_time(dpx_insideclipp, dp_tempo)
                                    #print(in_time, in_duration, in_playStart, in_playStop, dpx_insideclipp.findall('Audio'))
                                    inside_clip = {}
                                    inside_clip['position'] = in_time
                                    inside_clip['duration'] = in_duration
                                    audio_data = dpx_insideclipp.findall('Audio')
                                    if audio_data:
                                        audio_file_data = audio_data[0].findall('File')
                                        if audio_file_data:
                                            audio_file_external = audio_file_data[0].get('external')
                                            audio_file_path = audio_file_data[0].get('path')

                                            if audio_file_path != None:
                                                zip_data.extract(audio_file_path, path=samplefolder, pwd=None)
                                                inside_clip['file'] = os.path.join(samplefolder,audio_file_path)

                                    clip_events.append(inside_clip)

                                pl_data['events'] = clip_events
                                tracks_r.add_pl(cvpj_l, trackidchan, 'audio_nested', pl_data)


        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['timesig'] = dp_timesig
        song.add_param(cvpj_l, 'bpm', dp_tempo)
        return json.dumps(cvpj_l)


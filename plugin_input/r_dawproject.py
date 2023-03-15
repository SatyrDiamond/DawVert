# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
import plugin_input
import json
import zipfile
import xml.etree.ElementTree as ET

def getvalue(varx, name, fallbackval):
    if len(varx.findall(name)) != 0:
        varxi = varx.findall(name)[0]
        return varxi.get('value')
    else:
        return fallbackval


def dp_parse_trackinfo(dpx_track): 
    global cvpj_l
    global trackchanid

    track_data = cvpj_l['track_data']
    track_order = cvpj_l['track_order']
    track_return = cvpj_l['track_return']
    track_master = cvpj_l['track_master']

    cvpj_l_track = {}

    dpt_contentType = dpx_track.get('contentType')
    dpt_id = dpx_track.get('id')
    dpx_chan = dpx_track.findall('Channel')[0]
    dpt_destination = dpx_chan.get('destination')
    dpt_role = dpx_chan.get('role')
    dpt_cid = dpx_chan.get('id')
    dpt_color = dpx_track.get('color')
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

    cvpj_l_track['pan'] = float(getvalue(dpx_chan, 'Pan', 0))
    cvpj_l_track['vol'] = float(getvalue(dpx_chan, 'Volume', 1))

    if dpt_color != None: cvpj_l_track['color'] = colors.hex_to_rgb_float(dpt_color)
    if dpt_name != None: cvpj_l_track['name'] = dpt_name

    if track_role == "instrument" or track_role == "audio":
        track_data[dpt_cid] = cvpj_l_track
        track_order.append(dpt_cid)

def parse_auto(pointsxml):
    cvpj_auto_out = []
    for xmlpoint in pointsxml.findall('RealPoint'):
        cvpj_auto_point = {}
        cvpj_auto_point['position'] = float(xmlpoint.get('time')*4)
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
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        global trackchanid

        zip_data = zipfile.ZipFile(input_file, 'r')

        cvpj_l = {}
        trackchanid = {}

        dp_timesig = [4,4]
        dp_tempo = 140

        cvpj_l['track_data'] = {}
        cvpj_l['track_order'] = []
        cvpj_l['track_return'] = {}
        cvpj_l['track_placements'] = {}

        cvpj_l['track_master'] = {}

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
                trackidchan = trackchanid[trackid]
                cvpj_l['track_placements'][trackidchan] = {}
                if dpx_trklane.findall('Clips') != []:
                    dpx_clips = dpx_trklane.findall('Clips')[0]
                    for dpx_clip in dpx_clips.findall('Clip'):
                        dpx_p_time = dpx_clip.get('time')
                        dpx_p_duration = dpx_clip.get('duration')
                        dpx_p_playStart = dpx_clip.get('playStart')

                        dpx_p_loopStart = dpx_clip.get('loopStart')
                        dpx_p_loopEnd = dpx_clip.get('loopEnd')

                        cvpj_pldata = {}
                        cvpj_pldata["position"] = float(dpx_p_time)*4
                        cvpj_pldata["duration"] = float(dpx_p_duration)*4
                        cvpj_pldata["notelist"] = []

                        #print(' ----- ', end="")
                        if dpx_p_loopStart == None and dpx_p_loopEnd == None:
                            #print('Cut', dpx_p_playStart, dpx_p_duration)
                            cvpj_pldata["cut"] = {}
                            cvpj_pldata["cut"]['type'] = 'cut'
                            cvpj_pldata["cut"]['start'] = float(dpx_p_playStart)*4
                            cvpj_pldata["cut"]['end'] = (float(dpx_p_duration)+float(dpx_p_playStart))*4
                        elif dpx_p_loopStart != None and dpx_p_loopEnd != None:
                            #print('Warp', dpx_p_playStart, dpx_p_duration, dpx_p_loopStart,dpx_p_loopEnd)
                            cvpj_pldata["cut"] = {}
                            cvpj_pldata["cut"]['type'] = 'warp'
                            cvpj_pldata["cut"]['start'] = float(dpx_p_playStart)*4
                            cvpj_pldata["cut"]['loopstart'] = float(dpx_p_loopStart)*4
                            cvpj_pldata["cut"]['loopend'] = float(dpx_p_loopEnd)*4

                        if dpx_clip.findall('Notes') != []:
                            cvpj_l['track_placements'][trackidchan]['notes'] = []
                            dpx_notes = dpx_clip.findall('Notes')[0]
                            dpx_notelist = dpx_notes.findall('Note')
                            for dpx_note in dpx_notelist:
                                cvpj_note = {}
                                cvpj_note["position"] = float(dpx_note.get('time'))*4
                                cvpj_note["duration"] = float(dpx_note.get('duration'))*4
                                cvpj_note["key"] = int(dpx_note.get('key'))-60
                                cvpj_note["vol"] = float(dpx_note.get('vel'))
                                cvpj_note["release"] = float(dpx_note.get('rel'))
                                if dpx_note.get('channel') != None: cvpj_note["channel"] = int(dpx_note.get('channel'))

                                cvpj_notemod = {}

                                cvpj_auto_points = None
                                if dpx_note.findall('Points') != []:
                                    parse_note_points(cvpj_notemod, dpx_note.findall('Points')[0])

                                if dpx_note.findall('Lanes') != []:
                                    xml_lanes = dpx_note.findall('Lanes')[0]
                                    if xml_lanes.findall('Points') != []:
                                        for pointxml in xml_lanes.findall('Points'):
                                            parse_note_points(cvpj_notemod, pointxml)

                                if cvpj_notemod != {}: cvpj_note["notemod"] = cvpj_notemod

                                cvpj_pldata["notelist"].append(cvpj_note)


                            cvpj_l['track_placements'][trackidchan]['notes'].append(cvpj_pldata)


        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['timesig_numerator'] = dp_timesig[0]
        cvpj_l['timesig_denominator'] = dp_timesig[1]
        cvpj_l['bpm'] = dp_tempo
        return json.dumps(cvpj_l)


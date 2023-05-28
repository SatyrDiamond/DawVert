# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
import io
import zipfile
from bs4 import BeautifulSoup
from functions import placements
from functions import auto
from functions import colors

def addvalue_bool(xmltag, xmlname, i_value, i_id, i_name):
    x_temp = ET.SubElement(xmltag, xmlname)
    x_temp.set('value', str(i_value))
    x_temp.set('id', str(i_id))
    x_temp.set('name', str(i_name))

def addvalue(xmltag, xmlname, i_max, i_min, i_unit, i_value, i_id, i_name):
    x_temp = ET.SubElement(xmltag, xmlname)
    x_temp.set('max', str(i_max))
    x_temp.set('min', str(i_min))
    x_temp.set('unit', str(i_unit))
    x_temp.set('value', str(i_value))
    x_temp.set('id', str(i_id))
    x_temp.set('name', str(i_name))

def addmeta(xmltag, name, value):
    x_temp = ET.SubElement(xmltag, name)
    x_temp.text = str(value)

def getunusedvalue():
    global unusedvalue
    unusedvalue += 1
    return 'unused'+str(unusedvalue)

def make_auto_point(xmltag, value, position):
    x_autopoint = ET.SubElement(xmltag, "RealPoint")
    x_autopoint.set('value', str(value))
    x_autopoint.set('interpolation', 'linear')
    x_autopoint.set('time', str(position/4))

def make_automation(x_project_arr, xmlname, cvpj_auto, unit, cvpj_id):
    x_project_arr_tempo = ET.SubElement(x_project_arr, xmlname)
    x_project_arr_tempo.set('unit', unit)
    x_project_arr_target = ET.SubElement(x_project_arr_tempo, "Target")
    x_project_arr_target.set('parameter', cvpj_id)
    for cvpj_auto_pl in cvpj_auto['placements']:
        cvpj_auto_pl_pos = cvpj_auto_pl['position']
        t_points = auto.remove_instant(cvpj_auto_pl['points'], cvpj_auto_pl['position'], False)
        for t_point in t_points:
            make_auto_point(x_project_arr_tempo, t_point['value'], t_point['position'])

def make_auto_note(xmltag, cvpj_points, unit, expression):
    xml_points = ET.SubElement(xmltag, "Points")
    xml_points.set('unit', unit)
    xml_points.set('id', get_unused_id())
    xml_target = ET.SubElement(xml_points, "Target")
    xml_target.set('expression', expression)
    t_points = auto.remove_instant(cvpj_points, 0, True)
    for t_point in t_points:
        make_auto_point(xml_points, t_point['value'], t_point['position'])

def maketrack(xmltag, cvpj_trackdata, cvpj_trackname):
    x_str_track = ET.SubElement(xmltag, "Track")
    x_str_track.set('loaded', 'true')
    x_str_track.set('id', '__track__'+cvpj_trackname)
    if 'color' in cvpj_trackdata: x_str_track.set('color', '#'+colors.rgb_float_2_hex(cvpj_trackdata['color']))
    if 'name' in cvpj_trackdata: x_str_track.set('name', cvpj_trackdata['name'])
    x_str_track_ch = ET.SubElement(x_str_track, "Channel")
    x_str_track_ch.set('audioChannels', '2')
    x_str_track_ch.set('destination', '__mastertrack__')
    x_str_track_ch.set('role', 'regular')
    x_str_track_ch.set('solo', 'false')
    x_str_track_ch.set('id', 'trackch_'+cvpj_trackname)
    addvalue_bool(x_str_track_ch, 'Mute', 'false',  '__param__track__mute__'+cvpj_trackname, 'Mute')
    if 'pan' in cvpj_trackdata: addvalue(x_str_track_ch, 'Pan', 1, -1, 'linear', cvpj_trackdata['pan'], '__param__track__pan__'+cvpj_trackname, 'Pan')
    else: addvalue(x_str_track_ch, 'Pan', 1, -1, 'linear', 0, cvpj_trackname+'_pan', 'Pan')
    if 'vol' in cvpj_trackdata: addvalue(x_str_track_ch, 'Volume', 2, 0, 'linear', cvpj_trackdata['vol'], '__param__track__vol__'+cvpj_trackname, 'Volume')
    else: addvalue(x_str_track_ch, 'Volume', 2, 0, 'linear', 1, cvpj_trackname+'_vol', 'Volume')
    if cvpj_trackdata['type'] == 'instrument': 
        x_str_track.set('contentType', 'notes')

unuseditnum = 0

def get_unused_id():
    global unuseditnum
    unuseditnum += 1
    return 'unused_'+str(unuseditnum)

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def getname(self): return 'DawProject'
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'dawproject'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_loop': True,
        'no_placements': False,
        'no_pl_auto': True,
        'audio_events': True
        }
    def parse(self, convproj_json, output_file):
        global NoteStep
        global tracknum

        tracknum = 0

        projJ = json.loads(convproj_json)
        
        cvpj_trackdata = projJ['track_data']
        cvpj_trackordering = projJ['track_order']
        cvpj_trackplacements = projJ['track_placements']

        x_project = ET.Element("Project")
        x_project.set('version', '0.1')

        x_metadata = ET.Element("MetaData")

        # ----------------------------------------- Application -----------------------------------------
        x_project_app = ET.SubElement(x_project, "Application")
        x_project_app.set('name', 'DawVert: The DAW ConVERTer')

        # ----------------------------------------- Transport -----------------------------------------

        if 'timesig_numerator' in projJ: dp_numerator = projJ['timesig_numerator']
        else: dp_numerator = 4
        if 'timesig_denominator' in projJ: dp_denominator = projJ['timesig_denominator']
        else: dp_denominator = 4

        x_project_tr = ET.SubElement(x_project, "Transport")
        if 'bpm' in projJ: addvalue(x_project_tr, 'Tempo', 666, 20, 'bpm', projJ['bpm'], 'dawvert_bpm', 'Tempo')
        else: addvalue(x_project_tr, 'Tempo', 666, 20, 'bpm', 140, 'dawvert_bpm', 'Tempo')
        x_project_tr_ts = ET.SubElement(x_project_tr, 'TimeSignature')
        x_project_tr_ts.set('denominator', str(int(dp_denominator)))
        x_project_tr_ts.set('numerator', str(int(dp_numerator)))
        x_project_tr_ts.set('id', '__param__song__timesig')

        # ----------------------------------------- Structure -----------------------------------------
        x_str = ET.SubElement(x_project, "Structure")
        # ----------------------------------------- Arrangement -----------------------------------------

        x_project_arr = ET.SubElement(x_project, "Arrangement")
        x_project_arr.set('id', 'dawvert_arrangement')
        x_arr_lanes = ET.SubElement(x_project_arr, "Lanes")
        x_arr_lanes.set('timeUnit', 'beats')
        x_arr_markers = ET.SubElement(x_project_arr, "Markers")
        x_arr_tsa = ET.SubElement(x_project_arr, "TimeSignatureAutomation")
        x_arr_tsa.set('parameter', '__param__song__timesig')

        # ----------------------------------------- Tracks -----------------------------------------

        for cvpj_trackentry in cvpj_trackordering:
            if cvpj_trackentry in cvpj_trackdata:
                maketrack(x_str, cvpj_trackdata[cvpj_trackentry], cvpj_trackentry)

        # ----------------------------------------- Tracks -----------------------------------------

        for trackid in cvpj_trackplacements:
            pldata = cvpj_trackplacements[trackid]

            if 'notes' in pldata:
                s_pl_nl = pldata['notes']
                x_arr_lanes_pl = ET.SubElement(x_arr_lanes, "Lanes")
                x_arr_lanes_pl.set('track', '__track__'+trackid)
                #x_arr_lanes_pl.set('id', get_unused_id())
                x_arr_lanes_clips = ET.SubElement(x_arr_lanes_pl, "Clips")
                #x_arr_lanes_clips.set('id', get_unused_id())

                for s_trkplacement in s_pl_nl:
                    x_arr_lanes_clip = ET.SubElement(x_arr_lanes_clips, "Clip")
                    if 'color' in s_trkplacement: x_arr_lanes_clip.set('color', '#'+colors.rgb_float_2_hex(s_trkplacement['color']))
                    if 'name' in s_trkplacement: x_arr_lanes_clip.set('name', s_trkplacement['name'])
                    x_arr_lanes_clip.set('time', str(s_trkplacement['position']/4))

                    if 'cut' in s_trkplacement:
                        if s_trkplacement['cut']['type'] == 'cut':
                            x_arr_lanes_clip.set('duration', str((s_trkplacement['cut']['end'] - s_trkplacement['cut']['start'])/4))
                            x_arr_lanes_clip.set('playStart', str(s_trkplacement['cut']['start']/4))
                        if s_trkplacement['cut']['type'] == 'loop':
                            x_arr_lanes_clip.set('duration', str(s_trkplacement['duration']/4))
                            x_arr_lanes_clip.set('playStart', str(s_trkplacement['cut']['start']/4))
                            x_arr_lanes_clip.set('loopStart', str(s_trkplacement['cut']['loopstart']/4))
                            x_arr_lanes_clip.set('loopEnd', str(s_trkplacement['cut']['loopend']/4))
                    else:
                        x_arr_lanes_clip.set('time', str(s_trkplacement['position']/4))
                        x_arr_lanes_clip.set('duration', str(s_trkplacement['duration']/4))
                        x_arr_lanes_clip.set('playStart', '0.0')
                    if 'notelist' in s_trkplacement:
                        s_trknotelist = s_trkplacement['notelist']
                        nlidcount = 1
                        x_arr_lanes_clip_notes = ET.SubElement(x_arr_lanes_clip, "Notes")
                        #x_arr_lanes_clip_notes.set('id', get_unused_id())
                        for s_trknote in s_trknotelist:
                            x_arr_lanes_clip_note = ET.SubElement(x_arr_lanes_clip_notes, "Note")
                            x_arr_lanes_clip_note.set('time', str(s_trknote['position']/4))
                            x_arr_lanes_clip_note.set('duration', str(s_trknote['duration']/4))
                            x_arr_lanes_clip_note.set('key', str(s_trknote['key']+60))
                            if 'notemod' in s_trknote:
                                x_arr_lanes_clip_note_lanes = ET.SubElement(x_arr_lanes_clip_note, "Lanes")
                                #x_arr_lanes_clip_note_lanes.set('id', get_unused_id())
                                if 'auto' in s_trknote['notemod']:
                                    notemodauto = s_trknote['notemod']['auto']
                                    for expresstype in s_trknote['notemod']['auto']:
                                        if expresstype == 'pan': make_auto_note(x_arr_lanes_clip_note_lanes, notemodauto['pan'], 'linear', 'pan')
                                        if expresstype == 'gain': make_auto_note(x_arr_lanes_clip_note_lanes, notemodauto['gain'], 'linear', 'gain')
                                        if expresstype == 'timbre': make_auto_note(x_arr_lanes_clip_note_lanes, notemodauto['timbre'], 'linear', 'timbre')
                                        if expresstype == 'pitch': make_auto_note(x_arr_lanes_clip_note_lanes, notemodauto['pitch'], 'semitones', 'transpose')
                                        if expresstype == 'pressure': make_auto_note(x_arr_lanes_clip_note_lanes, notemodauto['pressure'], 'linear', 'pressure')
                            if 'vol' in s_trknote: x_arr_lanes_clip_note.set('vel', str(s_trknote['vol']))
                        nlidcount += 1

        # ----------------------------------------- Master -----------------------------------------
        x_str_master = ET.SubElement(x_str, "Track")
        x_str_master.set('contentType', 'audio notes')
        x_str_master.set('loaded', 'true')
        x_str_master.set('color', '#444444')
        x_str_master.set('name', 'Master')
        x_str_mas_ch = ET.SubElement(x_str_master, "Channel")
        x_str_mas_ch.set('audioChannels', '2')
        x_str_mas_ch.set('role', 'master')
        x_str_mas_ch.set('solo', 'false')
        x_str_mas_ch.set('id', '__mastertrack__')
        addvalue_bool(x_str_mas_ch, 'Mute', 'false', '__param__mastertrack__mute', 'Mute')
        addvalue(x_str_mas_ch, 'Pan', 1, -1, 'linear', 0, '__param__mastertrack__pan', 'Pan')
        addvalue(x_str_mas_ch, 'Volume', 2, 0, 'linear', 1, '__param__mastertrack__vol', 'Volume')

        # ----------------------------------------- info -----------------------------------------

        if 'info' in projJ:
            infoJ = projJ['info']
            if 'title' in infoJ: addmeta(x_metadata, 'Title', infoJ['title'])
            if 'author' in infoJ: addmeta(x_metadata, 'Artist', infoJ['author'])
            if 'original_author' in infoJ: addmeta(x_metadata, 'OriginalArtist', infoJ['original_author'])
            if 'songwriter' in infoJ: addmeta(x_metadata, 'Songwriter', infoJ['songwriter'])
            if 'producer' in infoJ: addmeta(x_metadata, 'Producer', infoJ['producer'])
            if 'year' in infoJ: addmeta(x_metadata, 'Year', str(infoJ['year']))
            if 'genre' in infoJ: addmeta(x_metadata, 'Genre', infoJ['genre'])
            if 'copyright' in infoJ: addmeta(x_metadata, 'Copyright', infoJ['copyright'])
            if 'Comment' in infoJ: addmeta(x_metadata, 'Comment', infoJ['genre'])
            if 'email' in infoJ: addmeta(x_metadata, 'Email', infoJ['email'])
            if 'message' in infoJ: 
                if infoJ['message']['type'] == 'html':
                    bst = BeautifulSoup(infoJ['message']['text'], "html.parser")
                    addmeta(x_metadata, 'Comment', bst.get_text().replace("\n", "\r"))
                if infoJ['message']['type'] == 'text':
                    addmeta(x_metadata, 'Comment', infoJ['message']['text'].replace("\n", "\r"))

        # ----------------------------------------- timemarkers -----------------------------------------

        if 'timemarkers' in projJ:
            for timemarker in projJ['timemarkers']:
                if 'type' in timemarker:
                    if timemarker['type'] == 'timesig':
                        x_arr_tsa_tsp = ET.SubElement(x_arr_tsa, "TimeSignaturePoint")
                        x_arr_tsa_tsp.set('numerator', str(timemarker['numerator']))
                        x_arr_tsa_tsp.set('denominator', str(timemarker['denominator']))
                        x_arr_tsa_tsp.set('time', str(timemarker['position']/4))
                    else:
                        x_arr_marker = ET.SubElement(x_arr_markers, "Marker")
                        x_arr_marker.set('name', str(timemarker['name']))
                        x_arr_marker.set('time', str(timemarker['position']/4))
                        x_arr_marker.set('color', '#444444')
                else:
                    x_arr_marker = ET.SubElement(x_arr_markers, "Marker")
                    x_arr_marker.set('name', str(timemarker['name']))
                    x_arr_marker.set('time', str(timemarker['position']/4))
                    x_arr_marker.set('color', '#444444')

        # ----------------------------------------- auto -----------------------------------------

        if 'automation' in projJ:
            if 'main' in projJ['automation']:
                if 'bpm' in projJ['automation']['main']:
                    make_automation(x_project_arr, "TempoAutomation", projJ['automation']['main']['bpm'], 'bpm', 'dawvert_bpm')


        # ----------------------------------------- zip -----------------------------------------

        zip_bio = io.BytesIO()
        zip_dp = zipfile.ZipFile(zip_bio, mode='w')
        zip_dp.writestr('project.xml', ET.tostring(x_project, encoding='unicode', method='xml'))
        zip_dp.writestr('metadata.xml', ET.tostring(x_metadata, encoding='unicode', method='xml'))
        zip_dp.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())

        outfile = ET.ElementTree(x_project)
        ET.indent(outfile)
        outfile.write('_test.xml', encoding='utf-8', xml_declaration = True)
        
        #outfile = ET.ElementTree(x_metadata)
        #ET.indent(outfile)
        #outfile.write('_test.xml', encoding='utf-8', xml_declaration = True)
        
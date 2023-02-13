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

class output_cvpj(plugin_output.base):
    def __init__(self): pass
    def getname(self): return 'DawProject'
    def is_dawvert_plugin(self): return 'output'
    def getshortname(self): return 'dawproject'
    def gettype(self): return 'r'
    def parse(self, convproj_json, output_file):
        global NoteStep
        global tracknum

        tracknum = 0

        projJ = json.loads(convproj_json)
        
        placements.lanefit(projJ)
        placements.removelanes(projJ)
        placements.split_single_notelist(projJ)
        placements.addwarps(projJ)
        
        cvpj_trackdata = projJ['track_data']
        cvpj_trackordering = projJ['track_order']

        x_project = ET.Element("Project")
        x_project.set('version', '0.1')

        x_metadata = ET.Element("MetaData")

        # ----------------------------------------- Application -----------------------------------------
        x_project_app = ET.SubElement(x_project, "Application")
        x_project_app.set('name', 'DawVert')

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
        x_project_tr_ts.set('id', 'dawvert_timesig')

        # ----------------------------------------- Structure -----------------------------------------
        x_str = ET.SubElement(x_project, "Structure")
        # ----------------------------------------- Arrangement -----------------------------------------

        x_project_arr = ET.SubElement(x_project, "Arrangement")
        x_project_arr.set('id', 'dawvert_arrangement')
        x_arr_lanes = ET.SubElement(x_project_arr, "Lanes")
        x_arr_lanes.set('timeUnit', 'beats')
        x_arr_lanes.set('id', 'x_arr_lanes')
        x_arr_markers = ET.SubElement(x_project_arr, "Markers")
        x_arr_markers.set('id', 'x_arr_markers')
        x_arr_tsa = ET.SubElement(x_project_arr, "TimeSignatureAutomation")
        x_arr_tsa.set('id', 'x_arr_tsa')
        x_arr_tsa_target = ET.SubElement(x_project_arr, "Target")
        x_arr_tsa.set('parameter', 'dawvert_timesig')

        # ----------------------------------------- Tracks -----------------------------------------

        for cvpj_trackentry in cvpj_trackordering:
            if cvpj_trackentry in cvpj_trackdata:
                s_trkdata = cvpj_trackdata[cvpj_trackentry]
                x_str_track = ET.SubElement(x_str, "Track")
                x_str_track.set('loaded', 'true')
                x_str_track.set('id', 'track_'+cvpj_trackentry)
                if 'color' in s_trkdata:
                    x_str_track.set('color', '#'+colors.rgb_float_2_hex(s_trkdata['color']))
                x_str_track.set('name', s_trkdata['name'])
                x_str_track_ch = ET.SubElement(x_str_track, "Channel")
                x_str_track_ch.set('audioChannels', '2')
                x_str_track_ch.set('destination', 'mastertrack_ch')
                x_str_track_ch.set('role', 'regular')
                x_str_track_ch.set('solo', 'false')
                x_str_track_ch.set('id', 'trackch_'+cvpj_trackentry)
                addvalue_bool(x_str_track_ch, 'Mute', 'false', cvpj_trackentry+'_mute', 'Mute')
                if 'pan' in s_trkdata: addvalue(x_str_track_ch, 'Pan', 1, -1, 'linear', s_trkdata['pan'], cvpj_trackentry+'_pan', 'Pan')
                if 'vol' in s_trkdata: addvalue(x_str_track_ch, 'Volume', 2, 0, 'linear', s_trkdata['vol'], cvpj_trackentry+'_vol', 'Volume')

                if s_trkdata['type'] == 'instrument':
                    x_str_track.set('contentType', 'notes')
                    if 'placements' in s_trkdata:
                        s_trkplacements = s_trkdata['placements']
                        x_arr_lanes_pl = ET.SubElement(x_arr_lanes, "Lanes")
                        x_arr_lanes_pl.set('track', 'track_'+cvpj_trackentry)
                        x_arr_lanes_pl.set('id', 'lanes_'+cvpj_trackentry)
                        x_arr_lanes_clips = ET.SubElement(x_arr_lanes_pl, "Clips")
                        x_arr_lanes_clips.set('id', 'clips_'+cvpj_trackentry)
                        for s_trkplacement in s_trkplacements:
                            x_arr_lanes_clip = ET.SubElement(x_arr_lanes_clips, "Clip")

                            if 'color' in s_trkplacement:
                                x_arr_lanes_clip.set('color', '#'+colors.rgb_float_2_hex(s_trkplacement['color']))

                            if 'name' in s_trkplacement:
                                x_arr_lanes_clip.set('name', s_trkplacement['name'])
                                
                            x_arr_lanes_clip.set('time', str(s_trkplacement['position']/4))

                            if 'cut' in s_trkplacement:
                                if s_trkplacement['cut']['type'] == 'cut':
                                    x_arr_lanes_clip.set('duration', str((s_trkplacement['cut']['end'] - s_trkplacement['cut']['start'])/4))
                                    x_arr_lanes_clip.set('playStart', str(s_trkplacement['cut']['start']/4))
                                if s_trkplacement['cut']['type'] == 'warp':
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
                                x_arr_lanes_clip_notes.set('id', 'notes'+str(nlidcount)+'_'+cvpj_trackentry)
                                for s_trknote in s_trknotelist:
                                    x_arr_lanes_clip_note = ET.SubElement(x_arr_lanes_clip_notes, "Note")
                                    x_arr_lanes_clip_note.set('time', str(s_trknote['position']/4))
                                    x_arr_lanes_clip_note.set('duration', str(s_trknote['duration']/4))
                                    x_arr_lanes_clip_note.set('key', str(s_trknote['key']+60))
                                    if 'vol' in s_trknote: x_arr_lanes_clip_note.set('vel', str(s_trknote['vol']))
                                nlidcount += 1

        # ----------------------------------------- Master -----------------------------------------
        x_str_master = ET.SubElement(x_str, "Track")
        x_str_master.set('contentType', 'audio notes')
        x_str_master.set('loaded', 'true')
        x_str_master.set('id', 'mastertrack')
        x_str_master.set('color', '#444444')
        x_str_master.set('name', 'Master')
        x_str_mas_ch = ET.SubElement(x_str_master, "Channel")
        x_str_mas_ch.set('audioChannels', '2')
        x_str_mas_ch.set('role', 'master')
        x_str_mas_ch.set('solo', 'false')
        x_str_mas_ch.set('id', 'mastertrack_ch')
        addvalue_bool(x_str_mas_ch, 'Mute', 'false', 'dawvert_master_mute', 'Mute')
        addvalue(x_str_mas_ch, 'Pan', 1, -1, 'linear', 0, 'dawvert_master_pan', 'Pan')
        addvalue(x_str_mas_ch, 'Volume', 2, 0, 'linear', 1, 'dawvert_master_vol', 'Volume')

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
                    prevvalue = None
                    bpm_auto = projJ['automation']['main']['bpm']
                    x_project_arr_tempo = ET.SubElement(x_project_arr, "TempoAutomation")
                    x_project_arr_tempo.set('unit', 'bpm')
                    x_project_arr_target = ET.SubElement(x_project_arr_tempo, "Target")
                    x_project_arr_target.set('parameter', 'dawvert_bpm')
                    for bpm_auto_pl in bpm_auto:
                        bpm_auto_pl_pos = bpm_auto_pl['position']
                        startpoint = True
                        for bpm_auto_poi in bpm_auto_pl['points']:
                            bpm_auto_poi['position'] += bpm_auto_pl_pos
                            #print(bpm_auto_poi)
                            instanttype = False
                            if 'type' in bpm_auto_poi:
                                if bpm_auto_poi['type'] == 'instant':
                                    instanttype = True

                            if (instanttype == True and prevvalue != None) or (startpoint == True and prevvalue != None):
                                x_project_arr_tpoint = ET.SubElement(x_project_arr_tempo, "RealPoint")
                                x_project_arr_tpoint.set('value', str(prevvalue))
                                x_project_arr_tpoint.set('interpolation', 'linear')
                                x_project_arr_tpoint.set('time', str(bpm_auto_poi['position']/4))

                            x_project_arr_tpoint = ET.SubElement(x_project_arr_tempo, "RealPoint")
                            x_project_arr_tpoint.set('value', str(bpm_auto_poi['value']))
                            x_project_arr_tpoint.set('interpolation', 'linear')
                            x_project_arr_tpoint.set('time', str(bpm_auto_poi['position']/4))

                            prevvalue = bpm_auto_poi['value']

                            startpoint = False


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
        
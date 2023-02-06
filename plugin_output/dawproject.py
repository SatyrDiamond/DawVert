# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import lxml.etree as ET
import mido
import io
import zipfile
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

unusedvalue = 0

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
        
        placements.removelanes(projJ)
        
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
        x_arr_tsa = ET.SubElement(x_project_arr, "TimeSignatureAutomation")

        # ----------------------------------------- Tracks -----------------------------------------

        for cvpj_trackentry in cvpj_trackordering:
            if cvpj_trackentry in cvpj_trackdata:
                s_trkdata = cvpj_trackdata[cvpj_trackentry]
                x_str_track = ET.SubElement(x_str, "Track")
                x_str_track.set('contentType', 'notes')
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
                addvalue(x_str_track_ch, 'Pan', 1, -1, 'linear', 0, cvpj_trackentry+'_pan', 'Pan')
                addvalue(x_str_track_ch, 'Volume', 2, 0, 'linear', 1, cvpj_trackentry+'_vol', 'Volume')

                if 'placements' in s_trkdata:
                    s_trkplacements = s_trkdata['placements']
                    x_arr_lanes_pl = ET.SubElement(x_arr_lanes, "Lanes")
                    x_arr_lanes_pl.set('track', 'track_'+cvpj_trackentry)
                    x_arr_lanes_pl.set('id', 'lanes_'+cvpj_trackentry)
                    x_arr_lanes_clips = ET.SubElement(x_arr_lanes_pl, "Clips")
                    x_arr_lanes_clips.set('id', 'clips_'+cvpj_trackentry)
                    for s_trkplacement in s_trkplacements:
                        x_arr_lanes_clip = ET.SubElement(x_arr_lanes_clips, "Clip")
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


        zip_bio = io.BytesIO()
        zip_dp = zipfile.ZipFile(zip_bio, mode='w')
        zip_dp.writestr('project.xml', ET.tostring(x_project, encoding='unicode', method='xml'))
        zip_dp.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())

        #outfile = ET.ElementTree(x_project)
        #ET.indent(outfile)
        #outfile.write('_test.xml', encoding='utf-8', xml_declaration = True)
        
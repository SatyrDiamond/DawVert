# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import tracks
from functions import note_data
from functions import song
import xml.etree.ElementTree as ET
import plugin_input
import json
import zipfile

as_pattern_color = {
    0: [0.07, 0.64, 0.86],
    1: [0.07, 0.84, 0.90],
    2: [0.05, 0.71, 0.56],
    3: [0.05, 0.69, 0.30],
    4: [0.64, 0.94, 0.22],
    5: [0.95, 0.79, 0.38],
    6: [0.95, 0.49, 0.32],
    7: [0.94, 0.25, 0.38],
    8: [0.93, 0.20, 0.70],
    9: [0.69, 0.06, 0.79],
}

def getvalue(xmltag, xmlname, fallbackval): 
    if xmltag.findall(xmlname) != []: return xmltag.findall(xmlname)[0].text.strip()
    else: return fallbackval

class input_audiosanua(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'audiosanua'
    def getname(self): return 'AudioSanua'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_warp': False,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        zip_data = zipfile.ZipFile(input_file, 'r')

        cvpj_l = {}

        songdataxml_filename = None

        t_audiosanua_project = zip_data.read('songdata.xml')

        x_proj = ET.fromstring(t_audiosanua_project)

        x_proj_channels = x_proj.findall('channels')[0]
        x_proj_tracks = x_proj.findall('tracks')[0]
        x_proj_songPatterns = x_proj.findall('songPatterns')[0]

        xt_chan = x_proj_channels.findall('channel')
        xt_track = x_proj_tracks.findall('track')
        xt_pattern = x_proj_songPatterns.findall('pattern')

        cvpj_plnotes = {}
        as_patt_notes = {}

        # ------------------------------------------ tracks ------------------------------------------
        for x_track in xt_track:
            x_track_trackIndex = int(x_track.get('trackIndex'))
            xt_track_seqNote = x_track.findall('seqNote')
            tracks.r_addtrack_inst(cvpj_l, 'audiosanua'+str(x_track_trackIndex), {})
            for x_track_seqNote in xt_track_seqNote:
                as_note_patternId = int(x_track_seqNote.get('patternId'))

                as_note_startTick = int(x_track_seqNote.get('startTick'))
                as_note_endTick = int(x_track_seqNote.get('endTick'))
                as_note_noteLength = int(x_track_seqNote.get('noteLength'))
                as_note_pitch = int(x_track_seqNote.get('pitch'))
                as_note_noteVolume = int(x_track_seqNote.get('noteVolume'))
                as_note_noteCutoff = int(x_track_seqNote.get('noteCutoff'))
                if as_note_patternId not in as_patt_notes: as_patt_notes[as_note_patternId] = []
                as_patt_notes[as_note_patternId].append(
                    [as_note_startTick, as_note_endTick, as_note_noteLength, as_note_pitch, as_note_noteVolume, as_note_noteCutoff]
                    )

        # ------------------------------------------ channels ------------------------------------------
        for x_chan in xt_chan:
            cvpj_tr_vol = int(x_chan.get('volume'))/100
            cvpj_tr_pan = int(x_chan.get('pan'))/100
            cvpj_tr_name = x_chan.get('name')
            as_channum = int(x_chan.get('channelNro'))
            tracks.r_addtrack_data(cvpj_l, 'audiosanua'+str(as_channum), cvpj_tr_name, None, cvpj_tr_vol, cvpj_tr_pan)
            
        # ------------------------------------------ patterns ------------------------------------------
        for x_pattern in xt_pattern:
            as_pattern_trackNro = int(x_pattern.get('trackNro'))
            as_pattern_patternId = int(x_pattern.get('patternId'))
            as_pattern_patternColor = int(x_pattern.get('patternColor'))
            as_pattern_startTick = int(x_pattern.get('startTick'))
            as_pattern_endTick = int(x_pattern.get('endTick'))
            as_pattern_patternLength = int(x_pattern.get('patternLength'))

            cvpj_pldata = {}
            cvpj_pldata["position"] = as_pattern_startTick/32
            cvpj_pldata["duration"] = (as_pattern_endTick-as_pattern_startTick)/32
            cvpj_pldata['cut'] = {'type': 'cut', 'start': 0, 'end': as_pattern_patternLength/32}
            cvpj_pldata['color'] = as_pattern_color[as_pattern_patternColor]
            cvpj_pldata['notelist'] = []

            if as_pattern_patternId in as_patt_notes:
                t_notelist = as_patt_notes[as_pattern_patternId]
                for t_note in t_notelist:
                    # as_note_startTick, as_note_endTick, as_note_noteLength, as_note_pitch, as_note_noteVolume, as_note_noteCutoff]
                    cvpj_note = note_data.rx_makenote((t_note[0]-as_pattern_startTick)/32, t_note[2]/32, t_note[3]-60, t_note[4]/100, None)
                    cvpj_note['cutoff'] = t_note[5]
                    cvpj_pldata['notelist'].append(cvpj_note)

            if as_pattern_trackNro not in cvpj_plnotes: cvpj_plnotes[as_pattern_trackNro] = []
            cvpj_plnotes[as_pattern_trackNro].append(cvpj_pldata)

        for tracknum in cvpj_plnotes:
            tracks.r_addtrackpl(cvpj_l, 'audiosanua'+str(tracknum), cvpj_plnotes[tracknum])

        as_loopstart = float(getvalue(x_proj, 'appLoopStart', 0))
        as_loopend = float(getvalue(x_proj, 'appLoopEnd', 0))
        if as_loopstart != 0 and as_loopend != 0:
            song.add_timemarker_looparea(cvpj_l, None, as_loopstart, as_loopend)

        if 'track_data' not in cvpj_l: 
            tracks.r_addtrack_inst(cvpj_l, 'audiosanua0', {})
            tracks.r_addtrackpl(cvpj_l, 'audiosanua0', [])

        cvpj_l['bpm'] = float(getvalue(x_proj, 'appTempo', 170))
        return json.dumps(cvpj_l)



# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import colors
from functions import tracks
from functions import note_data
from functions import folder_samples

import plugin_input
import json
import os
import zipfile

# -------------------------------------------- notes --------------------------------------------

def parse_clip_notes(j_wvtl_trackclip, j_wvtl_tracktype):
    #print(j_wvtl_trackclip)
    j_wvtl_trc_type = j_wvtl_trackclip['type']
    j_wvtl_trc_loopStart = j_wvtl_trackclip['loopStart']
    j_wvtl_trc_loopEnd = j_wvtl_trackclip['loopEnd']
    j_wvtl_trc_timelineStart = j_wvtl_trackclip['timelineStart']
    j_wvtl_trc_timelineEnd = j_wvtl_trackclip['timelineEnd']
    j_wvtl_trc_readStart = j_wvtl_trackclip['readStart']

    cvpj_notelist = []

    cvpj_pldata = {}
    if 'color' in j_wvtl_trackclip: cvpj_pldata["color"] = colors.hex_to_rgb_float(j_wvtl_trackclip['color'])
    if 'name' in j_wvtl_trackclip: cvpj_pldata["name"] = j_wvtl_trackclip['name']
    if 'fadeIn' in j_wvtl_trackclip: cvpj_pldata["fade_in"] = j_wvtl_trackclip['fadeIn']*4
    if 'fadeOut' in j_wvtl_trackclip: cvpj_pldata["fade_out"] = j_wvtl_trackclip['fadeOut']*4
    cvpj_pldata["position"] = j_wvtl_trc_timelineStart*4
    cvpj_pldata["duration"] = j_wvtl_trc_timelineEnd*4 - j_wvtl_trc_timelineStart*4
    cvpj_pldata['cut'] = {'type': 'warp', 'start': j_wvtl_trc_readStart*4, 'loopstart': j_wvtl_trc_loopStart*4, 'loopend': j_wvtl_trc_loopEnd*4}

    if j_wvtl_trc_type == 'MIDI':
        if 'notes' in j_wvtl_trackclip:
            for j_wvtl_n in j_wvtl_trackclip['notes']:
                cvpj_notelist.append(
                    note_data.rx_makenote(
                        j_wvtl_n['start']*4, 
                        j_wvtl_n['end']*4 - j_wvtl_n['start']*4, 
                        j_wvtl_n['pitch']-60, 
                        j_wvtl_n['velocity'], 
                        None))

    cvpj_pldata["notelist"] = cvpj_notelist
    return cvpj_pldata

# -------------------------------------------- audio --------------------------------------------

def extract_audio(audioname):
    audio_filename = None
    for s_file in zip_data.namelist():
        if audioname in s_file:
            audio_filename = samplefolder+s_file
            if os.path.exists(samplefolder+s_file) == False:
                zip_data.extract(s_file, path=samplefolder, pwd=None)
                break
    return audio_filename

def parse_clip_audio(j_wvtl_trackclip, j_wvtl_tracktype):
    #print(j_wvtl_trackclip)
    j_wvtl_trc_type = j_wvtl_trackclip['type']
    j_wvtl_trc_loopStart = j_wvtl_trackclip['loopStart']
    j_wvtl_trc_loopEnd = j_wvtl_trackclip['loopEnd']
    j_wvtl_trc_timelineStart = j_wvtl_trackclip['timelineStart']
    j_wvtl_trc_timelineEnd = j_wvtl_trackclip['timelineEnd']
    j_wvtl_trc_readStart = j_wvtl_trackclip['readStart']

    cvpj_pldata = {}
    if 'color' in j_wvtl_trackclip: cvpj_pldata["color"] = colors.hex_to_rgb_float(j_wvtl_trackclip['color'])
    if 'name' in j_wvtl_trackclip: cvpj_pldata["name"] = j_wvtl_trackclip['name']
    if 'fadeIn' in j_wvtl_trackclip: cvpj_pldata["fade_in"] = j_wvtl_trackclip['fadeIn']*4
    if 'fadeOut' in j_wvtl_trackclip: cvpj_pldata["fade_out"] = j_wvtl_trackclip['fadeOut']*4
    cvpj_pldata["position"] = j_wvtl_trc_timelineStart*4
    cvpj_pldata["duration"] = j_wvtl_trc_timelineEnd*4 - j_wvtl_trc_timelineStart*4
    cvpj_pldata['cut'] = {'type': 'warp', 'start': j_wvtl_trc_readStart*4, 'loopstart': j_wvtl_trc_loopStart*4, 'loopend': j_wvtl_trc_loopEnd*4}

    if 'audioBufferId' in j_wvtl_trackclip: 
        audio_filename = extract_audio(j_wvtl_trackclip['audioBufferId'])
        if audio_filename != None: cvpj_pldata["file"] = audio_filename

    return cvpj_pldata

# -------------------------------------------- track --------------------------------------------


def parse_track(j_wvtl_track):
    j_wvtl_tracktype = j_wvtl_track['type']
    j_wvtl_trackname = j_wvtl_track['name']
    j_wvtl_trackid = j_wvtl_track['id']
    j_wvtl_trackcolor = colors.hex_to_rgb_float(j_wvtl_track['color'])
    j_wvtl_trackclips = j_wvtl_track['clips']
    
    print('[input-wavtool] '+j_wvtl_tracktype+' Track: '+j_wvtl_trackname)

    if j_wvtl_tracktype == 'MIDI':
        tracks.r_addtrack_inst(cvpj_l, j_wvtl_trackid, {})
        tracks.r_addtrack_data(cvpj_l, j_wvtl_trackid, j_wvtl_trackname, j_wvtl_trackcolor, None, None)
        cvpj_placements = []
        for j_wvtl_trackclip in j_wvtl_trackclips:
            cvpj_placements.append(parse_clip_notes(j_wvtl_trackclip, j_wvtl_tracktype))
        tracks.r_addtrackpl(cvpj_l, j_wvtl_trackid, cvpj_placements)

    if j_wvtl_tracktype == 'Audio':
        tracks.r_addtrack_audio(cvpj_l, j_wvtl_trackid, {})
        tracks.r_addtrack_data(cvpj_l, j_wvtl_trackid, j_wvtl_trackname, j_wvtl_trackcolor, None, None)
        cvpj_placements = []
        for j_wvtl_trackclip in j_wvtl_trackclips:
            cvpj_placements.append(parse_clip_audio(j_wvtl_trackclip, j_wvtl_tracktype))
        tracks.r_addtrackpl_audio(cvpj_l, j_wvtl_trackid, cvpj_placements)

# -------------------------------------------- main --------------------------------------------

class input_cvpj_f(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'wavtool'
    def getname(self): return 'wavtool'
    def gettype(self): return 'r'
    def getdawcapabilities(self): 
        return {
        'fxrack': False,
        'r_track_lanes': False,
        'placement_cut': True,
        'placement_warp': True,
        'no_placements': False
        }
    def supported_autodetect(self): return False
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(12)
        if bytesdata == b'CONVPROJ___M': return True
        else: return False
    def parse(self, input_file, extra_param):
        global cvpj_l
        global samplefolder
        global zip_data

        cvpj_l = {}

        zip_data = zipfile.ZipFile(input_file, 'r')

        json_filename = None

        file_name = os.path.splitext(os.path.basename(input_file))[0]
        samplefolder = folder_samples.samplefolder(extra_param, file_name)

        for jsonname in zip_data.namelist():
            if '.json' in jsonname:
                json_filename = jsonname

        t_wavtool_project = zip_data.read(json_filename)
        j_wvtl_project = json.loads(t_wavtool_project)
        #print(j_wvtl_project)

        with open('testout.json', "w") as fileout:
            json.dump(j_wvtl_project, fileout, indent=4, sort_keys=True)

        j_wvtl_bpm = j_wvtl_project['bpm']
        j_wvtl_beatDenominator = j_wvtl_project['beatDenominator']
        j_wvtl_beatNumerator = j_wvtl_project['beatNumerator']
        j_wvtl_tracks = j_wvtl_project['tracks']
        for j_wvtl_track in j_wvtl_tracks:
            parse_track(j_wvtl_track)

        cvpj_l['use_fxrack'] = False

        cvpj_l['timesig_numerator'] = j_wvtl_beatNumerator
        cvpj_l['timesig_denominator'] = j_wvtl_beatDenominator
        cvpj_l['bpm'] = j_wvtl_bpm
        return json.dumps(cvpj_l)


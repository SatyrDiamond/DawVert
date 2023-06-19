# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import colors
from functions import note_data
import plugin_input
import struct
import json


def parse_clip_notes(sndstat_clip):
    cvpj_notelist = []
    ticksdiv = 5168
    sndstat_clip_position = sndstat_clip['position']/ticksdiv
    sndstat_clip_duration = sndstat_clip['length']/ticksdiv
    sndstat_clip_start = sndstat_clip['contentPosition']/ticksdiv
    sndstat_clip_loopcount = sndstat_clip['loopcount']

    sndstat_clip_loopduration = sndstat_clip_duration*sndstat_clip_loopcount

    if sndstat_clip_start < 0: sndstat_clip_start += sndstat_clip_duration

    cvpj_pldata = {}
    if 'color' in sndstat_clip: 
        if isinstance(sndstat_clip['color'],str): 
            clipcolor = colors.hex_to_rgb_float(sndstat_clip['color'])
        else: 
            clipcolor = struct.unpack("4B", struct.pack("i", sndstat_clip["color"]))
            print(clipcolor)
            clipcolor = [clipcolor[2]/255, clipcolor[1]/255, clipcolor[0]/255]
            clipcolor = colors.darker(clipcolor, 0.3)

        cvpj_pldata["color"] = clipcolor

    cvpj_pldata["position"] = sndstat_clip_position
    cvpj_pldata["duration"] = sndstat_clip_loopduration
    cvpj_pldata['cut'] = {'type': 'loop', 'start': sndstat_clip_start, 'loopstart': 0, 'loopend': sndstat_clip_duration}

    for sndstat_note in sndstat_clip['notes']:
        cvpj_notelist.append( note_data.rx_makenote(sndstat_note['position']/ticksdiv, sndstat_note['length']/ticksdiv, sndstat_note['note']-60, sndstat_note['velocity'], None) )

    cvpj_pldata["notelist"] = cvpj_notelist
    return cvpj_pldata

class input_soundation(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'soundation'
    def getname(self): return 'Soundation'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'placement_loop': True
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)

        cvpj_l = {}

        timeSignaturesplit = sndstat_data['timeSignature'].split('/')
        cvpj_l['timesig_numerator'] = int(timeSignaturesplit[0])
        cvpj_l['timesig_denominator'] = int(timeSignaturesplit[1])
        cvpj_l['bpm'] = sndstat_data['bpm']
        sndstat_chans = sndstat_data['channels']

        tracknum = 0
        for sndstat_chan in sndstat_chans:

            tracknum_hue = (tracknum/-11) - 0.2
            tracknum += 1
            sound_chan_type = sndstat_chan['type']
            trackid = 'soundation'+str(tracknum)
            trackcolor = colors.hsv_to_rgb(tracknum_hue, 0.7, 0.7)
            if sound_chan_type == 'instrument':
                tracks.r_create_inst(cvpj_l, trackid, {})
                tracks.r_basicdata(cvpj_l, trackid, sndstat_chan['name'], [trackcolor[0], trackcolor[1], trackcolor[2]], sndstat_chan['volume'], (sndstat_chan['pan']-0.5)*2)
                tracks.r_param(cvpj_l, trackid, 'enabled', int(not sndstat_chan['mute']))
                tracks.r_param(cvpj_l, trackid, 'solo', int(sndstat_chan['solo']))
                for sndstat_region in sndstat_chan['regions']:
                    tracks.r_pl_notes(cvpj_l, trackid, parse_clip_notes(sndstat_region))

        return json.dumps(cvpj_l)

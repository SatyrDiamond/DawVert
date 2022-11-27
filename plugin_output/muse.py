# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import lxml.etree as ET
import json
from math import sqrt

muse_colors = (
    (255, 0, 0, 1),
    (0, 255, 0, 2),
    (0, 0, 255, 3),
    (255, 255, 0, 4),
    (0, 255, 255, 5),
    (255, 0, 255, 6),
    (159, 199, 239, 7),
    (0, 255, 127, 8),
    (127, 0, 0, 9),
    (0, 127, 0, 10),
    (0, 0, 127, 11),
    (127, 127, 63, 12),
    (0, 127, 127, 13),
    (127, 0, 127, 14),
    (0, 127, 255, 15),
    (0, 63, 63, 16),
    (170, 85, 0, 17),
)

def closest_color(rgb):
    r, g, b = rgb
    color_diffs = []
    for color in muse_colors:
        red, green, blue, cid = color
        color_diff = sqrt((r - red)**2 + (g - green)**2 + (b - blue)**2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def musexml_addvalue(xmltag, name, value):
    insideX = ET.SubElement(xmltag, name)
    insideX.text = value

def m_i(value):
    global ppq
    return int(value * ppq)

class output_muse(plugin_output.base):
    def __init__(self):
        pass

    def getname(self):
        return 'MusE'

    def getshortname(self):
        return 'muse'

    def getcvpjtype(self):
        return 'single'

    def parse(self, convproj_json, output_file):
        print('[output-muse] Output Start')
        projJ = json.loads(convproj_json)

        global ppq
        ppq = 384
        
        projX = ET.Element("muse")
        projX.set('version', "3.3")
        songX = ET.SubElement(projX, "song")
        musexml_addvalue(songX, 'info', '')
        musexml_addvalue(songX, 'showinfo', '0')
        musexml_addvalue(songX, 'cpos', '0')
        musexml_addvalue(songX, 'rpos', '0')
        musexml_addvalue(songX, 'lpos', '0')
        musexml_addvalue(songX, 'loop', '0')
        musexml_addvalue(songX, 'punchin', '0')
        musexml_addvalue(songX, 'punchout', '0')
        musexml_addvalue(songX, 'record', '0')
        musexml_addvalue(songX, 'solo', '0')
        musexml_addvalue(songX, 'recmode', '0')
        musexml_addvalue(songX, 'cycle', '0')
        musexml_addvalue(songX, 'click', '0')
        musexml_addvalue(songX, 'quantize', '0')
        musexml_addvalue(songX, 'follow', '1')
        musexml_addvalue(songX, 'midiDivision', str(ppq))
        musexml_addvalue(songX, 'sampleRate', '44100')
        
        for trackJ in projJ['tracks']:
            if trackJ['type'] == 'instrument':
                printcountplace = 0
                print('[output-muse] Instrument Track Name: ' + trackJ['name'])
                trackX = ET.SubElement(songX, "miditrack")
                if 'name' in trackJ: musexml_addvalue(trackX, 'name', trackJ['name'])
                if 'color' in trackJ:
                    color = trackJ['color']
                    musexml_addvalue(trackX, 'color', '#' + rgb_to_hex((int(color[0]*255),int(color[1]*255),int(color[2]*255))))
                for placementJ in trackJ['placements']:
                    printcountplace += 1
                    print('[output-muse] └──── Placement ' + str(printcountplace) + ': ', end='')
                    notecut_start = 0
                    notecut_end = None
                    if 'notecut' in placementJ:
                        notecut_start = m_i(placementJ['notecut']['start'])
                        notecut_end = m_i( placementJ['notecut']['end'])
                        track_duration = notecut_end - notecut_start
                    else:
                        track_duration = m_i(placementJ['duration'])
                    partX = ET.SubElement(trackX, "part")
                    if 'color' in placementJ:
                        color = placementJ['color']
                        if 'color' in trackJ:
                            if trackJ['color'] != placementJ['color']:
                                closestcolor = closest_color((int(color[0]*255),int(color[1]*255),int(color[2]*255)))
                                musexml_addvalue(partX, 'color', str(closestcolor[3]))
                        else:
                            closestcolor = closest_color((int(color[0]*255),int(color[1]*255),int(color[2]*255)))
                            musexml_addvalue(partX, 'color', str(closestcolor[3]))
                    track_posbase = m_i(placementJ['position'])
                    poslenX = ET.SubElement(partX, 'poslen')
                    poslenX.set('tick', str(track_posbase))
                    poslenX.set('len', str(track_duration))
                    notelist = placementJ['notelist']
                    print('Notes:', end=' ')
                    printcountpat = 0
                    for note in notelist:
                        eventX = ET.SubElement(partX, "event")
                        note_duration = m_i(note['duration'])
                        note_key = note['key']
                        note_vol = note['vol']
                        note_position = m_i(note['position']) - notecut_start
                        note_posbase = track_posbase + note_position
                        eventX.set('tick', str(note_posbase))
                        eventX.set('len', str(note_duration))
                        eventX.set('a', str(note_key + 84))
                        eventX.set('b', str(int(note_vol*127)))
                        printcountpat += 1
                        print(str(printcountpat), end=' ')
                    print(' ')
        
        outfile = ET.ElementTree(projX)
        ET.indent(outfile)
        outfile.write(output_file, encoding='utf-8')
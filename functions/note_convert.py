# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from functions import note_mod

global ActiveNotes
global position_global
global position_notelist
global output_noteslist
global placements
global currentplacement
global note_pan
global usedinstruments
#ActiveNotes: Position,Duration,Note,velocity,program,extra
ActiveNotes = []
usedinstruments = []
placements = []
output_noteslist = []
position_global = 0
position_notelist = 0

def timednotes2notelist_note_on(key, velocity, program, extra):
    ActiveNotes.append([position_notelist,0,int(key),velocity, program, extra])

def timednotes2notelist_rest(duration):
    global ActiveNotes
    global position_global
    position_global += float(duration)
    global position_notelist
    position_notelist += float(duration)
    for ActiveNote in ActiveNotes:
        ActiveNote[1] = ActiveNote[1] + float(duration)

def timednotes2notelist_note_off(key):
    global ActiveNotes
    global note_pan
    ActiveNoteTablePos = 0
    ActiveNoteFound = 0
    NumActiveNotes = len(ActiveNotes)
    while ActiveNoteTablePos < NumActiveNotes and ActiveNoteFound == 0:
        if ActiveNotes[ActiveNoteTablePos][2] == key:
            ActiveNoteFound = 1
            FoundNote = ActiveNotes.pop(ActiveNoteTablePos)
            notejson = {}
            notejson['position'] = float(FoundNote[0])
            notejson['key'] = int(FoundNote[2])
            notejson['duration'] = float(FoundNote[1])
            notejson['vol'] = FoundNote[3]
            notejson['instrument'] = FoundNote[4]
            if 'pan' in FoundNote[5]: notejson['pan'] = FoundNote[5]['pan']
            output_noteslist.append(notejson)
        ActiveNoteTablePos += 1

def timednotes2notelistplacement_parse_timednotes(TimedNotesTable, startstr):
    print("[note-conv] tn2np: " + str(len(TimedNotesTable)) + ' cmds', end='')
    global ActiveNotes
    currentprogram = 0
    ActiveNotes = []
    output_noteslist = []
    extrajson = {}
    numnotecmds = 0
    #ActiveNotes: Position,Duration,Note,ExtraVars
    timednotes2notelistplacement_placement_start()
    for TimedNote in TimedNotesTable:
        TimedNoteLineSplit = TimedNote.split(';')
        TimedNoteCommand = TimedNoteLineSplit[0]
        TimedNoteValues = TimedNoteLineSplit[1].split(',')
        TimedNoteValuesFirst = TimedNoteValues[0]
        if len(TimedNoteValues) == 2:
            TimedNoteValuesSecond = TimedNoteValues[1]
        else:
            TimedNoteValuesSecond = None
        if TimedNoteCommand == 'note_on':
            timednotes2notelist_note_on(int(TimedNoteValuesFirst), float(TimedNoteValuesSecond), currentprogram, extrajson)
            numnotecmds += 1
        if TimedNoteCommand == 'note_off':
            timednotes2notelist_note_off(int(TimedNoteValuesFirst))
            numnotecmds += 1
        if TimedNoteCommand == 'break':
            timednotes2notelist_rest(float(TimedNoteValuesFirst))
        if TimedNoteCommand == 'seperate':
            timednotes2notelistplacement_placement_end()
            timednotes2notelistplacement_placement_start()
        if TimedNoteCommand == 'seperate_safe' and ActiveNotes == []:
            timednotes2notelistplacement_placement_end()
            timednotes2notelistplacement_placement_start()
        if TimedNoteCommand == 'instrument':
            numnotecmds += 1
            currentprogram = startstr + TimedNoteValuesFirst
            if currentprogram not in usedinstruments: usedinstruments.append(currentprogram)
        if TimedNoteCommand == 'pan':
            numnotecmds += 1
            extrajson['pan'] = TimedNoteValues[0]
    timednotes2notelistplacement_placement_end()
    print(', ' + str(numnotecmds) + ' notecmds', end='')
    print(', ' + str(len(placements)) + ' placements')
    return placements

def timednotes2notelist_note_off_all():
    global ActiveNotes
    for ActiveNote in ActiveNotes:
        timednotes2notelist_note_off(ActiveNote[2])

def timednotes2notelist_get_used_instruments():
    return usedinstruments

def timednotes2notelistplacement_track_start():
    global placements
    global position_global
    global position_notelist
    global usedinstruments
    placements = []
    ActiveNotes = []
    usedinstruments = []
    position_global = 0
    position_notelist = 0

def timednotes2notelistplacement_placement_start():
    global currentplacement
    global position_global
    global position_notelist
    currentplacement = {}
    position_notelist = 0
    currentplacement['position'] = position_global

def timednotes2notelistplacement_placement_end():
    global currentplacement
    global output_noteslist
    global placements
    global ActiveNotes
    global position_notelist
    timednotes2notelist_note_off_all()
    currentplacement['type'] = "instruments"
    currentplacement['duration'] = position_notelist
    if output_noteslist != []:
        currentplacement['notelist'] = note_mod.sortnotes(output_noteslist)
        placements.append(currentplacement)
    ActiveNotes = []
    output_noteslist = []

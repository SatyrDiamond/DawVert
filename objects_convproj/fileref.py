# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import av
import os
import sys
import getpass

from objects_convproj import visual

username = getpass.getuser()

os_path = 'unix' if sys.platform != 'win32' else 'win'

class cvpj_fileref:
    __slots__ = ['os_type','filepath','relative','basename','filename','extension','win_drive']

    def __init__(self, in_path):
        self.os_type = None
        self.win_drive = None
        self.filepath = []
        self.basename = None
        self.filename = None
        self.extension = ''
        self.relative = False
        self.change_path(in_path)

    def change_path(self, in_path):
        splitpath = in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

        iswindowspath = False
        if len(splitpath[0]) == 2:
            if splitpath[0][1] == ':': iswindowspath = True

        self.relative = False
        if iswindowspath:
            self.os_type = 'win'
            self.win_drive = splitpath[0][0]
            self.filepath = splitpath[1:]
        elif splitpath[0] == '': 
            self.os_type = 'unix'
            self.filepath = splitpath[1:] if len(splitpath) != 1 else []
        else:
            self.relative = True
            self.filepath = splitpath

        self.basename = splitpath[-1]
        filenamesplit = self.basename.split('.', 1)
        self.filename = filenamesplit[0]

        if self.filepath:
            if self.filepath[0] == '.': del self.filepath[0]

        if len(filenamesplit) > 1: self.extension = filenamesplit[1]

    def find_relative(self, in_folder):
        if self.relative:
            filepath = self.get_path(None, True)
            fullpath = in_folder+'\\'+filepath
            if os.path.exists(fullpath):
                print('[fileref] relative found: '+in_folder+' | '+filepath)
                self.change_path(fullpath)
                return True
            return False
        return False

    def get_path(self, os_type, absolute):
        if os_type not in ['unix', 'win']: os_type = os_path
        if self.relative == False:
            if self.filepath:
                if self.os_type == 'win':
                    if os_type == 'win': return self.win_drive+':\\'+'\\'.join(self.filepath)
                    if os_type == 'unix': return '/home/'+username+'/.wine/drive_'+self.win_drive.lower()+'/'+'/'.join(self.filepath)
                if self.os_type == 'unix':
                    if os_type == 'win': return 'Z:\\'+'\\'.join(self.filepath)
                    if os_type == 'unix': return '/'+'/'.join(self.filepath)
            else:
                return ''
        else:
            if os_type == 'win': return '\\'.join(self.filepath)
            elif os_type == 'unix': return '/'.join(self.filepath)

class cvpj_sampleref:
    __slots__ = ['fileref','dur_samples','dur_sec','timebase','hz','channels','found','file_size','file_date', 'visual']

    def __init__(self, in_path):
        self.fileref = cvpj_fileref(in_path)
        self.found = False
        self.dur_samples = 0
        self.dur_sec = 1
        self.timebase = 44100
        self.hz = 44100
        self.channels = 1
        self.file_size = 0
        self.file_date = 0
        self.visual = visual.cvpj_visual()

        self.get_info()
        
    def get_info(self):
        wav_realpath = self.fileref.get_path(os_path, None)
        if os.path.exists(wav_realpath):

            self.file_size = os.path.getsize(wav_realpath)
            self.file_date = int(os.path.getmtime(wav_realpath))

            if self.fileref.extension.lower() in ['wav', 'mp3', 'flac', 'ogg']:
                self.found = True

                self.visual.name = self.fileref.filename
                avdata = av.open(wav_realpath)
                if len(avdata.streams.audio) != 0:
                    self.dur_samples = avdata.streams.audio[0].duration
                    self.timebase = avdata.streams.audio[0].time_base.denominator
                    audio_hz_b = avdata.streams.audio[0].rate
                    if audio_hz_b != None: self.hz = audio_hz_b
                    self.dur_sec = (self.dur_samples/self.timebase)
                    self.channels = avdata.streams.audio[0].channels

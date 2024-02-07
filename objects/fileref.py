# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_fileref:
    __slots__ = ['os_type','filepath','relative','basename','filename','extension','win_drive']

    def __init__(self, in_path):
        splitpath = in_path.replace('/', '\\').replace('\\\\', '\\').split('\\')

        iswindowspath = False
        if len(splitpath[0]) == 2:
            if splitpath[0][1] == ':': iswindowspath = True

        self.os_type = None
        self.win_drive = None
        self.filepath = []
        self.basename = None
        self.filename = None
        self.extension = ''
        self.filepath = splitpath

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

        self.basename = splitpath[-1]
        filenamesplit = self.basename.split('.', 1)
        self.filename = filenamesplit[0]
        if len(filenamesplit) > 1: self.extension = filenamesplit[1]

        print(
            self.relative, self.os_type, self.filepath, 
            self.filename, self.win_drive, self.extension)


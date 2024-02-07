# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_visual_ui:
    def __init__(self):
        self.height = 1

class cvpj_visual:
    __slots__ = ['name','color']
    def __init__(self):
        self.name = None
        self.color = None

    def add(self, v_name, v_color):
        if v_name != None: self.name = v_name
        if v_color != None: self.color = v_color

class cvpj_metadata:
    def __init__(self):
        self.name = ''
        self.author = ''
        self.original_author = ''
        self.comment_text = ''
        self.comment_datatype = 'text'
        self.url = ''
        self.genre = ''
        self.t_seconds = -1
        self.t_minutes = -1
        self.t_hours = -1
        self.t_day = -1
        self.t_month = -1
        self.t_year = -1
        self.email = ''

class cvpj_window_data:
    __slots__ = ['pos_x','pos_y','size_x','size_y','open','detatched','maximized','minimized']
    def __init__(self):
        self.pos_x = -1
        self.pos_y = -1
        self.size_x = -1
        self.size_y = -1
        self.open = -1
        self.maximized = -1
        self.minimized = -1
        self.detatched = -1

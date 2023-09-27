# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

author = None
titlefound = True
from functions import song

def getinfo(cvpj_l, textin):
    global author
    global titlefound
    # ------------------------ copyright + year ------------------------
    copyrightdatefound = False
    for copyrightstring in ['(c)','(C)','©','copyright','Copyright','Copyright (C)']:
        if copyrightstring in textin:
            copyrightpart = textin.split(copyrightstring, 1)
            break

    if 'Composed by' in textin:
        authorpart = textin.split('Composed by', 1)
        if len(authorpart) != 1: author = authorpart[1]
    if 'by ' in textin:
        authorpart = textin.split('by ', 1)
        if len(authorpart) != 1: author = authorpart[1]
    if 'By ' in textin:
        authorpart = textin.split('By ', 1)
        if len(authorpart) != 1: author = authorpart[1]

    if copyrightdatefound == True:
        copyrightmsg_len = len(copyrightpart)
        if copyrightmsg_len >= 2:
            copyrightisyear = copyrightpart[1].lstrip().split(' ', 1)
            if copyrightisyear[0].isnumeric() == True:
                song.add_info(cvpj_l, 'year', int(copyrightisyear[0]))
                if len(copyrightisyear) == 2: song.add_info(cvpj_l, 'author', copyrightisyear[1])
            else:
                song.add_info(cvpj_l, 'author', copyrightisyear[0])

    # ------------------------ URL ------------------------
    if 'http://' in textin:
        urlparts = textin.split('"')
        for urlpart in urlparts:
            if 'http://' in urlpart: song.add_info(cvpj_l, 'url', urlpart)

    # ------------------------ title ------------------------
    if textin.count('"') == 2 and titlefound == False:
        titlefound = True
        song.add_info(cvpj_l, 'title', textin.split('"')[1::2][0])

    # ------------------------ email ------------------------
    if '.' in textin and '@' in textin:
        emailparts = textin.split('"')
        for emailpart in emailparts:
            if '.' in emailpart and '@' in emailpart: song.add_info(cvpj_l, 'email', emailpart)

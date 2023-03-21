# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get_lower_tempo(i_tempo, i_notelen, maxtempo):
    while i_tempo > maxtempo:
        i_tempo = i_tempo/2
        i_notelen = i_notelen/2
    return (i_tempo, i_notelen)
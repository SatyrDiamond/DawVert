# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import av
import os
import configparser
from os.path import exists
from tinydb import TinyDB, Query

audioinfo_cache_filepath = './__config/cache_audioinfo.db'
db = TinyDB(audioinfo_cache_filepath)
samplesdb = Query()

def get_audiofile_info(sample_filename):
    audio_path = ''
    audio_filesize = 0
    audio_moddate = 0
    audio_duration = 5
    audio_timebase = 44100
    audio_hz = 44100

    db_searchfound = db.search(samplesdb.path == sample_filename)

    out_data = {}
    out_data['path'] = sample_filename
    out_data['file_size'] = 0
    out_data['mod_date'] = 0
    out_data['dur'] = 1
    out_data['crc'] = 0
    out_data['audio_timebase'] = 44100
    out_data['rate'] = 44100
    out_data['dur_sec'] = 1

    if db_searchfound != []:
        out_data = db_searchfound[0]

    elif os.path.exists(sample_filename):
        avdata = av.open(sample_filename)
        audio_path = sample_filename
        audio_filesize = os.path.getsize(sample_filename)
        audio_moddate = int(os.path.getmtime(sample_filename))
        if len(avdata.streams.audio) != 0:
            audio_duration = avdata.streams.audio[0].duration
            audio_timebase = avdata.streams.audio[0].time_base.denominator
            audio_hz_b = avdata.streams.audio[0].rate
            if audio_hz_b != None: audio_hz = audio_hz_b

            if db.search(samplesdb.path == audio_path) == []:
                out_db_data = {}
                out_db_data['path'] = audio_path
                out_db_data['file_size'] = audio_filesize
                out_db_data['mod_date'] = audio_moddate
                out_db_data['dur'] = audio_duration
                out_db_data['crc'] = 0
                out_db_data['audio_timebase'] = audio_timebase
                out_db_data['rate'] = audio_hz
                out_db_data['dur_sec'] = (audio_duration/audio_timebase)
                db.insert(out_db_data)
                out_data = out_db_data

    return out_data

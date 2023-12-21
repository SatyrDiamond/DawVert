# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import av
from tinydb import TinyDB, Query
from io import BytesIO

os.makedirs(os.getcwd() + '/__config/', exist_ok=True)
audioinfo_cache_filepath = './__config/cache_audioinfo.db'
db = TinyDB(audioinfo_cache_filepath)
samplesdb = Query()

def get_audiofile_info(sample_filename):
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

    if db_searchfound:
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

            if audio_duration == None: audio_duration = 1
            if not db.search(samplesdb.path == audio_path):
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

def get_audiofile_info_nocache(sample_filename):
    audio_hz = 44100

    out_data = {}
    out_data['path'] = sample_filename
    out_data['file_size'] = 0
    out_data['mod_date'] = 0
    out_data['dur'] = 1
    out_data['crc'] = 0
    out_data['audio_timebase'] = 44100
    out_data['rate'] = 44100
    out_data['dur_sec'] = 1
    out_data['found'] = False

    if os.path.exists(sample_filename):
        avdata = av.open(sample_filename)
        audio_path = sample_filename
        audio_filesize = os.path.getsize(sample_filename)
        audio_moddate = int(os.path.getmtime(sample_filename))
        if len(avdata.streams.audio) != 0:
            audio_duration = avdata.streams.audio[0].duration
            audio_timebase = avdata.streams.audio[0].time_base.denominator
            audio_hz_b = avdata.streams.audio[0].rate
            if audio_hz_b != None: audio_hz = audio_hz_b

            out_db_data = {}
            out_db_data['path'] = audio_path
            out_db_data['file_size'] = audio_filesize
            out_db_data['mod_date'] = audio_moddate
            out_db_data['dur'] = audio_duration
            out_db_data['crc'] = 0
            out_db_data['audio_timebase'] = audio_timebase
            out_db_data['rate'] = audio_hz
            out_db_data['dur_sec'] = (audio_duration/audio_timebase)
            out_db_data['found'] = True
            out_data = out_db_data

    return out_data

def convert_to_wav(filepath):
    container = av.open(filepath, 'r')
    for stream in container.streams:
        if stream.type == 'audio':
            audio_stream = stream
            break
    if audio_stream:
        print('[audio] Converting', filepath)
        outdata = BytesIO()
        out_container = av.open(outdata, 'w', format='wav')
        out_stream = out_container.add_stream(codec_name='pcm_s16le', rate=44100)
        for i, frame in enumerate(container.decode(audio_stream)):
            for packet in out_stream.encode(frame):
                out_container.mux(packet)
        for packet in out_stream.encode(None):
            out_container.mux(packet)
        out_container.close()
        return outdata.getvalue()
    else:
        return b''
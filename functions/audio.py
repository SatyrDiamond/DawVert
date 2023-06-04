# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import av
import os

def get_audiofile_info(sample_filename):
    audio_path = ''
    audio_filesize = 0
    audio_crc = 0
    audio_moddate = 0
    audio_duration = 0
    audio_timebase = 44100
    audio_hz = 44100

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

    out_data = {}
    out_data['path'] = audio_path
    out_data['file_size'] = audio_filesize
    out_data['crc'] = audio_crc
    out_data['mod_date'] = audio_moddate
    out_data['dur'] = audio_duration
    out_data['audio_timebase'] = audio_timebase
    out_data['rate'] = audio_hz
    out_data['dur_sec'] = (audio_duration/audio_timebase)
    return out_data

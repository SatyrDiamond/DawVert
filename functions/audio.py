# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import av
import os

def get_audiofile_info(sample_filename):
    RelativePath = ''
    FilePath = ''
    OriginalFileSize = 0
    OriginalCrc = 0
    LastModDate = 0
    DefaultDuration = 0
    TimeBase = 44100
    DefaultSampleRate = 44100

    if os.path.exists(sample_filename):
        avdata = av.open(sample_filename)
        FilePath = sample_filename
        OriginalFileSize = os.path.getsize(sample_filename)
        LastModDate = int(os.path.getmtime(sample_filename))
        if len(avdata.streams.audio) != 0:
            DefaultDuration = avdata.streams.audio[0].duration
            TimeBase = avdata.streams.audio[0].time_base.denominator
            DefaultSampleRate_b = avdata.streams.audio[0].rate
            if DefaultSampleRate_b != None: DefaultSampleRate = DefaultSampleRate_b

    out_data = {}
    out_data['path'] = FilePath
    out_data['file_size'] = OriginalFileSize
    out_data['crc'] = OriginalCrc
    out_data['mod_date'] = LastModDate
    out_data['dur'] = DefaultDuration
    out_data['timebase'] = TimeBase
    out_data['rate'] = DefaultSampleRate
    out_data['dur_sec'] = (DefaultDuration/TimeBase)
    return out_data

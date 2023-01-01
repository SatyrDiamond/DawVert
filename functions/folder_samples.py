# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import os

def samplefolder(extra_param, songname):
    if 'samplefolder' in extra_param:
        samplefolder = extra_param['samplefolder'] + '/' + songname + '/'
    else:
        samplefolder = os.getcwd() + '/extracted_samples/' + songname + '/'
        os.makedirs(os.getcwd() + '/extracted_samples/', exist_ok=True)
    os.makedirs(samplefolder, exist_ok=True)
    return samplefolder
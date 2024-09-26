#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from plugins import base as dv_plugins
from objects import audio_data

dv_plugins.load_plugindir('audiocodecs', '')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-ot", default=None)
parser.add_argument("-o", default=None)
args = parser.parse_args()

in_file = args.i
out_file = args.o
out_format = args.ot

file_obj = open(in_file, 'rb')
ofile_obj = open(out_file, 'wb')

audio_obj = audio_data.audio_obj()
audio_obj.set_codec('int16')
audio_obj.pcm_from_bytes(file_obj.read())
ofile_obj.write( audio_obj.encode_to_codec(out_format) )


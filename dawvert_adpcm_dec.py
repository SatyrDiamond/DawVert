#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from plugins import base as dv_plugins
from objects import audio_data

dv_plugins.load_plugindir('audiocodecs', '')

parser = argparse.ArgumentParser()
parser.add_argument("-i", default=None)
parser.add_argument("-it", default=None)
parser.add_argument("-o", default=None)
args = parser.parse_args()

in_file = args.i
out_file = args.o
in_format = args.it

file_obj = open(in_file, 'rb')

audio_obj = audio_data.audio_obj()
audio_obj.decode_from_codec(in_format, file_obj.read())
audio_obj.to_file_wav(out_file)


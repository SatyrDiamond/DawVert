# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def calc_channum(i_chan, i_port, numchans):
	return (i_chan)+(i_port*numchans)

def split_channum(i_val, numchans):
	return i_val//numchans, (i_val%numchans)

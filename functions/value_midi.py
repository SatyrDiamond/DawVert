# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def midiid_to_num(i_bank, i_patch, i_isdrum, i_iskey): 
	return i_bank*256 + i_patch + int(i_isdrum)<<8 + int(i_iskey)<<16

def midiid_from_num(value): 
	v_isdrum = int(bool(value&0b10000000))
	v_iskey = int(bool((value>>8)&0b10000000))
	v_patch = (value%128)
	v_bank = (value>>8)
	return v_bank, v_patch, v_isdrum, v_iskey


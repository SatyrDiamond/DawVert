# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes

def decode(model, device, command, data):
	groups = [None, None]
	nameval = [None, None]
	isdatadump = False

	nameval[1] = data

	devicename = 'universal'

	if model == 3:
		groups[0] = 'notation'
		if command == 1: nameval[0] = 'bar_number'
		if command == 2: nameval[0] = 'time_signature_immediate'
		if command == 66: nameval[0] = 'time_signature_delayed'

	if model == 4:
		groups[0] = 'device'
		if command == 1: nameval[0] = 'master_volume'
		if command == 2: nameval[0] = 'master_pan'
		if command == 3: nameval[0] = 'master_fune_tune'
		if command == 4: nameval[0] = 'master_coarse_tuning'
		if command == 5: nameval[0] = 'global_param_control'

	return devicename, groups, nameval
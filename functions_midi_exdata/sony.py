# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import data_values

def decode(model, device, command, data):
	groups = [None, None]
	nameval = [None, None]
	devicename = None

	if [model, device] == [81, 127]:
		devicename = 'aibo'
		if command == 0:
			groups[0] = 'system'
			nameval = ['enable?', data[0]]

		if command == 2 and data[1]:
			groups =['unknown',data[1]]
			if data[0] == 2:
				nameval = ['data', data[2:]]

	return devicename, groups, nameval
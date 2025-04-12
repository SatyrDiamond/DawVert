# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

DEVICETYPE_GS = 1
DEVICETYPE_XG = 2
DEVICETYPE_MT32 = 3

def get_devname(instdevice):
	outdevice = 'gm'
	if instdevice == DEVICETYPE_GS: outdevice = 'gs'
	if instdevice == DEVICETYPE_XG: outdevice = 'xg'
	if instdevice == DEVICETYPE_MT32: outdevice = 'mt32'
	return outdevice
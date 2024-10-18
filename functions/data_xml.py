# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def find_first(xml_data, name):
	t = xml_data.findall(name)
	if t: return t[0]
	else: return None
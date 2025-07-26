# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def process(convproj_obj, in_compat, out_compat, out_type, dawvert_intent):

	if convproj_obj.type not in ['ts']:
		convproj_obj.time_tempocalc.proc_points()
		convproj_obj.calc_pl_tempo()
		return True
	else:
		return False
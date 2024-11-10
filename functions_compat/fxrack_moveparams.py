# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

def process(convproj_obj, in_compat, out_compat, out_type):

	if convproj_obj.type in ['ri','r']:
		if in_compat == out_compat: return False
		else:
			fx_trackids = {}
			for trackid, track_obj in convproj_obj.track__iter():
				if track_obj.fxrack_channel not in fx_trackids: fx_trackids[track_obj.fxrack_channel] = []
				fx_trackids[track_obj.fxrack_channel].append([trackid, track_obj])

			for fx_num, fxchannel_obj in convproj_obj.fxrack.items():
				if fx_num != 0:
					paramlist = fxchannel_obj.params.list()
					if 'vol' in paramlist: paramlist.remove('vol')
					if 'pan' in paramlist: paramlist.remove('pan')

					if fx_num in fx_trackids:
						for trackid, track_obj in fx_trackids[fx_num]:
							for paramid in paramlist:
								fxchannel_obj.params.copy(track_obj.params, paramid)
								convproj_obj.automation.copy(['fxmixer',str(fx_num),paramid], ['track',trackid,paramid])

			return True
			
	else: return False

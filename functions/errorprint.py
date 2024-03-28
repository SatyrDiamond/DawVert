# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def printerr(i_type, i_data):
	if i_type == 'ext_noncompat': 
		print('[plug-conv] No Equivalent Plugin Found for '+str(i_data[0])+':'+str(i_data[1]))
	if i_type == 'ext_notfound': 
		print('[plug-conv] '+i_data[0]+' Plugin Not Found: '+i_data[1])
	if i_type == 'ext_notfound_multi': 
		print('[plug-conv] One of the plugins is not found: ')
		for t in i_data:
			print('[plug-conv]     '+t[1]+' ('+t[0]+')')
	if i_type == 'ext_other': 
		print('[plug-conv] '+i_data[0])

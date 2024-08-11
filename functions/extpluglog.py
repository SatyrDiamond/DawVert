# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger_plugconv = logging.getLogger('plugconv')

pluglist = []

class pluglist_entry:
	def __init__(self):
		self.type = ''
		self.cat = ''
		self.type = ''
		self.name = ''
		self.vendor = ''
		self.status = 0

	def __str__():
		return self.cat+' '+self.type+': '+self.name+('[%s]' % self.vendor if self.vendor else '')

class extpluglist:
	extpluglist_data = []

	def clear():
		extpluglist.extpluglist_data = []

	def add(i_cat, i_type, i_name, i_vendor):
		ple_obj = pluglist_entry()
		ple_obj.cat = i_cat
		ple_obj.type = i_type
		ple_obj.name = i_name
		ple_obj.vendor = i_vendor
		extpluglist.extpluglist_data.append(ple_obj)

	def success(i_cat, i_name):
		lastplug = extpluglist.extpluglist_data[-1]
		lastplug.status = 1
		logger_plugconv.info('   EXT | '+i_cat+' to '+lastplug.type+': '+i_name+' > '+lastplug.name+(' [%s]' % lastplug.vendor if lastplug.vendor else ''))

def convinternal(i_type, i_name, o_type, o_name):
	logger_plugconv.info('INT    | '+i_type+' to '+o_type+': '+i_name+' > '+o_name)

def printerr(i_type, i_data):
	if i_type == 'ext_noncompat': 
		logger_plugconv.info('No Equivalent Plugin Found for '+str(i_data[0])+':'+str(i_data[1]))
	if i_type == 'ext_notfound': 
		logger_plugconv.info(''+i_data[0]+' Plugin Not Found: '+i_data[1])
	if i_type == 'ext_notfound_multi': 
		logger_plugconv.info('One of the plugins is not found: ')
		for t in i_data:
			logger_plugconv.info('    '+t[1]+' ('+t[0]+')')
	if i_type == 'ext_other': 
		logger_plugconv.info(''+i_data[0])

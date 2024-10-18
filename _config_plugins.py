#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from plugins import base as dv_plugins
from objects import globalstore

dv_plugins.load_plugindir('externalsearch', '')

externalsearch_obj = dv_plugins.create_selector('externalsearch')
for shortname, plug_obj, prop_obj in externalsearch_obj.iter():
	if globalstore.os_platform in prop_obj.supported_os:
		plug_obj.import_plugins()
globalstore.extplug.write()
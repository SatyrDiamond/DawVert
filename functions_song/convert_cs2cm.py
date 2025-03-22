# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import numpy as np
import struct

logger_project = logging.getLogger('project')

def convert(convproj_obj):
	convproj_obj.type = 'rm'

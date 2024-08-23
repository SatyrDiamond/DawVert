# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np
from objects.data_bytes import structalloc

timesig_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('numerator', np.uint8),
	('denominator', np.uint8)])

bpm_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('tempo', np.float32)])

pitchauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('value', np.int16),
	('mode', np.int16)]
	)

otherauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('value', np.uint8)])


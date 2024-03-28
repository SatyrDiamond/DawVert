# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects_file._caustic import controls

class caustic_mixer:
	data = None
	controls = controls.caustic_controls()
	solo_mute = [0 for x in range(14)]

	chainnum = 0

	def parse(self):
		self.data.read(4)
		self.controls.parse(self.data)
		for n in range(14): self.solo_mute[n] = self.data.read(1)[0]
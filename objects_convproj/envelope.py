# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_envelope_adsr:
    def __init__(self):
        self.predelay = 0
        self.attack = 0
        self.hold = 0
        self.decay = 0
        self.sustain = 1
        self.release = 0
        self.amount = 0

        self.attack_tension = 0
        self.decay_tension = 0
        self.release_tension = 0

class cvpj_envelope_blocks:
    def __init__(self):
        self.values = []
        self.time = 0.01
        self.max = 1
        self.loop = -1
        self.release = -1

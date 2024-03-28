# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from fractions import Fraction

class cvpj_time:
    def __init__(self):
        self.type = 'seconds'
        self.org_bpm = 120
        self.speed_seconds = 1
        self.speed_steps = 8

    def set_seconds(self, seconds):
        self.type = 'seconds'
        self.org_bpm = 120
        self.speed_seconds = seconds
        self.speed_steps = (seconds*8)

    def set_steps(self, steps, convproj_obj):
        bpm = convproj_obj.params.get('bpm', 120).value
        self.type = 'steps'
        self.org_bpm = bpm
        self.speed_seconds = (steps*(120/bpm))/8
        self.speed_steps = steps

    def set_frac(self, num, denum, letter, convproj_obj):
        calc_val = (num/denum)*16
        if letter == 'd': calc_val /= 4/3
        if letter == 't': calc_val *= 11/8
        self.set_steps(calc_val, convproj_obj)

    def get_frac(self):
        if self.type == 'steps':
            frac = Fraction(self.speed_steps/4).limit_denominator()
            return frac.numerator, frac.denominator
        else:
            return self.speed_seconds, 1
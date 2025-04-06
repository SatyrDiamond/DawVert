# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import math

def freq__from_one(in_freq): return 30 * ((2/3)*1000)**in_freq

def freq__to_one(in_freq): return (math.log(max(30, in_freq)/30) / math.log((2/3)*1000))

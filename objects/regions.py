# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class regions:
    def __init__(self):
        self.data = []

    def __iter__(self):
        for x in self.data:
            yield x

    def add(self, i_min, i_max, i_data):
        self.data.append([i_min, i_max, i_data])

    def from_boollist(self, boollist):
        poslist = []
        for c, v in enumerate(boollist):
            if v: poslist.append(c)

        prev_val = -2
        for v in poslist:
            if prev_val != v-1: self.data.append([v, v, None])
            else: self.data[-1][1] += 1
            prev_val = v

    def out_txt(self, sep, num):
        txttab = [[' ']*sep for x in range(num)]
        for s,e,d in self.data:
            for v in range(s,e+1): txttab[v] = ['-']*sep
            txttab[s][0] = '['
            txttab[e][-1] = ']'

        return '|'.join([''.join(x) for x in txttab])

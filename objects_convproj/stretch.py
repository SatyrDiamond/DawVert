# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_stretch:
    __slots__ = ['rate','rate_tempo','warp','algorithm','params','is_warped','use_tempo']
    def __init__(self):
        self.rate = 1
        self.rate_tempo = 1
        self.is_warped = False
        self.use_tempo = False
        self.warp = []
        self.algorithm = 'stretch'
        self.params = {}

    def get(self, bpm, uses_tempo):
        tempomul = (120/bpm)
        out_is_speed = not self.use_tempo
        out_rate = self.rate
        if self.use_tempo == True and uses_tempo == False: out_rate /= tempomul
        if self.use_tempo == False and uses_tempo == True: out_rate *= tempomul
        return out_is_speed, out_rate

    def set_rate(self, bpm, rate):
        self.rate = rate
        self.rate_tempo = self.rate/(120/bpm)

    def __eq__(self, x):
        s_is_warped = self.is_warped == x.is_warped
        s_use_tempo = self.use_tempo == x.use_tempo
        s_rate = self.rate == x.rate
        s_warp = self.warp == x.warp
        s_algorithm = self.algorithm == x.algorithm
        s_params = self.params == x.params
        return s_rate and s_warp and s_algorithm and s_params and s_is_warped and s_use_tempo

    def changestretch(self, samplereflist, sampleref, target, tempo, ppq):
        iffound = sampleref in samplereflist
        #print(iffound, sampleref, target, tempomul, self.method, self.rate, self.warp, self.algorithm)
        pos_offset = 0
        cut_offset = 0

        if iffound:
            sampleref_obj = samplereflist[sampleref]

            if not self.is_warped and target == 'warp':
                pos_real = sampleref_obj.dur_sec*self.rate_tempo
                self.warp.append([0.0, 0.0])
                self.warp.append([sampleref_obj.dur_sec, pos_real])

            finalspeed = 1
            if self.is_warped and target == 'rate':
                warplen = len(self.warp)-1
                firstwarp = self.warp[0]
                fw_p = firstwarp[0]
                fw_s = firstwarp[1]

                for wn, warpd in enumerate(self.warp):
                    pos, pos_real = warpd
                    pos -= fw_p
                    pos_real -= fw_s
                    timecalc = (pos_real*8)
                    speedchange = (pos/timecalc if timecalc else 1)
                    finalspeed = speedchange

                self.rate = 1/finalspeed

                self.is_warped = False
                self.use_tempo = True
                #print(finalspeed)

                pos_offset = fw_p
                cut_offset = (fw_s*8)

        return pos_offset, cut_offset*finalspeed, finalspeed


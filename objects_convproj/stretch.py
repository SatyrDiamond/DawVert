# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

class cvpj_stretch:
    def __init__(self):
        self.algorithm = 'stretch'
        self.params = {}
        self.is_warped = False
        self.warp = []

        self.uses_tempo = False

        self.bpm = 120
        self.org_speed = 1
        self.calc_bpm_speed = 1
        self.calc_bpm_size = 1
        self.calc_tempo_speed = 1
        self.calc_tempo_size = 1
        self.calc_real_speed = 1
        self.calc_real_size = 1

    def __eq__(self, x):
        s_algorithm = self.algorithm == x.algorithm
        s_params = self.params == x.params
        s_is_warped = self.is_warped == x.is_warped
        s_warp = self.warp == x.warp
        uses_tempo = self.uses_tempo == x.uses_tempo

        s_bpm = self.bpm == x.bpm
        s_org_speed = self.org_speed == x.org_speed
        s_calc_bpm_speed = self.calc_bpm_speed == x.calc_bpm_speed
        s_calc_bpm_size = self.calc_bpm_size == x.calc_bpm_size
        s_calc_tempo_speed = self.calc_tempo_speed == x.calc_tempo_speed
        s_calc_tempo_size = self.calc_tempo_size == x.calc_tempo_size
        s_calc_real_speed = self.calc_real_speed == x.calc_real_speed
        s_calc_real_size = self.calc_real_size == x.calc_real_size

        return s_algorithm and s_params and s_is_warped and s_warp and uses_tempo and s_bpm and s_org_speed and s_calc_bpm_speed and s_calc_bpm_size and (s_calc_tempo_speed or s_calc_tempo_size or s_calc_real_speed or s_calc_real_size)

    def set_rate_speed(self, bpm, rate, is_size):
        self.uses_tempo = False
        self.bpm = bpm
        self.calc_bpm_speed = 120/self.bpm
        self.calc_bpm_size = self.bpm/120
        self.org_speed = rate
        self.calc_real_speed = rate if not is_size else 1/rate
        self.calc_real_size = 1/rate if not is_size else rate
        self.calc_tempo_speed = self.calc_real_speed*self.calc_bpm_speed
        self.calc_tempo_size = self.calc_real_size*self.calc_bpm_size

    def set_rate_tempo(self, bpm, rate, is_size):
        self.uses_tempo = True
        self.bpm = bpm
        self.calc_bpm_speed = 120/self.bpm
        self.calc_bpm_size = self.bpm/120
        self.org_speed = rate
        self.calc_tempo_speed = rate if not is_size else 1/rate
        self.calc_tempo_size = 1/rate if not is_size else rate
        self.calc_real_speed = self.calc_tempo_speed/self.calc_bpm_speed
        self.calc_real_size = self.calc_tempo_size/self.calc_bpm_size

    def changestretch(self, samplereflist, sampleref, target, tempo, ppq):
        iffound = sampleref in samplereflist
        #print(iffound, sampleref, target, tempomul, self.method, self.rate, self.warp, self.algorithm)
        pos_offset = 0
        cut_offset = 0

        finalspeed = 1

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

                self.set_rate_tempo(tempo, finalspeed, True)

                pos_offset = fw_p
                cut_offset = (fw_s*8)

        return pos_offset, cut_offset*finalspeed, finalspeed

    def debugtxt(self):
        print('- main')
        print('uses tempo:', self.uses_tempo)
        print('bpm:', self.bpm)
        print('speed:', self.org_speed)
        print('- bpm calc')
        print('speed:', self.calc_bpm_speed)
        print('size:', self.calc_bpm_size)
        print('- with tempo')
        print('speed:', self.calc_tempo_speed)
        print('size:', self.calc_tempo_size)
        print('- no tempo')
        print('speed:', self.calc_real_speed)
        print('size:', self.calc_real_size)
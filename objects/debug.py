# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

verbose_blocks_gfx = [' ','▁','▂','▃','▄','▅','▆','▇','█']

verbose_vsize = 6
verbose_hsize = 70

def blockpoint_gfx(points, txti, sustain, vsize=verbose_vsize, hsize=verbose_hsize):
	import numpy
	gfxdata_colors = ['\x1b[37;40m' for x in range(hsize)]

	print(txti)

	if isinstance(points[0], int):
		f = [(x/(hsize-1))*(len(points)-1) for x in range(hsize)]
		fd = [[x%1, points[x.__floor__()], points[min(len(points)-1, x.__floor__()+1)]] for x in f]
		fd = [xtramath.between_from_one(imin, imax, perc) for perc, imin, imax in fd]
		for n in range(len(points)):
			blocknum = int((n/(len(points)-1))*hsize)
			gfxdata_colors[min(blocknum, hsize-1)] = '\x1b[36;44m'

	if isinstance(points[0], list):
		fd = [0 for x in range(hsize)]

		debp = [[int(xtramath.clamp(x,0,1)*verbose_hsize), y] for x,y in points]

		for n in range(len(debp)-1):
			curp = debp[n]
			nextp = debp[n+1]
			size = nextp[0]-curp[0]
			for x in range(size):
				fd[debp[n][0]+x] = xtramath.between_from_one(curp[1], nextp[1], x/size)

		for n, d in enumerate(points):
			p, v = d
			blocknum = int((p)*hsize)
			gfxdata_colors[min(blocknum, hsize-1)] = '\x1b[96;44m'
			if sustain>=0:
				if sustain==n:
					gfxdata_colors[min(blocknum, hsize-1)] = '\x1b[33;41m'



	for vh in range(vsize, 0, -1):
		ft = [int(xtramath.clamp((x*vsize)-(vh-1), 0, 1)*(len(verbose_blocks_gfx)-1)) for x in fd]
		gfxdata_txt = [' ' for x in range(hsize)]
		for n, x in enumerate(ft): gfxdata_txt[n] = verbose_blocks_gfx[int(x)]
		for x in range(hsize): print(gfxdata_colors[x]+gfxdata_txt[x], end='')
		print('\033[0;0m')

# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import xtramath

def create_points_cut(convproj_obj, mode):
	songduration = convproj_obj.get_dur()
	ppq = convproj_obj.time_ppq

	timesig_num, timesig_dem = convproj_obj.timesig
	if mode == 1:
		timesig_num *= timesig_dem

	timesigposs = []

	if mode == 0:
		for p, v in convproj_obj.timesig_auto: timesigposs.append([p, v[0]*ppq])
	if mode == 1:
		for p, v in convproj_obj.timesig_auto: timesigposs.append([p, v[0]*v[1]*ppq])

	if timesigposs == []: timesigposs.append([0, int(4*ppq)])
	timesigposs.append([songduration, None])
	if timesigposs == []: timesigposs = [[0, timesig_num*ppq],[songduration, timesig_num*ppq]] 

	timesigblocks = []
	for timesigposnum in range(len(timesigposs)-1):
		timesigpos = timesigposs[timesigposnum]
		timesigblocks.append([timesigpos[0], timesigposs[timesigposnum+1][0], timesigpos[1]])

	splitpoints = []
	p_splitts = {}
	for t in timesigblocks:
		if t[0] not in splitpoints: splitpoints.append(t[0])
		p_splitts[t[0]] = t[2]
		curpos = t[0]
		for x in xtramath.gen_float_blocks(t[1]-t[0],t[2]):
			curpos += x
			p_splitts[curpos] = t[2]
			if curpos not in splitpoints: splitpoints.append(curpos)

	splitts = [p_splitts[x] for x in splitpoints]


	#print(splitpoints, timesigposs, songduration)

	if False:
		import matplotlib.pyplot as plt
		import matplotlib
		matplotlib.interactive(True)
		plt.scatter(splitpoints, [0 for x in splitpoints])
		plt.scatter([0,songduration], [0.3,0.3])
		plt.scatter([x[0] for x in timesigposs], [0.1 for x in timesigposs])
		plt.scatter([1,1], [-1,1])
		plt.show(block=True)

	print(splitpoints)
	print(splitts)
	print(timesigposs)

	return splitpoints, splitts, timesigposs
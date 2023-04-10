# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def get(vstdata):
	nbpvstdata = vstdata.split(b'\x00')
	nbp = [{}]
	groupnum = 0
	isvalname = False
	for datavalue in nbpvstdata:
		print(datavalue)
		if isvalname == True:
			nbp[groupnum][valname] = datavalue.decode()
			isvalname = False
		else:
			if datavalue == b'':
				groupnum += 1
				nbp.append({})
			else:
				isvalname = True
				valname = datavalue.decode()
	return nbp

def make(larr):
	nbp = bytes()
	for grouplist in larr:
		for param in grouplist:
			nbp += str(param).encode('utf-8')+b'\x00'+str(grouplist[param]).encode('utf-8')+b'\x00'
		nbp += b'\x00'
	return nbp

# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

# -------------------- wolfshaper --------------------

def wolfshaper_init():
	global wolfshapergraph
	global wolfshaperparams
	wolfshapergraph = {}
	wolfshapergraph['graph'] = ''
	wolfshaperparams = {}
	wolfshaperparams['pregain'] = 2.000000
	wolfshaperparams['wet'] = 1.000000
	wolfshaperparams['postgain'] = 1.000000
	wolfshaperparams['removedc'] = 1.000000
	wolfshaperparams['oversample'] = 0.000000
	wolfshaperparams['bipolarmode'] = 0.000000
	wolfshaperparams['warptype'] = 0.000000
	wolfshaperparams['warpamount'] = 0.000000
	wolfshaperparams['vwarptype'] = 0.000000
	wolfshaperparams['vwarpamount'] = 0.000000
def wolfshaper_setvalue(name, value):
	global wolfshaperparams
	wolfshaperparams[name] = value
def wolfshaper_addpoint(posX,posY,tension,pointtype):
	global wolfshapergraph
	wolfshapergraph['graph'] += float.hex(posX)+','+float.hex(posY)+','+float.hex(tension)+','+str(int(pointtype))+';'
def wolfshaper_get():
	global wolfshapergraph
	global wolfshaperparams
	return [wolfshapergraph, wolfshaperparams]

# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values

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
def wolfshaper_addshape(cvpj_auto):
	for cvpj_point in cvpj_auto['points']:
		tension = data_values.get_value(cvpj_point, 'tension', 0)
		pointtype = data_values.get_value(cvpj_point, 'type', 'normal')
		wolfshaper_addpoint(cvpj_point['position'],cvpj_point['value'],tension,pointtype)
def wolfshaper_addpoint(posX,posY,tension,pointtype):
	global wolfshapergraph
	if pointtype == 'normal': pointtype = 0
	elif pointtype in ['doublecurve', 'doublecurve2', 'doublecurve3']: pointtype = 1
	elif pointtype == 'stairs': 
		pointtype = 2
		tension *= -1
	elif pointtype == 'wave': 
		pointtype = 3
		tension = ((abs(tension)*-1)+100)*0.2
	else: 
		pointtype = 1

	wolfshapergraph['graph'] += float.hex(posX)+','+float.hex(posY)+','+float.hex(tension*-100)+','+str(int(pointtype))+';'
def wolfshaper_get():
	global wolfshapergraph
	global wolfshaperparams
	return [wolfshapergraph, wolfshaperparams]


import chardet
import numpy as np
import os 

dt_cvpj = np.dtype([
		('paramid', np.str_, 32),
		('extid', np.str_, 32),
		('def_one', np.float64), 
		('def', np.float64), 
		('min', np.float64), 
		('max', np.float64), 
		('mathtype', np.str_, 3),
		('mathval', np.float64), 
		('visname', np.str_, 64)
		])

dt_vst2 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 16)
		])

dt_vst3 = np.dtype([
		('paramnum', np.short),
		('visname', np.str_, 24)
		])

class paramremap:
	def __init__(self, filename):
		self.cvpj = np.zeros(0, dtype=dt_cvpj)
		self.vst2 = np.zeros(0, dtype=dt_vst2)
		self.vst3 = np.zeros(0, dtype=dt_vst3)
		if os.path.exists(filename):
			with open(filename, 'rb') as csvfile:
				csvdata = csvfile.read()
				csvcharset = chardet.detect(csvdata)['encoding']
				csvtext = csvdata.decode(csvcharset).splitlines()

				if len(csvtext)>2:
					self.cvpj = np.zeros(len(csvtext)-2, dtype=dt_cvpj)
					self.vst2 = np.zeros(len(csvtext)-2, dtype=dt_vst2)
					self.vst3 = np.zeros(len(csvtext)-2, dtype=dt_vst3)

					self.cvpj['min'] = 0
					self.cvpj['max'] = 1
					self.cvpj['mathtype'] = 'lin'
					self.cvpj['mathval'] = 1
					self.vst2['paramnum'] = -1
					self.vst3['paramnum'] = -1

					self.usedparamnames = {'cvpj': [],'vst2': [],'vst3': []}

					for count, row_unsep in enumerate(csvtext):
						splitsep = row_unsep.split(',')
						if count == 0: 
							data_exttypes = splitsep

						elif count == 1: 
							data_typenames = splitsep
							data_len = len(data_exttypes)
							for n,v in enumerate(data_typenames):
								self.usedparamnames[data_exttypes[n]].append(v)
						else:
							numparam = count-2
							for x in range(max(data_len, len(splitsep))):
								extname = data_exttypes[x]
								dataname = data_typenames[x]
								dataval = splitsep[x]

								if dataname in ['def_one','def','min','max']: dataval = float(dataval)
								if dataname == 'paramnum': dataval = float(dataval)
								if extname == 'cvpj': self.cvpj[numparam][dataname] = dataval
								if extname == 'vst2': self.vst2[numparam][dataname] = dataval
								if extname == 'vst3': self.vst3[numparam][dataname] = dataval

					if 'def' not in self.usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def'] *= mulvals
						self.cvpj['def'] += self.cvpj['min']
					elif 'def_one' not in self.usedparamnames['cvpj']:
						mulvals = self.cvpj['max']-self.cvpj['min']
						self.cvpj['def_one'] = np.asarray(self.cvpj['def_one'], dtype=np.float64)
						self.cvpj['def_one'] -= self.cvpj['min']
						self.cvpj['def_one'] /= mulvals

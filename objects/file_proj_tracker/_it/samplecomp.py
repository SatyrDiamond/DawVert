# code from https://gist.github.com/defensem3ch/8a871435974bf7e8c05dedba85cdd259

DECOMPRESS_IT214 = True

# types are "recursive crater", "abstract fillin", "fillin", and "crater".
IT214_ALGO_SELECT = "recursive crater"

# this should hopefully speed up what's been done.
IT214_ALGO_RECURSIVE_CRATER = IT214_ALGO_SELECT == "recursive crater"

# this has been an experiment and is currently very inefficient. don't use it.
IT214_ALGO_ABSTRACT_FILLIN = IT214_ALGO_SELECT == "abstract fillin"

# if you want to, try this algorithm. about half the time, it beats crater.
IT214_ALGO_FILLIN = IT214_ALGO_SELECT == "fillin"

IT214_COMP_LOWER8  = [0,-1,-3,-7,-15,-31]
IT214_COMP_LOWER8 += [-(1<<(i-1))+4 for i in range(7,8+1,1)]
IT214_COMP_LOWER8 += [-128]
IT214_COMP_UPPER8  = [0, 1, 3, 7, 15, 31]
IT214_COMP_UPPER8 += [ (1<<(i-1))-5 for i in range(7,8+1,1)]
IT214_COMP_UPPER8 += [ 127]
IT214_COMP_LOWER16  = [0,-1,-3,-7,-15,-31]
IT214_COMP_LOWER16 += [-(1<<(i-1))+8 for i in range(7,16+1,1)]
IT214_COMP_LOWER16 += [-32768]
IT214_COMP_UPPER16  = [0, 1, 3, 7, 15, 31]
IT214_COMP_UPPER16 += [ (1<<(i-1))-9 for i in range(7,16+1,1)]
IT214_COMP_UPPER16 += [ 32767]
IT214_WIDTHCHANGESIZE = [4,5,6,7,8,9,7,8,9,10,11,12,13,14,15,16,17]

def decode_undelta(xdata, is16):
	base = 0
	if is16:
		for i in range(len(xdata)):
			base += xdata[i]
			base &= 0xFFFF
			xdata[i] = base
	else:
		for i in range(len(xdata)):
			base += xdata[i]
			base &= 0xFF
			xdata[i] = base

def ord_shim(v):
	# print("ORDING:", v, type(v))
	if type(v) == int:
		return v
	return ord(v)

class IT214Exception(Exception):
	pass

class IT214ContinueException(Exception):
	pass

class IT214Compressor:
	def __init__(self, data, offs, length, is16, is215):
		# Probably the only IT214 compressor in the world to handle stereo samples.
		# (ok i can just about guarantee that Storlek has something)
		
		self.base_length = min(length,0x4000 if is16 else 0x8000)
		self.length = self.base_length
		
		self.packed_data = [0,0]
		self.bpos = 0
		self.brem = 8
		self.bval = 0
		self.block_length_pos = 0
		self.offs = offs
		
		self.is16 = is16
		
		self.lowertab = IT214_COMP_LOWER16 if is16 else IT214_COMP_LOWER8
		self.uppertab = IT214_COMP_UPPER16 if is16 else IT214_COMP_UPPER8
		self.dwidth = 17 if is16 else 9
		self.fetch_a = 4 if is16 else 3
		self.lower_b = -8 if is16 else -4
		
		self.data = []
		if is16:
			clamp_part = lambda x : x - 0x10000 if x >= 0x8000 else x
			self.clamp = lambda x : clamp_part(x&0xFFFF)
			self.clamp_unsigned = lambda x : (x&0xFFFF)
			for i in range(self.base_length):
				self.data.append(ord_shim(data[(offs+i)*2])|(ord_shim(data[(offs+i)*2+1])<<8))
		else:
			clamp_part = lambda x : x - 0x100 if x >= 0x80 else x
			self.clamp = lambda x : clamp_part(x&0xFF)
			self.clamp_unsigned = lambda x : (x&0xFF)
			for i in range(self.base_length):
				self.data.append(ord_shim(data[(offs+i)]))
		
		self.deltafy()
		if is215:
			# DO IT AGAIN LOLOLOLOLOLOL
			self.deltafy()
		
		if IT214_ALGO_RECURSIVE_CRATER:
			self.squish_recursive()
		else:
			self.squish()
		
		self.packed_data.append(self.bval)
		self.packed_data[0] = (len(self.packed_data)-2)&0xFF
		self.packed_data[1] = (len(self.packed_data)-2)>>8
		
		if len(self.packed_data) >= 0x10002:
			raise Exception("somehow we exceeded the 16-bit counter while packing the data.")
	
	def get_length(self):
		return self.base_length
	
	def get_data(self):
		return self.packed_data
	
	def write(self, width, v):
		while width > self.brem:
			self.bval |= (v<<self.bpos)&0xFF
			width -= self.brem
			v >>= self.brem
			self.bpos = 0
			self.brem = 8
			self.packed_data.append(self.bval)
			self.bval = 0
		
		if width > 0: # uhh, this check might be redundant
			self.bval |= (v & ((1<<width)-1)) << self.bpos
			self.brem -= width
			self.bpos += width
	
	def deltafy(self):
		root = 0
		for i in range(self.base_length):
			root, self.data[i] = self.data[i], self.clamp(self.data[i]-root)
	
	def get_width_change_size(self, w):
		wcs = IT214_WIDTHCHANGESIZE[w-1]
		if w <= 6 and self.is16:
			wcs += 1
		
		return wcs
	
	def squish_recursive_part(self, bwt, swidth, lwidth, rwidth, width, offs, length):
		#print("width", width+1, offs, length)
		if width+1 < 1:
			for i in range(offs,offs+length,1):
				bwt[i] = swidth
			
			return
		
		i = offs
		itarg = length+offs
		while i < itarg:
			if self.data[i] >= self.lowertab[width] and self.data[i] <= self.uppertab[width]:
				j = i
				while i < itarg and self.data[i] >= self.lowertab[width] and self.data[i] <= self.uppertab[width]:
					i += 1
				
				blklen = i-j
				
				twidth = swidth
				comparison = False
				xlwidth = lwidth if j == offs else swidth
				xrwidth = rwidth if i == itarg else swidth
				
				wcsl = self.get_width_change_size(xlwidth)
				wcss = self.get_width_change_size(swidth)
				wcsw = self.get_width_change_size(width+1)
				
				if i == self.base_length:
					keep_down = wcsl+(width+1)*blklen
					level_left = wcsl+swidth*blklen
					
					if xlwidth == swidth:
						level_left -= wcsl
					
					comparison = keep_down <= level_left
				else:
					keep_down = wcsl+(width+1)*blklen+wcsw
					level_left = wcsl+swidth*blklen+wcss
					
					if xlwidth == swidth:
						level_left -= wcsl
					if xrwidth == swidth:
						level_left -= wcss
					
					comparison = keep_down <= level_left
				
				if comparison:
					self.squish_recursive_part(bwt, width+1, xlwidth, xrwidth, width-1, j, blklen)
				else:
					self.squish_recursive_part(bwt, swidth, xlwidth, xrwidth, width-1, j, blklen)
			else:
				bwt[i] = swidth
				i += 1
	
	def squish_recursive(self):
		# initialise bit width table with initial values
		bwt = [self.dwidth for i in range(self.base_length)]
		
		# recurse
		self.squish_recursive_part(bwt, self.dwidth, self.dwidth, self.dwidth, self.dwidth-2, 0, self.base_length)
		
		# write
		self.squish_write(bwt)
	
	def squish(self):
		# initialise bit width table with initial values
		bwt = [self.dwidth for i in range(self.base_length)]
		
		if IT214_ALGO_ABSTRACT_FILLIN: # "Abstract fillin" algorithm
			# precrater then analyse
			print("building craters")
			for i in range(self.base_length):
				for width in range(self.dwidth):
					if self.data[i] >= self.lowertab[width] and self.data[i] <= self.uppertab[width]:
						bwt[i] = width+1
						break
					
					assert width != self.dwidth-1
			
			print("analysing cratery")
			l = []
			w = self.dwidth
			c = 0
			n = 0
			for v in bwt:
				if w != v:
					l.append((w,c,n))
					w = v
					c = IT214_WIDTHCHANGESIZE[w-1]
					if w <= 6 and self.is16:
						c += 1
					n = 0
				
				n += 1
			
			l.append((w,c,n))
			
			print("removing crap cratery")
			k = True
			r = 0
			while k:
				k = False
				print(len(l))
				print("iteration", r+1)
				r += 1
				
				i = len(l)-1
				while i >= 1:
					wl,cl,nl = l[i-1]
					wm,cm,nm = l[i]
					
					# action cost for keep / merge
					ak = wl*nl + cl + wm*nm + cm
					am = wl*(nl+nm) + cl
					act = 0 # middle -> left
					
					# target width for merge
					tw = wl
					tn = nl+nm
					
					if i == len(l)-1:
						ak -= cm
						am -= cl
					else:
						wr,cr,nr = l[i+1]
						if wr == wl:
							act = 1 # right -> middle -> left base
							am -= cl
							tn = nl+nm+nr
						else:
							amr = cl + wr*(nl+nm)
							if amr < am and wl > wm:
								act = 2 # right base -> middle
								tm = l[i+1][0]
								tw = wm
								tn = nm+nr
					
					
					if am < ak and tw > wm:
						if act == 0:
							l = l[:i-1] + [(tw,self.get_width_change_size(tw),tn)] + l[i+1:]
						elif act == 1:
							l = l[:i-1] + [(tw,self.get_width_change_size(tw),tn)] + l[i+2:]
						elif act == 2:
							l = l[:i] + [(tw,self.get_width_change_size(tw),tn)] + l[i+2:]
						else:
							raise Exception("EDOOFUS this should never happen")
						
						i -= 2
						k = True
					else:
						i -= 1
					
			
			print(len(l))
			
			print("recreating bit width table")
			w,c,n = l.pop(0)
			for i in range(len(bwt)):
				if n == 0:
					w,c,n = l.pop(0)
				
				bwt[i] = w
				n -= 1
			
		elif IT214_ALGO_FILLIN: # "Fill in" algorithm
			# precrater then raise craters
			print("building craters")
			for i in range(self.base_length):
				for width in range(self.dwidth):
					if self.data[i] >= self.lowertab[width] and self.data[i] <= self.uppertab[width]:
						bwt[i] = width+1
						break
					
					assert width != self.dwidth-1
			
			print("raising craters")
			for width in range(self.dwidth):
				print("width", width+1)
				beg = None
				swidth = None
				for i in range(self.base_length):
					if bwt[i] == width+1:
						if beg == None:
							swidth = self.dwidth
							if i > 0:
								swidth = bwt[i-1]
							beg = i
						
						if i != self.base_length-1:
							continue
						
						i += 1
					
					if beg != None:
						length = i - beg
						wcsl = IT214_WIDTHCHANGESIZE[swidth-1]
						wcsr = IT214_WIDTHCHANGESIZE[width]
						if swidth <= 6 and self.is16:
							wcsl += 1
						if (width+1) <= 6 and self.is16:
							wcsr += 1
						
						
						twidth = width
						if i == self.base_length:
							keep_down = wcsl+(width+1)*length
							raise_left = swidth*length
							
							if keep_down <= raise_left or (width+1) > swidth:
								twidth = width+1
							else:
								twidth = swidth
						else:
							keep_down = wcsl+(width+1)*length+wcsr
							raise_left = swidth*length+wcsl
							raise_right = wcsl+bwt[i]*length
							if bwt[i] == swidth:
								raise_left -= wcsl
								raise_right -= wcsl
							
							if keep_down <= raise_left or (width+1) > swidth:
								if keep_down <= raise_right or (width+1) > bwt[i]:
									twidth = width+1
								else:
									twidth = bwt[i]
							elif raise_left < raise_right or (width+1) > bwt[i]:
								twidth = swidth
							else:
								twidth = bwt[i]
						
						if twidth != width+1:
							for j in range(beg,i,1):
								bwt[j] = twidth
						
						if i == self.base_length:
							break
						beg = None
		else: # new "Crater" algorithm
			# determine whether it would be wise to crater stuff
			for width in range(self.dwidth-2,0-1,-1):
				print("width", width+1)
				beg = None
				swidth = None
				for i in range(self.base_length):
					if self.data[i] >= self.lowertab[width] and self.data[i] <= self.uppertab[width]:
						if beg == None:
							swidth = self.dwidth
							if i > 0:
								swidth = bwt[i-1]
							beg = i
						
						if i != self.base_length-1:
							continue
						
						i += 1
					
					if beg != None:
						length = i - beg
						# only if we save bytes do we lower the bit width
						# note, this is a greedy algorithm and might not be optimal
						# UPDATE: it actually isn't.
						
						wcsl = IT214_WIDTHCHANGESIZE[swidth-1]
						wcsr = IT214_WIDTHCHANGESIZE[width]
						if swidth <= 6 and self.is16:
							wcsl += 1
						if (width+1) <= 6 and self.is16:
							wcsr += 1
						
						twidth = swidth
						if i == self.base_length:
							keep_down = wcsl+(width+1)*length
							level_left = swidth*length
							
							if keep_down <= level_left:
								for j in range(beg,i,1):
									bwt[j] = width+1
						else:
							keep_down = wcsl+(width+1)*length+wcsr
							level_left = swidth*length+wcsl
							level_right = wcsl+bwt[i]*length
							if bwt[i] == swidth:
								level_left -= wcsl
								level_right -= wcsl
							
							if keep_down <= level_left:
								if keep_down <= level_right:
									for j in range(beg,i,1):
										bwt[j] = width+1
						
						
						
						if i == self.base_length:
							break
						beg = None
			
		#print(bwt)
		
		self.squish_write(bwt)
	
	def squish_write(self, bwt):
		# write values
		print("writing")
		dwidth = self.dwidth
		for i in range(self.base_length):
			if bwt[i] != dwidth:
				if dwidth <= 6: # MODE A
					self.write(dwidth, (1<<(dwidth-1)))
					self.write(self.fetch_a, self.convert_width(dwidth,bwt[i]))
				elif dwidth < self.dwidth: # MODE B
					xv = (1<<(dwidth-1))+self.lower_b+self.convert_width(dwidth,bwt[i])
					self.write(dwidth, xv)
				else: # MODE C
					assert (bwt[i]-1) >= 0
					self.write(dwidth, (1<<(dwidth-1))+bwt[i]-1)
				
				dwidth = bwt[i]
			
			assert self.data[i] >= self.lowertab[dwidth-1] and self.data[i] <= self.uppertab[dwidth-1]
			
			if dwidth == self.dwidth:
				assert (self.clamp_unsigned(self.data[i]) & (1<<(self.dwidth-1))) == 0
			self.write(dwidth, self.clamp_unsigned(self.data[i]))
	
	def convert_width(self, curwidth, newwidth):
		curwidth -= 1
		newwidth -= 1
		assert newwidth != curwidth
		if newwidth > curwidth:
			newwidth -= 1
		
		return newwidth

class IT214Decompressor:
	def __init__(self, data, length, is16):
		self.data = data
		self.dpos = 0
		self.bpos = 0
		self.brem = 8
		
		self.base_length = length
		self.grab_length = length
		self.running_count = 0
		
		self.is16 = is16
		self.fetch_a = 4 if is16 else 3
		self.spread_b = 16 if is16 else 8
		self.lower_b = -8 if is16 else -4
		self.upper_b = 7 if is16 else 3
		self.width = self.widthtop = 17 if is16 else 9
		self.unpack_mask = 0xFFFF if is16 else 0xFF
		self.maxgrablen = 0x4000 if is16 else 0x8000
		
		self.unpacked_data = []
		
		try:
			self.unpack()
		except IT214ContinueException as e:
			print("WARNING: IT214ContinueException occurred:", e)
			print("This might actually be a bug.")
			return # it's OK dear
		except IT214Exception as e:
			#print("WARNING! WARNING! SAMPLE DATA DECOMPRESSED BADLY!")
			#print("IT214Exception:", e)
			#print("old running count:", self.running_count)
			while self.running_count < self.base_length:
				self.unpacked_data.append(self.unpacked_root)
				self.running_count += 1
			self.running_count = self.base_length
			return
			
	
	def unpack(self):
		#while self.grab_length > 0:
		# I think THIS is what itsex.c meant. --GM
		self.length = min(self.grab_length,self.maxgrablen)
		self.grab_length -= self.length
		#print("subchunk length: %i" % self.length)
		self.unpacked_root = 0
		while self.length > 0 and not self.end_of_block():
			if self.width == 0 or self.width > self.widthtop:
				raise IT214Exception("invalid bit width")
			
			v = self.read(self.width)
			topbit = (1<<(self.width-1))
			#print(self.width,v)
			if self.width <= 6: # MODE A
				if v == topbit:
					self.change_width(self.read(self.fetch_a))
					#print(self.width)
				else:
					self.write(self.width, v, topbit)
			elif self.width < self.widthtop: # MODE B
				if v >= topbit+self.lower_b and v <= topbit+self.upper_b:
					qv = v - (topbit+self.lower_b)
					#print("MODE B CHANGE",self.width,v,qv)
					self.change_width(qv)
					#print(self.width)
				else:
					self.write(self.width, v, topbit)
			else: # MODE C
				if v & topbit:
					self.width = (v & ~topbit)+1
					#print(self.width)
				else:
					self.write(self.width-1, (v & ~topbit), 0)
		
		#print("bytes remaining in block: %i" % (len(self.data)-self.dpos))
	
	def write(self, width, value, topbit):
		self.running_count += 1
		self.length -= 1
		
		if DECOMPRESS_IT214:
			v = value
			if v&topbit:#(1<<(width-1)):
				v -= topbit*2#1<<width
			self.unpacked_root = (self.unpacked_root+v) & self.unpack_mask
			self.unpacked_data.append(self.unpacked_root)
	
	def change_width(self, width):
		width += 1
		if width >= self.width:
			width += 1
		
		assert self.width != width # EDOOFUS
		self.width = width
	
	def get_length(self):
		return self.running_count
	
	def get_data(self):
		return self.unpacked_data
	
	def end_of_block(self):
		return self.dpos >= len(self.data)
	
	def read(self, width):
		v = 0
		vpos = 0
		vmask = (1<<width)-1
		while width >= self.brem:
			if self.dpos >= len(self.data):
				raise IT214Exception("unbalanced block end")
			
			v |= (ord_shim(self.data[self.dpos])>>self.bpos)<<vpos
			vpos += self.brem
			width -= self.brem
			self.dpos += 1
			self.brem = 8
			self.bpos = 0
		
		if width > 0:
			if self.dpos >= len(self.data):
				raise IT214Exception("unbalanced block end")
			
			v |= (ord_shim(self.data[self.dpos])>>self.bpos)<<vpos
			v &= vmask
			self.brem -= width
			self.bpos += width
		
		return v

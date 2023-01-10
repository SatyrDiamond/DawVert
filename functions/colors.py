
# from hex
def hex_to_rgb_int(hexcode):
    nonumsign = hex.lstrip('#')
    return tuple(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))

def rgb_int_to_rgb_float(rgb_int):
    return [rgb_int[0]/255, rgb_int[1]/255, rgb_int[2]/255]

def hex_to_rgb_float(hexcode):
	return rgb_int_to_rgb_float(hex_to_rgb_int(hexcode))

# to hex
def rgb_float_2_rgb_int(rgb_float): return (int(rgb_float[0]*255),int(rgb_float[1]*255),int(rgb_float[2]*255))

def rgb_int_2_hex(rgb_int): return '%02x%02x%02x' % rgb_int

def rgb_float_2_hex(rgb_float): return rgb_int_2_hex(rgb_float_2_rgb_int(rgb_float))

# fx
def moregray(rgb_float): 
	return [(rgb_float[0]/2)+0.25,(rgb_float[1]/2)+0.25,(rgb_float[2]/2)+0.25]

def hz_to_value(freq): return 12*math.log2(freq/(440*pow(2, -4.75)))+12
def value_to_hz(note): return (440/32)*(2**((note-9)/12))

def devicesparam():
	return {
"volume":
	{
	'volume': ['float', '1.0'], 
	'pan': ['float', '0.0']
	},
"1bandEq":
	{
	'gain': ['float', '0.0'], 
	'freq': ['float', '83.21308898925781'], 
	'q': ['float', '0.5'], 
	'shape': ['int', '2']
	},
"3bandEq":
	{
	'freq1': ['float', '43.34996032714844'], 
	'freq2': ['float', '90.23263549804688'], 
	'freq3': ['float', '119.2130889892578'], 
	'gain1': ['float', '0.0'],
	'gain2': ['float', '0.0'],
	'gain3': ['float', '0.0']
	},
"8bandEq":
	{
	'mode': ['int', '1'], 
	'analyzer': ['int', '0'], 

	'enable1lm': ['float', '0'], 
	'enable1rs': ['float', '0'], 
	'freq1lm': ['float', '22.5063'], 
	'freq1rs': ['float', '22.5063'],
	'gain1lm': ['float', '0.0'],
	'gain1rs': ['float', '0.0'],
	'q1lm': ['float', '0.5'],
	'q1rs': ['float', '0.5'],
	'shape1lm': ['float', '1'],
	'shape1rs': ['float', '1'],

	'enable2lm': ['float', '0'], 
	'enable2rs': ['float', '0'], 
	'freq2lm': ['float', '22.5063'], 
	'freq2rs': ['float', '22.5063'],
	'gain2lm': ['float', '0.0'],
	'gain2rs': ['float', '0.0'],
	'q2lm': ['float', '0.5'],
	'q2rs': ['float', '0.5'],
	'shape2lm': ['float', '1'],
	'shape2rs': ['float', '1'],

	'enable3lm': ['float', '0'], 
	'enable3rs': ['float', '0'], 
	'freq3lm': ['float', '22.5063'], 
	'freq3rs': ['float', '22.5063'],
	'gain3lm': ['float', '0.0'],
	'gain3rs': ['float', '0.0'],
	'q3lm': ['float', '0.5'],
	'q3rs': ['float', '0.5'],
	'shape3lm': ['float', '1'],
	'shape3rs': ['float', '1'],

	'enable4lm': ['float', '0'], 
	'enable4rs': ['float', '0'], 
	'freq4lm': ['float', '22.5063'], 
	'freq4rs': ['float', '22.5063'],
	'gain4lm': ['float', '0.0'],
	'gain4rs': ['float', '0.0'],
	'q4lm': ['float', '0.5'],
	'q4rs': ['float', '0.5'],
	'shape4lm': ['float', '1'],
	'shape4rs': ['float', '1'],

	'enable5lm': ['float', '0'], 
	'enable5rs': ['float', '0'], 
	'freq5lm': ['float', '22.5063'], 
	'freq5rs': ['float', '22.5063'],
	'gain5lm': ['float', '0.0'],
	'gain5rs': ['float', '0.0'],
	'q5lm': ['float', '0.5'],
	'q5rs': ['float', '0.5'],
	'shape5lm': ['float', '1'],
	'shape5rs': ['float', '1'],

	'enable6lm': ['float', '0'], 
	'enable6rs': ['float', '0'], 
	'freq6lm': ['float', '22.5063'], 
	'freq6rs': ['float', '22.5063'],
	'gain6lm': ['float', '0.0'],
	'gain6rs': ['float', '0.0'],
	'q6lm': ['float', '0.5'],
	'q6rs': ['float', '0.5'],
	'shape6lm': ['float', '1'],
	'shape6rs': ['float', '1'],

	'enable7lm': ['float', '0'], 
	'enable7rs': ['float', '0'], 
	'freq7lm': ['float', '22.5063'], 
	'freq7rs': ['float', '22.5063'],
	'gain7lm': ['float', '0.0'],
	'gain7rs': ['float', '0.0'],
	'q7lm': ['float', '0.5'],
	'q7rs': ['float', '0.5'],
	'shape7lm': ['float', '1'],
	'shape7rs': ['float', '1'],

	'enable8lm': ['float', '0'], 
	'enable8rs': ['float', '0'], 
	'freq8lm': ['float', '22.5063'], 
	'freq8rs': ['float', '22.5063'],
	'gain8lm': ['float', '0.0'],
	'gain8rs': ['float', '0.0'],
	'q8lm': ['float', '0.5'],
	'q8rs': ['float', '0.5'],
	'shape8lm': ['float', '1'],
	'shape8rs': ['float', '1'],
	},
"chorusEffect":
	{
	'mode': ['float', '1.0'], 
	'delay': ['float', '10.0'], 
	'depth': ['float', '20.0'], 
	'sync': ['float', '0.0'],
	'rateSyncOff': ['float', '0.4'],
	'rateSyncOn': ['float', '15.0'],
	'mix': ['float', '1.0'],
	'mixLock': ['float', '0.0']
	},
"comp":
	{
	'rms': ['float', '0'], 
	'threshold': ['float', '-30.0'], 
	'ratio': ['float', '2.0'], 
	'attack': ['float', '50.0'],
	'release': ['float', '500.0'],
	'knee': ['float', '0.0'],
	'outputDb': ['float', '0.0'],
	'sidechainTrigger': ['float', '0'],
	'inputDb': ['float', '0.0']
	},
"stereoDelay":
	{
	'crossL': ['float', '8.0'], 
	'crossR': ['float', '8.0'], 
	'delaySyncOffL': ['float', '0.0'], 
	'delaySyncOnL': ['float', '1.0'],
	'delaySyncOnR': ['float', '1.0'],
	'feedbackL': ['float', '8.0'], 
	'feedbackR': ['float', '8.0'], 
	'highcut': ['float', '5000.0'],
	'lowcut': ['float', '300.0'],
	'mix': ['float', '1.0'],
	'mixLock': ['float', '0.0'],
	'panL': ['float', '-1.0'],
	'panR': ['float', '1.0'], 
	'sync': ['float', '0.0'],
	'volL': ['float', '0.0'],
	'volR': ['float', '0.0'],
	},
"distortion":
	{
	'emphasis': ['float', '0.25'], 
	'tone': ['float', '1.0'], 
	'postGain': ['float', '1.0'], 
	'drive': ['float', '0.0'],
	'dtype': ['int', '0'],
	'mix': ['float', '1.0'],
	'mixLock': ['float', '0.0']
	},
"plateReverb":
	{
	'preDelay': ['float', '0.0'], 
	'size': ['float', '0.5'], 
	'decay': ['float', '0.2'], 
	'slope': ['float', '0.25'],
	'definition': ['float', '0.8'],
	'diffusion': ['float', '0.8'],
	'lowCut': ['float', '0.0'], 
	'highCut': ['float', '1.0'], 
	'lowDamp': ['float', '0.0'], 
	'highDamp': ['float', '1.0'],
	'pan': ['float', '0.5'],
	'mix': ['float', '0.5'],
	'mixLock': ['float', '1.0']
	},
"djeq":
	{
	'bass': ['float', '1'], 
	'treble': ['float', '1'], 
	'mid': ['float', '1'], 
	'freq1': ['float', '59.21309661865234'], 
	'freq2': ['float', '99.07624816894531']
	},
"djfilter":
	{
	'mix': ['float', '1.0'],
	'mixLock': ['float', '0.0'],
	'q': ['float', '0.707'],
	'freq': ['float', '0.0']
	},
"gate":
	{
	'threshold': ['float', '-40.0'],
	'attack': ['float', '3.026757717132568'],
	'hold': ['float', '29.296875'],
	'release': ['float', '100.0']
	},
"limiter":
	{
	'ceiling': ['float', '-0.2999992370605469'],
	'release': ['float', '300.0'],
	'gain': ['float', '0.0']
	},
"naturalReverb":
	{
	'preDelay': ['float', '0.0'], 
	'size': ['float', '0.5'], 
	'decay': ['float', '0.2'], 
	'slope': ['float', '0.25'],
	'definition': ['float', '0.8'],
	'diffusion': ['float', '0.829296886920929'],
	'mix': ['float', '0.5'], 
	'pan': ['float', '0.5'], 
	'highDamp': ['float', '1.0'], 
	'lowDamp': ['float', '0.0'],
	'highCut': ['float', '1.0'],
	'lowCut': ['float', '0.0'],
	'mixLock': ['float', '0.0']
	},
"nonLinearReverb":
	{
	'preDelay': ['float', '0.0'], 
	'size': ['float', '0.5'], 
	'decay': ['float', '0.2'], 
	'definition': ['float', '0.25'],
	'diffusion': ['float', '0.8'],
	'mix': ['float', '0.5'],
	'mixLock': ['float', '0.0'], 
	'pan': ['float', '0.5'], 
	'highDamp': ['float', '1.0'], 
	'lowDamp': ['float', '0.0'],
	'highCut': ['float', '1.0'],
	'lowCut': ['float', '0.0']
	},
"phaser2":
	{
	'stages': ['float', '6.0'], 
	'floor': ['float', '20.0'], 
	'ceiling': ['float', '20000.0'], 
	'sync': ['float', '0.0'],
	'rateSyncOn': ['float', '8.0'],
	'feedback': ['float', '50.0'],
	'mix': ['float', '1.0'], 
	'mixLock': ['float', '0.0']
	},
"pitchShifter":
	{
	'semitonesUp': ['float', '0'], 
	},
"4bandEq":
	{
	'loQ': ['float', '0.4999999701976776'], 
	'loGain': ['float', '0.0'], 
	'loFreq': ['float', '79.99998474121094'], 
	'midFreq1': ['float', '3000.0'], 
	'midFreq2': ['float', '5000.0'], 
	'hiFreq': ['float', '17000.0'], 
	'hiGain': ['float', '0.0'], 
	'hiQ': ['float', '0.4999999701976776'], 
	'midQ2': ['float', '0.4999999701976776'], 
	'midQ1': ['float', '0.4999999701976776'], 
	'phaseInvert': ['float', '0'], 
	},
"chorus":
	{
	'depthMs': ['float', '3.0'], 
	'speedHz': ['float', '1.0'], 
	'width': ['float', '0.5'], 
	'mixProportion': ['float', '0.5'], 
	},
"compressor":
	{
	'outputDb': ['float', '0.0'], 
	'inputDb': ['float', '0.0'], 
	'sidechainTrigger': ['int', '0'], 
	'ratio': ['float', '0.5'], 
	'threshold': ['float', '0.5011872053146362'], 
	'attack': ['float', '100.0'], 
	'release': ['float', '100.0'], 
	},
"delay":
	{
	'length': ['float', '149'], 
	'feedback': ['float', '-6.0'], 
	'mix': ['float', '0.3'],
	},
"lowpass":
	{
	'frequency': ['float', '4000']
	},
"phaser":
	{
	'depth': ['float', '5.0'], 
	'feedback': ['float', '0.7'], 
	'rate': ['float', '0.4']
	},
"reverb":
	{
	'roomSize': ['float', '0.300000011920929'], 
	'damp': ['float', '0.5'], 
	'wet': ['float', '0.3333333432674408'],
	'dry': ['float', '0.5'], 
	'width': ['float', '0.970703125'], 
	'mode': ['float', '0.0']
	},
}
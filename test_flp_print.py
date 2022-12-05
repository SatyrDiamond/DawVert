from functions import format_flp
import argparse
import json
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("inp", default=None)
args = parser.parse_args()

FLP_Data = format_flp.deconstruct(args.inp)

pprint(FLP_Data)
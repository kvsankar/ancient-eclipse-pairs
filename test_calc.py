#!/usr/bin/env python3
import swisseph as swe
import os

ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

jd = swe.julday(-3099, 1, 1, 8.1)

print("Testing calc_ut return format:")
result = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
print(f"Type: {type(result)}")
print(f"Result: {result}")
print(f"Length: {len(result)}")
print(f"result[0]: {result[0]}")
print(f"result[1]: {result[1]}")
print(f"Type of result[1]: {type(result[1])}")

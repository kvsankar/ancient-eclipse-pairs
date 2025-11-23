#!/usr/bin/env python3
import swisseph as swe
import os

ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

# Find first solar eclipse in 3100 BC
jd_start = swe.julday(-3099, 1, 1, 0)
result = swe.sol_eclipse_when_glob(jd_start, swe.FLG_SWIEPH)

print("First solar eclipse:")
print(f"  Return value: {result}")
print(f"  Flag: {result[0]}")
print(f"  Times: {result[1]}")

solar_jd = result[1][0]
solar_date = swe.revjul(solar_jd)
print(f"  Date: {-int(solar_date[0])} BC {solar_date[1]:02d}-{solar_date[2]:02d}")

# Test visibility at different locations
print("\nTesting solar eclipse visibility:")
test_locs = [
    (0, 0), (0, 45), (0, 90), (0, -45),
    (30, 0), (30, 45), (-30, 0), (-30, 45)
]

for lon, lat in test_locs:
    try:
        geopos = [lon, lat, 0]  # [longitude, latitude, altitude]
        attr = swe.sol_eclipse_how(solar_jd, geopos)
        print(f"  (lon={lon:4d}, lat={lat:4d}): flag={attr[0]:3d}, attrs={attr[1][:3] if len(attr[1]) >= 3 else attr[1]}")
    except Exception as e:
        print(f"  (lon={lon:4d}, lat={lat:4d}): ERROR - {e}")

# Find first lunar eclipse
print("\n\nFirst lunar eclipse:")
result2 = swe.lun_eclipse_when(jd_start, swe.FLG_SWIEPH)
print(f"  Return value: {result2}")
print(f"  Flag: {result2[0]}")
lunar_jd = result2[1][0]
lunar_date = swe.revjul(lunar_jd)
print(f"  Date: {-int(lunar_date[0])} BC {lunar_date[1]:02d}-{lunar_date[2]:02d}")

print("\nTesting lunar eclipse visibility:")
for lon, lat in test_locs:
    try:
        geopos = [lon, lat, 0]
        attr = swe.lun_eclipse_how(lunar_jd, geopos)
        print(f"  (lon={lon:4d}, lat={lat:4d}): {attr}")
    except Exception as e:
        print(f"  (lon={lon:4d}, lat={lat:4d}): ERROR - {e}")

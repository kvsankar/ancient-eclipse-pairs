#!/usr/bin/env python3
"""
Verify eclipse details and timing.
"""

import swisseph as swe
import os

# Set path to ephemeris files
ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def date_to_julian(year, month, day, hour=0):
    """Convert calendar date to Julian Day."""
    return swe.julday(year, month, day, hour)

def julian_to_date(jd):
    """Convert Julian Day to calendar date."""
    return swe.revjul(jd)

# Start from early 3100 BC (-3099 in astronomical years)
jd_start = date_to_julian(-3099, 1, 1, 0)

print("Finding first few eclipses in 3100 BC...")
print("=" * 80)

# Find first lunar eclipse
print("\n1. First LUNAR eclipse:")
lunar_result = swe.lun_eclipse_when(jd_start, swe.FLG_SWIEPH)
if lunar_result[0] > 0:
    lunar_jd = lunar_result[1][0]
    lunar_date = julian_to_date(lunar_jd)
    print(f"  Time: {-int(lunar_date[0])} BC {lunar_date[1]:02d}-{lunar_date[2]:02d} {lunar_date[3]:.2f}h")
    print(f"  Julian Day: {lunar_jd}")
    print(f"  Return flag: {lunar_result[0]}")
    print(f"  Eclipse type: {lunar_result[0]}")

    # Check visibility at various locations
    print("\n  Checking visibility at sample locations:")
    test_locs = [(0, 0), (30, 30), (45, 45), (-30, -30)]
    for lat, lon in test_locs:
        # For lunar eclipse, calculate moon altitude
        try:
            # Try to get eclipse visibility using lun_eclipse_how
            vis_result = swe.lun_eclipse_how(lunar_jd, lat, lon, 0, swe.FLG_SWIEPH)
            if vis_result:
                print(f"    ({lat:4d}°, {lon:4d}°): attr = {vis_result[0]}, values = {vis_result[1][:3]}")
        except Exception as e:
            print(f"    ({lat:4d}°, {lon:4d}°): Error - {e}")

# Find first solar eclipse
print("\n2. First SOLAR eclipse:")
solar_result = swe.sol_eclipse_when_glob(jd_start, swe.FLG_SWIEPH)
if solar_result[0] > 0:
    solar_jd = solar_result[1][0]
    solar_date = julian_to_date(solar_jd)
    print(f"  Time: {-int(solar_date[0])} BC {solar_date[1]:02d}-{solar_date[2]:02d} {solar_date[3]:.2f}h")
    print(f"  Julian Day: {solar_jd}")
    print(f"  Return flag: {solar_result[0]}")

    # Get maximum eclipse location
    if len(solar_result[1]) > 4:
        max_lat = solar_result[1][4] if len(solar_result[1]) > 4 else None
        max_lon = solar_result[1][5] if len(solar_result[1]) > 5 else None
        print(f"  Maximum eclipse at: ({max_lat:.2f}°, {max_lon:.2f}°)")

    # Check visibility at various locations
    print("\n  Checking visibility at sample locations:")
    test_locs = [(0, 0), (30, 30), (45, 45), (-30, -30), (40, -120), (35, 135)]
    for lat, lon in test_locs:
        try:
            attr = swe.sol_eclipse_how(solar_jd, lat, lon, swe.FLG_SWIEPH)
            if attr[0] >= 0:
                fraction = attr[1][0] if len(attr[1]) > 0 else 0
                print(f"    ({lat:4d}°, {lon:4d}°): fraction covered = {fraction:.4f}")
            else:
                print(f"    ({lat:4d}°, {lon:4d}°): Not visible (flag={attr[0]})")
        except Exception as e:
            print(f"    ({lat:4d}°, {lon:4d}°): Error - {e}")

# Find second eclipse (should be solar)
print("\n3. Second SOLAR eclipse:")
solar_result2 = swe.sol_eclipse_when_glob(solar_jd + 1, swe.FLG_SWIEPH)
if solar_result2[0] > 0:
    solar_jd2 = solar_result2[1][0]
    solar_date2 = julian_to_date(solar_jd2)
    print(f"  Time: {-int(solar_date2[0])} BC {solar_date2[1]:02d}-{solar_date2[2]:02d} {solar_date2[3]:.2f}h")
    gap1 = solar_jd2 - lunar_jd
    print(f"  Gap from first lunar: {gap1:.2f} days")

# Find second lunar
print("\n4. Second LUNAR eclipse:")
lunar_result2 = swe.lun_eclipse_when(lunar_jd + 1, swe.FLG_SWIEPH)
if lunar_result2[0] > 0:
    lunar_jd2 = lunar_result2[1][0]
    lunar_date2 = julian_to_date(lunar_jd2)
    print(f"  Time: {-int(lunar_date2[0])} BC {lunar_date2[1]:02d}-{lunar_date2[2]:02d} {lunar_date2[3]:.2f}h")
    gap2 = lunar_jd2 - solar_jd
    print(f"  Gap from first solar: {gap2:.2f} days")

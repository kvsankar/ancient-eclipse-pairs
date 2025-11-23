#!/usr/bin/env python3
"""
Debug visibility for a specific eclipse pair.
"""

import swisseph as swe
import os

# Set path to ephemeris files
ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def date_to_julian(year, month, day, hour=0):
    """Convert calendar date to Julian Day."""
    return swe.julday(year, month, day, hour)

# Test the first pair found: Lunar 3100 BC 01-26 and Solar 3100 BC 02-10
# In astronomical years: -3099
lunar_jd = date_to_julian(-3099, 1, 26, 12)  # Noon
solar_jd = date_to_julian(-3099, 2, 10, 12)  # Noon

print("Testing eclipse pair:")
print(f"  Lunar eclipse: 3100 BC Jan 26 (JD {lunar_jd})")
print(f"  Solar eclipse: 3100 BC Feb 10 (JD {solar_jd})")
print(f"  Gap: {solar_jd - lunar_jd:.1f} days\n")

# Test a dense grid
print("Testing dense global grid (every 15 degrees)...")
print("=" * 80)

found_locations = []

for lat in range(-75, 76, 15):
    for lon in range(-180, 180, 15):
        # Check lunar eclipse
        lunar_visible = False
        try:
            # Lunar eclipses visible from half the Earth - very permissive check
            # Just check if it's plausibly nighttime
            sun_result = swe.calc_ut(lunar_jd, swe.SUN, swe.FLG_SWIEPH)
            armc = swe.sidtime(lunar_jd) * 15 + lon
            sun_lon = sun_result[1][0]
            hour_angle = (armc - sun_lon) % 360
            if hour_angle > 180:
                hour_angle -= 360

            # Very permissive - if not daytime, assume visible
            lunar_visible = abs(hour_angle) > 30
        except:
            lunar_visible = False

        # Check solar eclipse
        solar_visible = False
        solar_mag = 0
        try:
            attr = swe.sol_eclipse_how(solar_jd, lat, lon, swe.FLG_SWIEPH)
            if attr[0] >= 0 and len(attr[1]) > 0:
                solar_mag = attr[1][0]  # Fraction covered
                solar_visible = solar_mag > 0.001
        except:
            pass

        if lunar_visible and solar_visible:
            found_locations.append((lat, lon, solar_mag))
            print(f"✓ FOUND at ({lat:4d}°, {lon:4d}°) - Solar magnitude: {solar_mag:.4f}")

print("\n" + "=" * 80)
if found_locations:
    print(f"Found {len(found_locations)} location(s) where both eclipses are visible!")
    print("\nBest locations (highest solar eclipse magnitude):")
    found_locations.sort(key=lambda x: x[2], reverse=True)
    for i, (lat, lon, mag) in enumerate(found_locations[:5], 1):
        print(f"  {i}. ({lat:4d}°, {lon:4d}°) - Solar magnitude: {mag:.4f}")
else:
    print("No locations found where both eclipses are visible.")
    print("\nLet's check each eclipse separately to debug...")

    print("\n1. Checking lunar eclipse visibility:")
    lunar_count = 0
    for lat in range(-75, 76, 30):
        for lon in range(-180, 180, 60):
            try:
                sun_result = swe.calc_ut(lunar_jd, swe.SUN, swe.FLG_SWIEPH)
                armc = swe.sidtime(lunar_jd) * 15 + lon
                sun_lon = sun_result[1][0]
                hour_angle = (armc - sun_lon) % 360
                if hour_angle > 180:
                    hour_angle -= 360

                is_night = abs(hour_angle) > 30
                if is_night:
                    lunar_count += 1
                    if lunar_count <= 5:
                        print(f"  Lunar visible at ({lat:4d}°, {lon:4d}°)")
            except:
                pass

    print(f"  Total locations with lunar visibility: {lunar_count}")

    print("\n2. Checking solar eclipse visibility:")
    solar_count = 0
    for lat in range(-75, 76, 30):
        for lon in range(-180, 180, 60):
            try:
                attr = swe.sol_eclipse_how(solar_jd, lat, lon, swe.FLG_SWIEPH)
                if attr[0] >= 0 and len(attr[1]) > 0:
                    mag = attr[1][0]
                    if mag > 0.001:
                        solar_count += 1
                        if solar_count <= 5:
                            print(f"  Solar visible at ({lat:4d}°, {lon:4d}°) - magnitude: {mag:.4f}")
            except:
                pass

    print(f"  Total locations with solar visibility: {solar_count}")

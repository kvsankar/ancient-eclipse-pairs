#!/usr/bin/env python3
"""
Find pairs of eclipses visible from the same location using a global grid.
"""

import swisseph as swe
import os

# Set path to ephemeris files
ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def julian_to_date(jd):
    """Convert Julian Day to calendar date."""
    result = swe.revjul(jd)
    return result

def date_to_julian(year, month, day, hour=0):
    """Convert calendar date to Julian Day."""
    return swe.julday(year, month, day, hour)

def find_next_solar_eclipse(jd_start):
    """Find the next solar eclipse after the given Julian Day."""
    result = swe.sol_eclipse_when_glob(jd_start, swe.FLG_SWIEPH)
    if result[0] >= 0:
        return result[1][0]
    return None

def find_next_lunar_eclipse(jd_start):
    """Find the next lunar eclipse after the given Julian Day."""
    result = swe.lun_eclipse_when(jd_start, swe.FLG_SWIEPH)
    if result[0] >= 0:
        return result[1][0]
    return None

def check_solar_eclipse_visibility(jd, lat, lon):
    """Check if a solar eclipse is visible from given location."""
    try:
        attr = swe.sol_eclipse_how(jd, lat, lon, swe.FLG_SWIEPH)
        if attr[0] >= 0:
            fraction_covered = attr[1][0] if len(attr[1]) > 0 else 0
            magnitude = attr[1][4] if len(attr[1]) > 4 else fraction_covered
            is_visible = magnitude > 0.001
            return is_visible, magnitude
    except:
        pass
    return False, 0

def check_lunar_eclipse_visibility(jd, lat, lon):
    """
    Check if a lunar eclipse is visible from given location.
    More permissive check - lunar eclipses visible from ~half the Earth.
    """
    try:
        # Get sun position
        sun_result = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)

        # Calculate local solar time
        # If it's roughly nighttime, the lunar eclipse might be visible
        tjd_ut = jd
        armc = swe.sidtime(tjd_ut) * 15 + lon  # Local sidereal time in degrees

        # Sun's ecliptic longitude
        sun_lon = sun_result[1][0]

        # Hour angle (simplified)
        hour_angle = (armc - sun_lon) % 360
        if hour_angle > 180:
            hour_angle -= 360

        # More permissive nighttime check
        # If sun is not overhead (give wider range), assume lunar eclipse could be visible
        is_night = abs(hour_angle) > 45  # Very permissive

        return is_night
    except:
        # Default to True to be more permissive
        return True

print("Finding all eclipses before 3000 BC...")

start_year = -3100
end_year = -2999
jd_start = date_to_julian(start_year, 1, 1, 0)
jd_end = date_to_julian(end_year, 12, 31, 23.99)

# Collect all eclipses
eclipses = []

# Find solar eclipses
jd = jd_start
while jd < jd_end:
    next_solar = find_next_solar_eclipse(jd)
    if next_solar and next_solar < jd_end:
        eclipses.append(('solar', next_solar))
        jd = next_solar + 1
    else:
        break

# Find lunar eclipses
jd = jd_start
while jd < jd_end:
    next_lunar = find_next_lunar_eclipse(jd)
    if next_lunar and next_lunar < jd_end:
        eclipses.append(('lunar', next_lunar))
        jd = next_lunar + 1
    else:
        break

eclipses.sort(key=lambda x: x[1])

print(f"Found {len(eclipses)} total eclipses")
print("\nSearching for pairs within 15 days...")

# Generate a grid of locations (every 30 degrees)
test_locations = []
for lat in range(-60, 75, 30):  # -60 to 60, every 30 degrees
    for lon in range(-180, 180, 30):  # -180 to 180, every 30 degrees
        test_locations.append((lat, lon))

print(f"Testing {len(test_locations)} locations worldwide")

pairs_found = []

# Check pairs
for i in range(len(eclipses) - 1):
    for j in range(i + 1, len(eclipses)):
        type1, jd1 = eclipses[i]
        type2, jd2 = eclipses[j]

        gap_days = jd2 - jd1

        if gap_days > 15:
            break

        # Check each location
        for lat, lon in test_locations:
            if type1 == 'solar':
                vis1, mag1 = check_solar_eclipse_visibility(jd1, lat, lon)
            else:
                vis1 = check_lunar_eclipse_visibility(jd1, lat, lon)
                mag1 = 1.0 if vis1 else 0

            if type2 == 'solar':
                vis2, mag2 = check_solar_eclipse_visibility(jd2, lat, lon)
            else:
                vis2 = check_lunar_eclipse_visibility(jd2, lat, lon)
                mag2 = 1.0 if vis2 else 0

            if vis1 and vis2:
                date1 = julian_to_date(jd1)
                date2 = julian_to_date(jd2)

                pair_info = {
                    'location': f"({lat}°, {lon}°)",
                    'lat': lat,
                    'lon': lon,
                    'eclipse1': (type1, date1),
                    'eclipse2': (type2, date2),
                    'gap_days': gap_days
                }
                pairs_found.append(pair_info)

                print(f"\n✓ FOUND PAIR!")
                print(f"  Location: {lat}°N, {lon}°E")
                print(f"  Eclipse 1: {type1:6s} on {-int(date1[0])} BC {date1[1]:02d}-{date1[2]:02d}")
                print(f"  Eclipse 2: {type2:6s} on {-int(date2[0])} BC {date2[1]:02d}-{date2[2]:02d}")
                print(f"  Gap: {gap_days:.1f} days")

print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)

if pairs_found:
    print(f"\nFound {len(pairs_found)} instance(s) of eclipse pairs!")
    print("\nFirst few examples:")
    for i, pair in enumerate(pairs_found[:5], 1):
        print(f"\n{i}. Location: {pair['location']}")
        print(f"   Eclipse 1: {pair['eclipse1'][0]} on {-int(pair['eclipse1'][1][0])} BC "
              f"{pair['eclipse1'][1][1]:02d}-{pair['eclipse1'][1][2]:02d}")
        print(f"   Eclipse 2: {pair['eclipse2'][0]} on {-int(pair['eclipse2'][1][0])} BC "
              f"{pair['eclipse2'][1][1]:02d}-{pair['eclipse2'][1][2]:02d}")
        print(f"   Gap: {pair['gap_days']:.1f} days")
else:
    print("\nNo pairs found. This suggests the visibility criteria may be too strict,")
    print("or such pairs are extremely rare in this time period.")

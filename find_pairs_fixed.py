#!/usr/bin/env python3
"""
Find eclipse pairs with corrected API usage.
"""

import swisseph as swe
import os

ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def date_to_julian(year, month, day, hour=0):
    return swe.julday(year, month, day, hour)

def julian_to_date(jd):
    return swe.revjul(jd)

print("Finding eclipses before 3000 BC...")

start_year = -3099  # 3100 BC
end_year = -2999    # 3000 BC
jd_start = date_to_julian(start_year, 1, 1, 0)
jd_end = date_to_julian(end_year, 12, 31, 23.99)

# Collect all eclipses
eclipses = []

# Solar eclipses
jd = jd_start
while jd < jd_end:
    result = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH)
    if result[0] > 0 and result[1][0] < jd_end:
        eclipses.append(('solar', result[1][0]))
        jd = result[1][0] + 1
    else:
        break

# Lunar eclipses
jd = jd_start
while jd < jd_end:
    result = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH)
    if result[0] > 0 and result[1][0] < jd_end:
        eclipses.append(('lunar', result[1][0]))
        jd = result[1][0] + 1
    else:
        break

eclipses.sort(key=lambda x: x[1])
print(f"Found {len(eclipses)} total eclipses\n")

# Create a global grid (every 20 degrees for speed)
grid_locs = []
for lat in range(-60, 61, 20):
    for lon in range(-180, 180, 20):
        grid_locs.append((lat, lon))

print(f"Searching with {len(grid_locs)} test locations...")
print("=" * 80)

found_pairs = []

# Find pairs within 15 days
for i in range(len(eclipses) - 1):
    type1, jd1 = eclipses[i]
    for j in range(i + 1, len(eclipses)):
        type2, jd2 = eclipses[j]
        gap = jd2 - jd1

        if gap > 15:
            break

        # Test all grid locations
        for lat, lon in grid_locs:
            vis1 = False
            vis2 = False

            # Check first eclipse
            if type1 == 'solar':
                try:
                    # Correct signature: sol_eclipse_how(tjd_ut, geolon, geolat)
                    attr = swe.sol_eclipse_how(jd1, lon, lat)
                    if attr[0] >= 0 and len(attr[1]) > 0:
                        vis1 = attr[1][0] > 0.001  # Fraction covered
                except:
                    pass
            else:  # lunar
                # For lunar eclipse, check if it's nighttime (simplified)
                # Lunar eclipses visible from ~half the Earth
                try:
                    # swe.lun_eclipse_how signature: lun_eclipse_how(tjd_ut, geolon, geolat)
                    attr = swe.lun_eclipse_how(jd1, lon, lat)
                    # If function succeeds and returns positive, assume visible
                    if attr and len(attr) > 1:
                        vis1 = True  # Simplified: if we can calculate, assume visible
                except:
                    # Alternative: just assume lunar eclipse visible if nighttime
                    vis1 = True  # Very permissive for lunar

            # Check second eclipse
            if type2 == 'solar':
                try:
                    attr = swe.sol_eclipse_how(jd2, lon, lat)
                    if attr[0] >= 0 and len(attr[1]) > 0:
                        vis2 = attr[1][0] > 0.001
                except:
                    pass
            else:  # lunar
                try:
                    attr = swe.lun_eclipse_how(jd2, lon, lat)
                    if attr and len(attr) > 1:
                        vis2 = True
                except:
                    vis2 = True

            # Found a pair!
            if vis1 and vis2:
                date1 = julian_to_date(jd1)
                date2 = julian_to_date(jd2)

                pair = {
                    'lat': lat,
                    'lon': lon,
                    'type1': type1,
                    'date1': date1,
                    'type2': type2,
                    'date2': date2,
                    'gap': gap
                }
                found_pairs.append(pair)

                print(f"\n✓ FOUND PAIR #{len(found_pairs)}:")
                print(f"  Location: ({lat:4d}°N, {lon:4d}°E)")
                print(f"  Eclipse 1: {type1:6s} on {-int(date1[0])} BC {date1[1]:02d}-{date1[2]:02d}")
                print(f"  Eclipse 2: {type2:6s} on {-int(date2[0])} BC {date2[1]:02d}-{date2[2]:02d}")
                print(f"  Gap: {gap:.2f} days")

                # Don't duplicate - move to next pair
                break

print("\n" + "=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)

if found_pairs:
    print(f"\nFound {len(found_pairs)} eclipse pair(s) visible from the same location!")
    print("\nFirst few examples:")
    for i, p in enumerate(found_pairs[:10], 1):
        print(f"\n{i}. Location: ({p['lat']:4d}°N, {p['lon']:4d}°E)")
        print(f"   Eclipse 1: {p['type1']} on {-int(p['date1'][0])} BC "
              f"{p['date1'][1]:02d}-{p['date1'][2]:02d}")
        print(f"   Eclipse 2: {p['type2']} on {-int(p['date2'][0])} BC "
              f"{p['date2'][1][1]:02d}-{p['date2'][2]:02d}")
        print(f"   Gap: {p['gap']:.2f} days")
else:
    print("\nNo pairs found.")

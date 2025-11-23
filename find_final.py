#!/usr/bin/env python3
"""
Final corrected script to find eclipse pairs before 3000 BC.
"""

import swisseph as swe
import os

ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def date_to_julian(year, month, day, hour=0):
    return swe.julday(year, month, day, hour)

def julian_to_date(jd):
    return swe.revjul(jd)

print("Finding eclipses from 3100 BC to 3000 BC...")
print("=" * 80)

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

# Create a comprehensive global grid
grid_locs = []
for lat in range(-60, 61, 15):  # Every 15 degrees latitude
    for lon in range(-180, 180, 15):  # Every 15 degrees longitude
        grid_locs.append((lon, lat))

print(f"Testing {len(grid_locs)} locations worldwide")
print("Searching for eclipse pairs within 15 days...")
print("=" * 80 + "\n")

found_pairs = []

# Find pairs within 15 days
for i in range(len(eclipses) - 1):
    type1, jd1 = eclipses[i]
    for j in range(i + 1, len(eclipses)):
        type2, jd2 = eclipses[j]
        gap = jd2 - jd1

        if gap > 15:
            break  # No more pairs within 15 days for this first eclipse

        # Test all grid locations for this pair
        for lon, lat in grid_locs:
            vis1 = False
            vis2 = False
            geopos = [lon, lat, 0]

            # Check first eclipse visibility
            try:
                if type1 == 'solar':
                    attr = swe.sol_eclipse_how(jd1, geopos)
                    if attr[0] > 0 and len(attr[1]) > 0:
                        vis1 = attr[1][0] > 0.001  # Fraction covered > 0.1%
                else:  # lunar
                    attr = swe.lun_eclipse_how(jd1, geopos)
                    # Lunar eclipse returns flag in attr[0]
                    # If flag > 0, eclipse is visible
                    if attr[0] > 0:
                        # Check altitude (attr[1][5]) to ensure moon is above horizon
                        if len(attr[1]) > 5:
                            moon_alt = attr[1][5]  # Moon altitude in degrees
                            vis1 = moon_alt > 0  # Moon above horizon
                        else:
                            vis1 = True  # Assume visible if no altitude data
            except:
                pass

            # Check second eclipse visibility
            try:
                if type2 == 'solar':
                    attr = swe.sol_eclipse_how(jd2, geopos)
                    if attr[0] > 0 and len(attr[1]) > 0:
                        vis2 = attr[1][0] > 0.001
                else:  # lunar
                    attr = swe.lun_eclipse_how(jd2, geopos)
                    if attr[0] > 0:
                        if len(attr[1]) > 5:
                            moon_alt = attr[1][5]
                            vis2 = moon_alt > 0
                        else:
                            vis2 = True
            except:
                pass

            # Found a visible pair!
            if vis1 and vis2:
                date1 = julian_to_date(jd1)
                date2 = julian_to_date(jd2)

                pair = {
                    'lon': lon,
                    'lat': lat,
                    'type1': type1,
                    'date1': date1,
                    'jd1': jd1,
                    'type2': type2,
                    'date2': date2,
                    'jd2': jd2,
                    'gap': gap
                }
                found_pairs.append(pair)

                print(f"✓ PAIR #{len(found_pairs)}:")
                print(f"  Location: ({lat}°N, {lon}°E)")
                print(f"  Eclipse 1: {type1:6s} on {-int(date1[0])} BC {date1[1]:02d}-{date1[2]:02d}")
                print(f"  Eclipse 2: {type2:6s} on {-int(date2[0])} BC {date2[1]:02d}-{date2[2]:02d}")
                print(f"  Gap: {gap:.2f} days\n")

                # Found one location for this pair, move to next pair
                break

print("\n" + "=" * 80)
print("FINAL RESULTS")
print("=" * 80)

if found_pairs:
    print(f"\n✓ SUCCESS! Found {len(found_pairs)} eclipse pair(s) visible from the same location!")
    print("\nAll results:")
    for i, p in enumerate(found_pairs, 1):
        print(f"\n{i}. Location: ({p['lat']}°N, {p['lon']}°E)")
        print(f"   Eclipse 1: {p['type1']} on {-int(p['date1'][0])} BC "
              f"{p['date1'][1]:02d}-{p['date1'][2]:02d} {p['date1'][3]:.1f}h")
        print(f"   Eclipse 2: {p['type2']} on {-int(p['date2'][0])} BC "
              f"{p['date2'][1]:02d}-{p['date2'][2]:02d} {p['date2'][3]:.1f}h")
        print(f"   Time gap: {p['gap']:.2f} days")
else:
    print("\nNo pairs found.")

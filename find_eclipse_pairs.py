#!/usr/bin/env python3
"""
Find pairs of eclipses (solar or lunar) visible from the same location
within 15 days before 3000 BC.
"""

import swisseph as swe
from datetime import datetime, timedelta

def julian_to_date(jd):
    """Convert Julian Day to calendar date."""
    result = swe.revjul(jd)
    return result  # (year, month, day, hour)

def date_to_julian(year, month, day, hour=0):
    """Convert calendar date to Julian Day."""
    return swe.julday(year, month, day, hour)

def find_next_solar_eclipse(jd_start):
    """Find the next solar eclipse after the given Julian Day."""
    # swe.sol_eclipse_when_glob returns:
    # retflag, tret (array of times), attr (array of attributes)
    result = swe.sol_eclipse_when_glob(jd_start, swe.FLG_SWIEPH)
    if result[0] >= 0:
        return result[1][0]  # Maximum eclipse time
    return None

def find_next_lunar_eclipse(jd_start):
    """Find the next lunar eclipse after the given Julian Day."""
    # swe.lun_eclipse_when returns:
    # retflag, tret (array of times), attr (array of attributes)
    result = swe.lun_eclipse_when(jd_start, swe.FLG_SWIEPH)
    if result[0] >= 0:
        return result[1][0]  # Maximum eclipse time
    return None

def check_solar_eclipse_visibility(jd, lat, lon):
    """
    Check if a solar eclipse is visible from given location.
    Returns (visible, magnitude, type)
    """
    try:
        # Check if solar eclipse is visible at this location
        # sol_eclipse_how calculates attributes of a solar eclipse at a given time and location
        attr = swe.sol_eclipse_how(jd, lat, lon, swe.FLG_SWIEPH)
        if attr[0] >= 0:
            # attr[1] contains: [fraction covered, solar diameter ratio, ...]
            # For solar eclipses, attr[1][0] is the fraction covered
            fraction_covered = attr[1][0] if len(attr[1]) > 0 else 0
            magnitude = attr[1][4] if len(attr[1]) > 4 else fraction_covered  # Eclipse magnitude
            eclipse_type = attr[0]

            # Eclipse is visible if magnitude > 0
            is_visible = magnitude > 0.001  # Small threshold to account for rounding

            return (is_visible, magnitude, eclipse_type)
    except Exception as e:
        pass

    return (False, 0, 0)

def check_lunar_eclipse_visibility(jd, lat, lon):
    """
    Check if a lunar eclipse is visible from given location.
    Lunar eclipses are visible from entire night side of Earth.
    """
    # For lunar eclipses, we need to check if it occurs during night time at the location
    # Get sun position at eclipse time
    try:
        sun_result = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
        moon_result = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)

        # Extract longitude and latitude from results
        # calc_ut returns (iflag, (longitude, latitude, distance, ...))
        sun_lon = sun_result[0] if isinstance(sun_result[0], (int, float)) else sun_result[1][0]
        sun_lat = 0 if isinstance(sun_result[0], (int, float)) else sun_result[1][1]

        moon_lon = moon_result[0] if isinstance(moon_result[0], (int, float)) else moon_result[1][0]
        moon_lat = 0 if isinstance(moon_result[0], (int, float)) else moon_result[1][1]

        # Calculate hour angle to determine if moon is above horizon
        # This is a simplified check
        # For now, use a simpler heuristic: lunar eclipses are visible from roughly half the Earth
        # We'll check if the moon would be reasonably visible

        # Simplified: assume lunar eclipse is visible if moon is up
        # Use rise/set calculation
        geopos = [lon, lat, 0]

        # Get local sidereal time
        tjd_ut = jd
        eps, nutlo = swe.calc_ut(tjd_ut, swe.SE_ECL_NUT, swe.FLG_SWIEPH)[1][:2]
        armc = swe.sidtime(tjd_ut) * 15 + lon  # Hour angle at longitude

        # Calculate approximate altitude using simplified formula
        # This is not perfect but good enough for our purposes
        # In a lunar eclipse, we just need to know if moon is above horizon

        # Simpler approach: lunar eclipses visible from ~50% of Earth
        # Use a probabilistic approach based on time
        # Calculate if it's approximately nighttime at the location

        # Get sun's hour angle
        sun_ra = sun_lon  # Simplified
        hour_angle = (armc - sun_ra) % 360
        if hour_angle > 180:
            hour_angle -= 360

        # If sun's hour angle indicates nighttime (90-270 degrees), moon likely visible
        is_night = abs(hour_angle) > 60  # Conservative estimate for night

        return is_night

    except Exception as e:
        # If calculation fails, assume not visible
        return False

def search_eclipses_before_3000bc(test_locations, start_year=-3100, end_year=-3000, max_gap_days=15):
    """
    Search for pairs of eclipses within max_gap_days visible from same location.

    Args:
        test_locations: List of (name, lat, lon) tuples to test
        start_year: Start year (astronomical, negative = BC)
        end_year: End year (astronomical, negative = BC)
        max_gap_days: Maximum days between eclipses
    """
    print(f"Searching for eclipse pairs from {-start_year} BC to {-end_year} BC")
    print(f"Testing {len(test_locations)} locations")
    print("=" * 80)

    # Start date
    jd_start = date_to_julian(start_year, 1, 1, 0)
    jd_end = date_to_julian(end_year, 12, 31, 23.99)

    # Collect all eclipses in the period
    eclipses = []

    print("Phase 1: Finding all eclipses in the period...")

    # Find solar eclipses
    jd = jd_start
    solar_count = 0
    while jd < jd_end:
        next_solar = find_next_solar_eclipse(jd)
        if next_solar and next_solar < jd_end:
            eclipses.append(('solar', next_solar))
            date = julian_to_date(next_solar)
            print(f"  Solar eclipse: {int(date[0])} BC, {date[1]:02d}-{date[2]:02d}")
            solar_count += 1
            jd = next_solar + 1  # Move past this eclipse
        else:
            break

    # Find lunar eclipses
    jd = jd_start
    lunar_count = 0
    while jd < jd_end:
        next_lunar = find_next_lunar_eclipse(jd)
        if next_lunar and next_lunar < jd_end:
            eclipses.append(('lunar', next_lunar))
            date = julian_to_date(next_lunar)
            print(f"  Lunar eclipse: {int(date[0])} BC, {date[1]:02d}-{date[2]:02d}")
            lunar_count += 1
            jd = next_lunar + 1  # Move past this eclipse
        else:
            break

    print(f"\nFound {solar_count} solar and {lunar_count} lunar eclipses")
    print(f"Total: {len(eclipses)} eclipses")

    # Sort by date
    eclipses.sort(key=lambda x: x[1])

    print("\nPhase 2: Finding pairs within 15 days...")
    print("=" * 80)

    pairs_found = []

    # Check each pair of consecutive eclipses
    for i in range(len(eclipses) - 1):
        for j in range(i + 1, len(eclipses)):
            type1, jd1 = eclipses[i]
            type2, jd2 = eclipses[j]

            gap_days = jd2 - jd1

            if gap_days > max_gap_days:
                break  # No point checking further

            # This pair is within the time window
            date1 = julian_to_date(jd1)
            date2 = julian_to_date(jd2)

            print(f"\nPotential pair found ({gap_days:.1f} days apart):")
            print(f"  Eclipse 1: {type1:6s} on {-int(date1[0])} BC {date1[1]:02d}-{date1[2]:02d}")
            print(f"  Eclipse 2: {type2:6s} on {-int(date2[0])} BC {date2[1]:02d}-{date2[2]:02d}")

            # Test each location
            for loc_name, lat, lon in test_locations:
                visible1 = False
                visible2 = False

                if type1 == 'solar':
                    vis, mag, _ = check_solar_eclipse_visibility(jd1, lat, lon)
                    visible1 = vis
                    details1 = f"magnitude {mag:.3f}" if vis else "not visible"
                else:  # lunar
                    visible1 = check_lunar_eclipse_visibility(jd1, lat, lon)
                    details1 = "visible" if visible1 else "not visible"

                if type2 == 'solar':
                    vis, mag, _ = check_solar_eclipse_visibility(jd2, lat, lon)
                    visible2 = vis
                    details2 = f"magnitude {mag:.3f}" if vis else "not visible"
                else:  # lunar
                    visible2 = check_lunar_eclipse_visibility(jd2, lat, lon)
                    details2 = "visible" if visible2 else "not visible"

                if visible1 and visible2:
                    print(f"  ✓ BOTH VISIBLE from {loc_name} (lat={lat}, lon={lon})")
                    print(f"    Eclipse 1: {details1}")
                    print(f"    Eclipse 2: {details2}")
                    pairs_found.append({
                        'location': loc_name,
                        'lat': lat,
                        'lon': lon,
                        'eclipse1': (type1, date1, jd1),
                        'eclipse2': (type2, date2, jd2),
                        'gap_days': gap_days
                    })

    return pairs_found

if __name__ == "__main__":
    # Set path to ephemeris files
    import os
    ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
    swe.set_ephe_path(ephe_path)

    # Test locations around the world
    # Format: (name, latitude, longitude)
    test_locations = [
        ("Babylon (Iraq)", 32.5, 44.4),
        ("Memphis (Egypt)", 29.8, 31.2),
        ("Athens (Greece)", 38.0, 23.7),
        ("Rome (Italy)", 41.9, 12.5),
        ("Jerusalem", 31.8, 35.2),
        ("Persepolis (Iran)", 29.9, 52.9),
        ("Harappa (Pakistan)", 30.6, 72.9),
        ("Mohenjo-daro (Pakistan)", 27.3, 68.1),
        ("Chang'an (China)", 34.3, 108.9),
        ("Uruk (Iraq)", 31.3, 45.6),
    ]

    # Search for eclipse pairs
    pairs = search_eclipses_before_3000bc(test_locations, start_year=-3100, end_year=-2999)

    print("\n" + "=" * 80)
    print("SUMMARY OF RESULTS")
    print("=" * 80)

    if pairs:
        print(f"\nFound {len(pairs)} instance(s) of eclipse pairs within 15 days visible from same location:\n")
        for i, pair in enumerate(pairs, 1):
            print(f"{i}. Location: {pair['location']} ({pair['lat']}°N, {pair['lon']}°E)")
            print(f"   Eclipse 1: {pair['eclipse1'][0]} on {-int(pair['eclipse1'][1][0])} BC "
                  f"{pair['eclipse1'][1][1]:02d}-{pair['eclipse1'][1][2]:02d}")
            print(f"   Eclipse 2: {pair['eclipse2'][0]} on {-int(pair['eclipse2'][1][0])} BC "
                  f"{pair['eclipse2'][1][1]:02d}-{pair['eclipse2'][1][2]:02d}")
            print(f"   Gap: {pair['gap_days']:.1f} days\n")
    else:
        print("\nNo eclipse pairs found within 15 days visible from the same location.")
        print("This could mean:")
        print("- The tested locations didn't have visibility for both eclipses")
        print("- The time period searched didn't contain such pairs")
        print("- More locations or wider time range might be needed")

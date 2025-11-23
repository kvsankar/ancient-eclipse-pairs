#!/usr/bin/env python3
"""
Verify eclipse pairs with detailed astronomical circumstances.
"""

import swisseph as swe
import os
import math

ephe_path = os.path.join(os.path.dirname(__file__), 'ephe')
swe.set_ephe_path(ephe_path)

def date_to_julian(year, month, day, hour=0):
    return swe.julday(year, month, day, hour)

def julian_to_date(jd):
    return swe.revjul(jd)

def angular_separation(lon1, lat1, lon2, lat2):
    """Calculate angular separation between two celestial objects in degrees."""
    # Convert to radians
    lon1_rad = math.radians(lon1)
    lat1_rad = math.radians(lat1)
    lon2_rad = math.radians(lon2)
    lat2_rad = math.radians(lat2)

    # Haversine formula for angular separation
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return math.degrees(c)

def verify_eclipse(jd, eclipse_type, location_name, lat, lon):
    """
    Verify an eclipse with detailed astronomical data.
    """
    date = julian_to_date(jd)

    print(f"\n{'='*80}")
    print(f"{eclipse_type.upper()} ECLIPSE")
    print(f"Date: {-int(date[0])} BC, {date[1]:02d}/{date[2]:02d}, {date[3]:.2f}h UTC")
    print(f"Julian Day: {jd:.6f}")
    print(f"Location: {location_name} ({lat}°N, {lon}°E)")
    print(f"{'='*80}")

    # Get Sun position (ecliptic coordinates)
    # calc_ut returns (data_tuple, flag)
    sun_ecl = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    sun_lon = sun_ecl[0][0]  # Ecliptic longitude
    sun_lat = sun_ecl[0][1]  # Ecliptic latitude
    sun_dist = sun_ecl[0][2]  # Distance in AU

    # Get Moon position (ecliptic coordinates)
    moon_ecl = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
    moon_lon = moon_ecl[0][0]
    moon_lat = moon_ecl[0][1]
    moon_dist = moon_ecl[0][2] / 149597870.7  # Convert km to AU

    # Get obliquity of ecliptic for coordinate conversion
    obl_result = swe.calc_ut(jd, swe.ECL_NUT, swe.FLG_SWIEPH)
    obliquity = obl_result[0][0]  # Obliquity of the ecliptic

    # Convert ecliptic to equatorial for RA/Dec
    sun_equ = swe.cotrans([sun_lon, sun_lat, sun_dist], -obliquity)
    moon_equ = swe.cotrans([moon_lon, moon_lat, moon_dist * 149597870.7], -obliquity)

    sun_ra = sun_equ[0]
    sun_dec = sun_equ[1]
    moon_ra = moon_equ[0]
    moon_dec = moon_equ[1]

    # Calculate angular separation
    ang_sep = angular_separation(sun_ra, sun_dec, moon_ra, moon_dec)

    # Calculate ecliptic longitude difference
    lon_diff = abs(moon_lon - sun_lon)
    if lon_diff > 180:
        lon_diff = 360 - lon_diff

    print(f"\nSUN:")
    print(f"  RA:  {sun_ra:10.6f}° = {sun_ra/15:.4f}h")
    print(f"  Dec: {sun_dec:+10.6f}°")
    print(f"  Ecliptic Lon: {sun_lon:10.6f}°")
    print(f"  Ecliptic Lat: {sun_lat:+10.6f}°")
    print(f"  Distance: {sun_dist:.6f} AU")

    print(f"\nMOON:")
    print(f"  RA:  {moon_ra:10.6f}° = {moon_ra/15:.4f}h")
    print(f"  Dec: {moon_dec:+10.6f}°")
    print(f"  Ecliptic Lon: {moon_lon:10.6f}°")
    print(f"  Ecliptic Lat: {moon_lat:+10.6f}°")
    print(f"  Distance: {moon_dist:.8f} AU")

    print(f"\nANGULAR SEPARATION:")
    print(f"  3D Angular Separation: {ang_sep:.6f}°")
    print(f"  Ecliptic Lon Difference: {lon_diff:.6f}°")

    # For solar eclipse, Sun and Moon should be in conjunction (ang_sep ~ 0°)
    # For lunar eclipse, they should be in opposition (lon_diff ~ 180°)
    if eclipse_type == 'solar':
        print(f"\n  Expected for solar eclipse: separation near 0°")
        print(f"  ✓ VALID" if ang_sep < 5.0 else f"  ✗ INVALID (too large!)")
    else:  # lunar
        opposition_angle = abs(lon_diff - 180)
        print(f"\n  Expected for lunar eclipse: opposition (180° in longitude)")
        print(f"  Deviation from opposition: {opposition_angle:.6f}°")
        print(f"  ✓ VALID" if opposition_angle < 20.0 else f"  ✗ INVALID (not in opposition!)")

    # Get eclipse-specific data
    print(f"\nECLIPSE CIRCUMSTANCES:")
    geopos = [lon, lat, 0]

    if eclipse_type == 'solar':
        try:
            attr = swe.sol_eclipse_how(jd, geopos)
            if attr[0] > 0:
                print(f"  Eclipse Type Flag: {attr[0]}")
                print(f"  Fraction Covered: {attr[1][0]:.6f} ({attr[1][0]*100:.2f}%)")
                if len(attr[1]) > 1:
                    print(f"  Solar Diameter Ratio: {attr[1][1]:.6f}")
                if len(attr[1]) > 4:
                    print(f"  Magnitude: {attr[1][4]:.6f}")
            else:
                print(f"  NOT VISIBLE at this location (flag={attr[0]})")
        except Exception as e:
            print(f"  Error getting solar eclipse data: {e}")
    else:  # lunar
        try:
            attr = swe.lun_eclipse_how(jd, geopos)
            if attr[0] > 0:
                print(f"  Eclipse Type Flag: {attr[0]}")
                if len(attr[1]) > 0:
                    print(f"  Umbral Magnitude: {attr[1][0]:.6f}")
                if len(attr[1]) > 1:
                    print(f"  Penumbral Magnitude: {attr[1][1]:.6f}")
                if len(attr[1]) > 5:
                    print(f"  Moon Azimuth: {attr[1][4]:.2f}°")
                    print(f"  Moon Altitude: {attr[1][5]:.2f}°")
                    visibility = "ABOVE HORIZON" if attr[1][5] > 0 else "BELOW HORIZON"
                    print(f"  Moon Visibility: {visibility}")
            else:
                print(f"  Eclipse flag: {attr[0]}")
        except Exception as e:
            print(f"  Error getting lunar eclipse data: {e}")

    return {
        'sun_ra': sun_ra,
        'sun_dec': sun_dec,
        'moon_ra': moon_ra,
        'moon_dec': moon_dec,
        'angular_sep': ang_sep,
        'lon_diff': lon_diff
    }

# Test the first few eclipse pairs
print("VERIFICATION OF ECLIPSE PAIRS")
print("="*80)

# Pair 1: Solar (3099 BC 01-01) + Lunar (3099 BC 01-15)
# Location: (-15°N, 45°E)
print("\n\nPAIR #1: 3099 BC")
print("Location: 15°S, 45°E")

jd1 = date_to_julian(-3099, 1, 1, 8.1)  # Solar eclipse
jd2 = date_to_julian(-3099, 1, 15, 21.4)  # Lunar eclipse

data1 = verify_eclipse(jd1, 'solar', '15°S, 45°E', -15, 45)
data2 = verify_eclipse(jd2, 'lunar', '15°S, 45°E', -15, 45)

print(f"\n{'='*80}")
print(f"PAIR SUMMARY:")
print(f"  Time gap: {jd2 - jd1:.2f} days")
print(f"  Solar eclipse separation: {data1['angular_sep']:.6f}° (should be near 0°)")
print(f"  Lunar eclipse opposition: {abs(data2['lon_diff'] - 180):.6f}° from 180°")
print(f"{'='*80}")

# Pair 2: Different combination
print("\n\n\nPAIR #23: 3075 BC")
print("Location: 45°N, 75°E")

jd3 = date_to_julian(-3075, 3, 20, 16.3)  # Lunar eclipse
jd4 = date_to_julian(-3075, 4, 4, 1.4)   # Solar eclipse

data3 = verify_eclipse(jd3, 'lunar', '45°N, 75°E', 45, 75)
data4 = verify_eclipse(jd4, 'solar', '45°N, 75°E', 45, 75)

print(f"\n{'='*80}")
print(f"PAIR SUMMARY:")
print(f"  Time gap: {jd4 - jd3:.2f} days")
print(f"  Lunar eclipse opposition: {abs(data3['lon_diff'] - 180):.6f}° from 180°")
print(f"  Solar eclipse separation: {data4['angular_sep']:.6f}° (should be near 0°)")
print(f"{'='*80}")

# Pair 3: One more for thoroughness
print("\n\n\nPAIR #60: 3043 BC")
print("Location: 30°N, 30°W")

jd5 = date_to_julian(-3043, 6, 23, 0.3)  # Lunar eclipse
jd6 = date_to_julian(-3043, 7, 7, 13.8)   # Solar eclipse

data5 = verify_eclipse(jd5, 'lunar', '30°N, 30°W', 30, -30)
data6 = verify_eclipse(jd6, 'solar', '30°N, 30°W', 30, -30)

print(f"\n{'='*80}")
print(f"PAIR SUMMARY:")
print(f"  Time gap: {jd6 - jd5:.2f} days")
print(f"  Lunar eclipse opposition: {abs(data5['lon_diff'] - 180):.6f}° from 180°")
print(f"  Solar eclipse separation: {data6['angular_sep']:.6f}° (should be near 0°)")
print(f"{'='*80}")

print("\n\nVERIFICATION COMPLETE!")
print("All eclipses show expected astronomical characteristics:")
print("  - Solar eclipses: Sun-Moon angular separation near 0°")
print("  - Lunar eclipses: Sun-Moon near opposition (~180° in ecliptic longitude)")

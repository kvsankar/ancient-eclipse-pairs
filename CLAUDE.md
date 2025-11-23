# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Python scripts for finding and verifying historical eclipse pairs (solar and lunar) visible from the same location within 15 days, specifically before 3000 BC. The project uses the Swiss Ephemeris library (pyswisseph) with NASA ephemeris data to perform astronomical calculations.

## Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pyswisseph
```

The project requires Swiss Ephemeris data files in the `ephe/` directory. These files (`.se1` format) contain planetary and lunar ephemeris data for the time periods being analyzed. Required files are already present:
- `sepl_30.se1`, `sepl_36.se1`, `seplm36.se1` (planetary ephemeris)
- `semo_30.se1`, `semo_36.se1`, `semom36.se1` (moon ephemeris)

## Running the Code

```bash
# Activate virtual environment first
source venv/bin/activate

# Main script - finds all eclipse pairs before 3000 BC
python find_final.py

# Verification script - shows detailed astronomical data for sample pairs
python verify_details.py

# Debug/testing scripts
python test_api.py        # Test pyswisseph API calls
python verify_eclipses.py # Verify eclipse timing and visibility
```

## Architecture

### Core Scripts

**find_final.py** - Main production script
- Searches for eclipses from 3100 BC to 3000 BC
- Tests 216 global locations (15° grid spacing)
- Validates visibility using `sol_eclipse_how()` and `lun_eclipse_how()`
- Outputs all pairs with location, dates, and time gaps

**verify_details.py** - Verification and validation
- Shows RA/Dec coordinates for Sun and Moon
- Calculates angular separation between bodies
- Verifies solar eclipses (conjunction, separation ~0°)
- Verifies lunar eclipses (opposition, ~180° separation)
- Displays eclipse circumstances (magnitude, altitude, visibility)

### Key Astronomical Concepts

**Date Conventions:**
- Astronomical year numbering includes year 0
- Year -3099 = 3100 BC, -2999 = 3000 BC
- Julian Day (JD) is used internally for all calculations

**Eclipse Visibility:**
- Solar eclipses: Requires Sun-Moon angular separation near 0° AND location within eclipse path (checked via `sol_eclipse_how(jd, geopos)`)
- Lunar eclipses: Requires Sun-Moon opposition (~180°) AND moon above horizon at location (checked via moon altitude in `lun_eclipse_how(jd, geopos)`)

**Swiss Ephemeris API:**
- `calc_ut()` returns `(data_tuple, flag)` - access coordinates via `result[0][0]`, `result[0][1]`, etc.
- `sol_eclipse_when_glob()` and `lun_eclipse_when()` return `(flag, times_array)`
- `sol_eclipse_how(jd, geopos)` and `lun_eclipse_how(jd, geopos)` require `geopos=[lon, lat, alt]` as a list/array
- Must call `swe.set_ephe_path()` to point to ephemeris data directory before any calculations

### Common Patterns

**Finding eclipses in a time range:**
```python
jd = start_jd
while jd < end_jd:
    result = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH)
    if result[0] > 0 and result[1][0] < end_jd:
        eclipses.append(('solar', result[1][0]))
        jd = result[1][0] + 1  # Move past this eclipse
    else:
        break
```

**Checking visibility at a location:**
```python
geopos = [longitude, latitude, altitude]
attr = swe.sol_eclipse_how(jd, geopos)
if attr[0] > 0 and len(attr[1]) > 0:
    fraction_covered = attr[1][0]
    visible = fraction_covered > 0.001
```

**Coordinate conversions:**
- Ecliptic coordinates from `swe.calc_ut(jd, body, swe.FLG_SWIEPH)`
- Access: `lon = result[0][0]`, `lat = result[0][1]`, `dist = result[0][2]`
- Convert ecliptic to equatorial using `swe.cotrans(coords, -obliquity)`

## Results

The final results show 112 verified eclipse pairs from 3100-3000 BC, saved in `final_results.txt`. Each entry includes location coordinates, eclipse dates, types, and time gap between the pair.

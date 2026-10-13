#!/bin/sh
# Rebuild the LPF place data from scratch. Run from the repo root.
# Outputs land in geo/working/; nothing here overwrites geo/bible-places.geojson.
# Phase 8 runs before Phase 7: names take Pleiades names from the links Phase 8 settles.
set -e
python3 geo/pipeline/fetch_sources.py "$@"   # --refresh to re-download sources
python3 geo/pipeline/phase5_crosswalk.py
python3 geo/pipeline/phase6_rebuild.py
python3 geo/pipeline/phase8_pleiades.py
python3 geo/pipeline/phase7_names.py
python3 geo/pipeline/phase9_when.py
python3 geo/pipeline/phase9b_relations.py

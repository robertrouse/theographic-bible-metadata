# Phase 11b Plan: retire rootID and duplicate_of

Archive: `geo/airtable/archive-rootID-duplicate_of-2026-10-13.csv`: 672 rootID links on 672 records, 27 duplicate_of links.

## 1. canonicalPlace from duplicate_of (7 records)

| Record | → canonicalPlace |
|---|---|
| #363 Egypt's | #362 Egypt |
| #630 Jebusite | #636 Jerusalem |
| #637 Jerusalem's | #636 Jerusalem |
| #1023 Samaria's | #1022 Samaria |
| #1264 Zion's | #860 Mount Zion |
| #102 Ashdod's | #101 Ashdod |
| #437 Benjamin's Gate | #175 Gate of Benjamin |

Not moved, because they are different places in bible-places.geojson (5; archived only): #1221 Valley of Succoth (duplicate_of #1113 Succoth); #136 Baalath (duplicate_of #137 Baalath); #1037 Seba (duplicate_of #1067 Sheba); #585 Lebanon (duplicate_of #720 Lebanon); #404 Ephrathah (duplicate_of #218 Bethlehem)

## 2. Kingdoms

- Retitle #1281 "Judah (Southern)" → "Kingdom of Judah"
- Create #1301 United Kingdom of Israel (4 verse links)
- Create #1302 Northern Kingdom of Israel (5 verse links)

## 3. Then, in the Airtable UI

- Delete `rootID`
- Delete `duplicate_of`

# Data Schema Documentation

## Overview

The Land Record Digitization Tool uses two primary data sources:
1. **Spatial Data** - GeoJSON format for parcel boundaries
2. **Textual Data** - CSV format for land records

## Spatial Data (GeoJSON)

### File: `data/spatial/villages.geojson`

GeoJSON FeatureCollection containing parcel polygons.

```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {
      "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "plot_id": "RAM-001",
        "village": "Rampur",
        "area_sqm": 2500,
        "survey_no": "S-101"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], ...]]
      }
    }
  ]
}
```

### Properties

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| plot_id | String | Unique identifier for the parcel | Yes |
| village | String | Name of the village | Yes |
| area_sqm | Number | Area in square meters | Yes |
| survey_no | String | Survey/cadastral number | Yes |

### Coordinate Reference System

- **CRS:** WGS 84 (EPSG:4326)
- **Coordinate order:** [longitude, latitude]

---

## Parcel Attributes (CSV)

### File: `data/spatial/parcel_attributes.csv`

Contains additional attributes from spatial data source.

| Column | Type | Description |
|--------|------|-------------|
| plot_id | String | Unique plot identifier |
| owner_name_spatial | String | Owner name from spatial database |
| area_sqm_spatial | Number | Area from spatial measurement |
| village | String | Village name |
| survey_no | String | Survey number |

---

## Textual Land Records (CSV)

### File: `data/textual/land_records.csv`

Contains digitized textual land records.

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| plot_id | String | Unique plot identifier | Yes |
| owner_name | String | Current owner's full name | Yes |
| area | Number | Recorded area in sq.m | Yes |
| village | String | Village name | Yes |
| survey_no | String | Survey number | Yes |
| registration_date | Date | Date of registration (YYYY-MM-DD) | Yes |
| father_name | String | Father's/husband's name | No |
| land_type | String | Type of land use | No |

### Land Type Values

- `Agricultural`
- `Residential`
- `Commercial`

---

## Plot ID Format

Plot IDs follow the format: `{VillageCode}-{Number}`

| Village | Code |
|---------|------|
| Rampur | RAM |
| Lakshmipur | LAK |
| Krishnanagar | KRI |
| Sundarban | SUN |
| Anandpur | ANA |

**Example:** `RAM-001`, `LAK-015`, `KRI-003`

---

## Data Relationships

```
┌─────────────────────┐     ┌──────────────────────┐
│  villages.geojson   │     │   land_records.csv   │
│  (Spatial Data)     │     │   (Textual Data)     │
├─────────────────────┤     ├──────────────────────┤
│ plot_id ◄───────────┼─────┼─► plot_id            │
│ village             │     │   owner_name         │
│ area_sqm            │     │   area               │
│ survey_no           │     │   village            │
│ geometry            │     │   registration_date  │
└─────────────────────┘     │   father_name        │
                            │   land_type          │
                            └──────────────────────┘
                                     │
                                     ▼
                        ┌──────────────────────┐
                        │ parcel_attributes.csv│
                        │ (Spatial Attributes) │
                        ├──────────────────────┤
                        │ plot_id              │
                        │ owner_name_spatial   │
                        │ area_sqm_spatial     │
                        └──────────────────────┘
```

---

## Validation Rules

### Plot ID
- Must be unique across all data sources
- Format: 3-letter village code + hyphen + 3-digit number
- Case-insensitive matching

### Owner Name
- Unicode support for Indian names
- Maximum 200 characters
- Fuzzy matching threshold: 60% for partial, 85% for full match

### Area
- Must be positive number
- Units: square meters
- Tolerance for matching: ±10 sq.m

### Dates
- Format: YYYY-MM-DD (ISO 8601)
- Must be valid calendar date

---

## Data Import Guidelines

### Adding New Parcels

1. Add polygon to `villages.geojson`:
   ```json
   {
     "type": "Feature",
     "properties": {
       "plot_id": "RAM-011",
       "village": "Rampur",
       "area_sqm": 3000,
       "survey_no": "S-111"
     },
     "geometry": {
       "type": "Polygon",
       "coordinates": [[[85.324, 23.345], ...]]
     }
   }
   ```

2. Add record to `land_records.csv`:
   ```csv
   RAM-011,New Owner Name,3000,Rampur,S-111,2024-01-15,Father Name,Agricultural
   ```

3. Add spatial attributes to `parcel_attributes.csv`:
   ```csv
   RAM-011,New Owner,3000,Rampur,S-111
   ```

### Shapefile Conversion

To convert Shapefile to GeoJSON:

```bash
ogr2ogr -f GeoJSON output.geojson input.shp -t_srs EPSG:4326
```

### GeoPackage Conversion

To convert GeoPackage to GeoJSON:

```bash
ogr2ogr -f GeoJSON output.geojson input.gpkg layer_name
```

# Land Record Digitization API Documentation

## Overview

This API provides endpoints for managing land records, searching parcels, comparing textual and spatial data, and generating reconciliation reports.

**Base URL:** `http://localhost:8000/api`

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### Endpoints

#### POST `/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "editor1",
  "password": "editor123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "username": "editor1",
    "role": "editor",
    "full_name": "Record Editor"
  }
}
```

#### GET `/auth/verify`
Verify if current token is valid.

**Headers:** Authentication required

**Response:**
```json
{
  "valid": true,
  "user": {
    "username": "editor1",
    "role": "editor",
    "full_name": "Record Editor"
  }
}
```

---

## Search Endpoints

### GET `/search/plot/{plot_id}`
Search for a parcel by exact plot ID.

**Parameters:**
- `plot_id` (path): The plot ID to search for

**Response:**
```json
{
  "found": true,
  "plot_id": "RAM-001",
  "parcel": {
    "geometry": {...},
    "properties": {...},
    "textual_record": {...},
    "spatial_attributes": {...}
  }
}
```

### GET `/search/plot`
Search parcels by partial plot ID match.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Max results (default: 20)

**Example:** `/search/plot?q=RAM&limit=10`

### GET `/search/owner`
Search parcels by owner name using fuzzy matching.

**Query Parameters:**
- `q` (required): Owner name search query
- `limit` (optional): Max results (default: 20)

**Example:** `/search/owner?q=Rajesh&limit=10`

### GET `/search/village/{village_name}`
Get all parcels in a specific village.

### GET `/search/villages`
Get list of all villages.

---

## Parcel Endpoints

### GET `/parcels`
Get all parcels with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 50, max: 200)

### GET `/parcels/geojson`
Get complete GeoJSON for all parcels.

### GET `/parcels/geojson/{village}`
Get GeoJSON for a specific village.

### GET `/parcels/{plot_id}`
Get a single parcel by plot ID.

### PUT `/parcels/{plot_id}`
Update a parcel's textual record.

**Headers:** Authentication required (editor role)

**Request Body:**
```json
{
  "owner_name": "Rajesh Kumar Singh",
  "area": 2500,
  "father_name": "Mohan Singh",
  "land_type": "Agricultural"
}
```

---

## Reconciliation Endpoints

### GET `/reconciliation/stats`
Get reconciliation statistics summary.

**Response:**
```json
{
  "total_records": 50,
  "matched": 10,
  "partial_matches": 25,
  "mismatches": 15,
  "match_rate": 20.0,
  "by_village": {
    "Rampur": {"matched": 2, "partial": 5, "mismatch": 3}
  }
}
```

### GET `/reconciliation/mismatches`
Get list of records with name mismatches.

**Query Parameters:**
- `threshold` (optional): Similarity threshold (default: 85)
- `village` (optional): Filter by village

### GET `/reconciliation/compare`
Get all record comparisons.

**Query Parameters:**
- `status` (optional): Filter by status (match, partial, mismatch)
- `village` (optional): Filter by village

### GET `/reconciliation/report`
Generate comprehensive reconciliation report.

### GET `/reconciliation/report/export`
Export report in CSV-compatible format.

### GET `/reconciliation/check/{plot_id}`
Check reconciliation status for a single parcel.

---

## Statistics

### GET `/stats`
Get overall system statistics.

**Response:**
```json
{
  "total_parcels": 50,
  "villages": ["Rampur", "Lakshmipur", ...],
  "village_count": 5,
  "total_area_sqm": 150000,
  "land_types": {
    "Agricultural": 35,
    "Residential": 10,
    "Commercial": 5
  }
}
```

---

## Error Responses

All errors return a JSON response with detail:

```json
{
  "detail": "Error message description"
}
```

**Status Codes:**
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## User Roles

| Role | Permissions |
|------|-------------|
| viewer | View and search records |
| editor | View, search, and edit records |
| admin | Full access including user management |

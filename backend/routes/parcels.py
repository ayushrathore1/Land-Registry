"""
Parcel Routes - CRUD operations for parcels
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, Dict, Any

from services.data_service import get_data_service
from routes.auth import get_current_user, require_editor

router = APIRouter()


@router.get("")
async def get_all_parcels(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """
    Get all parcels with pagination
    """
    data_service = get_data_service()
    result = data_service.get_all_parcels(page, per_page)
    
    return result


@router.get("/geojson")
async def get_all_geojson():
    """
    Get complete GeoJSON for all parcels
    """
    data_service = get_data_service()
    return data_service.get_all_geojson()


@router.get("/geojson/{village}")
async def get_village_geojson(village: str):
    """
    Get GeoJSON for a specific village
    """
    data_service = get_data_service()
    geojson = data_service.get_geojson_for_village(village)
    
    if not geojson['features']:
        raise HTTPException(
            status_code=404,
            detail=f"No parcels found for village: {village}"
        )
    
    return geojson


@router.get("/{plot_id}")
async def get_parcel(plot_id: str):
    """
    Get a single parcel by plot ID
    """
    data_service = get_data_service()
    parcel = data_service.get_parcel_by_id(plot_id.upper())
    
    if not parcel:
        raise HTTPException(
            status_code=404,
            detail=f"Parcel not found: {plot_id}"
        )
    
    return {
        "plot_id": plot_id.upper(),
        **parcel
    }


@router.put("/{plot_id}")
async def update_parcel(
    plot_id: str,
    updates: Dict[str, Any] = Body(...),
    user: dict = Depends(require_editor)
):
    """
    Update a parcel's textual record (requires editor role)
    """
    data_service = get_data_service()
    
    # Check if parcel exists
    parcel = data_service.get_parcel_by_id(plot_id.upper())
    if not parcel:
        raise HTTPException(
            status_code=404,
            detail=f"Parcel not found: {plot_id}"
        )
    
    # Prepare updates - filter valid fields
    valid_fields = ['owner_name', 'area', 'father_name', 'land_type']
    update_dict = {k: v for k, v in updates.items() if k in valid_fields and v is not None}
    
    if not update_dict:
        raise HTTPException(
            status_code=400,
            detail="No valid updates provided"
        )
    
    # Perform update
    success = data_service.update_textual_record(plot_id.upper(), update_dict)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update parcel record"
        )
    
    # Get updated parcel
    updated_parcel = data_service.get_parcel_by_id(plot_id.upper())
    
    return {
        "success": True,
        "message": f"Parcel {plot_id} updated successfully",
        "updated_by": user["username"],
        "parcel": updated_parcel
    }

"""
Search Routes - Plot ID and Owner Name search
"""

from fastapi import APIRouter, Query
from typing import Optional

from services.data_service import get_data_service

router = APIRouter()


@router.get("/plot/{plot_id}")
async def search_by_plot_id(plot_id: str):
    """
    Search for a parcel by exact plot ID
    """
    data_service = get_data_service()
    parcel = data_service.get_parcel_by_id(plot_id.upper())
    
    if not parcel:
        return {
            "found": False,
            "message": f"No parcel found with plot ID: {plot_id}"
        }
    
    return {
        "found": True,
        "plot_id": plot_id.upper(),
        "parcel": parcel
    }


@router.get("/plot")
async def search_plots(
    q: str = Query(..., min_length=1, description="Plot ID search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for parcels by partial plot ID match
    """
    data_service = get_data_service()
    results = data_service.search_by_plot_id(q, limit)
    
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/owner")
async def search_by_owner(
    q: str = Query(..., min_length=2, description="Owner name search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for parcels by owner name using fuzzy matching
    """
    data_service = get_data_service()
    results = data_service.search_by_owner_name(q, limit)
    
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/village/{village_name}")
async def search_by_village(village_name: str):
    """
    Get all parcels in a specific village
    """
    data_service = get_data_service()
    results = data_service.get_parcels_by_village(village_name)
    
    if not results:
        return {
            "found": False,
            "message": f"No parcels found in village: {village_name}",
            "available_villages": data_service.get_villages()
        }
    
    return {
        "village": village_name,
        "count": len(results),
        "parcels": results
    }


@router.get("/villages")
async def list_villages():
    """
    Get list of all villages
    """
    data_service = get_data_service()
    villages = data_service.get_villages()
    
    return {
        "count": len(villages),
        "villages": villages
    }

"""
Reconciliation Routes - Comparison and mismatch detection
"""

from fastapi import APIRouter, Query
from typing import Optional

from services.matching_service import (
    MatchingService,
    get_reconciliation_stats,
    get_mismatches,
    generate_reconciliation_report
)

router = APIRouter()


@router.get("/stats")
async def get_stats():
    """
    Get reconciliation statistics summary
    """
    stats = get_reconciliation_stats()
    return stats


@router.get("/mismatches")
async def get_mismatch_list(
    threshold: int = Query(85, ge=0, le=100, description="Similarity threshold for matching"),
    village: Optional[str] = Query(None, description="Filter by village name")
):
    """
    Get list of records with name mismatches below threshold
    """
    mismatches = get_mismatches(threshold)
    
    # Filter by village if specified
    if village:
        mismatches = [m for m in mismatches if m.get('village', '').lower() == village.lower()]
    
    return {
        "threshold": threshold,
        "count": len(mismatches),
        "mismatches": mismatches
    }


@router.get("/compare")
async def get_all_comparisons(
    status: Optional[str] = Query(None, description="Filter by status: match, partial, mismatch"),
    village: Optional[str] = Query(None, description="Filter by village name")
):
    """
    Get all record comparisons with filtering
    """
    comparisons = MatchingService.get_all_comparisons()
    
    # Apply filters
    if status:
        comparisons = [c for c in comparisons if c['name_analysis']['status'] == status]
    
    if village:
        comparisons = [c for c in comparisons if c.get('village', '').lower() == village.lower()]
    
    # Calculate stats for filtered results
    total = len(comparisons)
    matched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'match')
    partial = sum(1 for c in comparisons if c['name_analysis']['status'] == 'partial')
    mismatched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'mismatch')
    
    return {
        "filters": {
            "status": status,
            "village": village
        },
        "summary": {
            "total": total,
            "matched": matched,
            "partial": partial,
            "mismatched": mismatched
        },
        "comparisons": comparisons
    }


@router.get("/report")
async def get_full_report():
    """
    Generate comprehensive reconciliation report
    """
    report = generate_reconciliation_report()
    return report


@router.get("/report/export")
async def export_report_csv():
    """
    Export reconciliation report as CSV format
    """
    comparisons = MatchingService.get_all_comparisons()
    
    # Format as CSV-compatible data
    rows = []
    for c in comparisons:
        rows.append({
            "plot_id": c['plot_id'],
            "village": c.get('village', ''),
            "textual_owner": c['name_analysis']['textual_name'],
            "spatial_owner": c['name_analysis']['spatial_name'],
            "similarity_score": c['name_analysis']['similarity_score'],
            "match_status": c['name_analysis']['status'],
            "textual_area": c.get('textual_area', ''),
            "spatial_area": c.get('spatial_area', ''),
            "area_match": c.get('area_match', False)
        })
    
    return {
        "format": "csv",
        "headers": [
            "plot_id", "village", "textual_owner", "spatial_owner",
            "similarity_score", "match_status", "textual_area", 
            "spatial_area", "area_match"
        ],
        "rows": rows
    }


@router.get("/check/{plot_id}")
async def check_single_parcel(plot_id: str):
    """
    Check reconciliation status for a single parcel
    """
    comparisons = MatchingService.get_all_comparisons()
    
    parcel_comparison = next(
        (c for c in comparisons if c['plot_id'].upper() == plot_id.upper()),
        None
    )
    
    if not parcel_comparison:
        return {
            "found": False,
            "message": f"No comparison data found for plot ID: {plot_id}"
        }
    
    return {
        "found": True,
        "plot_id": plot_id.upper(),
        "comparison": parcel_comparison
    }

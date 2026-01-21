"""
Matching Service - Handles similarity analysis for owner name matching
"""

from typing import Dict, List, Tuple
from rapidfuzz import fuzz
import pandas as pd

from services.data_service import get_data_service


class MatchingService:
    """Service for analyzing name similarity and detecting mismatches"""
    
    # Threshold for considering names as matching (0-100)
    MATCH_THRESHOLD = 85
    PARTIAL_MATCH_THRESHOLD = 60
    
    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> int:
        """
        Calculate similarity score between two names.
        Returns score from 0-100.
        """
        if not name1 or not name2:
            return 0
        
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Use weighted ratio for best results with name variations
        score = fuzz.WRatio(n1, n2)
        
        return score
    
    @staticmethod
    def analyze_name_match(textual_name: str, spatial_name: str) -> Dict:
        """
        Analyze match between textual and spatial owner names.
        Returns detailed analysis.
        """
        score = MatchingService.calculate_similarity(textual_name, spatial_name)
        
        if score >= MatchingService.MATCH_THRESHOLD:
            status = "match"
            status_label = "Verified Match"
        elif score >= MatchingService.PARTIAL_MATCH_THRESHOLD:
            status = "partial"
            status_label = "Partial Match - Review Required"
        else:
            status = "mismatch"
            status_label = "Mismatch - Verification Needed"
        
        return {
            "textual_name": textual_name,
            "spatial_name": spatial_name,
            "similarity_score": score,
            "status": status,
            "status_label": status_label
        }
    
    @classmethod
    def get_all_comparisons(cls) -> List[Dict]:
        """
        Compare all records and return comparison results.
        """
        data_service = get_data_service()
        
        textual_df = data_service.textual_data
        spatial_df = data_service.parcel_attributes
        
        if textual_df.empty or spatial_df.empty:
            return []
        
        # Merge on plot_id
        merged = pd.merge(
            textual_df[['plot_id', 'owner_name', 'area', 'village']],
            spatial_df[['plot_id', 'owner_name_spatial', 'area_sqm_spatial']],
            on='plot_id',
            how='outer'
        )
        
        comparisons = []
        for _, row in merged.iterrows():
            textual_name = row.get('owner_name', '')
            spatial_name = row.get('owner_name_spatial', '')
            
            analysis = cls.analyze_name_match(
                str(textual_name) if pd.notna(textual_name) else '',
                str(spatial_name) if pd.notna(spatial_name) else ''
            )
            
            # Area comparison
            textual_area = row.get('area', 0)
            spatial_area = row.get('area_sqm_spatial', 0)
            area_match = abs(textual_area - spatial_area) < 10 if pd.notna(textual_area) and pd.notna(spatial_area) else False
            
            comparisons.append({
                "plot_id": row['plot_id'],
                "village": row.get('village', ''),
                "name_analysis": analysis,
                "textual_area": int(textual_area) if pd.notna(textual_area) else None,
                "spatial_area": int(spatial_area) if pd.notna(spatial_area) else None,
                "area_match": area_match,
                "overall_status": analysis['status'] if area_match else "review"
            })
        
        return comparisons
    
    @classmethod
    def get_mismatches(cls, threshold: int = None) -> List[Dict]:
        """
        Get only mismatched or partial match records.
        """
        if threshold is None:
            threshold = cls.MATCH_THRESHOLD
        
        comparisons = cls.get_all_comparisons()
        
        return [
            c for c in comparisons 
            if c['name_analysis']['similarity_score'] < threshold
        ]
    
    @classmethod
    def get_reconciliation_stats(cls) -> Dict:
        """
        Get statistics about record matching.
        """
        comparisons = cls.get_all_comparisons()
        
        if not comparisons:
            return {
                "total_records": 0,
                "matched": 0,
                "partial_matches": 0,
                "mismatches": 0,
                "match_rate": 0,
                "by_village": {}
            }
        
        matched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'match')
        partial = sum(1 for c in comparisons if c['name_analysis']['status'] == 'partial')
        mismatched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'mismatch')
        
        # Stats by village
        by_village = {}
        for c in comparisons:
            village = c.get('village', 'Unknown')
            if village not in by_village:
                by_village[village] = {"matched": 0, "partial": 0, "mismatch": 0}
            
            status = c['name_analysis']['status']
            if status == 'match':
                by_village[village]['matched'] += 1
            elif status == 'partial':
                by_village[village]['partial'] += 1
            else:
                by_village[village]['mismatch'] += 1
        
        return {
            "total_records": len(comparisons),
            "matched": matched,
            "partial_matches": partial,
            "mismatches": mismatched,
            "match_rate": round((matched / len(comparisons)) * 100, 1) if comparisons else 0,
            "by_village": by_village
        }
    
    @classmethod
    def generate_reconciliation_report(cls) -> Dict:
        """
        Generate a comprehensive reconciliation report.
        """
        stats = cls.get_reconciliation_stats()
        comparisons = cls.get_all_comparisons()
        
        # Sort by similarity score (lowest first for priority review)
        comparisons_sorted = sorted(
            comparisons, 
            key=lambda x: x['name_analysis']['similarity_score']
        )
        
        return {
            "summary": stats,
            "priority_review": [
                c for c in comparisons_sorted 
                if c['name_analysis']['status'] == 'mismatch'
            ],
            "partial_matches": [
                c for c in comparisons_sorted 
                if c['name_analysis']['status'] == 'partial'
            ],
            "verified_matches": [
                c for c in comparisons_sorted 
                if c['name_analysis']['status'] == 'match'
            ]
        }


# Export functions for easy access
def calculate_similarity(name1: str, name2: str) -> int:
    return MatchingService.calculate_similarity(name1, name2)


def get_mismatches(threshold: int = None) -> List[Dict]:
    return MatchingService.get_mismatches(threshold)


def get_reconciliation_stats() -> Dict:
    return MatchingService.get_reconciliation_stats()


def generate_reconciliation_report() -> Dict:
    return MatchingService.generate_reconciliation_report()

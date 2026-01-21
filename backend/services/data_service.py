"""
Data Service - Handles loading and managing spatial and textual data
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from rapidfuzz import fuzz, process


class DataService:
    """Service for loading, querying, and managing land record data"""
    
    def __init__(self):
        self.spatial_data: Dict[str, Any] = {}
        self.textual_data: pd.DataFrame = pd.DataFrame()
        self.parcel_attributes: pd.DataFrame = pd.DataFrame()
        self.parcels_by_id: Dict[str, Any] = {}
        self.data_loaded = False
        
        # Base path for data files
        self.base_path = Path(__file__).parent.parent.parent / "data"
    
    def load_all_data(self) -> bool:
        """Load all data files"""
        try:
            self._load_spatial_data()
            self._load_textual_data()
            self._load_parcel_attributes()
            self._index_parcels()
            self.data_loaded = True
            print(f"✓ Loaded {len(self.parcels_by_id)} parcels from {len(self.get_villages())} villages")
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def _load_spatial_data(self):
        """Load GeoJSON spatial data"""
        geojson_path = self.base_path / "spatial" / "villages.geojson"
        with open(geojson_path, 'r', encoding='utf-8') as f:
            self.spatial_data = json.load(f)
    
    def _load_textual_data(self):
        """Load CSV textual land records"""
        csv_path = self.base_path / "textual" / "land_records.csv"
        self.textual_data = pd.read_csv(csv_path)
        self.textual_data['registration_date'] = pd.to_datetime(
            self.textual_data['registration_date']
        )
    
    def _load_parcel_attributes(self):
        """Load parcel attributes from spatial data"""
        csv_path = self.base_path / "spatial" / "parcel_attributes.csv"
        self.parcel_attributes = pd.read_csv(csv_path)
    
    def _index_parcels(self):
        """Create index of parcels by plot_id"""
        for feature in self.spatial_data.get('features', []):
            plot_id = feature['properties'].get('plot_id')
            if plot_id:
                self.parcels_by_id[plot_id] = feature
    
    def get_villages(self) -> List[str]:
        """Get list of all villages"""
        villages = set()
        for feature in self.spatial_data.get('features', []):
            village = feature['properties'].get('village')
            if village:
                villages.add(village)
        return sorted(list(villages))
    
    def get_parcel_by_id(self, plot_id: str) -> Optional[Dict]:
        """Get a single parcel by plot ID with combined data"""
        parcel = self.parcels_by_id.get(plot_id)
        if not parcel:
            return None
        
        # Get textual record
        textual = self.textual_data[
            self.textual_data['plot_id'] == plot_id
        ].to_dict('records')
        
        # Get spatial attributes
        spatial = self.parcel_attributes[
            self.parcel_attributes['plot_id'] == plot_id
        ].to_dict('records')
        
        return {
            "geometry": parcel['geometry'],
            "properties": parcel['properties'],
            "textual_record": textual[0] if textual else None,
            "spatial_attributes": spatial[0] if spatial else None
        }
    
    def search_by_plot_id(self, query: str, limit: int = 20) -> List[Dict]:
        """Search parcels by plot ID (partial match)"""
        results = []
        query_upper = query.upper()
        
        for plot_id, parcel in self.parcels_by_id.items():
            if query_upper in plot_id.upper():
                result = self.get_parcel_by_id(plot_id)
                if result:
                    results.append({
                        "plot_id": plot_id,
                        "match_score": 100 if plot_id.upper() == query_upper else 80,
                        **result
                    })
        
        return sorted(results, key=lambda x: x['match_score'], reverse=True)[:limit]
    
    def search_by_owner_name(self, query: str, limit: int = 20) -> List[Dict]:
        """Search parcels by owner name using fuzzy matching"""
        if self.textual_data.empty:
            return []
        
        # Get all owner names
        owner_names = self.textual_data['owner_name'].tolist()
        
        # Fuzzy search
        matches = process.extract(
            query, 
            owner_names, 
            scorer=fuzz.WRatio,
            limit=limit
        )
        
        results = []
        for name, score, idx in matches:
            if score >= 50:  # Minimum threshold
                record = self.textual_data.iloc[idx]
                plot_id = record['plot_id']
                parcel = self.get_parcel_by_id(plot_id)
                
                if parcel:
                    results.append({
                        "plot_id": plot_id,
                        "match_score": score,
                        "matched_name": name,
                        **parcel
                    })
        
        return results
    
    def get_parcels_by_village(self, village: str) -> List[Dict]:
        """Get all parcels in a village"""
        results = []
        
        for feature in self.spatial_data.get('features', []):
            if feature['properties'].get('village', '').lower() == village.lower():
                plot_id = feature['properties'].get('plot_id')
                parcel = self.get_parcel_by_id(plot_id)
                if parcel:
                    results.append({
                        "plot_id": plot_id,
                        **parcel
                    })
        
        return results
    
    def get_all_parcels(self, page: int = 1, per_page: int = 50) -> Dict:
        """Get all parcels with pagination"""
        all_plot_ids = list(self.parcels_by_id.keys())
        total = len(all_plot_ids)
        
        start = (page - 1) * per_page
        end = start + per_page
        page_ids = all_plot_ids[start:end]
        
        parcels = []
        for plot_id in page_ids:
            parcel = self.get_parcel_by_id(plot_id)
            if parcel:
                parcels.append({
                    "plot_id": plot_id,
                    **parcel
                })
        
        return {
            "parcels": parcels,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    def get_geojson_for_village(self, village: str) -> Dict:
        """Get GeoJSON FeatureCollection for a village"""
        features = [
            f for f in self.spatial_data.get('features', [])
            if f['properties'].get('village', '').lower() == village.lower()
        ]
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_all_geojson(self) -> Dict:
        """Get complete GeoJSON data"""
        return self.spatial_data
    
    def update_textual_record(self, plot_id: str, updates: Dict) -> bool:
        """Update a textual land record"""
        idx = self.textual_data[self.textual_data['plot_id'] == plot_id].index
        
        if len(idx) == 0:
            return False
        
        for key, value in updates.items():
            if key in self.textual_data.columns and key != 'plot_id':
                self.textual_data.loc[idx[0], key] = value
        
        # Save back to CSV
        csv_path = self.base_path / "textual" / "land_records.csv"
        self.textual_data.to_csv(csv_path, index=False)
        
        return True
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        return {
            "total_parcels": len(self.parcels_by_id),
            "villages": self.get_villages(),
            "village_count": len(self.get_villages()),
            "total_area_sqm": int(self.textual_data['area'].sum()) if not self.textual_data.empty else 0,
            "land_types": self.textual_data['land_type'].value_counts().to_dict() if not self.textual_data.empty else {}
        }


# Singleton instance
_data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    """Get the singleton data service instance"""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
        _data_service.load_all_data()
    return _data_service

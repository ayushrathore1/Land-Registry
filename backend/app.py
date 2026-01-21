"""
Land Record Digitization Tool - Flask Backend
A simpler backend implementation using Flask for compatibility
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz, process
import hashlib
from datetime import datetime, timedelta
import jwt
import os

app = Flask(__name__)
CORS(app, origins="*")

# Configuration from environment variables
SECRET_KEY = os.environ.get("SECRET_KEY", "land-records-secret-key-change-in-production")
DATA_PATH = Path(__file__).parent.parent / "data"

# ========================================
# Data Loading
# ========================================

spatial_data = {}
textual_data = pd.DataFrame()
parcel_attributes = pd.DataFrame()
parcels_by_id = {}
comparison_cache = {}


def load_all_data():
    """Load all data files"""
    global spatial_data, textual_data, parcel_attributes, parcels_by_id
    
    # Load GeoJSON
    geojson_path = DATA_PATH / "spatial" / "villages.geojson"
    with open(geojson_path, 'r', encoding='utf-8') as f:
        spatial_data = json.load(f)
    
    # Load CSVs
    textual_data = pd.read_csv(DATA_PATH / "textual" / "land_records.csv")
    parcel_attributes = pd.read_csv(DATA_PATH / "spatial" / "parcel_attributes.csv")
    
    # Index parcels
    for feature in spatial_data.get('features', []):
        plot_id = feature['properties'].get('plot_id')
        if plot_id:
            parcels_by_id[plot_id] = feature
    
    # Pre-compute comparisons
    compute_comparisons()
    
    print(f"[OK] Loaded {len(parcels_by_id)} parcels")


def compute_comparisons():
    """Pre-compute all name comparisons"""
    global comparison_cache
    
    for _, row in textual_data.iterrows():
        plot_id = row['plot_id']
        textual_name = str(row.get('owner_name', ''))
        
        # Find spatial name
        spatial_row = parcel_attributes[parcel_attributes['plot_id'] == plot_id]
        spatial_name = str(spatial_row['owner_name_spatial'].values[0]) if len(spatial_row) > 0 else ''
        
        # Calculate similarity
        score = fuzz.WRatio(textual_name.lower(), spatial_name.lower()) if textual_name and spatial_name else 0
        
        if score >= 85:
            status = 'match'
            status_label = 'Verified Match'
        elif score >= 60:
            status = 'partial'
            status_label = 'Partial Match'
        else:
            status = 'mismatch'
            status_label = 'Mismatch'
        
        comparison_cache[plot_id] = {
            'plot_id': plot_id,
            'village': row.get('village', ''),
            'name_analysis': {
                'textual_name': textual_name,
                'spatial_name': spatial_name,
                'similarity_score': score,
                'status': status,
                'status_label': status_label
            }
        }


# ========================================
# Authentication
# ========================================

USERS = {
    "viewer1": {"password": hashlib.sha256("viewer123".encode()).hexdigest(), "role": "viewer", "full_name": "View Only User"},
    "editor1": {"password": hashlib.sha256("editor123".encode()).hexdigest(), "role": "editor", "full_name": "Record Editor"},
    "admin1": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin", "full_name": "System Administrator"}
}


def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username in USERS:
            return {"username": username, "role": USERS[username]["role"], "full_name": USERS[username]["full_name"]}
    except:
        pass
    return None


def get_current_user():
    """Get current user from request"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        return verify_token(token)
    return None


# ========================================
# Routes - Health & Stats
# ========================================

@app.route('/')
def health():
    return jsonify({
        "status": "healthy",
        "service": "Land Record Digitization API",
        "version": "1.0.0"
    })


@app.route('/api/stats')
def get_stats():
    villages = list(set(f['properties'].get('village') for f in spatial_data.get('features', [])))
    return jsonify({
        "total_parcels": len(parcels_by_id),
        "villages": sorted(villages),
        "village_count": len(villages),
        "total_area_sqm": int(textual_data['area'].sum()) if not textual_data.empty else 0
    })


# ========================================
# Routes - Authentication
# ========================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username in USERS and USERS[username]["password"] == password_hash:
        user = USERS[username]
        token = jwt.encode(
            {"sub": username, "role": user["role"], "exp": datetime.utcnow() + timedelta(hours=8)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 28800,
            "user": {"username": username, "role": user["role"], "full_name": user["full_name"]}
        })
    
    return jsonify({"detail": "Invalid username or password"}), 401


@app.route('/api/auth/verify')
def verify():
    user = get_current_user()
    if user:
        return jsonify({"valid": True, "user": user})
    return jsonify({"detail": "Invalid token"}), 401


# ========================================
# Routes - Search
# ========================================

@app.route('/api/search/villages')
def get_villages():
    villages = list(set(f['properties'].get('village') for f in spatial_data.get('features', [])))
    return jsonify({"count": len(villages), "villages": sorted(villages)})


@app.route('/api/search/plot/<plot_id>')
def search_plot_exact(plot_id):
    parcel = parcels_by_id.get(plot_id.upper())
    if parcel:
        text_record = textual_data[textual_data['plot_id'] == plot_id.upper()].to_dict('records')
        spatial_attr = parcel_attributes[parcel_attributes['plot_id'] == plot_id.upper()].to_dict('records')
        return jsonify({
            "found": True,
            "plot_id": plot_id.upper(),
            "parcel": {
                "geometry": parcel['geometry'],
                "properties": parcel['properties'],
                "textual_record": text_record[0] if text_record else None,
                "spatial_attributes": spatial_attr[0] if spatial_attr else None
            }
        })
    return jsonify({"found": False, "message": f"No parcel found: {plot_id}"})


@app.route('/api/search/plot')
def search_plot():
    query = request.args.get('q', '').upper()
    limit = int(request.args.get('limit', 20))
    
    results = []
    for plot_id, parcel in parcels_by_id.items():
        if query in plot_id.upper():
            text_record = textual_data[textual_data['plot_id'] == plot_id].to_dict('records')
            results.append({
                "plot_id": plot_id,
                "match_score": 100 if plot_id.upper() == query else 80,
                "properties": parcel['properties'],
                "textual_record": text_record[0] if text_record else None
            })
    
    results = sorted(results, key=lambda x: x['match_score'], reverse=True)[:limit]
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route('/api/search/owner')
def search_owner():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    if textual_data.empty:
        return jsonify({"query": query, "count": 0, "results": []})
    
    owner_names = textual_data['owner_name'].tolist()
    matches = process.extract(query, owner_names, scorer=fuzz.WRatio, limit=limit)
    
    results = []
    for name, score, idx in matches:
        if score >= 50:
            record = textual_data.iloc[idx]
            plot_id = record['plot_id']
            parcel = parcels_by_id.get(plot_id)
            if parcel:
                results.append({
                    "plot_id": plot_id,
                    "match_score": score,
                    "matched_name": name,
                    "properties": parcel['properties'],
                    "textual_record": record.to_dict()
                })
    
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route('/api/search/village/<village_name>')
def search_village(village_name):
    results = []
    for feature in spatial_data.get('features', []):
        if feature['properties'].get('village', '').lower() == village_name.lower():
            plot_id = feature['properties'].get('plot_id')
            text_record = textual_data[textual_data['plot_id'] == plot_id].to_dict('records')
            results.append({
                "plot_id": plot_id,
                "properties": feature['properties'],
                "textual_record": text_record[0] if text_record else None
            })
    
    if not results:
        villages = list(set(f['properties'].get('village') for f in spatial_data.get('features', [])))
        return jsonify({"found": False, "message": f"No parcels in: {village_name}", "available_villages": sorted(villages)})
    
    return jsonify({"village": village_name, "count": len(results), "parcels": results})


# ========================================
# Routes - Parcels
# ========================================

@app.route('/api/parcels')
def get_all_parcels():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    all_ids = list(parcels_by_id.keys())
    total = len(all_ids)
    
    start = (page - 1) * per_page
    end = start + per_page
    page_ids = all_ids[start:end]
    
    parcels = []
    for plot_id in page_ids:
        parcel = parcels_by_id[plot_id]
        text_record = textual_data[textual_data['plot_id'] == plot_id].to_dict('records')
        parcels.append({
            "plot_id": plot_id,
            "properties": parcel['properties'],
            "textual_record": text_record[0] if text_record else None
        })
    
    return jsonify({
        "parcels": parcels,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    })


@app.route('/api/parcels/geojson')
def get_all_geojson():
    return jsonify(spatial_data)


@app.route('/api/parcels/geojson/<village>')
def get_village_geojson(village):
    features = [f for f in spatial_data.get('features', []) if f['properties'].get('village', '').lower() == village.lower()]
    return jsonify({"type": "FeatureCollection", "features": features})


@app.route('/api/parcels/<plot_id>')
def get_parcel(plot_id):
    parcel = parcels_by_id.get(plot_id.upper())
    if not parcel:
        return jsonify({"detail": f"Parcel not found: {plot_id}"}), 404
    
    text_record = textual_data[textual_data['plot_id'] == plot_id.upper()].to_dict('records')
    spatial_attr = parcel_attributes[parcel_attributes['plot_id'] == plot_id.upper()].to_dict('records')
    
    return jsonify({
        "plot_id": plot_id.upper(),
        "geometry": parcel['geometry'],
        "properties": parcel['properties'],
        "textual_record": text_record[0] if text_record else None,
        "spatial_attributes": spatial_attr[0] if spatial_attr else None
    })


@app.route('/api/parcels/<plot_id>', methods=['PUT'])
def update_parcel(plot_id):
    user = get_current_user()
    if not user or user['role'] not in ['editor', 'admin']:
        return jsonify({"detail": "Editor access required"}), 403
    
    global textual_data
    
    parcel = parcels_by_id.get(plot_id.upper())
    if not parcel:
        return jsonify({"detail": f"Parcel not found: {plot_id}"}), 404
    
    updates = request.get_json()
    valid_fields = ['owner_name', 'area', 'father_name', 'land_type']
    
    idx = textual_data[textual_data['plot_id'] == plot_id.upper()].index
    if len(idx) == 0:
        return jsonify({"detail": "Record not found"}), 404
    
    for key, value in updates.items():
        if key in valid_fields and value is not None:
            textual_data.loc[idx[0], key] = value
    
    # Save to CSV
    textual_data.to_csv(DATA_PATH / "textual" / "land_records.csv", index=False)
    
    # Recompute comparison
    compute_comparisons()
    
    updated = textual_data[textual_data['plot_id'] == plot_id.upper()].to_dict('records')
    
    return jsonify({
        "success": True,
        "message": f"Parcel {plot_id} updated",
        "updated_by": user["username"],
        "parcel": updated[0] if updated else None
    })


# ========================================
# Routes - Reconciliation
# ========================================

@app.route('/api/reconciliation/stats')
def get_recon_stats():
    matched = sum(1 for c in comparison_cache.values() if c['name_analysis']['status'] == 'match')
    partial = sum(1 for c in comparison_cache.values() if c['name_analysis']['status'] == 'partial')
    mismatched = sum(1 for c in comparison_cache.values() if c['name_analysis']['status'] == 'mismatch')
    total = len(comparison_cache)
    
    by_village = {}
    for c in comparison_cache.values():
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
    
    return jsonify({
        "total_records": total,
        "matched": matched,
        "partial_matches": partial,
        "mismatches": mismatched,
        "match_rate": round((matched / total) * 100, 1) if total > 0 else 0,
        "by_village": by_village
    })


@app.route('/api/reconciliation/compare')
def get_comparisons():
    status_filter = request.args.get('status')
    village_filter = request.args.get('village')
    
    comparisons = list(comparison_cache.values())
    
    if status_filter:
        comparisons = [c for c in comparisons if c['name_analysis']['status'] == status_filter]
    if village_filter:
        comparisons = [c for c in comparisons if c.get('village', '').lower() == village_filter.lower()]
    
    return jsonify({
        "filters": {"status": status_filter, "village": village_filter},
        "summary": {
            "total": len(comparisons),
            "matched": sum(1 for c in comparisons if c['name_analysis']['status'] == 'match'),
            "partial": sum(1 for c in comparisons if c['name_analysis']['status'] == 'partial'),
            "mismatched": sum(1 for c in comparisons if c['name_analysis']['status'] == 'mismatch')
        },
        "comparisons": comparisons
    })


@app.route('/api/reconciliation/mismatches')
def get_mismatches():
    threshold = int(request.args.get('threshold', 85))
    mismatches = [c for c in comparison_cache.values() if c['name_analysis']['similarity_score'] < threshold]
    return jsonify({"threshold": threshold, "count": len(mismatches), "mismatches": mismatches})


@app.route('/api/reconciliation/report')
def get_report():
    comparisons = sorted(comparison_cache.values(), key=lambda x: x['name_analysis']['similarity_score'])
    
    matched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'match')
    partial = sum(1 for c in comparisons if c['name_analysis']['status'] == 'partial')
    mismatched = sum(1 for c in comparisons if c['name_analysis']['status'] == 'mismatch')
    
    return jsonify({
        "summary": {
            "total_records": len(comparisons),
            "matched": matched,
            "partial_matches": partial,
            "mismatches": mismatched,
            "match_rate": round((matched / len(comparisons)) * 100, 1) if comparisons else 0
        },
        "priority_review": [c for c in comparisons if c['name_analysis']['status'] == 'mismatch'],
        "partial_matches": [c for c in comparisons if c['name_analysis']['status'] == 'partial'],
        "verified_matches": [c for c in comparisons if c['name_analysis']['status'] == 'match']
    })


@app.route('/api/reconciliation/check/<plot_id>')
def check_parcel(plot_id):
    comparison = comparison_cache.get(plot_id.upper())
    if comparison:
        return jsonify({"found": True, "plot_id": plot_id.upper(), "comparison": comparison})
    return jsonify({"found": False, "message": f"No comparison for: {plot_id}"})


@app.route('/api/reconciliation/report/export')
def export_report():
    rows = []
    for c in comparison_cache.values():
        rows.append({
            "plot_id": c['plot_id'],
            "village": c.get('village', ''),
            "textual_owner": c['name_analysis']['textual_name'],
            "spatial_owner": c['name_analysis']['spatial_name'],
            "similarity_score": c['name_analysis']['similarity_score'],
            "match_status": c['name_analysis']['status']
        })
    
    return jsonify({
        "format": "csv",
        "headers": ["plot_id", "village", "textual_owner", "spatial_owner", "similarity_score", "match_status"],
        "rows": rows
    })


# ========================================
# Main
# ========================================

if __name__ == '__main__':
    load_all_data()
    print("Starting Land Record Digitization API on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)

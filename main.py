import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# ------------------ Products API ------------------

def _serialize_product(doc: dict) -> dict:
    if not doc:
        return doc
    d = dict(doc)
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    return d

@app.on_event("startup")
def seed_products_if_empty():
    try:
        from database import db
        if db is None:
            return
        coll = db["product"]
        if coll.count_documents({}) == 0:
            sample_products = [
                {
                    "slug": "aurora-array-pro",
                    "title": "Aurora Array Pro",
                    "subtitle": "Line-array speaker system for arenas",
                    "description": "High-SPL line-array with precision waveguides and redundant power for mission-critical venues.",
                    "price": 11999.0,
                    "category": "speakers",
                    "in_stock": True,
                    "hero_image": "/products/array.svg",
                    "images": ["/products/array.svg", "/products/amp.svg"],
                    "features": [
                        "140 dB peak SPL",
                        "Dual-redundant PSU",
                        "Rigging hardware included",
                        "IP54 weather rating"
                    ],
                    "specs": {
                        "Frequency Response": "45 Hz – 18 kHz",
                        "Coverage": "110° x 10°",
                        "Weight": "24 kg",
                        "Amplification": "Powered"
                    },
                    "tags": ["array", "arena", "touring"]
                },
                {
                    "slug": "nebula-s12-sub",
                    "title": "Nebula S12 Sub",
                    "subtitle": "Compact 12-inch subwoofer",
                    "description": "Tight, musical low-end for theaters and houses of worship with cardioid presets.",
                    "price": 1499.0,
                    "category": "speakers",
                    "in_stock": True,
                    "hero_image": "/products/subwoofer.svg",
                    "images": ["/products/subwoofer.svg"],
                    "features": ["Cardioid mode", "DSP presets", "Steel grille"],
                    "specs": {"LF Driver": "12\"", "Max SPL": "125 dB", "Weight": "18 kg"},
                    "tags": ["sub", "install", "theater"]
                },
                {
                    "slug": "orion-tower-x",
                    "title": "Orion Tower X",
                    "subtitle": "Floorstanding hi-fi tower",
                    "description": "Reference-grade tower with ribbon tweeter and phase-aligned crossover.",
                    "price": 2999.0,
                    "category": "speakers",
                    "in_stock": True,
                    "hero_image": "/products/tower.svg",
                    "images": ["/products/tower.svg"],
                    "features": ["Ribbon tweeter", "Walnut veneer", "Bi-amp ready"],
                    "specs": {"Drivers": "2x 6.5\" + ribbon", "Impedance": "4Ω", "Sensitivity": "90 dB"},
                    "tags": ["hifi", "tower"]
                },
                {
                    "slug": "vertex-dsp-2u",
                    "title": "Vertex DSP 2U",
                    "subtitle": "Rackmount audio processor",
                    "description": "96kHz, 64-bit float processing with Dante and AES67.",
                    "price": 2499.0,
                    "category": "electronics",
                    "in_stock": True,
                    "hero_image": "/products/dsp.svg",
                    "images": ["/products/dsp.svg"],
                    "features": ["Dante 64x64", "AES67", "Redundant PSU"],
                    "specs": {"Latency": "< 0.7 ms", "Sample Rate": "96 kHz"},
                    "tags": ["dsp", "install"]
                },
                {
                    "slug": "quantum-amp-8",
                    "title": "Quantum AMP-8",
                    "subtitle": "8-channel network amplifier",
                    "description": "Class-D efficiency with per-channel DSP and web control.",
                    "price": 3299.0,
                    "category": "electronics",
                    "in_stock": True,
                    "hero_image": "/products/amp.svg",
                    "images": ["/products/amp.svg"],
                    "features": ["8x 500W @ 4Ω", "PoE control", "HTTP API"],
                    "specs": {"THD+N": "0.03%", "SNR": ">110 dB"},
                    "tags": ["amp", "networked"]
                },
                {
                    "slug": "luna-bookshelf-r",
                    "title": "Luna Bookshelf R",
                    "subtitle": "Compact reference monitor",
                    "description": "Nearfield precision with room calibration via mobile app.",
                    "price": 799.0,
                    "category": "speakers",
                    "in_stock": True,
                    "hero_image": "/products/bookshelf.svg",
                    "images": ["/products/bookshelf.svg"],
                    "features": ["Room EQ", "Bluetooth LE", "Balanced inputs"],
                    "specs": {"Woofer": "5\"", "Tweeter": "1\" dome"},
                    "tags": ["studio", "bookshelf"]
                }
            ]
            coll.insert_many(sample_products)
    except Exception:
        # Non-fatal if seeding fails
        pass

@app.get("/api/products")
def list_products(limit: Optional[int] = Query(default=None, ge=1, le=100)):
    try:
        from database import db
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        cursor = db["product"].find({}, {"_id": 1, "slug": 1, "title": 1, "subtitle": 1, "price": 1, "category": 1, "hero_image": 1, "tags": 1})
        if limit:
            cursor = cursor.limit(limit)
        items = [_serialize_product(d) for d in cursor]
        return {"items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{slug}")
def get_product(slug: str):
    try:
        from database import db
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        doc = db["product"].find_one({"slug": slug})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        return _serialize_product(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, Depends, HTTPException
from app.core.database import complaints_col
from app.dependencies.auth import get_current_user, require_role
from app.routers import auth, admin, crew
from app.utils.helpers import fix_id, to_object_id, now
from fastapi import UploadFile, File, Form
from app.services.cloudinary_service import upload_image
from app.services.geo_service import get_gps_from_image


app = FastAPI(title="Swachh Netra API")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(crew.router)

@app.get("/", tags=["System"])
def home():
    return {"message": "Waste API is running"}

ALLOWED_CATEGORIES = {"garbage", "illegal_dumping", "overflowing_bin"}
ALLOWED_IMAGES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024   # 5 MB

@app.post("/complaints", tags=["Complaints"])
def create_complaint(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("garbage"),
    lat: float | None = Form(None),
    lng: float | None = Form(None),
    photo: UploadFile = File(...),
    user=Depends(require_role("citizen")),
):
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    if photo.content_type not in ALLOWED_IMAGES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WEBP photos")

    data = photo.file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Photo must be under 5 MB")

    # use GPS from the app; if missing, try the photo's own GPS
    if lat is None or lng is None:
        gps = get_gps_from_image(data)
        if not gps:
            raise HTTPException(status_code=400,
                                detail="Location missing. Send lat/lng or use a geotagged photo")
        lat, lng = gps

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    photo_url = upload_image(data)

    doc = {
        "citizen_id": str(user["_id"]),
        "title": title,
        "description": description,
        "category": category,
        "photos": [photo_url],
        "location": {"type": "Point", "coordinates": [lng, lat]},  # lng first
        "status": "submitted",
        "status_history": [{"status": "submitted", "by": str(user["_id"]),
                            "at": now()}],
        "created_at": now(),
    }
    complaints_col.insert_one(doc)
    return fix_id(doc)

# IMPORTANT: "/my" must come BEFORE "/{complaint_id}"
@app.get("/complaints/my", tags=["Complaints"])
def my_complaints(user=Depends(require_role("citizen"))):
    query = {"citizen_id": str(user["_id"])}
    return [fix_id(d) for d in complaints_col.find(query).sort("created_at", -1)]

@app.get("/complaints/{complaint_id}", tags=["Complaints"])
def get_complaint(complaint_id: str, user=Depends(get_current_user)):
    doc = complaints_col.find_one({"_id": to_object_id(complaint_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if user["role"] == "citizen" and doc.get("citizen_id") != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Not your complaint")
    return fix_id(doc)
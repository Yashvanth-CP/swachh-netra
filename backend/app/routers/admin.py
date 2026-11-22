from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import complaints_col, users_col
from app.dependencies.auth import require_role
from app.utils.helpers import fix_id, to_object_id, now

router = APIRouter(prefix="/admin", tags=["Admin"])

class AssignRequest(BaseModel):
    crew_id: str

@router.get("/complaints")
def list_all(status: str | None = None, admin=Depends(require_role("admin"))):
    query = {}
    if status:
        query["status"] = status
    return [fix_id(d) for d in complaints_col.find(query).sort("created_at", -1)]

@router.get("/crews")
def list_crews(admin=Depends(require_role("admin"))):
    return [
        {"id": str(u["_id"]), "name": u["name"], "email": u["email"]}
        for u in users_col.find({"role": "crew"})
    ]

@router.patch("/complaints/{complaint_id}/assign")
def assign(complaint_id: str, data: AssignRequest,
           admin=Depends(require_role("admin"))):
    oid = to_object_id(complaint_id)
    complaint = complaints_col.find_one({"_id": oid})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint["status"] != "submitted":
        raise HTTPException(status_code=400,
                            detail="Only 'submitted' complaints can be assigned")

    crew = users_col.find_one({"_id": to_object_id(data.crew_id), "role": "crew"})
    if not crew:
        raise HTTPException(status_code=404, detail="Crew member not found")

    complaints_col.update_one(
        {"_id": oid},
        {
            "$set": {"status": "assigned", "assigned_crew_id": data.crew_id},
            "$push": {"status_history": {
                "status": "assigned", "by": str(admin["_id"]), "at": now()}},
        },
    )
    return fix_id(complaints_col.find_one({"_id": oid}))
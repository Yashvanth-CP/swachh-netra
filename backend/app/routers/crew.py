from fastapi import APIRouter, Depends, HTTPException
from app.core.database import complaints_col
from app.dependencies.auth import require_role
from app.utils.helpers import fix_id, to_object_id, now, VALID_FLOW

router = APIRouter(prefix="/crew", tags=["Crew"])

@router.get("/tasks")
def my_tasks(crew=Depends(require_role("crew"))):
    query = {"assigned_crew_id": str(crew["_id"])}
    return [fix_id(d) for d in complaints_col.find(query)]

@router.patch("/tasks/{complaint_id}/status")
def update_task(complaint_id: str, new_status: str,
                crew=Depends(require_role("crew"))):
    oid = to_object_id(complaint_id)
    doc = complaints_col.find_one(
        {"_id": oid, "assigned_crew_id": str(crew["_id"])})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")

    if new_status not in ("in_progress", "resolved"):
        raise HTTPException(status_code=400,
                            detail="Crew can set only in_progress or resolved")
    if VALID_FLOW.get(doc["status"]) != new_status:
        raise HTTPException(status_code=400,
                            detail=f"Cannot change from {doc['status']} to {new_status}")

    changes = {"status": new_status}
    if new_status == "resolved":
        changes["resolved_at"] = now()

    complaints_col.update_one(
        {"_id": oid},
        {"$set": changes,
         "$push": {"status_history": {
             "status": new_status, "by": str(crew["_id"]), "at": now()}}},
    )
    return fix_id(complaints_col.find_one({"_id": oid}))
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

VALID_FLOW = {
    "submitted": "assigned",
    "assigned": "in_progress",
    "in_progress": "resolved",
}

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def fix_id(doc):
    doc["id"] = str(doc.pop("_id"))
    return doc

def to_object_id(id_str):
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID")
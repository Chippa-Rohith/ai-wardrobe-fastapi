from fastapi import APIRouter, HTTPException
from app.utils.database import execute_query

router = APIRouter()

@router.get("/")
async def get_all_wardrobe_items():
    """Retrieve all records from the wardrobe table."""
    try:
        query = "SELECT * FROM wadrobe"
        records = execute_query(query)
        return {"wardrobe": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

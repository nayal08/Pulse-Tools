from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def update_user():
    return {"message": "Admin getting schwifty"}


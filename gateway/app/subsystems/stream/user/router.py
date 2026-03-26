from fastapi import APIRouter, Query

from app.subsystems.stream.user.service import user_service

router = APIRouter()


@router.get("/admin/users")
async def list_users(
    page: int = Query(1),
    pageSize: int = Query(20),
    searchTerm: str = Query(""),
    status: str = Query(""),
):
    result = user_service.list_users(page, pageSize, searchTerm, status)
    return {"success": True, "data": result}

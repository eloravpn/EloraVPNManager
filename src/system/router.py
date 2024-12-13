from fastapi import APIRouter
from src.system.version_manager import version_manager

router = APIRouter()


@router.get("/version")
async def get_version():
    """Get application version information."""
    return version_manager.get_version_info()

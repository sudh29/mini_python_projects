"""
Screenshot / Artifact API routes.
Serves screenshots and debug artifacts for bot runs.
"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.auth.dependencies import CurrentUser, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/screenshots", tags=["screenshots"])


@router.get("/{run_id}")
async def list_screenshots(
    run_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """List all screenshot URLs for a bot run."""
    artifact_dir = settings.artifact_base / user.client_id / run_id
    if not artifact_dir.exists():
        return {"screenshots": [], "run_id": run_id}

    screenshots = []
    for f in sorted(artifact_dir.iterdir()):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            screenshots.append({
                "filename": f.name,
                "url": f"/api/screenshots/{run_id}/file/{f.name}",
                "size_bytes": f.stat().st_size,
            })

    return {"screenshots": screenshots, "run_id": run_id}


@router.get("/{run_id}/file/{filename}")
async def get_screenshot(
    run_id: str,
    filename: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Serve a screenshot file."""
    # Prevent path traversal
    safe_filename = os.path.basename(filename)
    filepath = settings.artifact_base / user.client_id / run_id / safe_filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(filepath, media_type="image/png")

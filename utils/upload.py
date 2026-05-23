import os
import uuid
from fastapi import UploadFile, HTTPException, status

# Allowed image MIME types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 5
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

def _compute_base_upload_dir() -> str:
    if os.environ.get("VERCEL"):
        return "/tmp/ps_by_prarambh/uploads"
    return os.path.join(os.path.dirname(__file__), "..", "uploads")


BASE_UPLOAD_DIR = _compute_base_upload_dir()


async def save_upload(file: UploadFile, folder: str) -> str:
    """
    Validates and saves an uploaded image.
    Returns the relative URL path e.g. /static/banners/abc123.jpg
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Allowed: JPEG, PNG, WEBP, GIF"
        )

    contents = await file.read()

    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_SIZE_MB}MB"
        )

    # Build unique filename preserving extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"

    save_dir = os.path.join(BASE_UPLOAD_DIR, folder)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    return f"/static/{folder}/{filename}"


def delete_upload(url_path: str):
    """
    Deletes a previously saved upload given its URL path.
    Silently ignores if file doesn't exist.
    """
    if not url_path or not url_path.startswith("/static/"):
        return

    relative = url_path.removeprefix("/static/")
    file_path = os.path.join(BASE_UPLOAD_DIR, relative)

    if os.path.isfile(file_path):
        os.remove(file_path)

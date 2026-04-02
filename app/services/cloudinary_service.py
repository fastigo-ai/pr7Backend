import cloudinary
import cloudinary.uploader
import cloudinary.api
from ..core.config import settings

# Configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image(file_path: str, folder: str = "pr7security"):
    """Uploads an image to Cloudinary and returns the URL and public_id."""
    result = cloudinary.uploader.upload(file_path, folder=folder)
    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }

def delete_image(public_id: str):
    """Deletes an image from Cloudinary by public_id."""
    cloudinary.uploader.destroy(public_id)

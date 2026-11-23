import io
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_image(file_bytes: bytes) -> str:
    """Send the photo to Cloudinary and return its public URL."""
    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes), folder="swachh_netra"
    )
    return result["secure_url"]
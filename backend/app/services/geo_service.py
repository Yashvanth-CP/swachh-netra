import io
from PIL import Image

def _to_degrees(value):
    d, m, s = value
    return float(d) + float(m) / 60 + float(s) / 3600


def get_gps_from_image(file_bytes: bytes):
    """Return (lat, lng) from photo EXIF data, or None if not found."""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        gps = img.getexif().get_ifd(0x8825)   # GPS section of EXIF
        if not gps:
            return None
        lat = _to_degrees(gps[2])             # 2 = latitude
        lng = _to_degrees(gps[4])             # 4 = longitude
        if gps.get(1) == "S":                 # 1 = N/S
            lat = -lat
        if gps.get(3) == "W":                 # 3 = E/W
            lng = -lng
        return lat, lng
    except Exception:
        return None

    
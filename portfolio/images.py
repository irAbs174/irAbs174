from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageOps

VARIANT_WIDTHS = {
    "thumb": 320,
    "card": 720,
    "stage": 1400,
}


def variant_relpath(field_name, key):
    path = Path(field_name)
    suffix = path.suffix.lower() or ".jpg"
    return str(path.parent / "variants" / f"{path.stem}_{key}{suffix}")


def variant_url(field, key="card"):
    if not field:
        return ""
    try:
        current_width = field.width
    except Exception:
        return field.url
    max_width = VARIANT_WIDTHS.get(key)
    if not max_width or current_width <= max_width:
        return field.url
    ensure_variants(field)
    rel = variant_relpath(field.name, key)
    if default_storage.exists(rel):
        return default_storage.url(rel)
    return field.url


def ensure_variants(field):
    if not field or not getattr(field, "name", ""):
        return
    try:
        field.open("rb")
        source = field.read()
    except Exception:
        return
    finally:
        try:
            field.close()
        except Exception:
            pass
    try:
        image = Image.open(BytesIO(source))
        image = ImageOps.exif_transpose(image)
    except Exception:
        return
    for key, max_width in VARIANT_WIDTHS.items():
        if image.width <= max_width:
            continue
        rel = variant_relpath(field.name, key)
        if default_storage.exists(rel):
            continue
        payload = _resized_bytes(image, max_width)
        if payload:
            default_storage.save(rel, ContentFile(payload))


def _resized_bytes(image, max_width):
    ratio = max_width / float(image.width)
    size = (max_width, max(1, int(image.height * ratio)))
    resized = image.resize(size, Image.Resampling.LANCZOS)
    fmt = (image.format or "JPEG").upper()
    if fmt not in {"JPEG", "JPG", "PNG", "WEBP"}:
        fmt = "JPEG"
    if fmt in {"JPEG", "JPG"} and resized.mode in {"RGBA", "P"}:
        resized = resized.convert("RGB")
        fmt = "JPEG"
    buffer = BytesIO()
    save_kw = {"format": "JPEG" if fmt == "JPG" else fmt}
    if save_kw["format"] == "JPEG":
        save_kw.update(quality=82, optimize=True)
    elif save_kw["format"] == "PNG":
        save_kw["optimize"] = True
    resized.save(buffer, **save_kw)
    return buffer.getvalue()

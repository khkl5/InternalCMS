from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django.conf import settings
from django.core.exceptions import ValidationError


DEFAULT_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".txt",
}

DEFAULT_ALLOWED_CONTENT_TYPES = {
    "application/msword",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/gif",
    "image/jpeg",
    "image/png",
    "text/plain",
}


def validate_uploaded_file(uploaded_file):
    max_size = getattr(settings, "MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
    if uploaded_file.size > max_size:
        raise ValidationError(f"حجم الملف يتجاوز الحد المسموح ({max_size // (1024 * 1024)} MB).")

    extension = Path(uploaded_file.name).suffix.lower()
    allowed_extensions = set(
        getattr(settings, "ALLOWED_UPLOAD_EXTENSIONS", DEFAULT_ALLOWED_EXTENSIONS)
    )
    if extension not in allowed_extensions:
        raise ValidationError("نوع الملف غير مسموح.")

    content_type = getattr(uploaded_file, "content_type", "")
    allowed_content_types = set(
        getattr(settings, "ALLOWED_UPLOAD_CONTENT_TYPES", DEFAULT_ALLOWED_CONTENT_TYPES)
    )
    if content_type not in allowed_content_types:
        raise ValidationError("محتوى الملف لا يطابق الأنواع المسموحة.")

    uploaded_file.seek(0)
    header = uploaded_file.read(16)
    uploaded_file.seek(0)

    signatures = {
        ".pdf": (b"%PDF-",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".jpg": (b"\xff\xd8\xff",),
        ".jpeg": (b"\xff\xd8\xff",),
        ".gif": (b"GIF87a", b"GIF89a"),
        ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    }
    if extension in signatures and not any(header.startswith(sig) for sig in signatures[extension]):
        raise ValidationError("محتوى الملف لا يطابق امتداده.")

    if extension in {".docx", ".xlsx"}:
        try:
            with ZipFile(uploaded_file) as archive:
                names = archive.namelist()
        except BadZipFile as exc:
            raise ValidationError("ملف Office غير صالح.") from exc
        finally:
            uploaded_file.seek(0)

        expected_prefix = "word/" if extension == ".docx" else "xl/"
        if "[Content_Types].xml" not in names or not any(
            name.startswith(expected_prefix) for name in names
        ):
            raise ValidationError("محتوى ملف Office لا يطابق امتداده.")

    if extension == ".txt" and b"\x00" in header:
        raise ValidationError("الملف النصي غير صالح.")

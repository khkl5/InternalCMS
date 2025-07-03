# content/utils.py
import unicodedata
import re
import uuid

def slugify_filename(filename):
    name, ext = filename.rsplit('.', 1)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^a-zA-Z0-9_-]+', '-', name).strip('-')
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{name}-{unique_suffix}.{ext}"

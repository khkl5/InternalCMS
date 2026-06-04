import uuid
from pathlib import Path

from utils.supabase_client import upload_file


def upload_to_supabase(file_obj, original_filename):
    extension = Path(original_filename).suffix.lower()
    path_in_bucket = f"task_files/task_{uuid.uuid4().hex}{extension}"
    upload_file(file_obj, path_in_bucket)
    return path_in_bucket

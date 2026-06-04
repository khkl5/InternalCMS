import logging

from core.decorators import get_user_role
from utils.supabase_client import create_signed_file_url

logger = logging.getLogger(__name__)


def can_view_task(user, task):
    return get_user_role(user) == "admin" or task.assigned_to_id == getattr(user, "id", None)


def attach_task_download_url(task):
    if not task.file_path:
        task.file_url = ""
        return
    try:
        task.file_url = create_signed_file_url(task.file_path)
    except Exception:
        logger.exception("Failed to create a signed URL for task %s", task.pk)
        task.file_url = ""

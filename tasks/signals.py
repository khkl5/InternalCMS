import logging

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from utils.supabase_client import delete_file

from .models import Task

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Task)
def delete_task_file_from_supabase(sender, instance, **kwargs):
    if not instance.file_path or not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        return
    try:
        delete_file(instance.file_path)
    except Exception:
        logger.exception("Failed to delete task file %s", instance.file_path)

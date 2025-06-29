from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'المهام'

    def ready(self):
        import tasks.signals  # ← هذا يفعّل signals لما يبدأ المشروع

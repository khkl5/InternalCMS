import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from clients.models import Client
from content.permissions import visible_documents_for
from core.decorators import get_user_role, role_required
from core.supabase_utils import upload_to_supabase
from utils.supabase_client import create_signed_file_url, delete_file

from .access import attach_task_download_url, can_view_task
from .forms import TaskForm
from .models import Task

logger = logging.getLogger(__name__)


def _save_task(form, client=None):
    task = form.save(commit=False)
    if client is not None:
        task.client = client

    uploaded_path = ""
    uploaded_file = form.files.get("file")
    try:
        if uploaded_file:
            uploaded_path = upload_to_supabase(uploaded_file, uploaded_file.name)
            task.file_path = uploaded_path
        task.save()
        form.save_m2m()
    except Exception:
        if uploaded_path:
            try:
                delete_file(uploaded_path)
            except Exception:
                logger.exception("Failed to clean up an incomplete task upload")
        raise
    return task


@role_required(["admin", "staff"])
def task_list_view(request):
    if get_user_role(request.user) == "admin":
        tasks = list(Task.objects.select_related("assigned_to", "client"))
    else:
        tasks = list(
            Task.objects.filter(assigned_to=request.user).select_related("assigned_to", "client")
        )
    for task in tasks:
        attach_task_download_url(task)
    return render(request, "tasks/list.html", {"all_tasks": tasks})


@role_required(["admin", "staff"])
def task_detail_view(request, task_id):
    task = get_object_or_404(Task.objects.select_related("assigned_to", "client"), id=task_id)
    if not can_view_task(request.user, task):
        return render(request, "403.html", status=403)

    attach_task_download_url(task)
    visible_documents = list(
        task.documents.filter(
            pk__in=visible_documents_for(request.user).values("pk")
        ).select_related("uploaded_by", "client")
    )
    for document in visible_documents:
        try:
            document.file_url = create_signed_file_url(document.file_path)
        except Exception:
            logger.exception("Failed to create a signed URL for document %s", document.pk)
            document.file_url = ""

    return render(
        request,
        "tasks/detail.html",
        {"task": task, "visible_documents": visible_documents},
    )


@role_required(["admin"])
def add_task_view(request):
    form = TaskForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse(
                {"success": False, "error": "البيانات غير صالحة أو ناقصة."},
                status=400,
            )
        try:
            _save_task(form)
        except Exception:
            logger.exception("Failed to create a task")
            return JsonResponse(
                {"success": False, "error": "تعذر إنشاء المهمة. يرجى المحاولة لاحقًا."},
                status=502,
            )
        return JsonResponse({"success": True, "message": "تم إنشاء المهمة بنجاح."})

    return render(request, "tasks/add_task.html", {"form": form})


@role_required(["admin"])
def add_task_for_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    form = TaskForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse(
                {"success": False, "error": "البيانات غير صالحة أو ناقصة."},
                status=400,
            )
        try:
            _save_task(form, client=client)
        except Exception:
            logger.exception("Failed to create a task for client %s", client.pk)
            return JsonResponse(
                {"success": False, "error": "تعذر إنشاء المهمة. يرجى المحاولة لاحقًا."},
                status=502,
            )
        return JsonResponse(
            {"success": True, "message": "تمت إضافة المهمة لهذا العميل بنجاح."}
        )

    return render(request, "tasks/add_task.html", {"form": form, "client": client})


@require_POST
@role_required(["admin", "staff"])
def update_task_status(request, task_id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "تنسيق البيانات غير صالح"}, status=400)

    new_status = data.get("status")
    if new_status not in dict(Task.STATUS_CHOICES):
        return JsonResponse({"success": False, "error": "الحالة غير صالحة"}, status=400)

    task = get_object_or_404(Task, pk=task_id)
    if get_user_role(request.user) != "admin" and request.user != task.assigned_to:
        return JsonResponse(
            {"success": False, "error": "غير مصرح لك بتعديل هذه المهمة"},
            status=403,
        )

    task.status = new_status
    task.save(update_fields=["status"])
    return JsonResponse({"success": True, "message": "تم تحديث الحالة بنجاح"})


@require_POST
@role_required(["admin"])
def delete_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({"success": True, "message": "تم حذف المهمة بنجاح"})

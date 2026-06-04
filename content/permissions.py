from django.db.models import Q

from core.decorators import get_user_role

from .models import Document


def visible_documents_for(user):
    if get_user_role(user) == "admin":
        return Document.objects.all()

    if not getattr(user, "is_authenticated", False):
        return Document.objects.none()

    return (
        Document.objects.filter(
            Q(access_level="public")
            | Q(uploaded_by=user)
            | Q(access_level="restricted", allowed_users=user)
            | Q(access_level="client_shared", client__assigned_to=user)
        )
        .distinct()
    )

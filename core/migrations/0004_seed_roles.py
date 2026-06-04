from django.db import migrations


def seed_roles(apps, schema_editor):
    role = apps.get_model("core", "Role")
    roles = {
        "admin": "مدير النظام",
        "staff": "موظف",
        "viewer": "قارئ فقط",
    }
    for name, description in roles.items():
        role.objects.get_or_create(name=name, defaults={"description": description})


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_userprofile_created_at"),
    ]

    operations = [
        migrations.RunPython(seed_roles, migrations.RunPython.noop),
    ]

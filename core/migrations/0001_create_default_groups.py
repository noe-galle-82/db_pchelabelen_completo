from django.db import migrations

def create_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ["gerente", "empleado", "cajero"]:
        Group.objects.get_or_create(name=name)

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_groups),
    ]

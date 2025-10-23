from django.db import migrations

def create_venta_rapida(apps, schema_editor):
    Clientes = apps.get_model('clientes', 'Clientes')
    Clientes.objects.create(
        id=1,
        nombre='Venta',
        apellido='Rápida',
        email=None,
        telefono=None,
        direccion=None,
        dni='99999999',
        fecha_nacimiento=None,
        condicion_iva='CF',
        notas='Cliente especial para ventas rápidas',
        activo=True,
    )

class Migration(migrations.Migration):
    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_venta_rapida),
    ]

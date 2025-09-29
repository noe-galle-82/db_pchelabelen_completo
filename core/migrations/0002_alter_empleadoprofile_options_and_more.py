

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # 1. AlterModelOptions y AlterModelTable (Sin cambios)
        migrations.AlterModelOptions(
            name='empleadoprofile',
            options={'verbose_name': 'Perfil de Empleado', 'verbose_name_plural': 'Perfiles de Empleados'},
        ),
        
        # 2. AddField: Campos Obligatorios (NOT NULL)
        # Usamos default y preserve_default=False para llenar las filas existentes
        # con 'PENDIENTE', evitando un error durante la migración.
        migrations.AddField(
            model_name='empleadoprofile',
            name='apellidos',
            field=models.CharField(default='PENDIENTE', max_length=150, verbose_name='Apellidos'),
            preserve_default=False, 
        ),
        
        # ⚠️ CRÍTICO: Campo 'dni' (ÚNICO y OBLIGATORIO) ⚠️
        # Lo hacemos temporalmente NULLable (null=True, blank=True) y quitamos
        # el default para evitar un error de unicidad (no puede haber dos 'PENDIENTE').
        migrations.AddField(
            model_name='empleadoprofile',
            name='dni',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, verbose_name='DNI/Cédula'),
        ),
        
        migrations.AddField(
            model_name='empleadoprofile',
            name='email_personal',
            field=models.EmailField(default='pendiente@ejemplo.com', max_length=100, verbose_name='Email Personal (Opcional)'),
            preserve_default=False,
        ),
        
        migrations.AddField(
            model_name='empleadoprofile',
            name='nombre',
            field=models.CharField(default='PENDIENTE', max_length=100, verbose_name='Nombre(s)'),
            preserve_default=False,
        ),
        
        migrations.AddField(
            model_name='empleadoprofile',
            name='telefono',
            field=models.CharField(default='PENDIENTE', max_length=20, verbose_name='Teléfono/Celular'),
            preserve_default=False,
        ),

        # 3. AddField: Campos Opcionales (NULL=True)
        # Estos campos no deberían haber causado problemas, pero se mantienen por claridad.
        migrations.AddField(
            model_name='empleadoprofile',
            name='contacto_emergencia',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Contacto de Emergencia'),
        ),
        migrations.AddField(
            model_name='empleadoprofile',
            name='direccion',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección de Domicilio'),
        ),
        migrations.AddField(
            model_name='empleadoprofile',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento'),
        ),
        migrations.AddField(
            model_name='empleadoprofile',
            name='lugar_nacimiento',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Lugar de Nacimiento'),
        ),
        migrations.AddField(
            model_name='empleadoprofile',
            name='nacionalidad',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Nacionalidad'),
        ),
        
        migrations.AlterModelTable(
            name='empleadoprofile',
            table='core_empleadoprofile',
        ),
    ]
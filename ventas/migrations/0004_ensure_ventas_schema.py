from django.db import migrations


def ensure_columns(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # Helper: check if a column exists
        def column_exists(table, column):
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table, column],
            )
            return cursor.fetchone()[0] > 0

        # Ensure ventas_detalleventa.id_lote_id
        if not column_exists('ventas_detalleventa', 'id_lote_id'):
            try:
                cursor.execute("ALTER TABLE ventas_detalleventa ADD COLUMN id_lote_id BIGINT NULL")
            except Exception:
                pass
            # Try adding FK constraint (best-effort)
            try:
                cursor.execute(
                    "ALTER TABLE ventas_detalleventa ADD CONSTRAINT ventas_detalleventa_id_lote_fk FOREIGN KEY (id_lote_id) REFERENCES lotes_lote(id)"
                )
            except Exception:
                pass

        # Ensure ventas_detalleventa.id_producto_id
        if not column_exists('ventas_detalleventa', 'id_producto_id'):
            try:
                cursor.execute("ALTER TABLE ventas_detalleventa ADD COLUMN id_producto_id BIGINT NULL")
            except Exception:
                pass
            try:
                cursor.execute(
                    "ALTER TABLE ventas_detalleventa ADD CONSTRAINT ventas_detalleventa_id_producto_fk FOREIGN KEY (id_producto_id) REFERENCES core_producto(id)"
                )
            except Exception:
                pass


class Migration(migrations.Migration):
    dependencies = [
        ('ventas', '0003_alter_detalleventa_id_producto_and_more'),
    ]

    operations = [
        migrations.RunPython(ensure_columns, migrations.RunPython.noop),
    ]

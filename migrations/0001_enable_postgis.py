"""
Enable PostGIS extension for geospatial functionality.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS postgis;",
            reverse_sql="DROP EXTENSION IF EXISTS postgis;"
        ),
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS postgis_topology;",
            reverse_sql="DROP EXTENSION IF EXISTS postgis_topology;"
        ),
    ]

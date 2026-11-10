from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('seniors', '0002_sync_date_of_death_column'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE seniors_seniorcitizen '
                'ADD COLUMN IF NOT EXISTS transferred_to varchar(100) NULL, '
                'ADD COLUMN IF NOT EXISTS archived_at timestamp with time zone NULL'
            ),
            reverse_sql=(
                'ALTER TABLE seniors_seniorcitizen '
                'DROP COLUMN IF EXISTS transferred_to, '
                'DROP COLUMN IF EXISTS archived_at'
            ),
        ),
    ]

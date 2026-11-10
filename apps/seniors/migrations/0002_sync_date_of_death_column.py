from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('seniors', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE seniors_seniorcitizen '
                'ADD COLUMN IF NOT EXISTS date_of_death date NULL'
            ),
            reverse_sql=(
                'ALTER TABLE seniors_seniorcitizen '
                'DROP COLUMN IF EXISTS date_of_death'
            ),
        ),
    ]

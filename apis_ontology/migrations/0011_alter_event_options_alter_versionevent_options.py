# Generated by Django 5.1.2 on 2024-11-25 09:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0010_poster_versionposter"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="event",
            options={
                "verbose_name": "Veranstaltung",
                "verbose_name_plural": "Veranstaltungen",
            },
        ),
        migrations.AlterModelOptions(
            name="versionevent",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Veranstaltung",
                "verbose_name_plural": "historical Veranstaltungen",
            },
        ),
    ]
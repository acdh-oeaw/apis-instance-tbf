# Generated by Django 5.1.2 on 2024-10-29 09:06

import apis_core.generic.abc
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0008_personisauthorofwork_versionpersonisauthorofwork"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("relations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupIsPublisherOfManifestation",
            fields=[
                (
                    "relation_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="relations.relation",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("relations.relation", models.Model),
        ),
        migrations.CreateModel(
            name="VersionGroupIsPublisherOfManifestation",
            fields=[
                (
                    "relation_ptr",
                    models.ForeignKey(
                        auto_created=True,
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        parent_link=True,
                        related_name="+",
                        to="relations.relation",
                    ),
                ),
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("subj_object_id", models.PositiveIntegerField()),
                ("obj_object_id", models.PositiveIntegerField()),
                (
                    "version_tag",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "obj_content_type",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "subj_content_type",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical group is publisher of manifestation",
                "verbose_name_plural": "historical group is publisher of manifestations",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(
                simple_history.models.HistoricalChanges,
                models.Model,
                apis_core.generic.abc.GenericModel,
            ),
        ),
    ]

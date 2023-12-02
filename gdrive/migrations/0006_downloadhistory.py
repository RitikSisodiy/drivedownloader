# Generated by Django 4.2.7 on 2023-12-02 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("gdrive", "0005_downloading_downloaded_thread_downloading_location_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="downloadHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
                (
                    "file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gdrive.downloading",
                    ),
                ),
            ],
        ),
    ]

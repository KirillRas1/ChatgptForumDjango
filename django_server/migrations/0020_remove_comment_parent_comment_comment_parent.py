# Generated by Django 4.2.4 on 2023-09-05 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("django_server", "0019_comment_parent_comment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="parent_comment",
        ),
        migrations.AddField(
            model_name="comment",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="django_server.comment",
                verbose_name="parent",
            ),
        ),
    ]

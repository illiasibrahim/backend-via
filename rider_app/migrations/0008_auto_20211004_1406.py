# Generated by Django 3.2.6 on 2021-10-04 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rider_app', '0007_alter_task_bucket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='bucket',
        ),
        migrations.AddField(
            model_name='task',
            name='bucket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='rider_app.bucket'),
        ),
    ]

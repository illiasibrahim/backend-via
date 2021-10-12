# Generated by Django 3.2.6 on 2021-10-04 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider_app', '0005_auto_20211004_1251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='bucket',
        ),
        migrations.AddField(
            model_name='task',
            name='bucket',
            field=models.ManyToManyField(null=True, related_name='tasks', to='rider_app.Bucket'),
        ),
    ]

# Generated by Django 3.2.6 on 2021-10-08 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider_app', '0011_auto_20211008_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='riderrequest',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
# Generated by Django 3.2.6 on 2021-10-11 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rider_app', '0012_riderrequest_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rider',
            name='id_proof',
            field=models.ImageField(null=True, upload_to='{account.username}/id_proof', verbose_name='id_proof'),
        ),
    ]

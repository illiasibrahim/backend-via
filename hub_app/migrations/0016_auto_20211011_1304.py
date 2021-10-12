# Generated by Django 3.2.6 on 2021-10-11 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0015_auto_20211008_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('collected', 'collected'), ('initiated', 'initiated'), ('delivered', 'delivered'), ('assigned', 'assigned'), ('cancelled', 'cancelled')], default='initiated', max_length=200),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='transit_type',
            field=models.CharField(choices=[('forward', 'forward'), ('return', 'return')], default='forward', max_length=40),
        ),
    ]

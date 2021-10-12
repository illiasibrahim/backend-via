# Generated by Django 3.2.6 on 2021-09-29 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0002_alter_assignment_transit_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('delivered', 'delivered'), ('initiated', 'initiated'), ('collected', 'collected'), ('cancelled', 'cancelled')], default='initiated', max_length=200),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='transit_type',
            field=models.CharField(choices=[('return', 'return'), ('forward', 'forward')], default='forward', max_length=40),
        ),
    ]

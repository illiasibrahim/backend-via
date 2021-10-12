# Generated by Django 3.2.6 on 2021-10-04 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0010_alter_assignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('collected', 'collected'), ('cancelled', 'cancelled'), ('delivered', 'delivered'), ('initiated', 'initiated')], default='initiated', max_length=200),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='transit_type',
            field=models.CharField(choices=[('forward', 'forward'), ('return', 'return')], default='forward', max_length=40),
        ),
    ]

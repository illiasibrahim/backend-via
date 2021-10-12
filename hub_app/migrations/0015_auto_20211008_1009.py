# Generated by Django 3.2.6 on 2021-10-08 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0014_alter_assignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('cancelled', 'cancelled'), ('assigned', 'assigned'), ('delivered', 'delivered'), ('initiated', 'initiated'), ('collected', 'collected')], default='initiated', max_length=200),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='transit_type',
            field=models.CharField(choices=[('return', 'return'), ('forward', 'forward')], default='forward', max_length=40),
        ),
    ]
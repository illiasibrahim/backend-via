# Generated by Django 3.2.6 on 2021-10-04 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0006_alter_assignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('delivered', 'delivered'), ('collected', 'collected'), ('initiated', 'initiated'), ('cancelled', 'cancelled')], default='initiated', max_length=200),
        ),
    ]

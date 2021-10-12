# Generated by Django 3.2.6 on 2021-10-04 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0005_alter_assignment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('initiated', 'initiated'), ('delivered', 'delivered'), ('collected', 'collected'), ('cancelled', 'cancelled')], default='initiated', max_length=200),
        ),
    ]
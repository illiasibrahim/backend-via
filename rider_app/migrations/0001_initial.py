# Generated by Django 3.2.6 on 2021-09-17 06:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hub_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_proof', models.ImageField(null=True, upload_to='id_proof', verbose_name='id_proof')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rider', to=settings.AUTH_USER_MODEL)),
                ('hub', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_boy', to='hub_app.hub')),
            ],
        ),
    ]

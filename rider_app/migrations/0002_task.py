# Generated by Django 3.2.6 on 2021-10-02 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hub_app', '0005_alter_assignment_status'),
        ('rider_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('initiated', 'initiated'), ('completed', 'completed')], max_length=32)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hub_app.assignment')),
                ('rider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rider_app.rider')),
            ],
        ),
    ]
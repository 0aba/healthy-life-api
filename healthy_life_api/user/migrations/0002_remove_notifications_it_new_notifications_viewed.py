# Generated by Django 5.1.2 on 2024-11-14 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notifications',
            name='it_new',
        ),
        migrations.AddField(
            model_name='notifications',
            name='viewed',
            field=models.BooleanField(default=True, verbose_name='Новое'),
        ),
    ]

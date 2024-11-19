# Generated by Django 5.1.2 on 2024-11-16 01:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_settings_messages_from_friends_only_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bancommunication',
            name='active',
            field=models.BooleanField(default=True, verbose_name='Блокировка активна'),
        ),
        migrations.AlterField(
            model_name='awards',
            name='description',
            field=models.TextField(blank=True, max_length=512, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='awardsuser',
            name='award',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='award_fk', to='user.awards', verbose_name='Награда'),
        ),
    ]
# Generated by Django 5.1.2 on 2024-11-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024, verbose_name='Заголовок')),
                ('message', models.TextField(max_length=32768, verbose_name='Сообщение')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Время написания')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Черновик'), (1, 'Опубликовано'), (2, 'Удалено')], default=0, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Блог',
                'verbose_name_plural': 'Блоги',
            },
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Время написания')),
                ('date_change', models.DateTimeField(auto_now=True, verbose_name='Время изменения')),
                ('message', models.TextField(max_length=4096, verbose_name='Сообщение')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Отображается'), (1, 'Удалено')], default=0, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Комментарий блога',
                'verbose_name_plural': 'Комментарии блогов',
            },
        ),
        migrations.CreateModel(
            name='BlogGoods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Товар блога',
                'verbose_name_plural': 'Товары блогов',
            },
        ),
        migrations.CreateModel(
            name='SubscriberBlogUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-14 13:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='wrote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='wrote_fk', to=settings.AUTH_USER_MODEL, verbose_name='Написал'),
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='blog_comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_fk', to='blog.blog', verbose_name='Комментарий под блогом'),
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='reply',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_reply', to='blog.blogcomment', verbose_name='Ответ на сообщение'),
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='wrote',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_wrote', to=settings.AUTH_USER_MODEL, verbose_name='Написал'),
        ),
        migrations.AddField(
            model_name='bloggoods',
            name='blog_with_goods',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='blog_with_goods_fk', to='blog.blog', verbose_name='Блог с товарами'),
        ),
        migrations.AddField(
            model_name='bloggoods',
            name='goods_blog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='goods_blog_fk', to='blog.blog', verbose_name='Товар блога'),
        ),
        migrations.AddField(
            model_name='subscriberbloguser',
            name='blogger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='blogger_fk', to=settings.AUTH_USER_MODEL, verbose_name='Подписан на'),
        ),
        migrations.AddField(
            model_name='subscriberbloguser',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriber_fk', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
        migrations.AlterUniqueTogether(
            name='bloggoods',
            unique_together={('goods_blog', 'blog_with_goods')},
        ),
        migrations.AlterUniqueTogether(
            name='subscriberbloguser',
            unique_together={('blogger', 'subscriber')},
        ),
    ]

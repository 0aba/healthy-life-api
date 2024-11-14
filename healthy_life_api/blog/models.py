from healthy_life_api.settings import AUTH_USER_MODEL
from common.models import IMessage
from django.db import models


class StatusRecord(models.IntegerChoices):
    DRAFT = 0, 'Черновик'
    PUBLISHED = 1, 'Опубликовано'
    DELETED = 2, 'Удалено'


class Blog(models.Model):
    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'

    wrote = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='wrote_fk', verbose_name='Написал')
    title = models.CharField(max_length=1024, verbose_name='Заголовок')
    message = models.TextField(max_length=32_768, verbose_name='Сообщение')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время написания')
    status = models.PositiveSmallIntegerField(choices=StatusRecord.choices, default=StatusRecord.DRAFT,
                                              verbose_name='Статус')

    def __str__(self):
        return f'@{self.pk}'

    class PublishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status=StatusRecord.PUBLISHED)

    objects = models.Manager()
    published = PublishedManager()


class BlogGoods(models.Model):
    class Meta:
        unique_together = (('goods_blog', 'blog_with_goods',),)
        verbose_name = 'Товар блога'
        verbose_name_plural = 'Товары блогов'

    goods_blog = models.ForeignKey(Blog, on_delete=models.PROTECT, related_name='goods_blog_fk',
                                   verbose_name='Товар блога')
    blog_with_goods = models.ForeignKey(Blog, on_delete=models.PROTECT, related_name='blog_with_goods_fk',
                                        verbose_name='Блог с товарами')

    objects = models.Manager()


class BlogComment(IMessage):
    class Meta:
        verbose_name = 'Комментарий блога'
        verbose_name_plural = 'Комментарии блогов'

    blog_comment = models.ForeignKey(Blog,
                                     on_delete=models.CASCADE,
                                     related_name='blog_fk',
                                     verbose_name='Комментарий под блогом')


class SubscriberBlogUser(models.Model):
    class Meta:
        unique_together = (('blogger', 'subscriber',),)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    blogger = models.ForeignKey(AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                related_name='blogger_fk',
                                verbose_name='Подписан на')
    subscriber = models.ForeignKey(AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='subscriber_fk',
                                   verbose_name='Подписчик')

    objects = models.Manager()


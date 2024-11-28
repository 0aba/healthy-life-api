from healthy_life_api.settings import AUTH_USER_MODEL
from common.models import IMessage
from pharmacy.models import Goods
from django.db.models import Q
from django.db import models


class StatusRecord(models.IntegerChoices):
    DRAFT = 0, 'Черновик'
    PUBLISHED = 1, 'Опубликовано'
    DELETED = 2, 'Удалено'


class Post(models.Model):
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    title = models.CharField(unique=True, db_index=True, max_length=1024, verbose_name='Заголовок')
    wrote = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='wrote_fk', verbose_name='Автор')
    text = models.TextField(max_length=32_768, verbose_name='Сообщение')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время написания')
    date_change = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    status = models.PositiveSmallIntegerField(choices=StatusRecord.choices, default=StatusRecord.DRAFT,
                                              verbose_name='Статус')

    def __str__(self):
        return f'@\'{self.title}\''

    class PublishedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status=StatusRecord.PUBLISHED)

    class BloggerManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(Q(status=StatusRecord.PUBLISHED) | Q(status=StatusRecord.DRAFT))

    objects = models.Manager()
    blogger = BloggerManager()
    published = PublishedManager()


class PostGoods(models.Model):
    class Meta:
        unique_together = (('goods_post', 'post_with_goods',),)
        verbose_name = 'Товар поста'
        verbose_name_plural = 'Товары постов'

    goods_post = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='goods_post_fk',
                                   verbose_name='Товар поста')
    post_with_goods = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_with_goods_fk',
                                        verbose_name='Пост с товарами')

    objects = models.Manager()


class PostComment(IMessage):
    class Meta:
        verbose_name = 'Комментарий поста'
        verbose_name_plural = 'Комментарии постов'

    comment_in_post = models.ForeignKey(Post,
                                        on_delete=models.CASCADE,
                                        related_name='comment_in_post_fk',
                                        verbose_name='Комментарий под постом')


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

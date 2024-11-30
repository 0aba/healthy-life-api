from healthy_life_api.settings import AUTH_USER_MODEL
from common.models import IMessage
from pharmacy.models import Goods
from django.db.models import Q
from django.db import models


class StatusRecord(models.IntegerChoices):
    DRAFT = 0, 'draft'
    PUBLISHED = 1, 'published'
    DELETED = 2, 'deleted'


class Post(models.Model):
    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    title = models.CharField(unique=True, db_index=True, max_length=1024, verbose_name='title')
    wrote = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='wrote_fk', verbose_name='author')
    text = models.TextField(max_length=32_768, verbose_name='text')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='time of writing')
    date_change = models.DateTimeField(auto_now=True, verbose_name='time of change')
    status = models.PositiveSmallIntegerField(choices=StatusRecord.choices, default=StatusRecord.DRAFT,
                                              verbose_name='status')

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
        verbose_name = 'goods of the post'
        verbose_name_plural = 'goods of posts'

    goods_post = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='goods_post_fk',
                                   verbose_name='goods of the post')
    post_with_goods = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_with_goods_fk',
                                        verbose_name='post with goods')

    objects = models.Manager()


class PostComment(IMessage):
    class Meta:
        verbose_name = 'comment on the post'
        verbose_name_plural = 'comments on posts'

    comment_in_post = models.ForeignKey(Post,
                                        on_delete=models.CASCADE,
                                        related_name='comment_in_post_fk',
                                        verbose_name='comment under the post')


class SubscriberBlogUser(models.Model):
    class Meta:
        unique_together = (('blogger', 'subscriber',),)
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'

    blogger = models.ForeignKey(AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                related_name='blogger_fk',
                                verbose_name='subscribed to')
    subscriber = models.ForeignKey(AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='subscriber_fk',
                                   verbose_name='subscriber')

    objects = models.Manager()

from healthy_life_api.settings import AUTH_USER_MODEL
from django.db import models


class StatusMessage(models.IntegerChoices):
    DISPLAYED = 0, 'displayed'
    DELETED = 1, 'deleted'


class IMessage(models.Model):
    class Meta:
        abstract = True
        ordering = ('date_create',)

    wrote = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='%(app_label)s_%(class)s_wrote', verbose_name='author')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='time of creation')
    date_change = models.DateTimeField(auto_now=True, verbose_name='time of last change')
    message = models.TextField(max_length=4_096, verbose_name='message')
    status = models.PositiveSmallIntegerField(choices=StatusMessage.choices, default=StatusMessage.DISPLAYED,
                                              verbose_name='status')

    class DisplayedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status=StatusMessage.DISPLAYED)

    objects = models.Manager()
    displayed = DisplayedManager()

    def __str__(self):
        return f'@{self.pk}'

from healthy_life_api.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from common.models import IMessage
from django.db import models


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    avatar = models.ImageField(upload_to='users/avatars/%Y/%m/%d/', default='default/avatar.png',
                               verbose_name='Аватарка')
    background = models.ImageField(upload_to='users/backgrounds/%Y/%m/%d/', default='default/background.png',
                                   verbose_name='Задний фон')
    about = models.TextField(max_length=512, blank=True, verbose_name='О себе')

    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f'@{self.username}'


class Settings(models.Model):
    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    user_settings = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    display_subscribed_in_priority = models.BooleanField(default=True,
                                                         verbose_name='Отображать контент подписок в приоритете')
    display_bloggers_in_blacklisted = models.BooleanField(default=False,
                                                          verbose_name='Не отображать контент от тех, кто а ЧС')
    hide_yourself_subscriptions = models.BooleanField(default=False, verbose_name='Скрыть подписки')

    receive_notifications_about_discounts = models.BooleanField(default=False,
                                                                verbose_name='Получать уведомления об скидках')

    objects = models.Manager()


class PrivateMessage(IMessage):
    class Meta:
        verbose_name = 'Личное сообщение'
        verbose_name_plural = 'Личные сообщения'

    received = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                                 related_name='received_PM_fk', verbose_name='Кто получил')
    it_read = models.BooleanField(default=False, verbose_name='Прочитано')


class Friend(models.Model):
    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        unique_together = (('friends_user', 'user_friend',),)

    friends_user = models.ForeignKey(AUTH_USER_MODEL,
                                     on_delete=models.PROTECT,
                                     related_name='friends_user_fk')
    user_friend = models.ForeignKey(AUTH_USER_MODEL,
                                    on_delete=models.PROTECT,
                                    related_name='user_friend_fk')

    objects = models.Manager()


class BlackList(models.Model):
    class Meta:
        unique_together = (('user_black_list', 'in_black_list',),)
        verbose_name = 'ЧС'
        verbose_name_plural = 'ЧС'

    user_black_list = models.ForeignKey(AUTH_USER_MODEL,
                                        on_delete=models.PROTECT,
                                        related_name='user_black_list_fk')

    in_black_list = models.ForeignKey(AUTH_USER_MODEL,
                                      on_delete=models.PROTECT,
                                      related_name='in_black_list_fk')

    objects = models.Manager()


class Awards(models.Model):
    class Meta:
        verbose_name = 'Награда'
        verbose_name_plural = 'Награды'

    image = models.ImageField(upload_to='award/%Y/%m/%d/', verbose_name='Изображение награды')
    description = models.TextField(max_length=512, verbose_name='Описание')

    objects = models.Manager()


class AwardsUser(models.Model):
    class Meta:
        verbose_name = 'Награда пользователя'
        verbose_name_plural = 'Награды пользователей'

    award_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='award_user_fk',
                                   verbose_name='Изображение награды')
    award = models.ForeignKey(Awards, on_delete=models.PROTECT, related_name='award_fk',
                              verbose_name='Награда')
    time_awarded = models.DateTimeField(auto_now_add=True, verbose_name='Время награждения')

    objects = models.Manager()


class BanCommunication(models.Model):
    class Meta:
        verbose_name = 'Блокировка общения'
        verbose_name_plural = 'Блокировки общения'

    who_banned = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='who_banned_fk', verbose_name='Кто забанил')
    got_banned = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='got_banned_fk', verbose_name='Забаненный')
    banned_date = models.DateTimeField(auto_now_add=True, verbose_name='Когда забанели')

    ban_time = models.DurationField(null=True, verbose_name='Время бана')

    objects = models.Manager()


class Notifications(models.Model):
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    user_notify = models.OneToOneField(AUTH_USER_MODEL,
                                       on_delete=models.CASCADE,
                                       related_name='user_notify_fk',
                                       verbose_name='Уведомляемый пользователь')
    message = models.CharField(max_length=1024, verbose_name='Сообщение')
    date_notify = models.DateTimeField(auto_now_add=True, verbose_name='Время события')

    it_new = models.BooleanField(default=False, verbose_name='Новое')

    objects = models.Manager()

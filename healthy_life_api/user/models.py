from healthy_life_api.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from common.models import IMessage
from django.utils import timezone
from django.db import models
import decimal


class User(AbstractUser):
    MINIMUM_REPLENISHMENT_AT_ONE_TIME = decimal.Decimal('5.00')
    MAXIMUM_REPLENISHMENT_AT_ONE_TIME = decimal.Decimal('100000.00')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='balance_CK',
            ),
        ]
        verbose_name = 'user'
        verbose_name_plural = 'users'

    avatar = models.ImageField(upload_to='users/avatars/%Y/%m/%d/', default='default/avatar.png',
                               verbose_name='user avatar')
    background = models.ImageField(upload_to='users/backgrounds/%Y/%m/%d/', default='default/background.png',
                                   verbose_name='profile background')
    about = models.TextField(max_length=512, blank=True, verbose_name='about user')
    balance = models.DecimalField(default=0, max_digits=16, decimal_places=2, verbose_name='user balance')

    def __str__(self):
        return f'@\'{self.username}\''


class Settings(models.Model):
    class Meta:
        verbose_name = 'settings'
        verbose_name_plural = 'settings'

    user_settings = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings_fk',
                                         verbose_name='user settings')
    display_bloggers_in_blacklisted = models.BooleanField(default=False,
                                                          verbose_name='do not display content from blacklisted users')
    hide_yourself_subscriptions = models.BooleanField(default=False, verbose_name='hide subscriptions')
    messages_from_friends_only = models.BooleanField(default=False, verbose_name='receive messages only from friends')
    receive_notifications_about_discounts = models.BooleanField(default=False,
                                                                verbose_name='receive notifications about discounts')

    objects = models.Manager()


class PrivateMessage(IMessage):
    class Meta:
        verbose_name = 'private message'
        verbose_name_plural = 'private messages'

    received = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, elated_name='received_PM_fk',
                                 verbose_name='who received')
    it_read = models.BooleanField(default=False, verbose_name='read')


class Friend(models.Model):
    class Meta:
        verbose_name = 'friend'
        verbose_name_plural = 'friends'
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
        verbose_name = 'blacklist_user'
        verbose_name_plural = 'blacklist_users'

    user_black_list = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user_black_list_fk',
                                        verbose_name='user blacklist')

    in_black_list = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='in_black_list_fk',
                                      verbose_name='user in blacklist')

    objects = models.Manager()


class Awards(models.Model):
    class Meta:
        verbose_name = 'award'
        verbose_name_plural = 'awards'

    image = models.ImageField(upload_to='award/%Y/%m/%d/', verbose_name='image of the award')
    description = models.TextField(max_length=512, blank=True, verbose_name='description award')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.pk}\''


class AwardsUser(models.Model):
    class Meta:
        verbose_name = 'user award'
        verbose_name_plural = 'user awards'

    award_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='award_user_fk',
                                   verbose_name='rewarded user')
    award = models.ForeignKey(Awards, on_delete=models.CASCADE, related_name='award_fk',
                              verbose_name='award')
    time_awarded = models.DateTimeField(auto_now_add=True, verbose_name='award time')

    objects = models.Manager()


class BanCommunication(models.Model):
    class Meta:
        verbose_name = 'communication ban'
        verbose_name_plural = 'communication bans'

    who_banned = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='who_banned_fk',
                                   verbose_name='who banned')
    got_banned = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='got_banned_fk',
                                   verbose_name='got banned')
    banned_date = models.DateTimeField(auto_now_add=True, verbose_name='when banned')

    # info! null это перманентный
    ban_time = models.DurationField(null=True, verbose_name='ban time')

    active = models.BooleanField(default=True, verbose_name='active')

    class BanCommunicationManager(models.Manager):
        def get_queryset(self):
            now = timezone.now()

            super().get_queryset().filter(
                active=True,
                ban_time__isnull=False,
                banned_date__lt=now - models.F('ban_time')
            ).update(active=False)

            return super().get_queryset()

    objects = BanCommunicationManager()


class Notifications(models.Model):
    class Meta:
        ordering = ('date_notify',)
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'

    user_notify = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='user_notify_fk',
                                    verbose_name='notified user')
    message = models.CharField(max_length=512, verbose_name='notification message')
    date_notify = models.DateTimeField(auto_now_add=True, verbose_name='notification time')

    viewed = models.BooleanField(default=False, verbose_name='viewed')

    objects = models.Manager()

    def __str__(self):
        return f'@\'{self.pk}\''

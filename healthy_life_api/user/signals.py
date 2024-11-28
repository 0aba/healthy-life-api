from user.models import User, Settings, Friend, PrivateMessage, AwardsUser, BanCommunication, Notifications
from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import Group
from pharmacy.models import LoyaltyCard
from django.dispatch import receiver


@receiver(post_migrate)
def create_base_roles_if_not_exists(sender, **kwargs):
    Group.objects.get_or_create(name='Модератор')
    Group.objects.get_or_create(name='Фармацевт')
    # info! + супер пользователь как роль


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user_settings=instance)
        LoyaltyCard.objects.create(user_card=instance)


@receiver(post_save, sender=Friend)
def notify_about_adding_friend(sender, instance, created, **kwargs):
    if created:
        if Friend.objects.filter(friends_user=instance.user_friend,
                                 user_friend=instance.friends_user).exists():
            Notifications.objects.create(user_notify=instance.user_friend,
                                         message=f'Вы подружились с пользователем {instance.friends_user}')
        else:
            Notifications.objects.create(user_notify=instance.user_friend,
                                         message=f'Пользователь {instance.friends_user} хочет подружиться')


@receiver(post_save, sender=PrivateMessage)
def notify_about_pm(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(user_notify=instance.received,
                                     message=f'Вам пришло новое сообщение от {instance.wrote}')


@receiver(post_save, sender=AwardsUser)
def notify_about_new_award(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(user_notify=instance.award_user,
                                     message='У вас новая награда')


@receiver(post_save, sender=BanCommunication)
def notify_about_ban(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(user_notify=instance.got_banned,
                                     message=f'Вас заблокировали на {instance.ban_time
                                                                     if instance.ban_time
                                                                     else 'навсегда'}')

from django.db.models.signals import post_save, post_migrate
from django.contrib.auth.models import Group
from pharmacy.models import LoyaltyCard
from django.dispatch import receiver
from common.utils import Role
from user import models


@receiver(post_migrate)
def create_base_roles_if_not_exists(sender, **kwargs):
    Group.objects.get_or_create(name=Role.MODERATOR.value)
    Group.objects.get_or_create(name=Role.PHARMACIST.value)
    # info! + супер пользователь как роль и + обычный пользователь


@receiver(post_save, sender=models.User)
def create_user_related_models(sender, instance, created, **kwargs):
    if created:
        models.Settings.objects.create(user_settings=instance)
        LoyaltyCard.objects.create(user_card=instance)


@receiver(post_save, sender=models.Friend)
def notify_about_adding_friend(sender, instance, created, **kwargs):
    if created:
        if models.Friend.objects.filter(friends_user=instance.user_friend, user_friend=instance.friends_user).exists():
            models.Notifications.objects.create(user_notify=instance.user_friend,
                                                message=f'you have become friends with user {instance.friends_user}')
        else:
            models.Notifications.objects.create(user_notify=instance.user_friend,
                                                message=f'user {instance.friends_user} wants to be friends')


@receiver(post_save, sender=models.PrivateMessage)
def notify_about_pm(sender, instance, created, **kwargs):
    if created:
        models.Notifications.objects.create(user_notify=instance.received,
                                            message=f'you have received a new message from {instance.wrote}')


@receiver(post_save, sender=models.AwardsUser)
def notify_about_new_award(sender, instance, created, **kwargs):
    if created:
        models.Notifications.objects.create(user_notify=instance.award_user, message='you have a new reward')


@receiver(post_save, sender=models.BanCommunication)
def notify_about_ban(sender, instance, created, **kwargs):
    if created:
        models.Notifications.objects.create(user_notify=instance.got_banned,
                                            message=f'you have been banned for {instance.ban_time 
                                                                                if instance.ban_time 
                                                                                else 'permanently'}')

from pharmacy.models import GoodsReview, Promotion
from django.db.models.signals import post_save
from user.models import Notifications, User
from django.dispatch import receiver


@receiver(post_save, sender=Promotion)
def notify_about_promotion(sender, instance, created, **kwargs):
    if created:
        users_to_notify = (User.objects.select_related('settings_fk').filter(receive_notifications_about_discounts=True)
                           .values('pk'))

        for user in users_to_notify:
            Notifications.objects.create(user_notify=user.pk,
                                         message=f'Появилась новая скидка на товар {instance.promotion_goods}')


@receiver(post_save, sender=GoodsReview)
def notify_reply_message_review(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(user_notify=instance.reply.wrote,
                                     message=f'На ваш отзыв ответил {instance.wrote}')

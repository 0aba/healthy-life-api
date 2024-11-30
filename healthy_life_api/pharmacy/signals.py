from django.db.models.signals import post_save
from user.models import Notifications, User
from pharmacy.models import Promotion
from django.dispatch import receiver


@receiver(post_save, sender=Promotion)
def notify_about_promotion(sender, instance, created, **kwargs):
    if created:
        users_to_notify = User.objects.filter(settings_fk__receive_notifications_about_discounts=True)

        for user in users_to_notify:
            Notifications.objects.create(user_notify=user,
                                         message=f'there is a new discount on the product {instance.promotion_goods}')

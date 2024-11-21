from blog.models import Post, SubscriberBlogUser
from django.db.models.signals import post_save
from user.models import Notifications
from django.dispatch import receiver


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        subscribers = SubscriberBlogUser.objects.filter(blogger=instance.wrote).values('subscriber')

        for subscriber in subscribers:
            Notifications.objects.create(user_notify=subscriber['subscriber'],
                                         message=f'Новый блог с подписанного канала {instance}')

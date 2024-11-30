from blog.models import Post, SubscriberBlogUser
from django.db.models.signals import post_save
from user.models import Notifications
from blog.models import StatusRecord
from django.dispatch import receiver


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if instance.status == StatusRecord.PUBLISHED:
        subscribers = SubscriberBlogUser.objects.filter(blogger=instance.wrote)

        for subscriber in subscribers:
            Notifications.objects.create(user_notify=subscriber.subscriber,
                                         message=f'new post {instance} from a blogger you follow')

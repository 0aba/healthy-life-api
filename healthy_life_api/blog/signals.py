from blog.models import Blog, BlogComment, SubscriberBlogUser
from django.db.models.signals import post_save
from user.models import Notifications
from django.dispatch import receiver


@receiver(post_save, sender=Blog)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        subscribers = SubscriberBlogUser.objects.filter(blogger=instance.wrote).values('subscriber')

        for subscriber in subscribers:
            Notifications.objects.create(user_notify=subscriber['subscriber'],
                                         message=f'Новый блог с подписанного канала {instance}')


@receiver(post_save, sender=BlogComment)
def notify_reply_message_blog(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(user_notify=instance.reply.wrote,
                                     message=f'На ваш отзыв ответил {instance.wrote}')


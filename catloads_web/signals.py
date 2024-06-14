
from django.db.models.signals import post_save, post_delete,pre_save
from django.dispatch import receiver
from .models import Cart, CartItem,CustomUser


@receiver(pre_save, sender=CustomUser)
def update_username_from_email(sender, instance, **kwargs):
    user_email = instance.email
    username = user_email[:30]
    n = 1
    while CustomUser.objects.exclude(pk=instance.pk).filter(username=username).exists():
        n += 1
        username = f'{user_email[:29 - len(str(n))]}-{n}'
    instance.username = username
    instance.save()
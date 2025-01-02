from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Account

@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    if created:
        # Create an Account object when a User is created
        Account.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_account(sender, instance, **kwargs):
    # Ensure the Account object exists before saving
    account, created = Account.objects.get_or_create(user=instance)
    account.save()

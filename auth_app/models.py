from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.db.models import signals
from .tasks import send_verification_email


# Create your models here.
class CustomUser(AbstractUser):
    # favourite_pizza = models.ForeignKey(
    #     'pizza_app.PizzaMenuItem', null=True, default=None, blank=True, on_delete=models.PROTECT)

    our_note = models.CharField(max_length=140, blank=True)

    is_verified = models.BooleanField('verified', default=False) # Add the `is_verified` flag
    verification_uuids = models.UUIDField('Unique Verification UUID', default=uuid.uuid4)


def user_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_verified:
        # Send verification email
        send_verification_email.delay(instance.pk)


# subscribe a handler to post_save CustomerUser event
signals.post_save.connect(user_post_save, sender=CustomUser)

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.shortcuts import reverse
from django.db.models import signals
from django.core.mail import send_mail
from django.conf import settings
#from publish.models import Post

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
        # send_mail(
        #     'Verify your QuickPublisher account',  # subject
        #     'Follow this link to verify your account: '  # message
        #     'http://localhost:8000%s' % reverse('publish:verify', kwargs={'uuid': str(instance.verification_uuids)}),
        #     'from@quickpublisher.dev',
        #     [instance.email],
        #     fail_silently=False,
        # )
        subject = 'Thank you for registering to our site'
        message = ' it  means a world to us '
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email, ]
        try:
            a = send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(str(e))


signals.post_save.connect(user_post_save, sender=CustomUser)

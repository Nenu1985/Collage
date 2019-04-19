import logging

from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from Collag.celery import app


@app.task
def send_verification_email(user_id):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=user_id)
        send_mail(
            'Verify your QuickPublisher account',
            'Follow this link to verify your account: '
            'http://localhost:8000{}'.format(reverse('publish:verify', kwargs={'uuid': str(user.verification_uuids)})),
            'from_me@nenu.by',
            [user.email,],
            fail_silently=False,
        )
    except UserModel.DoesNotExist:
        logging.warning("Tried to send verification email "
                        "to non-existing user '{}' - "
                        "{};--{}".format(user_id, user.email, user.verification_uuids))
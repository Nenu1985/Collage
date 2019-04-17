from django.shortcuts import render, reverse, redirect

# Create your views here.
from django.http import Http404

from .models import Post
from auth_app.models import CustomUser
from django.core.mail import send_mail




def view_post(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        raise Http404("Poll does not exist")

    return render(request, 'publish/post.html', context={'post': post})


def home(request):
    return render(request, 'publish/home.html')


def verify(request, uuid):
    try:
        user = CustomUser.objects.get(verification_uuid=uuid, is_verified=False)
    except CustomUser.DoesNotExist:
        raise Http404("User does not exist or is already verified")

    user.is_verified = True
    user.save()

    return redirect(reverse('publish:home'))

def send_email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = 'nenuzhny@mail.ru'
    recipient_list = ['nenuzhny112018@gmail.com', ]
    to_template = ''
    try:
        to_template = str(send_mail(
            subject,
            message,
            email_from,
            recipient_list,

        ))
    except Exception as e:
        print(e)
        to_template = e

    context = {
        'message': to_template,
    }
    return redirect(reverse('publish:home'))

from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from .models import Collage, PhotoSize
from .forms import CollageInputForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required

import threading
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from .processor import Processor

# Create your views here.
def index(request):
    collages = Collage.objects.all()[:5]
    return render(request, 'collage/index.html', {'collages': collages})


def collage_view(request, collage_id):
    collage = Collage.objects.get(id=collage_id)
    collage.get_cv2_images()
    collage.generate_collage()
    return render(request, 'collage/view.html', {'collage': collage})


def collage_view_processing(request, collage_id):
    collage = Collage.objects.get(id=collage_id)
    collage.get_cv2_images()
    collage.generate_collage()

    return HttpResponse("hello")
#
def get_photo(request, collage_id):
    #     collage = Collage.objects.all().filter(id=collage_id).first()
    #     urls = collage.get_photos_urls()
    #
    #     for i, url in enumerate(urls):
    #         collage.download_photos_by_url(url, i)
    #
    #     urls_photos = list(zip(urls, range(len(urls))))
    #     context = {
    #         'urls': urls,
    #         'collage': collage,
    #         'urls_photos': urls_photos
    #     }
    return HttpResponse('get_photo')


def collage_input(request):
    if request.method == 'GET':
        context = {
            'collage_input': CollageInputForm(),

        }
        return render(request, 'collage/input.html', context)

@login_required
def collage_create(request):
    if request.method == 'GET':
        c = {

            #'collage_form': CollageCreateForm(),
        }
        return render(request, 'collage/create.html', c)

    elif request.method == 'POST':
        collage_input_form = CollageInputForm(request.POST)
        if collage_input_form.is_valid():
            collage = collage_input_form.save(commit=False)

        collage.user = request.user
        collage.save()
        photo_urls = collage.get_photos_urls()

        # download, store and return photos
        for i, url in enumerate(photo_urls):
            new_photo = collage.download_photos_by_url(url)
            new_photo.save()
            collage.photos.add(new_photo)

        #collage.save()
        #collage.photos = photos

        #collage_form = CollageCreateForm()

        return redirect(reverse(
            'collage:view',
            kwargs={'collage_id': collage.pk}
            )
        )
        # if collage_input_form.is_valid():
        #     with transaction.atomic():
        #         delivery = delivery_from.save()
        #         pizza = pizza_form.save(delivery=delivery)
        #         pizza_form.save_m2m()
        #
        #     return redirect(reverse('pizza:view', kwargs={
        #         'pizza_order_id': pizza.pk
        #     }))
        # else:
        #     c = {
        #         'pizza_form': pizza_form,
        #         'delivery_form': delivery_from,
        #     }
        #     return render(request, 'pizza_app/create.html', c)
    return HttpResponse(status=405)


def collage_save(request):
    if request.method == 'POST':
        return HttpResponse('Hello')
    return HttpResponse(status=405)


@csrf_protect
def request_handler(request):

    if request.is_ajax() and request.method == 'POST':
        if "count" in request.POST and request.POST["count"]:
            count = int(request.POST["count"])
        else:
            count = 1


        processor = Processor()

        thread = threading.Thread(target=processor.process, args=(count,))
        thread.start()

        return render(request,
                      "collage/input.html"
                      )

    else:
        return render(request,
                      "collage/input.html"
                      )
from django.shortcuts import render, reverse
from django.http import HttpResponse, Http404
from .models import Collage
from .forms import CollageInputForm
import threading
from django.views.decorators.csrf import csrf_protect
from .processor import Processor
from .tasks import launch_processing, test_long_task, test_long_task2, my_task, my_task2, my_task3
from Collag.celery import app

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


def get_photo(request, collage_id):
    return HttpResponse('get_photo')


@csrf_protect
# views.py
def collage_input(request):

    if request.method == 'GET':
        context = {
            'collage_input': CollageInputForm(),
         }
        return render(request, 'collage/input.html', context)

    elif request.is_ajax() and request.method == 'POST':

        query_type = request.POST["query_type"]

        if query_type == 'poll':
            # When images downloaded!
            collage = Collage.objects.filter(user=request.user).latest('id')
            collage.get_cv2_images()
            collage.generate_collage()

            return HttpResponse(collage.final_img.url)

        elif query_type == 'collage_launch':

            collage_input_form = CollageInputForm(request.POST)

            if collage_input_form.is_valid():
                collage = collage_input_form.save(commit=False)
            else:
                return Http404('Неверно заполнена форма!')

            collage.save()

            celery_status = get_celery_worker_status()

            if celery_status.get('ERROR', None):
                return HttpResponse(celery_status.get('ERROR'))

            result = launch_processing.delay(collage.pk)
            # task_id = test_long_task.delay()

            # result = my_task.delay(10)
            response = reverse('celery_progress:task_status', kwargs={'task_id': result.task_id})
            return HttpResponse(response)

        elif query_type == 'progress_launch':
            result = my_task.delay(10)
            response = reverse('celery_progress:task_status', kwargs={'task_id': result.task_id})
            return HttpResponse(response)
    else:
        return Http404('Данный тип запроса не поддерживается')



def get_celery_worker_status():

    ERROR_KEY = "ERROR"
    try:
        insp = app.control.inspect()

        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    except Exception as e:
        d = { ERROR_KEY: str(e)}
    return d



def collage_create(request):
    if request.method == 'GET':
        c = {

            #'collage_form': CollageCreateForm(),
        }
        return render(request, 'collage/create.html', c)




def collage_save(request):
    if request.method == 'POST':
        return HttpResponse('Hello')
    return HttpResponse(status=405)


@csrf_protect
def async_example(request):

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


def progress(request):
    result = my_task.delay(10)
    context = {
        'collage_input': CollageInputForm(),
        'some_text': 'get request',
        'task_id': result.task_id,

    }
    return render(request, "collage/progress.html", context)

import json
from django.http import HttpResponse
from .backend import Progress
from decimal import Decimal

def get_progress(request, task_id):
    progress = Progress(task_id)
    a = {}
    # try:
    c = progress.get_info()
    if (not c['progress'] is None) and type(c['progress']['percent']) is Decimal:
        c['progress']['percent'] = int(c['progress']['percent'])
    a = json.dumps(c)
    # except Exception as e:
    #     print(e)
    return HttpResponse(a, content_type='application/json')
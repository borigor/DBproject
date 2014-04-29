from DBproject.view import DBconnector

__author__ = 'igor'

import json
from django.http import HttpResponse


def clear(request):
    try:
        response = DBconnector.clear()
    except Exception as e:
        return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
    return HttpResponse(json.dumps({"code": 0, "response": response}), content_type='application/json')



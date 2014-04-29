from DBproject.view import DBconnector
from api import views

__author__ = 'igor'

from api.view.api_tools import related_exists, choose_required, intersection
import json
from django.http import HttpResponse


def create(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["name", "short_name", "user"]
        try:
            choose_required(data=request_data, required=required_data)

            name = request_data["name"]
            short_name = request_data["short_name"]
            user = request_data["user"]

            DBconnector.exist(entity="Users", identifier="email", value=user)
            forum = DBconnector.select_query('SELECT id, name, short_name, user FROM Forums WHERE short_name = %s',
                                             (short_name, ))
            if len(forum) == 0:
                DBconnector.update_query('INSERT INTO Forums (name, short_name, user) VALUES (%s, %s, %s)',
                                         (name, short_name, user, ))

                forum = DBconnector.select_query('SELECT id, name, short_name, user FROM Forums WHERE short_name = %s',
                                                 (short_name, ))
            forum = views.forum_format(forum)

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": forum}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def details(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["forum"]
        related = related_exists(request_data)
        try:
            choose_required(data=request_data, required=required_data)
            forum = views.detail_forum(short_name=request_data["forum"], related=related)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": forum}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_threads(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["forum"]
        related = related_exists(request_data)
        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            choose_required(data=request_data, required=required_data)
            threads_l = views.threads_list(entity="forum", identifier=request_data["forum"],
                                            related=related, params=optional)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": threads_l}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_posts(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["forum"]
        related = related_exists(request_data)

        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            choose_required(data=request_data, required=required_data)
            posts_l = views.posts_list(entity="forum", params=optional, identifier=request_data["forum"],
                                       related=related)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": posts_l}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_users(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["forum"]
        optional = intersection(request=request_data, values=["limit", "order", "since_id"])
        try:
            choose_required(data=request_data, required=required_data)

            users_list = views.l_users(request_data["forum"], optional)

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": users_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)
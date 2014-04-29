from DBproject.view import DBconnector
from api import views

__author__ = 'igor'

from api.view.api_tools import related_exists, choose_required, intersection
import json
from django.http import HttpResponse


def create(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["forum", "title", "isClosed", "user", "date", "message", "slug"]
        optional = intersection(request=request_data, values=["isDeleted"])
        try:
            choose_required(data=request_data, required=required_data)

            forum = request_data["forum"]
            title = request_data["title"]
            isClosed = request_data["isClosed"]
            user = request_data["user"]
            date = request_data["date"]
            message = request_data["message"]
            slug = request_data["slug"]

            DBconnector.exist(entity="Users", identifier="email", value=user)
            DBconnector.exist(entity="Forums", identifier="short_name", value=forum)

            isDeleted = 0
            if "isDeleted" in optional:
                isDeleted = optional["isDeleted"]
            thread = DBconnector.select_query(
                'SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts ' \
                'FROM Threads WHERE slug = %s', (slug, ))

            if len(thread) == 0:
                DBconnector.update_query('INSERT INTO Threads (forum, title, isClosed, user, date, message, slug, isDeleted) ' \
                                         'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                         (forum, title, isClosed, user, date, message, slug, isDeleted, ))

                thread = DBconnector.select_query('SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts ' \
                                                  'FROM Threads WHERE slug = %s', (slug, ))

            response = views.thread_format(thread)
            del response["dislikes"]
            del response["likes"]
            del response["points"]
            del response["posts"]

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": response}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def details(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["thread"]
        related = related_exists(request_data)
        try:
            choose_required(data=request_data, required=required_data)
            thread = views.detail_thread(id=request_data["thread"], related=related)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def vote(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread", "vote"]
        try:
            choose_required(data=request_data, required=required_data)

            id = request_data["thread"]
            vote = request_data["vote"]

            DBconnector.exist(entity="Threads", identifier="id", value=id)
            if vote == -1:
                DBconnector.update_query("UPDATE Threads SET dislikes=dislikes+1, points=points-1 where id = %s", (id, ))
            else:
                DBconnector.update_query("UPDATE Threads SET likes=likes+1, points=points+1  where id = %s", (id, ))
            thread = views.detail_thread(id=id, related=[])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def subscribe(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread", "user"]
        try:
            choose_required(data=request_data, required=required_data)

            email=request_data["user"]
            thread_id=request_data["thread"]

            DBconnector.exist(entity="Threads", identifier="id", value=thread_id)
            DBconnector.exist(entity="Users", identifier="email", value=email)
            subscription = DBconnector.select_query('SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s',
                                                    (email, thread_id, ))

            if len(subscription) == 0:
                DBconnector.update_query('INSERT INTO Subscriptions (thread, user) VALUES (%s, %s)',
                                         (thread_id, email, ))
                subscription = DBconnector.select_query('SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s',
                                                        (email, thread_id, ))

            subscription = {
                "thread": subscription[0][0],
                "user": subscription[0][1]
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": subscription}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def unsubscribe(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread", "user"]
        try:
            choose_required(data=request_data, required=required_data)

            email=request_data["user"]
            thread_id=request_data["thread"]

            DBconnector.exist(entity="Threads", identifier="id", value=thread_id)
            DBconnector.exist(entity="Users", identifier="email", value=email)
            subscription = DBconnector.select_query('SELECT thread, user FROM Subscriptions WHERE user = %s AND thread = %s',
                                                    (email, thread_id, ))

            if len(subscription) == 0:
                raise Exception("user " + email + " does not subscribe thread #" + str(thread_id))
            DBconnector.update_query('DELETE FROM Subscriptions WHERE user = %s AND thread = %s',
                                     (email, thread_id, ))

            subscription = {
                "thread": subscription[0][0],
                "user": subscription[0][1]
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": subscription}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def open(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread"]
        try:
            choose_required(data=request_data, required=required_data)

            id = request_data["thread"]
            DBconnector.exist(entity="Threads", identifier="id", value=id)
            DBconnector.update_query("UPDATE Threads SET isClosed = 0 WHERE id = %s", (id, ))

            thread = {
                "thread": id
            }
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def close(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread"]
        try:
            choose_required(data=request_data, required=required_data)

            id = request_data["thread"]
            DBconnector.exist(entity="Threads", identifier="id", value=id)
            DBconnector.update_query("UPDATE Threads SET isClosed = 1 WHERE id = %s", (id, ))

            thread = {
                "thread": id
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def update(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread", "slug", "message"]
        try:
            choose_required(data=request_data, required=required_data)

            id=request_data["thread"]
            slug=request_data["slug"]
            message=request_data["message"]

            DBconnector.exist(entity="Threads", identifier="id", value=id)
            DBconnector.update_query('UPDATE Threads SET slug = %s, message = %s WHERE id = %s', (slug, message, id, ))

            thread = views.detail_thread(id=id, related=[])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def remove(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread"]
        try:
            choose_required(data=request_data, required=required_data)

            thread_id=request_data["thread"]
            DBconnector.exist(entity="Threads", identifier="id", value=thread_id)
            DBconnector.update_query("UPDATE Threads SET isDeleted = 1 WHERE id = %s", (thread_id, ))

            thread = {
                "thread": thread_id
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def restore(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["thread"]
        try:
            choose_required(data=request_data, required=required_data)

            thread_id=request_data["thread"]
            DBconnector.exist(entity="Threads", identifier="id", value=thread_id)
            DBconnector.update_query("UPDATE Threads SET isDeleted = 0 WHERE id = %s", (thread_id, ))

            thread = {
                "thread": thread_id
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": thread}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def thread_list(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        try:
            identifier = request_data["forum"]
            entity = "forum"
        except KeyError:
            try:
                identifier = request_data["user"]
                entity = "user"
            except KeyError:
                return HttpResponse(json.dumps({"code": 1, "response": "Any methods?"}),
                                    content_type='application/json')
        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            t_list = views.threads_list(entity=entity, identifier=identifier, related=[], params=optional)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": t_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_posts(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["thread"]
        entity = "thread"
        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            choose_required(data=request_data, required=required_data)
            p_list = views.posts_list(entity=entity, params=optional, identifier=request_data["thread"], related=[])
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": p_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)

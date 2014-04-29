from DBproject.view import DBconnector
from api import views

__author__ = 'igor'

import json
from django.http import HttpResponse
from api.view.api_tools import choose_required, intersection, related_exists


def create(request):
    if request.method == "POST":

        request_data = json.loads(request.body)
        required_data = ["user", "forum", "thread", "message", "date"]
        optional_data = ["parent", "isApproved", "isHighlighted", "isEdited", "isSpam", "isDeleted"]
        optional = intersection(request=request_data, values=optional_data)
        try:
            choose_required(data=request_data, required=required_data)

            date = request_data["date"]
            thread = request_data["thread"]
            message = request_data["message"]
            user = request_data["user"]
            forum = request_data["forum"]

            DBconnector.exist(entity="Threads", identifier="id", value=thread)
            DBconnector.exist(entity="Forums", identifier="short_name", value=forum)
            DBconnector.exist(entity="Users", identifier="email", value=user)

            isTread = DBconnector.select_query(
                "SELECT Threads.id FROM Threads JOIN Forums ON Threads.forum = Forums.short_name " \
                "WHERE Threads.forum = %s AND Threads.id = %s", (forum, thread, ))

            if len(isTread) == 0:
                raise Exception("no thread with id = " + str(thread) + " in forum " + forum)

            if "parent" in optional:
                isPost = DBconnector.select_query("SELECT Posts.id FROM Posts JOIN Threads ON Threads.id = Posts.thread "
                                                  "WHERE Posts.id = %s AND Threads.id = %s", (optional["parent"], thread, ))
                if len(isPost) == 0:
                    raise Exception("No post with id = " + optional["parent"])

            update_thread_posts = "UPDATE Threads SET posts = posts + 1 WHERE id = %s"

            query = "INSERT INTO Posts (message, user, forum, thread, date"
            values = "(%s, %s, %s, %s, %s"
            parameters = [message, user, forum, thread, date]

            for param in optional:
                query += ", " + param
                values += ", %s"
                parameters.append(optional[param])

            query += ") VALUES " + values + ")"

            DBconnector.update_query(update_thread_posts, (thread, ))
            post_id = DBconnector.update_query(query, parameters)

            post = DBconnector.select_query("SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited, " \
                                            "isHighlighted, isSpam, likes, message, parent, points, thread, user " \
                                            "FROM Posts WHERE id = %s", (post_id, ))
            post = views.post_format(post)

            del post["dislikes"]
            del post["likes"]
            del post["parent"]
            del post["points"]

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def details(request):
    if request.method == "GET":

        request_data = request.GET.dict()
        required_data = ["post"]
        related = related_exists(request_data)
        try:
            choose_required(data=request_data, required=required_data)
            post = views.detail_post(request_data["post"], related=related)
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def post_list(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        try:
            identifier = request_data["forum"]
            entity = "forum"
        except KeyError:
            try:
                identifier = request_data["thread"]
                entity = "thread"
            except Exception as e:
                return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')

        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            p_list = views.posts_list(entity=entity, params=optional, identifier=identifier, related=[])
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": p_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def remove(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["post"]
        try:
            choose_required(data=request_data, required=required_data)

            post_id=request_data["post"]
            DBconnector.exist(entity="Posts", identifier="id", value=post_id)
            DBconnector.update_query("UPDATE Posts SET isDeleted = 1 WHERE Posts.id = %s", (post_id, ))

            post = {
                "post": post_id
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def restore(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["post"]
        try:
            choose_required(data=request_data, required=required_data)

            post_id=request_data["post"]
            DBconnector.exist(entity="Posts", identifier="id", value=post_id)
            DBconnector.update_query("UPDATE Posts SET isDeleted = 0 WHERE Posts.id = %s", (post_id, ))

            post = {
                "post": post_id
            }

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def update(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["post", "message"]
        try:
            choose_required(data=request_data, required=required_data)

            update_id=request_data["post"]
            message=request_data["message"]

            DBconnector.exist(entity="Posts", identifier="id", value=update_id)
            DBconnector.update_query('UPDATE Posts SET message = %s WHERE id = %s', (message, update_id, ))

            post = views.detail_post(details_id=update_id, related=[])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def vote(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["post", "vote"]
        try:
            choose_required(data=request_data, required=required_data)

            vote_id=request_data["post"]
            vote_type=request_data["vote"]

            DBconnector.exist(entity="Posts", identifier="id", value=vote_id)
            if vote_type == -1:
                DBconnector.update_query("UPDATE Posts SET dislikes=dislikes+1, points=points-1 where id = %s", (vote_id, ))
            else:
                DBconnector.update_query("UPDATE Posts SET likes=likes+1, points=points+1  where id = %s", (vote_id, ))

            post = views.detail_post(details_id=vote_id, related=[])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": post}), content_type='application/json')
    else:
        return HttpResponse(status=405)
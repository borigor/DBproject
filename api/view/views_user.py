from DBproject.view import DBconnector
from api import views

__author__ = 'igor'

from api.view.api_tools import choose_required, intersection
import json
from django.http import HttpResponse


def create_user(request):
    if request.method == "POST":

        request_data = json.loads(request.body)
        required_data = ["email", "username", "name", "about"]
        optional = intersection(request=request_data, values=["isAnonymous"])
        try:
            choose_required(data=request_data, required=required_data)

            isAnonymous = 0
            if "isAnonymous" in optional:
                isAnonymous = optional["isAnonymous"]

            DBconnector.update_query("INSERT INTO Users (email, about, name, username, isAnonymous) VALUES (%s, %s, %s, %s, %s)",
                                         (request_data["email"], request_data["about"], request_data["name"], request_data["username"], isAnonymous, ))

            user = DBconnector.select_query('SELECT email, about, isAnonymous, id, name, username FROM Users WHERE email = %s',
                                                (request_data["email"], ))

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": views.user_format(user)}), content_type='application/json')

    else:
        return HttpResponse(status=405)


def details(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["user"]
        try:
            choose_required(data=request_data, required=required_data)

            email = request_data["user"]
            user = DBconnector.select_query('SELECT email, about, isAnonymous, id, name, username FROM Users WHERE email = %s', (email, ))
            user = views.user_format(user)

            if user is None:
                raise Exception("No user with email " + email)

            user["followers"] = views.l_followers(email)
            user["following"] = views.l_following(email)
            user["subscriptions"] = views.l_subscriptions(email)

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": user}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def follow(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["follower", "followee"]
        try:
            choose_required(data=request_data, required=required_data)

            DBconnector.exist(entity="Users", identifier="email", value=request_data["follower"])
            DBconnector.exist(entity="Users", identifier="email", value=request_data["followee"])

            if request_data["follower"] == request_data["followee"]:
                raise Exception("User with email=" + request_data["follower"] + " can't follow himself")

            follows = DBconnector.select_query(
                'SELECT id FROM Followers WHERE follower = %s AND followee = %s', (request_data["follower"], request_data["followee"], )
            )

            if len(follows) == 0:
                DBconnector.update_query('INSERT INTO Followers (follower, followee) VALUES (%s, %s)', (request_data["follower"], request_data["followee"], ))

            following = views.detail_user(request_data["follower"])
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": following}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def unfollow(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["follower", "followee"]
        try:
            choose_required(data=request_data, required=required_data)

            DBconnector.exist(entity="Users", identifier="email", value=request_data["follower"])
            DBconnector.exist(entity="Users", identifier="email", value=request_data["followee"])

            query = DBconnector.select_query(
                'SELECT id FROM Followers WHERE follower = %s AND followee = %s', (request_data["follower"], request_data["followee"], )
            )

            if len(query) != 0:
                DBconnector.update_query('DELETE FROM Followers WHERE follower = %s AND followee = %s', (request_data["follower"], request_data["followee"], ))
            else:
                raise Exception("No such following")
            following = views.detail_user(request_data["follower"])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": following}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_followers(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["user"]
        follow_param = intersection(request=request_data, values=["limit", "order", "since_id"])
        try:
            choose_required(data=request_data, required=required_data)

            query = "SELECT follower FROM Followers JOIN Users ON Users.email = Followers.follower WHERE followee = %s "

            if "since_id" in follow_param:
                query += " AND Users.id >= " + str(follow_param["since_id"])
            if "order" in follow_param:
                query += " ORDER BY Users.name " + follow_param["order"]
            else:
                query += " ORDER BY Users.name DESC "
            if "limit" in follow_param:
                query += " LIMIT " + str(follow_param["limit"])

            followers_tuple = DBconnector.select_query(query=query, params=(request_data["user"], ))
            followers_list = []
            for id in followers_tuple:
                id = id[0]
                followers_list.append(views.detail_user(email=id))

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": followers_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_following(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["user"]
        follow_param = intersection(request=request_data, values=["limit", "order", "since_id"])
        try:
            choose_required(data=request_data, required=required_data)

            query = "SELECT followee FROM Followers JOIN Users ON Users.email = Followers.followee WHERE follower = %s "

            if "since_id" in follow_param:
                query += " AND Users.id >= " + str(follow_param["since_id"])
            if "order" in follow_param:
                query += " ORDER BY Users.name " + follow_param["order"]
            else:
                query += " ORDER BY Users.name DESC "
            if "limit" in follow_param:
                query += " LIMIT " + str(follow_param["limit"])

            following_tuple = DBconnector.select_query(query=query, params=(request_data["user"], ))
            following_list = []
            for id in following_tuple:
                id = id[0]
                following_list.append(views.detail_user(email=id))

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": following_list}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def list_posts(request):
    if request.method == "GET":
        request_data = request.GET.dict()
        required_data = ["user"]
        optional = intersection(request=request_data, values=["limit", "order", "since"])
        try:
            choose_required(data=request_data, required=required_data)
            posts_l = views.posts_list(entity="user", params=optional, identifier=request_data["user"], related=[])
        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": posts_l}), content_type='application/json')
    else:
        return HttpResponse(status=405)


def update(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        required_data = ["user", "name", "about"]
        try:
            choose_required(data=request_data, required=required_data)

            DBconnector.exist(entity="Users", identifier="email", value=request_data["user"])

            DBconnector.update_query('UPDATE Users SET about = %s, name = %s WHERE email = %s',
                                     (request_data["about"], request_data["name"], request_data["user"], ))
            user = views.detail_user(request_data["user"])

        except Exception as e:
            return HttpResponse(json.dumps({"code": 1, "response": (e.message)}), content_type='application/json')
        return HttpResponse(json.dumps({"code": 0, "response": user}), content_type='application/json')
    else:
        return HttpResponse(status=405)

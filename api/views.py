from DBproject.view import DBconnector

# Post
#--------------------------------------------------------------------------------------------------------------------


def post_format(post):
    post = post[0]
    post_response = {
        'date': str(post[0]),
        'dislikes': post[1],
        'forum': post[2],
        'id': post[3],
        'isApproved': bool(post[4]),
        'isDeleted': bool(post[5]),
        'isEdited': bool(post[6]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[8]),
        'likes': post[9],
        'message': post[10],
        'parent': post[11],
        'points': post[12],
        'thread': post[13],
        'user': post[14],

    }
    return post_response


def detail_post(details_id, related):
    post = DBconnector.select_query("SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited, "
                       "isHighlighted, isSpam, likes, message, parent, points, thread, user "
                       "FROM Posts WHERE id = %s", (details_id, ))
    if len(post) == 0:
        raise Exception("no post with id = " + details_id)
    post = post_format(post)

    if "user" in related:
        post["user"] = detail_user(post["user"])
    if "forum" in related:
        post["forum"] = detail_forum(short_name=post["forum"], related=[])
    if "thread" in related:
        post["thread"] = detail_thread(id=post["thread"], related=[])

    return post


def posts_list(entity, params, identifier, related=[]):
    if entity == "forum":
        DBconnector.exist(entity="Forums", identifier="short_name", value=identifier)
    if entity == "thread":
        DBconnector.exist(entity="Threads", identifier="id", value=identifier)

    if entity == "user":
        DBconnector.exist(entity="Users", identifier="email", value=identifier)
    query = "SELECT id FROM Posts WHERE " + entity + " = %s "
    parameters = [identifier]
    if "since" in params:
        query += " AND date >= %s"
        parameters.append(params["since"])
    if "order" in params:
        query += " ORDER BY date " + params["order"]
    else:
        query += " ORDER BY date DESC "
    if "limit" in params:
        query += " LIMIT " + str(params["limit"])

    post_tuple = DBconnector.select_query(query=query, params=parameters)
    post_list = []
    for id in post_tuple:
        id = id[0]
        post_list.append(detail_post(details_id=id, related=related))
    return post_list


# Thread
#---------------------------------------------------------------------------------------------------------------------


def thread_format(thread):
    thread = thread[0]
    thread_response = {
        'date': str(thread[0]),
        'forum': thread[1],
        'id': thread[2],
        'isClosed': bool(thread[3]),
        'isDeleted': bool(thread[4]),
        'message': thread[5],
        'slug': thread[6],
        'title': thread[7],
        'user': thread[8],
        'dislikes': thread[9],
        'likes': thread[10],
        'points': thread[11],
        'posts': thread[12],
    }
    return thread_response


def detail_thread(id, related):
    thread = DBconnector.select_query(
        'SELECT date, forum, id, isClosed, isDeleted, message, slug, title, user, dislikes, likes, points, posts '
        'FROM Threads WHERE id = %s', (id, )
    )
    if len(thread) == 0:
        raise Exception('No thread exists with id=' + str(id))

    thread = thread_format(thread)

    if "user" in related:
        thread["user"] = detail_user(thread["user"])
    if "forum" in related:
        thread["forum"] = detail_forum(short_name=thread["forum"], related=[])

    return thread


def threads_list(entity, identifier, related, params):
    if entity == "forum":
        DBconnector.exist(entity="Forums", identifier="short_name", value=identifier)
    if entity == "user":
        DBconnector.exist(entity="Users", identifier="email", value=identifier)
    query = "SELECT id FROM Threads WHERE " + entity + " = %s "
    parameters = [identifier]

    if "since" in params:
        query += " AND date >= %s"
        parameters.append(params["since"])
    if "order" in params:
        query += " ORDER BY date " + params["order"]
    else:
        query += " ORDER BY date DESC "
    if "limit" in params:
        query += " LIMIT " + str(params["limit"])

    thread_tuple = DBconnector.select_query(query=query, params=parameters)
    thread_list = []
    for id in thread_tuple:
        id = id[0]
        thread_list.append(detail_thread(id=id, related=related))

    return thread_list

# User
#---------------------------------------------------------------------------------------------------------------------


def user_format(user):
    user = user[0]
    user_response = {
        'about': user[1],
        'email': user[0],
        'id': user[3],
        'isAnonymous': bool(user[2]),
        'name': user[4],
        'username': user[5]
    }
    return user_response


def detail_user(email):
    user = DBconnector.select_query('select email, about, isAnonymous, id, name, username FROM Users WHERE email = %s',
                                    (email, ))
    user = user_format(user)
    if user is None:
        raise Exception("No user with email " + email)
    user["followers"] = l_followers(email)
    user["following"] = l_following(email)
    user["subscriptions"] = l_subscriptions(email)
    return user


def l_followers(email):

    followers_tuple = DBconnector.select_query(
        "SELECT follower FROM Followers JOIN Users ON Users.email = Followers.follower WHERE followee = %s ", (email, ))

    followers = []
    for el in followers_tuple:
        followers.append(el[0])
    return followers


def l_following(email):

    following_tuple = DBconnector.select_query(
        "SELECT followee FROM Followers JOIN Users ON Users.email = Followers.followee WHERE follower = %s ", (email, ))

    following = []
    for el in following_tuple:
        following.append(el[0])
    return following


def l_subscriptions(email):

    subscriptions_tuple = DBconnector.select_query("SELECT thread FROM Subscriptions WHERE user = %s", (email, ))

    subscriptions = []
    for el in subscriptions_tuple:
        subscriptions.append(el[0])

    return subscriptions

# Forum
#----------------------------------------------------------------------------------------------------------------------\


def forum_format(forum):
    forum = forum[0]
    forum_response = {
        'id': forum[0],
        'name': forum[1],
        'short_name': forum[2],
        'user': forum[3]
    }
    return forum_response


def detail_forum(short_name, related):
    forum = DBconnector.select_query(
        'SELECT id, name, short_name, user FROM Forums WHERE short_name = %s', (short_name, )
    )
    if len(forum) == 0:
        raise ("No forum with exists short_name=" + short_name)

    forum = forum_format(forum)

    if "user" in related:
        forum["user"] = detail_user(forum["user"])
    return forum


def l_users(short_name, optional):
    DBconnector.exist(entity="Forums", identifier="short_name", value=short_name)

    query = "SELECT distinct email FROM Users JOIN Posts ON Posts.user = Users.email " \
            " JOIN Forums on Forums.short_name = Posts.forum WHERE Posts.forum = %s "
    if "since_id" in optional:
        query += " AND Users.id >= " + str(optional["since_id"])
    if "order" in optional:
        query += " ORDER BY Users.id " + optional["order"]
    if "limit" in optional:
        query += " LIMIT " + str(optional["limit"])

    users_tuple = DBconnector.select_query(query, (short_name, ))
    users_list = []
    for user in users_tuple:
        user = user[0]
        users_list.append(detail_user(user))
    return users_list


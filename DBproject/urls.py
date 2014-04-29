from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^db/api/clear/$', 'api.view.view_clear.clear', name='clear_database'),

    # Forum
    url(r'^db/api/forum/create/$', 'api.view.views_forum.create', name='create_forum'),
    url(r'^db/api/forum/details/$', 'api.view.views_forum.details', name='details_forum'),
    url(r'^db/api/forum/listThreads/$', 'api.view.views_forum.list_threads', name='listThreads_forum'),
    url(r'^db/api/forum/listPosts/$', 'api.view.views_forum.list_posts', name='listPosts_forum'),
    url(r'^db/api/forum/listUsers/$', 'api.view.views_forum.list_users', name='listUsers_forum'),

    # Post
    url(r'^db/api/post/create/$', 'api.view.views_post.create', name='create_post'),
    url(r'^db/api/post/details/$', 'api.view.views_post.details', name='details_post'),
    url(r'^db/api/post/list/$', 'api.view.views_post.post_list', name='list_post'),
    url(r'^db/api/post/remove/$', 'api.view.views_post.remove', name='remove_post'),
    url(r'^db/api/post/restore/$', 'api.view.views_post.restore', name='restore_post'),
    url(r'^db/api/post/update/$', 'api.view.views_post.update', name='update_post'),
    url(r'^db/api/post/vote/$', 'api.view.views_post.vote', name='vote_post'),

    # User
    url(r'^db/api/user/create/$', 'api.view.views_user.create_user', name='create_user'),
    url(r'^db/api/user/details/$', 'api.view.views_user.details', name='details_user'),
    url(r'^db/api/user/follow/$', 'api.view.views_user.follow', name='follow_user'),
    url(r'^db/api/user/unfollow/$', 'api.view.views_user.unfollow', name='unfollow_user'),
    url(r'^db/api/user/listFollowers/$', 'api.view.views_user.list_followers', name='list_followers'),
    url(r'^db/api/user/listFollowing/$', 'api.view.views_user.list_following', name='list_following'),
    url(r'^db/api/user/updateProfile/$', 'api.view.views_user.update', name='update_user'),
    url(r'^db/api/user/listPosts/$', 'api.view.views_user.list_posts', name='posts_user'),

    # Thread
    url(r'^db/api/thread/create/$', 'api.view.views_thread.create', name='create_thread'),
    url(r'^db/api/thread/details/$', 'api.view.views_thread.details', name='details_thread'),
    url(r'^db/api/thread/subscribe/$', 'api.view.views_thread.subscribe', name='subscribe_thread'),
    url(r'^db/api/thread/unsubscribe/$', 'api.view.views_thread.unsubscribe', name='unsubscribe_thread'),
    url(r'^db/api/thread/open/$', 'api.view.views_thread.open', name='open_thread'),
    url(r'^db/api/thread/close/$', 'api.view.views_thread.close', name='close_thread'),
    url(r'^db/api/thread/vote/$', 'api.view.views_thread.vote', name='vote_thread'),
    url(r'^db/api/thread/list/$', 'api.view.views_thread.thread_list', name='list_thread'),
    url(r'^db/api/thread/update/$', 'api.view.views_thread.update', name='update_thread'),
    url(r'^db/api/thread/remove/$', 'api.view.views_thread.remove', name='remove_thread'),
    url(r'^db/api/thread/restore/$', 'api.view.views_thread.restore', name='restore_thread'),
    url(r'^db/api/thread/listPosts/$', 'api.view.views_thread.list_posts', name='list_posts_thread'),

)

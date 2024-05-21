from django.urls import path
from .views import FriendListView, MemberListView, FriendDeleteView
from . import views

app_name = "friends"

urlpatterns = [
    path("", FriendListView.as_view(), name="friend_list"),
    path("members/", MemberListView.as_view(), name="member_list"),
    path(
        "friend_delete/<int:pk>/",
        FriendDeleteView.as_view(),
        name="friend_delete",
    ),
    path(
        "send_friend_request/<int:receiver_id>/",
        views.send_friend_request,
        name="send_friend_request",
    ),
    path(
        "accept_friend_request/<int:friend_request_id>/",
        views.accept_friend_request,
        name="accept_friend_request",
    ),
    path(
        "reject_friend_request/<int:friend_request_id>/",
        views.reject_friend_request,
        name="reject_friend_request",
    ),
    path(
        "friend_requests/",
        views.friend_requests,
        name="friend_requests",
    ),
]

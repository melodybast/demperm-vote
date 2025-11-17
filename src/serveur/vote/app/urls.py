"""
URL configuration for vote project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from api.vote_controller import (
    VoteView,
    DeleteVoteView,
    VoterVoteView,
    RecipientVoteView,
)

urlpatterns = [
    path("votes", VoteView.as_view(), name="create_vote"),
    path("votes/<str:domain>", DeleteVoteView.as_view(), name="delete_vote"),
    path("votes/by_user/me", VoterVoteView.as_view(), name="retrieve_votes_by_me"),
    path(
        "votes/by_user/<uuid:voterId>",
        VoterVoteView.as_view(),
        name="retrieve_votes_by_user",
    ),
    path(
        "votes/for_user/me", RecipientVoteView.as_view(), name="retrieve_votes_for_me"
    ),
    path(
        "votes/for_user/<uuid:userId>",
        RecipientVoteView.as_view(),
        name="retrieve_votes_for_user",
    ),
]

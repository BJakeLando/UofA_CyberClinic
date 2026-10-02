
from django.urls import path

from . import views

app_name = "cybergame"

urlpatterns = [
    # 1. pick an avatar, get a handle
    path("", views.home, name="home"),
    path("squad/", views.avatar_select, name="avatar_select"),
    path("squad/claim/", views.claim_avatar, name="claim_avatar"),
    path("squad/leave/", views.leave, name="leave"),

    # 2. pick a grade, 3. pick a difficulty
    path("grades/", views.grade_select, name="grade_select"),
    path("grade/<int:number>/", views.difficulty_select, name="difficulty_select"),
    path("grade/<int:number>/<slug:difficulty>/", views.start_track, name="start_track"),

    # 4. play
    path("grade/<int:number>/<slug:difficulty>/q/<int:index>/", views.question, name="question"),
    path("grade/<int:number>/<slug:difficulty>/done/", views.results, name="results"),

    # 5. go back and fix the ones you missed
    path("grade/<int:number>/<slug:difficulty>/fix/", views.fix_next, name="fix_next"),

    # 6. leaderboard
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]

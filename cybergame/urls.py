
from django.urls import path

from . import views

app_name = "cybergame"

urlpatterns = [
    path("", views.grade_select, name="grade_select"),
    # pick a grade -> pick a difficulty
    path("grade/<int:number>/", views.difficulty_select, name="difficulty_select"),
    path("grade/<int:number>/<slug:difficulty>/", views.start_track, name="start_track"),
    path("grade/<int:number>/<slug:difficulty>/q/<int:index>/", views.question, name="question"),
    path("grade/<int:number>/<slug:difficulty>/done/", views.results, name="results"),
]

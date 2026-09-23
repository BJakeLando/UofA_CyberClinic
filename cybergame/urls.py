
from django.urls import path

from . import views

app_name = "cybergame"

urlpatterns = [
    path("", views.grade_select, name="grade_select"),
    path("grade/<int:number>/", views.start_grade, name="start_grade"),
    path("grade/<int:number>/q/<int:index>/", views.question, name="question"),
    path("grade/<int:number>/done/", views.results, name="results"),
]
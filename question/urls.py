from django.urls import path
from . import views

app_name = 'question'


urlpatterns = [
    path(r'respondents', views.Respondent.as_view(), name='respondent'),
    path(r'respondent', views.Respondent.as_view(), name='respondent'),
    path(r'manage', views.QuestionManage.as_view(), name='manage'),
    path(r'answer', views.QuestionAnswer.as_view(), name='answer'),
    path(r'result', views.QuestionResult.as_view(), name='result'),
    path(r'generate', views.Generate.as_view(), name='generate'),
]
from django.conf.urls import url

from students import views

urlpatterns = [
    url(r'^', views.studentsIndex,name='studentsIndex'),
    url(r'^score_inquiry',views.score_inquiry,name='score_inquiry')



]
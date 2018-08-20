from django.conf.urls import url

from zwAdmin import views


urlpatterns = [
    url(r'^$', views.zw_index, name='zw_index'),
    url(r'^login/', views.acc_login, name='zwlogin'),
    url(r'^logout/', views.acc_logout, name='zwlogout'),
    url(r'^(\w+)/(\w+)/$', views.table_fields, name='table_fields'),
    url(r'^(\w+)/(\w+)/(\d+)/change/$', views.table_fields_change,
        name='table_fields_change'),
    url(r'^(\w+)/(\w+)/add/$', views.table_fields_add,
        name='table_fields_add'),
]
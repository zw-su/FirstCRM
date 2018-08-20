from django.conf.urls import url
from crm import views

urlpatterns = [

    url(r'^$', views.saleIndex, name='saleIndex'),
    url(r'^stu_enrollment/$', views.stuEnrollment, name='stu_enrollment'),
    url(r"^sale_report/$", views.saleReport, name='sale_report'),
    url(r"^stu_agreement/(\w+)/$", views.stuAgreement, name='stu_agreement'),
    url(r"^stu_agreement/(\w+)/fileupload/$", views.stu_fileupload, name='stu_fileupload'),

]
from django.conf.urls import url
from crm import views

urlpatterns = [

    url(r'^$', views.saleIndex, name='saleIndex'),
    url(r'^stu_enrollment/$', views.stuEnrollment, name='stu_enrollment'),
    url(r'^stu_status/$', views.stu_status, name='stu_status'),
    url(r'^stu_enrollment/(\d+)/(\d+)/contract_approved/$', views.contract_approved, name='contract_approved'),
    url(r'^stu_enrollment/(\d+)/(\d+)/contract_payment/$', views.contract_payment, name='contract_payment'),
    url(r"^sale_report/$", views.saleReport, name='sale_report'),
    url(r"^stu_agreement/(\d+)/$", views.stuAgreement, name='stu_agreement'),
    url(r"^stu_agreement/(\d+)/fileupload/$", views.stu_fileupload, name='stu_fileupload'),

]
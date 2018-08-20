import json
import socket

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from crm import models
from crm.forms import CustomerForm


def get_host_ip():
    """查询本机ip地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


@login_required
def saleIndex(request):

    return render(request, 'crm/saleIndex.html')


@login_required
def stuEnrollment(request):
    customers = models.CustomerInfo.objects.select_related()
    classes = models.ClassList.objects.select_related()
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        class_id = request.POST.get('classes')
        enrollment_obj = models.StudentApply.objects.create(
            customer_id=customer_id,
            class_grade_id=class_id,
            consultant_id=request.user.userprofile.id
        )

        host_ip = get_host_ip()
        host_port = request.get_port()

        enrollment_link = "http://%s:%s/crm/stu_agreement/%s" % (host_ip, host_port, enrollment_obj.id)

    return render(request, 'crm/stu_enrollment.html', locals())


@login_required
def saleReport(request):
    pass


def stuAgreement(request, obj_id):

    # obj_id = models.CustomerInfo.objects.filter(name=obj_name)[0].id
    stu_obj = models.StudentApply.objects.filter(id=obj_id)[0]

    if request.method == 'POST':
        stu_forms = CustomerForm(instance=stu_obj.customer, data=request.POST)

        if stu_forms.is_valid():
            #为了不让前段修改只读字段,第一种方法(不把只读字段保存)
            # datas = stu_forms.cleaned_data
            # for i in CustomerForm.Meta.readonly_fields:
            #     datas.pop(i)
            # models.CustomerInfo.objects.filter(id=obj_id).update(**datas)
            #第二种(forms的clean方法)
            stu_forms.save()
            return HttpResponse('你已报名成功，请等待合同审核通过！')

    else:
        stu_forms = CustomerForm(instance=stu_obj.customer)

    return render(request, 'crm/stu_agreement.html', locals())


@csrf_exempt
def stu_fileupload(request, obj_id):
    if request.method == 'POST':
        agree_upload_dir = os.path.join(settings.CRM_FILE_UPLOAD_DIR, obj_id)

        if not os.path.isdir(agree_upload_dir):
            os.mkdir(agree_upload_dir)

        file_obj = request.FILES.get('file')
        if len(os.listdir(agree_upload_dir)) <= 3:
            with open(os.path.join(agree_upload_dir, file_obj.name), 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
        else:
            return HttpResponse(json.dumps({'status': False, 'err_msg': '文件最大上传数为3'}))

        return HttpResponse(json.dumps({'status': True}))
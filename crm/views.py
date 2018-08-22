import json
import socket
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse, request
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import datetime
from crm import models
from crm.forms import CustomerForm, StudentApplyForm
from django.db.utils import IntegrityError


def get_host_ip():
    """查询本机ip地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

HOST_IP = get_host_ip()



@login_required
def saleIndex(request):
    '''销售主页'''

    return render(request, 'crm/saleIndex.html')


def stu_status(request):
    if request.method == 'POST':
        customer = request.POST.get('customer', '')
        classes = request.POST.get('classes', '')
        enrollment_obj = models.StudentApply.objects.filter(customer_id=customer, class_grade=classes)
        if enrollment_obj:
            if enrollment_obj[0].contract_agreed:
                if enrollment_obj[0].contract_approved:
                    return JsonResponse({'contract_status_approved': 'ok'})
                else:
                    return JsonResponse({'contract_status_agreed': 'ok'})
            else:
                # enrollment_link = "http://%s:%s/crm/stu_agreement/%s" % (HOST_IP, HOST_PORT)
                return JsonResponse({'contract_sign': 'ok'})
        else:
            return JsonResponse({'contract_sign': 'false'})






@login_required
def stuEnrollment(request):
    '''合同登记'''
    customers = models.CustomerInfo.objects.select_related()
    classes = models.ClassList.objects.select_related()

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        class_id = request.POST.get('classes')
        host_port = request.get_port()
        try:
            enrollment_obj = models.StudentApply.objects.create(
                customer_id=customer_id,
                class_grade_id=class_id,
                consultant_id=request.user.userprofile.id
            )
            enrollment_link = "http://%s:%s/crm/stu_agreement/%s" % (HOST_IP, host_port, enrollment_obj.id)
        except IntegrityError as e:
            enrollment_obj = models.StudentApply.objects.get(customer_id=customer_id)
            enrollment_link = "http://%s:%s/crm/stu_agreement/%s" % (HOST_IP, host_port, enrollment_obj.id)
            if enrollment_obj.contract_agreed:
                return redirect('/crm/stu_enrollment/%s/%s/contract_approved' %
                                (enrollment_obj.id, enrollment_obj.class_grade_id))
        
        return JsonResponse({'contract_url': enrollment_link})

    return render(request, 'crm/stu_enrollment.html', locals())


@login_required
def saleReport(request):
    pass


def stuAgreement(request, obj_id):
    '''学生同意合同'''
    # 列出已有文件
    upload_files = []
    agree_upload_dir = os.path.join(settings.CRM_FILE_UPLOAD_DIR, obj_id)

    if os.path.isdir(agree_upload_dir):
        upload_files = os.listdir(agree_upload_dir)

    stu_obj = models.StudentApply.objects.filter(id=obj_id)[0]

    if stu_obj.contract_agreed:
        return HttpResponse('合同已提交,正在积极审核,请耐心等待...')

    if request.method == 'POST':
        file_name = request.POST.get('file_name', '')
        if file_name:
            file_name = file_name.split(' ')[0]
            file_name_dir = os.path.join(agree_upload_dir, file_name)
            if os.path.exists(file_name_dir):  # 如果文件存在
                os.remove(file_name_dir)  # 则删
                return HttpResponse(json.dumps({'remove_file': 'ok'}))
        else:
            stu_forms = CustomerForm(instance=stu_obj.customer, data=request.POST)

            if stu_forms.is_valid():
                #为了不让前端修改只读字段,第一种方法(不把只读字段保存)
                # datas = stu_forms.cleaned_data
                # for i in CustomerForm.Meta.readonly_fields:
                #     datas.pop(i)
                # models.CustomerInfo.objects.filter(id=obj_id).update(**datas)
                #第二种(forms的clean方法)
                stu_forms.save()
                stu_obj.contract_agreed = True
                stu_obj.contract_agreed_date = datetime.datetime.now()
                stu_obj.save()
                return HttpResponse('你已报名成功，请等待合同审核通过！')

    else:
        stu_forms = CustomerForm(instance=stu_obj.customer)

    return render(request, 'crm/stu_agreement.html', locals())



@csrf_exempt
def stu_fileupload(request, obj_id):
    '''学生证件信息上传'''

    if request.method == 'POST':
        agree_upload_dir = os.path.join(settings.CRM_FILE_UPLOAD_DIR, obj_id)

        if not os.path.isdir(agree_upload_dir):
            os.mkdir(agree_upload_dir)

        file_obj = request.FILES.get('file')

        if len(os.listdir(agree_upload_dir)) < 3:
            # 后端实现同文件上传，不实时显示出来(另一种是前端)
            if file_obj.name not in os.listdir(agree_upload_dir):
                with open(os.path.join(agree_upload_dir, file_obj.name), 'wb') as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)
                return HttpResponse(json.dumps({'status': True, 'file_obj_name': file_obj.name}))
            else:

                return HttpResponse(json.dumps({'status': True}))
        else:
            return HttpResponse(json.dumps({'status': False, 'err_msg': '文件最大上传总数为3个'}))


@login_required
def contract_approved(request, obj_id, class_id):
    '''合同审核'''
    enrollment_obj = models.StudentApply.objects.get(id=obj_id)
    if enrollment_obj.contract_approved:
        return redirect('/crm/stu_enrollment/%s/%s/contract_payment' % (obj_id, class_id))
    if request.method == "POST":
        print(request.POST)
        approved_data = StudentApplyForm(instance=enrollment_obj, data=request.POST)
        if approved_data.is_valid():
            approved_data.save()
            enrollment_obj.contract_approved_date = datetime.datetime.now()
            enrollment_obj.save()
            enrollment_obj.customer.status = 1
            enrollment_obj.customer.save()
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)
            stu_obj[0].class_grades.add(enrollment_obj.class_grade_id)
            stu_obj[0].save()
        return redirect('/crm/stu_enrollment/%s/%s/contract_payment' % (obj_id, class_id))

    stu_forms = CustomerForm(instance=enrollment_obj.customer)
    contract_forms = StudentApplyForm(instance=enrollment_obj)
    return render(request, 'crm/contract_approved.html', locals())


@login_required
def contract_payment(request, obj_id, class_id):
    '''合同缴费'''
    # enrollment_obj = models.StudentApply.objects.get(id=obj_id)
    # if request.method == "POST":
    #     print(request.POST)
    #     # approved_data = StudentApplyForm(instance=enrollment_obj, data= )
    # stu_forms = CustomerForm(instance=enrollment_obj.customer)
    # contract_forms = StudentApplyForm(instance=enrollment_obj)
    return render(request, 'crm/contract_payment.html', locals())

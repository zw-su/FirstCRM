from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from zwAdmin import app_setup
import json
from zwAdmin.sites import site
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from zwAdmin.make_forms import make_forms
import queue


app_setup.zwAdmin_auto_app()


def page_listing(request, data):
    # contact_list = Contacts.objects.all()
    paginator = Paginator(data, 2)
    page = request.GET.get('_page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return contacts


def acc_login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user =authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/zwAdmin/'))
        else :
            error_msg='用户名或密码错误'
        print(user)
    return render(request, 'zwadmin/login.html', {'error':error_msg})


def acc_logout(request):
    logout(request)
    return redirect('/zwlogin/')


@login_required(login_url='/zwAdmin/login/')
def zw_index(request):
    # print(conf.settings.INSTALLED_APPS)
    return render(request, 'zwadmin/zwindex.html', {'site': site})


def get_filter_data(request,data):
    '''得到过滤字段和过滤后的数据'''
    filter_dic = {}
    try:
        for key, val in request.GET.items():
            if key in ('_page', '_o', '_q'):
                continue
            if val:
                filter_dic[key] = val

        # print('filter_dic',filter_dic)
        return data.filter(**filter_dic), filter_dic
    except Exception as e:
        print(e)


def order_listing(request, filter_data, admin_class):
    '''排序后'''
    num = request.GET.get('_o', '')
    current_order_field = {}

    if num:
        num = num.split('.')
        for i in num:
            order_field = admin_class.list_display[abs(int(i)) - 1]
            if i.startswith('-'):
                filter_data = filter_data.order_by('-%s' % order_field)
            else:
                filter_data = filter_data.order_by(order_field)
            current_order_field[order_field] = i
        return filter_data, current_order_field
    else:
        return filter_data, current_order_field


def search_listing(request, filter_data, admin_class):
    '''搜索'''
    search_key = request.GET.get('_q', '')
    if search_key:
        q = Q()
        q.connector = 'OR'
        for search_field in admin_class.search_fields:

            q.children.append(('%s' % search_field, search_key))
            #'%s__contains'

        print(filter_data.filter(q))
        return filter_data.filter(q)
    return filter_data


@login_required(login_url='/zwAdmin/login/')
def table_fields(request, app_name, table_name):
    ''' 前端最终显示的字段 '''

    admin_class = site.global_app[app_name][table_name]
    if request.method == 'POST':
        action_method = request.POST.get('action')
        check_list = json.loads(request.POST.get('check_list'))
        query_data = admin_class.model.objects.filter(id__in=check_list)
        run_method = getattr(admin_class, action_method)
        run_method(request, query_data)

    data = admin_class.model.objects.select_related()
    filter_data, filter_dic = get_filter_data(request, data)#过滤
    search_data = search_listing(request, filter_data, admin_class) #搜索
    order_data, sorted_field = order_listing(request, search_data, admin_class)#排序
    page_data = page_listing(request, order_data)#分页
    datas = page_data
    admin_class.filter_dic = filter_dic
    admin_class.search_key = request.GET.get('_q', '')
    return render(request, 'zwadmin/table_fields.html', locals())


def table_fields_change(request, app_name, model_name, obj_id):
    '''数据修改'''

    admin_class = site.global_app[app_name][model_name]

    form_data = make_forms(admin_class)
    field_obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'GET':
        form_obj = form_data(instance=field_obj)
        admin_class.is_change = True
    elif request.method == 'POST':
        form_obj = form_data(instance=field_obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/zwAdmin/%s/%s' % (app_name, model_name))

    return render(request, 'zwadmin/table_fields_change.html', locals())


def table_fields_add(request, app_name, model_name):
    '''数据添加'''
    admin_class = site.global_app[app_name][model_name]
    form_data = make_forms(admin_class, form_add=True)

    if request.method == 'GET':
        form_obj = form_data()
        admin_class.is_change = False
    elif request.method == 'POST':
        form_obj = form_data(data=request.POST)
        print('form_obj', form_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/zwAdmin/%s/%s' % (app_name, model_name))

    return render(request, 'zwadmin/table_fields_add.html', locals())







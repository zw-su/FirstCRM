from django.template import Library
from django.utils.safestring import mark_safe
import datetime, time

register = Library()

@register.simple_tag
def filter_order_args(admin_class):
    '''先过滤在排序参数'''
    ll = admin_class.filter_dic
    ele = ''
    if ll:
        for k, v in ll.items():
            ele += '&%s=%s' % (k, v)
        return mark_safe(ele)
    else:
        return ''


@register.simple_tag
def get_sorted_result(sorted_field):
    '''过滤时获得排序字段'''
    if sorted_field:
        return '.'.join(list(sorted_field.values()))
    else:
        return ''


@register.simple_tag
def get_sorted_icon(field, sorted_field):
    '''排序图标'''
    if field in sorted_field:
        if sorted_field[field].startswith('-'):
            ord_ele = '<span class ="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span>'
        else:
            ord_ele = '<span class ="glyphicon glyphicon-triangle-top" aria-hidden="true"></span>'
        return mark_safe(ord_ele)
    else:
        return ''


@register.simple_tag
def get_sorted_field(field, sorted_field, forloop):
    '''排序'''

    if field in sorted_field:

        if sorted_field[field].startswith('-'):
            this_index = sorted_field[field].strip('-')
        else:
            this_index = '-%s' % sorted_field[field]
        if len(list(sorted_field.values())) > 1:
            data = [sorted_field[i] for i in sorted_field if i != field]
            return this_index + '.' + '.'.join(list(data))
        else:
            return this_index
    else:
        data = sorted_field.values()
        if data:
            return str(forloop['counter']) + '.' + '.'.join(list(data))
        return forloop['counter']


@register.simple_tag
def render_pagination(datas, admin_class, sorted_field):
    '''分页'''
    ele = '''<ul class="pagination">'''
    if datas.has_previous():
        pre_ele = '''<li class="disabled"><a style='cursor: pointer;' href="?_page=%s" 
                aria-label="Previous"><span aria-hidden="true">上一页&laquo;
                </span></a></li>''' % (datas.number - 1)
        ele += pre_ele
    for i in datas.paginator.page_range:
        if abs(datas.number - i) < 2:
            active = ""
            if datas.number == i:
                active = "active"
            filter_order_ele = filter_order_args(admin_class)
            sorted_data = ''
            if sorted_field:
                sorted_data = '&_o=' + '.'.join(list(sorted_field.values()))
            li_ele = '<li class=%s><a href="?_page=%s%s%s">%s </a> </li >'\
                     %(active, i, filter_order_ele, sorted_data, i)
            ele += li_ele
    if datas.has_next():
        next_ele = '''<li class="disabled"><a style='cursor: pointer;' href="?_page=%s" 
                    aria-label="Next"><span aria-hidden="true">下一页&raquo;
                    </span></a></li>''' % (datas.number+1)
        ele += next_ele
    ele += '</ul>'
    return mark_safe(ele)


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.model_name


@register.simple_tag
def build_table_row(obj, admin_class):
    '''过滤后字段显示'''
    ele = ''
    if admin_class.list_display:
        for index, column_name in enumerate(admin_class.list_display):
            column_obj = admin_class.model._meta.get_field(column_name)
            if column_obj.choices:
                column_data = getattr(obj, 'get_%s_display' % column_name)()
            else:
                column_data = getattr(obj, column_name)
            td_ele = '<td>%s</td>' % column_data
            if index == 0:
                td_ele = "<td><a href='%s/change/'>%s</a></td>" % (obj.id, column_data)
            ele += td_ele
    else:
        td_ele = "<td><a href='%s/change/'>%s</a></td>" % (obj.id, obj)
        ele += td_ele
    return mark_safe(ele)


@register.simple_tag
def build_filter_ele(obj, admin_class):
    '''过滤条件'''

    column_obj = admin_class.model._meta.get_field(obj)
    filter_name = '<span>%s: </span>' % obj
    try:

        filter_ele = '%s<select name=%s>' % (filter_name, obj)
        for choices_name in column_obj.get_choices():
            selected = ''
            if obj in admin_class.filter_dic:
                if str(choices_name[0]) == admin_class.filter_dic.get(obj):
                    selected = 'selected'

            choices_ele="<option value='%s' %s>%s</option>"%\
                        (choices_name[0], selected, choices_name[1])
            filter_ele += choices_ele
    except AttributeError:
        filter_ele = '%s<select name=%s__gte>' % (filter_name, obj)
        if column_obj.get_internal_type() in ('DateField', 'DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [
                ['', '---------'],
                [time_obj, '今天'],
                [time_obj-datetime.timedelta(7), '七天内'],
                [time_obj.replace(day=1), '本月'],
                [time_obj - datetime.timedelta(90), '三个月内'],
                [time_obj.replace(month=1, day=1), '本年'],
                # ['','ALL']
            ]
            obj = obj+'__gte'
            for i in time_list:
                selected = ''
                if obj in admin_class.filter_dic:
                    if i[0]:
                        if str(i[0].date()) == admin_class.filter_dic.get(obj):
                            selected = 'selected'
                choices_ele = "<option value='%s' %s>%s</option>" %\
                                ('' if not i[0] else str(i[0].date()), selected, i[1])
                filter_ele += choices_ele

    filter_ele += '</select>'
    return mark_safe(filter_ele)


@register.simple_tag
def get_readonly_field_val(readonly_field, form_obj):

    '''获得只读字段的值'''
    return getattr(form_obj.instance, readonly_field)


@register.simple_tag
def get_horizontal_avail(admin_class, field_name, form_obj):
    '''获得m2m字段的关联表的所有字段'''
    if admin_class.is_change:
        c1_obj = getattr(form_obj.instance, field_name)
        print(mark_safe(set(c1_obj.model.objects.all())-set(c1_obj.all())))
        return set(c1_obj.model.objects.all())-set(c1_obj.all())
    else:
        relevance_table = admin_class.model._meta.get_field(field_name)
        return relevance_table.related_model.objects.all()


@register.simple_tag
def get_horizontal_select(admin_class, field_name, form_obj):
    '''获得m2m字段中选择了的字段'''
    if admin_class.is_change:
        c1_obj = getattr(form_obj.instance, field_name)
        return c1_obj.all()
    else:
        return ''


@register.simple_tag
def get_model_verbose(admin_class):
    '''返回Meta里verbose_name'''
    return admin_class.model._meta.verbose_name



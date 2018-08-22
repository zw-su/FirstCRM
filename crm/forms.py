from django.forms import ModelForm, forms
from crm import models

class StudentApplyForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        datas = cls.base_fields
        for field_name in datas:
            field_obj = datas[field_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)

    class Meta:
        model = models.StudentApply
        fields = '__all__'
        exclude = ['contract_approved_date']
        readonly_fields = ['contract_agreed', 'contract_agreed_date']

    def clean(self):
        if self.errors:
            raise forms.ValidationError('请不要修改不能修改的字段')
        if self.instance.id is not None:
            for i in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, i)
                form_val = self.cleaned_data.get(i)
                if form_val != old_field_val:
                    self.add_error(i, '只读字段：字段的值为%s,不能为%s' % (old_field_val, form_val))

class CustomerForm(ModelForm):

    def __new__(cls, *args, **kwargs):
        datas = cls.base_fields
        for field_name in datas:
            field_obj = datas[field_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)

    class Meta:
        model = models.CustomerInfo
        fields = '__all__'
        exclude = ['consult_content', 'status', '咨询课程']
        readonly_fields = ['contact', 'contact_type', 'consultant', 'source',
                           'referral_from', ]

    def clean(self):
        if self.errors:
            raise forms.ValidationError('请不要修改不能修改的字段')
        if self.instance.id is not None:
            for i in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, i)
                form_val = self.cleaned_data.get(i)
                if form_val != old_field_val:
                    self.add_error(i, '只读字段：字段的值为%s,不能为%s' % (old_field_val, form_val))
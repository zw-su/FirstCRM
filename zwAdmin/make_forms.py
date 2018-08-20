from django.forms import ModelForm


def make_forms(admin_class, form_add=False):
    class Meta:
        model = admin_class.model
        fields = '__all__'
        if form_add:
            admin_class.change_form = False

        else:
            exclude = admin_class.readonly_fields
            admin_class.change_form = True

    def __new__(cls, *args, **kwargs):
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
            # if field_name in admin_class.readonly_fields:
            #     field_obj.widget.attrs.update({'disabled': 'true'})#form不提交,报错
            #     print('__new Meta', cls.Meta)
            #     cls.Meta.exclude.append(field_name)

        return ModelForm.__new__(cls)

    dynamic_form = type('DynamicForm',
                        (ModelForm,), {'Meta': Meta, '__new__': __new__})

    return dynamic_form
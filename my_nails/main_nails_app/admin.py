from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm, ValidationError
from .models import *
# Uncomment bottom to open uploaded image size processing.
from PIL import Image
from django.utils.safestring import mark_safe
# from django.forms import ModelForm, ValidationError


# Uncomment bottom to open uploaded image size processing.
# class ServiceAdminForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['picture'].help_text = mark_safe(
#             '<span style="color:red; font-size:14px;"> \
#             Загружайте изображение с минимальным разрешением {}x{}px и максимальным {}x{}px. '
#             'При превышении максимального разрешения оно будет обрезано.</span>'.format(
#                 *Service.MIN_RESOLUTION, *Service.MAX_RESOLUTION
#             )
#         )

# def clean_image(self):
#     image = self.cleaned_data["picture"]
#     img = Image.open(image)
#     min_height, min_width = Service.MIN_RESOLUTION
#     max_height, max_width = Service.MAX_RESOLUTION
#     if image.size > Service.MAX_IMAGE_SIZE:
#         raise ValidationError("Размер изображения не должен превышать 3МБ")
#     if img.height < min_height or img.width < min_width:
#         raise ValidationError("Разрешение изображения меньше минимального!")
#     if img.height > max_height or img.width > max_width:
#         raise ValidationError("Разрешение изображения больше максимального!")
#     return image


class ComplexCoatingAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance == None:
            pass
        else:
            if not instance.painting:
                self.fields['additional'].widget.attrs.update({
                    'readonly': True, 'style': 'background: blue'
                })

    def clean(self):
        if not self.cleaned_data['painting']:
            self.cleaned_data['additional'] = None
        return self.cleaned_data


class ComplexCoatingAdmin(admin.ModelAdmin):
    # Uncomment bottom to open uploaded image size processing.
    # form = ServiceAdminForm

    change_form_template = 'admin.html'
    form = ComplexCoatingAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='complexcoating'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ComplexBuildingAdmin(admin.ModelAdmin):
    # Uncomment bottom to open uploaded image size processing.
    # form = ServiceAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='complexbuilding'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(ComplexCoating, ComplexCoatingAdmin)
admin.site.register(ComplexBuilding, ComplexBuildingAdmin)
admin.site.register(CaseService)
admin.site.register(Case)
admin.site.register(Customer)

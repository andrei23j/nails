from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

# Uncomment bottom to open uploaded image size processing.
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_service_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:
    @staticmethod
    def get_services_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        services = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            services.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        services, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return services


class LatestProducts:
    objects = LatestProductsManager()


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'FOR_WOMAN': 'complexcoating__count',
        'FOR_MAN': 'complexbuilding__count',
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_central_card(self):
        models = get_models_for_count('complexbuilding', 'complexcoating')
        qs = list(self.get_queryset().annotate(*models).values())
        return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]


# ************
# List of basic models
# 1 - Category
# 2 - Service (Meta)
# 2.1 - ComplexCoating
# 2.2 - ComplexBuilding
# 3 - CaseService
# 4 - Case
# 5 - Order
# 6 - Customer
# ************

# 1 - Category
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категория услуги')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name


# 2 - Service (Meta)
class Service(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (3840, 2160)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Услуга', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Название услуги')
    slug = models.SlugField(unique=True)
    picture = models.ImageField(verbose_name='Изображение')
    description = models.TextField(null=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Стоимость')

    def __str__(self):
        return self.title

    # Uncomment bottom def to open uploaded image size processing.
    # def save(self, *args, **kwargs):
    #     # image = self.picture
    #     # img = Image.open(image)
    #     # min_height, min_width = self.MIN_RESOLUTION
    #     # max_height, max_width = self.MAX_RESOLUTION
    #     # if img.height < min_height or img.width < min_width:
    #     #     raise MinResolutionErrorException('Разрешение изображения меньше минимального!')
    #     # if img.height > max_height or img.width > max_width:
    #     #     raise MaxResolutionErrorException('Разрешение изображения больше максимального!')
    #     image = self.picture
    #     img = Image.open(image)
    #     new_img = img.convert('RGB')
    #     resized_new_image = new_img.resize((640, 360), Image.BICUBIC)
    #     filestream = BytesIO()
    #     resized_new_image.save(filestream, 'JPEG', quality=100)
    #     filestream.seek(0)
    #     name = '{}.{}'.format(*self.picture.name.split('.'))
    #     self.picture = InMemoryUploadedFile(
    #         filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
    #     )
    #     super().save(*args, **kwargs)


# 2.1 - ComplexCoating
class ComplexCoating(Service):
    painting = models.BooleanField(default=True, verbose_name='Рисунки на ногтях')
    additional = models.TextField(blank=True, null=True, verbose_name='Дополнительные услуги')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_service_url(self, 'service_detail')

    # @property
    # def painting(self):
    #     if self.painting:
    #         return 'Yes'
    #     return 'No'


# 2.2 - ComplexBuilding
class ComplexBuilding(Service):
    additional_description = models.TextField(verbose_name='Дополнительная информация', blank=True)

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_service_url(self, 'service_detail')


# 3 - CaseService
class CaseService(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Заказчик', on_delete=models.CASCADE)
    case = models.ForeignKey('Case', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_services')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return 'Услуга: {} (для заказа)'.format(self.content_object.title)


# 4 - Case
class Case(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    services = models.ManyToManyField('CaseService', blank=True, related_name='related_case')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Полная цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


# 6 - Customer
class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)

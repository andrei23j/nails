from django.urls import path
from .views import test_view, ServiceDetailView

urlpatterns = [
    path('', test_view, name='base'),
    path('service/<str:ct_model>/<str:slug>/', ServiceDetailView.as_view(), name='service_detail')
]

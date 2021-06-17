from django.shortcuts import render
from django.views.generic import DetailView
from .models import ComplexCoating, ComplexBuilding, Category
from django.urls import path


def test_view(request):
    categories = Category.objects.get_categories_for_central_card()
    return render(request, 'base.html', {'categories': categories})


class ServiceDetailView(DetailView):
    CT_MODEL_MODEL_CLASS = {
        'complexcoating': ComplexCoating,
        'complexbuilding': ComplexBuilding,
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # model = Model
    # queryset = Model.objects.all()
    context_object_name = 'service'
    template_name = 'service_detail.html'
    slug_url_kwarg = 'slug'

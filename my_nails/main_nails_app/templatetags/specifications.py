from django import template
from django.utils.safestring import mark_safe
from ..models import ComplexCoating

register = template.Library()

TABLE_HEAD = """
                <table class="table">
                <tbody>
            """
TABLE_TAIL = """
                </tbody>
                </table>
            """
TABLE_CONTENT = """
            <tr>
                <td>{name}</td>
                <td>{value}</td>
            </tr>
            """

SERVICE_SPEC = {
    'complexcoating': {
        'Дополнительные услуги': 'additional',
        'Рисунки на ногтях': 'painting'
    },
    'complexbuilding': {
        'Дополнительные услуги': 'additional_description',
    }
}


def get_service_special(service, model_name):
    table_content = ''
    for name, value in SERVICE_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(service, value))
    return table_content


@register.filter
def service_special(service):
    model_name = service.__class__._meta.model_name
    if isinstance(service, ComplexCoating):
        if not service.painting:
            SERVICE_SPEC['complexcoating'].pop('Дополнительные услуги')
        else:
            SERVICE_SPEC['complexcoating']['Дополнительные услуги'] = 'additional'
    return mark_safe(TABLE_HEAD + get_service_special(service, model_name) + TABLE_TAIL)

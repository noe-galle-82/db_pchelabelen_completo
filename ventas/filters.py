import django_filters
from datetime import datetime, time
from django.utils.timezone import make_aware, is_naive
from .models import Venta


class VentaFilter(django_filters.FilterSet):
    fecha_desde = django_filters.CharFilter(method='filter_fecha_desde')
    fecha_hasta = django_filters.CharFilter(method='filter_fecha_hasta')
    medio_pago = django_filters.CharFilter(field_name='medio_pago', lookup_expr='iexact')

    class Meta:
        model = Venta
        fields = ['medio_pago']

    def _parse_date(self, value: str):
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except Exception:
            return None

    def filter_fecha_desde(self, queryset, name, value):
        d = self._parse_date(value)
        if not d:
            return queryset
        dt = datetime.combine(d, time.min)
        if is_naive(dt):
            dt = make_aware(dt)
        return queryset.filter(fecha_venta__gte=dt)

    def filter_fecha_hasta(self, queryset, name, value):
        d = self._parse_date(value)
        if not d:
            return queryset
        dt = datetime.combine(d, time.max)
        if is_naive(dt):
            dt = make_aware(dt)
        return queryset.filter(fecha_venta__lte=dt)

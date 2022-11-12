import django_filters

from tasks import models


class TaskFilter(django_filters.FilterSet):
    category__name = django_filters.CharFilter(lookup_expr="icontains")
    status__name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = models.Task
        fields = ["available"]

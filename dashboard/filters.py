# dashboard/filters.py
import django_filters
from .models import Candidate

class CandidateFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="election_year__year")
    state = django_filters.CharFilter(field_name="state__name", lookup_expr="icontains")
    party = django_filters.CharFilter(field_name="party__name", lookup_expr="icontains")
    gender = django_filters.CharFilter(field_name="gender", lookup_expr="iexact")
    constituency = django_filters.CharFilter(field_name="constituency__name", lookup_expr="icontains")

    class Meta:
        model = Candidate
        fields = ['year', 'state', 'party', 'gender', 'constituency']

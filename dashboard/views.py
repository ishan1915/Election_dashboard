from django.shortcuts import render
# Create your views here.
from rest_framework import generics
from .models import Candidate
from .serializers import *
from .filters import CandidateFilter
from django_filters.rest_framework import DjangoFilterBackend

class CandidateListView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CandidateFilter

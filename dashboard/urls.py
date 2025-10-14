from django.urls import path,include
from .views import *
urlpatterns = [
    path('candidates/', CandidateListView.as_view(), name='candidate-list'),

]

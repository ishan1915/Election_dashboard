from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'constituencies', ConstituencyViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('candidates/', CandidateListView.as_view(), name='candidate-list'),

    path('winner-margins/', winner_margins, name='winner-margins'),

    path('gender-representation/', gender_representation, name='gender-representation'),
    path('turnout/', state_turnout, name='state-turnout'),

    path("vote-share/", vote_share_api, name="vote-share"),



     

]

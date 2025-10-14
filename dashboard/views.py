from django.shortcuts import render
# Create your views here.
from rest_framework import generics,viewsets
from .models import Candidate
from .serializers import *
from .filters import CandidateFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count,Avg,Sum



 

class CandidateListView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CandidateFilter
    
class ConstituencyViewSet(viewsets.ModelViewSet):
    queryset = Constituency.objects.all()
    serializer_class = ConstituencySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        state_name = self.request.query_params.get("state")
        if state_name:
            queryset = queryset.filter(state__name__iexact=state_name)
        return queryset
    



@api_view(['GET'])
def winner_margins(request):
     
    year = request.GET.get('year')
    state = request.GET.get('state')
    party = request.GET.get('party')

    candidates = Candidate.objects.filter(position=1) 

    if year:
        candidates = candidates.filter(election_year__year=year)
    if state:
        candidates = candidates.filter(state__name__iexact=state)
    if party:
        candidates = candidates.filter(party__name__iexact=party)

     
    data = candidates.values(
        'state__name',
        'constituency__name',
        'party__name',
        'margin',
    )

    return Response(list(data))




@api_view(['GET'])
def gender_representation(request):
     
    winners = Candidate.objects.filter(position=1)
    data = (
        winners.values('election_year__year', 'gender')
        .annotate(count=Count('id'))
        .order_by('election_year__year')
    )

    result = {}
    for entry in data:
        year = entry['election_year__year']
        gender = entry['gender'].capitalize() if entry['gender'] else "Unknown"
        count = entry['count']

        if year not in result:
            result[year] = {"year": year, "Male": 0, "Female": 0, "Unknown": 0}
        result[year][gender] = count

     
    years = [1991, 1996, 1998, 1999, 2004, 2009, 2014, 2019]
    filtered_result = [result[y] for y in years if y in result]

    return Response(filtered_result)



@api_view(['GET'])
def state_turnout(request):
    year = request.GET.get('year')
    qs = Candidate.objects.filter(position=1)   
    if year:
        qs = qs.filter(election_year__year=year)

    data = qs.values('state__name').annotate(avg_turnout=Avg('turnout_percentage')).order_by('state__name')
     
    return Response([{'state': d['state__name'], 'avg_turnout': d['avg_turnout'] or 0} for d in data])



@api_view(['GET'])
def vote_share_api(request):
    year = request.GET.get('year')
    if not year:
        return Response({"error": "Year parameter required"}, status=400)

    # Sum votes per party
    party_votes = (
        Candidate.objects
        .filter(election_year__year=year)
        .values('party')
        .annotate(total_votes=Sum('votes'))
        .order_by('-total_votes')
    )

    total_votes = sum(p['total_votes'] for p in party_votes)
    top_parties = list(party_votes[:10])
    others_votes = sum(p['total_votes'] for p in party_votes[10:])

    
    if others_votes > 0:
        top_parties.append({
            'party': 'Others',
            'total_votes': others_votes
        })

     
    for p in top_parties:
        p['vote_share'] = round((p['total_votes'] / total_votes) * 100, 2)

    return Response(top_parties)
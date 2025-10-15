from django.shortcuts import render
# Create your views here.
from rest_framework import generics,viewsets
from .models import Candidate,CandidateEducation
from .serializers import *
from .filters import CandidateFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count,Avg,Sum,Q

from dashboard import models



 

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

    
    party_votes = (
        Candidate.objects
        .filter(election_year__year=year)
        .values('party__name')  
        .annotate(total_votes=Sum('votes'))
        .order_by('-total_votes')
    )

    total_votes = sum(p['total_votes'] for p in party_votes)
    if total_votes == 0:
        return Response([])

    top_parties = list(party_votes[:10])
    others_votes = sum(p['total_votes'] for p in party_votes[10:])

    
    for p in top_parties:
        p['party'] = p.pop('party__name') or "Unknown"

    
    if others_votes > 0:
        top_parties.append({
            'party': 'Others',
            'total_votes': others_votes
        })

    
    for p in top_parties:
        p['vote_share'] = round((p['total_votes'] / total_votes) * 100, 2)

    return Response(top_parties)




@api_view(['GET'])
def turnout_summary(request):
    year = request.GET.get('year')
    if not year:
        return Response({"error": "Year parameter required"}, status=400)

     
    data = (
        Candidate.objects
        .filter(election_year__year=year)
        .values('state__name')
        .annotate(avg_turnout=Avg('turnout_percentage'))
        .order_by('-avg_turnout')
    )

    if not data:
        return Response({"message": "No data found for given year"}, status=404)

    top = data[0]
    return Response({
        "highest_state": top['state__name'],
        "highest_turnout": round(top['avg_turnout'], 2) if top['avg_turnout'] else None,
        "state_turnouts": [
            {
                "state": d['state__name'],
                "avg_turnout": round(d['avg_turnout'], 2) if d['avg_turnout'] else 0
            }
            for d in data
        ]
    })




 
@api_view(['GET'])
def party_seat_change(request):
    year1 = request.GET.get('year1')
    year2 = request.GET.get('year2')

    if not year1 or not year2:
        return Response({"error": "Both year1 and year2 are required"}, status=400)

    data_year1 = (
        Candidate.objects
        .filter(election_year__year=year1, result_status="Won")
        .values('party__name')
        .annotate(seats=Count('id'))
    )

    data_year2 = (
        Candidate.objects
        .filter(election_year__year=year2, result_status="Won")
        .values('party__name')
        .annotate(seats=Count('id'))
    )

     
    year1_dict = {d['party__name']: d['seats'] for d in data_year1}
    year2_dict = {d['party__name']: d['seats'] for d in data_year2}

     
    all_parties = set(year1_dict.keys()) | set(year2_dict.keys())
    result = []
    for party in all_parties:
        seats1 = year1_dict.get(party, 0)
        seats2 = year2_dict.get(party, 0)
        change = seats2 - seats1
        result.append({
            "party": party or "Independent",
            "year1_seats": seats1,
            "year2_seats": seats2,
            "seat_change": change
        })

     
    if result:
        max_gain = max(result, key=lambda x: x['seat_change'])
        max_loss = min(result, key=lambda x: x['seat_change'])
    else:
        max_gain = max_loss = None

    return Response({
        "comparison": f"{year1} vs {year2}",
        "max_gain": max_gain,
        "max_loss": max_loss,
        "details": sorted(result, key=lambda x: -x['seat_change'])
    })



@api_view(['GET'])
def education_win_correlation(request):
     
    years = [2009, 2014, 2019]

    data = (
        CandidateEducation.objects
        .filter(year__in=years)
        .values('education', 'year')
        .annotate(
            total_candidates=Count('id'),
            total_winners=Count('id', filter=Q(result_status='Won'))
        )
        .order_by('education', 'year')
    )

    result = []
    for d in data:
        total = d['total_candidates']
        won = d['total_winners']
        result.append({
            'education': d['education'],
            'year': d['year'],
            'win_percentage': round((won / total) * 100, 2) if total > 0 else 0
        })

    return Response(result)





@api_view(['GET'])
def narrow_victory_margins(request):
    year = request.GET.get('year')

    queryset = Candidate.objects.filter(position=1, margin__isnull=False)
    if year:
        queryset = queryset.filter(election_year__year=year)

    narrowest = (
        queryset
        .order_by('margin')[:10]
        .values(
            'state__name',
            'constituency__name',
            'party__name',
            'name',
            'margin',
            'election_year__year'
        )
    )

    data = [
        {
            'state': c['state__name'],
            'constituency': c['constituency__name'],
            'party': c['party__name'],
            'candidate': c['name'],
            'margin': c['margin'],
            'year': c['election_year__year']
        }
        for c in narrowest
    ]

    return Response(data)



 

@api_view(['GET'])
def women_candidates_percentage(request):
    """Calculate percentage of women candidates for selected election years."""
    
    # Only include these years
    valid_years = [1991, 1996, 1998, 1999, 2004, 2009, 2014, 2019]
    data = []

    for year in valid_years:
        total = Candidate.objects.filter(election_year__year=year).count()
        female = Candidate.objects.filter(
            election_year__year=year,
            gender__iexact='Female'
        ).count()

        if total > 0:
            female_percentage = round((female / total) * 100, 2)
        else:
            female_percentage = 0.0

        data.append({
            "year": year,
            "female_percentage": female_percentage,
            "total_candidates": total,
            "female_candidates": female,
        })

    return Response({"yearly_data": data})

from rest_framework import serializers
from .models import Candidate, State, Constituency, Party, ElectionYear

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class ConstituencySerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)
    class Meta:
        model = Constituency
        fields = '__all__'

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = '__all__'

class ElectionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionYear
        fields = '__all__'

class CandidateListSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source='state.name', read_only=True)
    party = serializers.CharField(source='party.name', read_only=True)
    year = serializers.IntegerField(source='election_year.year', read_only=True)
    votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['state', 'name', 'party', 'year', 'votes', 'result_status']

    def get_votes(self, obj):
         
        try:
            return int(float(obj.votes))
        except (ValueError, TypeError):
            return 0
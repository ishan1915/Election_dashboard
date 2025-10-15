from django.db import models

 


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Constituency(models.Model):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="constituencies")

    class Meta:
        unique_together = ('name', 'state')

    def __str__(self):
        return f"{self.name} ({self.state.name})"


class Party(models.Model):
    name = models.CharField(max_length=150, unique=True)
    abbreviation = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class ElectionYear(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


 
class Candidate(models.Model):
    name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, default="Unknown")
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    election_year = models.ForeignKey(ElectionYear, on_delete=models.CASCADE)

    # Election stats
    votes = models.FloatField(default=0.0)
    vote_share_percentage = models.FloatField(default=0.0)
    position = models.IntegerField(null=True, blank=True)
    margin = models.BigIntegerField(null=True, blank=True)
    turnout_percentage = models.FloatField(null=True, blank=True)
    result_status = models.CharField(max_length=20, default="Unknown")  # 'Won' or 'Lost'
    


    class Meta:
        indexes = [
            models.Index(fields=["election_year", "state", "party"]),
            models.Index(fields=["constituency", "state"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.party.name if self.party else 'Independent'} ({self.election_year.year})"




class CandidateEducation(models.Model):
    candidate_name = models.CharField(max_length=200)
    state_name = models.CharField(max_length=150)
    constituency_name = models.CharField(max_length=150)
    year = models.IntegerField()
    education = models.CharField(max_length=100, default="Unknown")
    position = models.IntegerField(null=True, blank=True)
    result_status = models.CharField(max_length=20, default="Unknown")   

    def __str__(self):
        return f"{self.candidate_name} ({self.year}) - {self.education}"

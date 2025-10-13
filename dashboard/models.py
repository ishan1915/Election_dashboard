from django.db import models

# Create your models here.
class ElectionResult(models.Model):
    state_name=models.CharField(max_length=20)
    assembly_no=models.IntegerField()
    constituency_no=models.IntegerField()
    year=models.IntegerField()
    month=models.FloatField()
    delimid=models.IntegerField()
    position=models.IntegerField()
    candidate=models.CharField(max_length=100)
    sex=models.CharField(max_length=10)
    party=models.CharField(max_length=50)
    votes=models.FloatField()
    candidate_type = models.CharField(max_length=100, null=True, blank=True)
    valid_votes = models.IntegerField()
    electors = models.FloatField()
    constituency_name = models.CharField(max_length=150)
    constituency_type = models.CharField(max_length=50)
    n_cand = models.IntegerField()
    turnout_percentage = models.FloatField()
    vote_share_percentage = models.FloatField()
    deposit_lost = models.CharField(max_length=10)
    margin = models.FloatField()
    margin_percentage = models.FloatField()
    enop = models.FloatField()
    pid = models.CharField(max_length=50)
    party_type_tcpd = models.CharField(max_length=50)
    party_id = models.FloatField()
    last_poll = models.BooleanField()
    contested = models.FloatField()
    no_terms = models.FloatField(null=True, blank=True)
    turncoat = models.CharField(max_length=10)
    incumbent = models.CharField(max_length=10)
    recontest = models.CharField(max_length=10)
    myneta_education = models.CharField(max_length=100, null=True, blank=True)
    tcpd_prof_main = models.CharField(max_length=100, null=True, blank=True)
    tcpd_prof_main_desc = models.CharField(max_length=100, null=True, blank=True)
    election_type = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.candidate} ({self.party}) - {self.state_name} {self.year}"
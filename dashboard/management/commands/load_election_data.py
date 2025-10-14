import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.models import State, Constituency, Party, ElectionYear, Candidate


class Command(BaseCommand):
    help = "Load election data from a CSV file into normalized models"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to CSV file (default: All_States_GE_Cleaned_v2.csv)',
            default=os.path.join(settings.BASE_DIR,  'All_States_GE_Cleaned_v2.csv')
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write(self.style.NOTICE(f"Loading data from {file_path}..."))

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [f.lower().strip() for f in reader.fieldnames]

            count = 0
            for row in reader:
                state_name = row.get('state_name', 'Unknown')
                constituency_name = row.get('constituency_name', 'Unknown')
                party_name = row.get('party', 'Independent')
                year_value = int(row.get('year', 0) or 0)

                # Create or get related objects
                state, _ = State.objects.get_or_create(name=state_name)
                constituency, _ = Constituency.objects.get_or_create(
                    name=constituency_name,
                    state=state
                )
                party, _ = Party.objects.get_or_create(name=party_name)
                election_year, _ = ElectionYear.objects.get_or_create(year=year_value)

                # Determine win/loss automatically if "position" or "votes" available
                result_status = "Unknown"
                try:
                    position = int(row.get('position', '') or 0)
                    if position == 1:
                        result_status = "Won"
                    elif position > 1:
                        result_status = "Lost"
                except ValueError:
                    pass

                # Create Candidate entry
                Candidate.objects.create(
                    name=row.get('candidate', 'Unknown'),
                    gender=row.get('gender', 'Unknown'),
                    party=party,
                    state=state,
                    constituency=constituency,
                    election_year=election_year,
                    votes=int(float(row.get('votes', 0) or 0)),
                    vote_share_percentage=float(row.get('vote_share_percentage', 0.0) or 0.0),
                    position=int(row.get('position', 0) or 0),
                    margin=float(row.get('margin', 0) or 0),
                    turnout_percentage=float(row.get('turnout_percentage', 0.0) or 0.0),
                    result_status=result_status
                )

                count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Successfully loaded {count} records!"))

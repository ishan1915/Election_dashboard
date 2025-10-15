import csv
from django.core.management.base import BaseCommand
from dashboard.models import CandidateEducation  # change 'your_app' to your actual app name


class Command(BaseCommand):
    help = "Import candidate education, position, and result directly from CSV."

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, required=True, help='Path to All_States_GE_Cleaned_v2.csv')

    def handle(self, *args, **options):
        csv_path = options['csv']
        count = 0

        education_map = {
            "Graduate Professional": "Graduate",
            "Graduate": "Graduate",
            "Post Graduate": "Post Graduate",
            "Doctrate": "Doctorate",
            "8th Pass": "8th Pass",
            "10th Pass": "10th Pass",
            "12th Pass": "12th Pass",
            "Illiterate": "Illiterate",
        }

        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    year = int(row.get('Year', '').strip())
                except (ValueError, TypeError):
                    continue

                # only import for 2009, 2014, 2019
                if year not in [2009, 2014, 2019]:
                    continue

                name = (row.get('Candidate') or '').strip()
                state = (row.get('State_Name') or '').strip()
                constituency = (row.get('Constituency_Name') or '').strip()
                education_raw = (row.get('MyNeta_education') or '').strip()
                position_raw = row.get('Position') or ''
                try:
                    position = int(position_raw)
                except ValueError:
                    position = None

                # Normalize education value using mapping
                education = education_map.get(education_raw, "Unknown")

                # Determine result
                result = "Won" if position == 1 else "Lost"

                CandidateEducation.objects.create(
                    candidate_name=name,
                    state_name=state,
                    constituency_name=constituency,
                    year=year,
                    education=education,
                    position=position,
                    result_status=result,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {count} candidate education records successfully."))

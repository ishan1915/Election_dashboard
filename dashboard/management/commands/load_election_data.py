import csv
from django.core.management.base import BaseCommand
from dashboard.models import ElectionResult

class Command(BaseCommand):
    help = "Load election data from cleaned CSV"

    def handle(self, *args, **options):
        file_path ="All_States_GE_Cleaned_v2.csv"

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Normalize header names (case-insensitive match)
            reader.fieldnames = [f.lower().strip() for f in reader.fieldnames]
            
            ElectionResult.objects.all().delete()  # optional

            records = []
            for row in reader:
                cleaned_row = {k: (None if v == "Unknown" else v) for k, v in row.items()}
                records.append(ElectionResult(**cleaned_row))

            ElectionResult.objects.bulk_create(records, batch_size=500)

            self.stdout.write(self.style.SUCCESS(f"Loaded {len(records)} records successfully!"))

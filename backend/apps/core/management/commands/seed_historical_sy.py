from django.core.management.base import BaseCommand
from apps.core.demo_dataset import seed_historical_school_year

class Command(BaseCommand):
    help = "Seed historical school year 2024-2025 with 60 realistic Filipino pupils, attendance, nutrition, BMI, ECCD assessments, and activities."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("BMV3 HISTORICAL SCHOOL YEAR (2024-2025) ARCHIVE SEEDING"))
        self.stdout.write(self.style.NOTICE("=" * 70))

        def on_progress(current, total):
            if current % 10 == 0 or current == total:
                self.stdout.write(f"  -> Generated {current}/{total} pupils and associated historical records...")

        result = seed_historical_school_year(progress_callback=on_progress)

        self.stdout.write(self.style.SUCCESS(f"\nHistorical School Year Archive [{result['historical_school_year']}] successfully populated!"))
        self.stdout.write(f"  - Total Enrolled Pupils: {result['total_children']} (Minimum requirement: 50)")
        self.stdout.write(f"  - Morning Shift Pupils: {result['morning_count']} (Minimum requirement: 25)")
        self.stdout.write(f"  - Afternoon Shift Pupils: {result['afternoon_count']} (Minimum requirement: 25)")
        self.stdout.write("  - Historical Status: COMPLETED / ARCHIVED (Read-Only)")
        self.stdout.write("  - Attendance, Nutrition, BMI, ECCD Milestones, and Activities: FULLY POPULATED\n")

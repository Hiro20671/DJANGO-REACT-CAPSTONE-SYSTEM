from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import SchoolYear, Child, UserProfile
import datetime

class Command(BaseCommand):
    help = "Seed or ensure Sky Dylan Villanueva as the sole enrolled pupil in the active school year (2026-2027)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ensuring Sky Dylan Villanueva in active school year (2026-2027)..."))

        # 1. School Year Setup: 2026-2027 must be active; 2025-2026 must be archived (inactive)
        SchoolYear.objects.filter(name="2025-2026").update(is_active=False)

        active_sy, _ = SchoolYear.objects.get_or_create(
            name="2026-2027",
            defaults={
                "is_active": True,
                "start_date": datetime.date(2026, 8, 24),
                "end_date": datetime.date(2027, 5, 28),
                "eccd_1st_start": datetime.date(2026, 9, 1),
                "eccd_1st_end": datetime.date(2026, 9, 25),
                "eccd_2nd_start": datetime.date(2027, 1, 4),
                "eccd_2nd_end": datetime.date(2027, 1, 29),
                "eccd_3rd_start": datetime.date(2027, 5, 3),
                "eccd_3rd_end": datetime.date(2027, 5, 28),
                "is_deleted": False,
            }
        )
        # Ensure only 2026-2027 is active
        SchoolYear.objects.exclude(id=active_sy.id).update(is_active=False)
        active_sy.is_active = True
        active_sy.save()

        # 2. Sky Dylan Villanueva (Sole Pupil in 2026-2027)
        sky, created_sky = Child.objects.update_or_create(
            first_name="Sky Dylan",
            last_name="Villanueva",
            school_year=active_sy,
            defaults={
                "middle_initial": "T",
                "age": 3,
                "gender": "Male",
                "dob": datetime.date(2023, 3, 15),
                "doe": datetime.date(2026, 8, 24),
                "shift": "Morning",
                "enrollment_status": "Enrolled",
                "attendance_status": "Present",
                "allergies": "Dairy / Milk",
                "health_conditions": "",
                "father_first_name": "Jeremy",
                "father_middle_initial": "T",
                "father_last_name": "Villanueva",
                "father_phone": "09053997797",
                "father_email": "jeremy_960@bmv3.local",
                "father_address": "Purok Central, Mayao Parada, Lucena City, Quezon, Region IV-A (CALABARZON)",
                "barangay": "Mayao Parada",
                "city_municipality": "Lucena City",
            }
        )

        # Link parent profile for Sky Dylan (jeremy_960)
        jeremy_parent = User.objects.filter(username="jeremy_960").first()
        if jeremy_parent and hasattr(jeremy_parent, 'userprofile'):
            sky.parents.add(jeremy_parent.userprofile)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Linked Sky Dylan Villanueva to parent account '{jeremy_parent.username}'."))

        self.stdout.write(self.style.SUCCESS(f"  [OK] Sky Dylan Villanueva enrolled in {active_sy.name} ({'Created' if created_sky else 'Updated'})"))

        # 3. Ensure Sky Dylan is the ONLY pupil in the current batch (2026-2027)
        deleted_others, _ = Child.objects.filter(school_year=active_sy).exclude(id=sky.id).delete()
        if deleted_others:
            self.stdout.write(self.style.WARNING(f"  [OK] Removed {deleted_others} other child records from {active_sy.name} so Sky Dylan is the only one."))

        # 4. Remove Sky Dylan & Denies Dador from 2025-2026 so 2025-2026 has exactly 60 archived pupils
        hist_sy = SchoolYear.objects.filter(name="2025-2026").first()
        if hist_sy:
            removed_from_hist, _ = Child.objects.filter(school_year=hist_sy, first_name__in=["Sky Dylan", "Denies"]).delete()
            if removed_from_hist:
                self.stdout.write(self.style.WARNING(f"  [OK] Removed {removed_from_hist} non-archive pupils from {hist_sy.name} to preserve exactly 60 archived pupils."))

        total_enrolled = Child.objects.filter(school_year=active_sy, enrollment_status="Enrolled").count()
        self.stdout.write(self.style.SUCCESS(f"  [DONE] Active School Year {active_sy.name} now has {total_enrolled} enrolled pupil (Sky Dylan Villanueva)."))


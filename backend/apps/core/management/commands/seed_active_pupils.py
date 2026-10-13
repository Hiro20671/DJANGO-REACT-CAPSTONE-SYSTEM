from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import (
    SchoolYear, Child, UserProfile, AttendanceRecord,
    NutritionRecord, BMIRecord, ECCDAssessment, EngagementRecord, Activity, NoClassDay
)
from apps.core.demo_dataset import seed_historical_school_year, seed_demo_parent_accounts
import datetime

class Command(BaseCommand):
    help = "Seed or ensure Sky Dylan Villanueva as the sole enrolled pupil in active school year (2026-2027), preserve 2025-2026 archive (60 pupils), and sanitize parent demo accounts."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ensuring proper school years and pupil cohorts..."))

        # 1. Historical Year (2025-2026, Completed & Archived)
        hist_sy, created_hist = SchoolYear.objects.get_or_create(
            name="2025-2026",
            defaults={
                "is_active": False,
                "start_date": datetime.date(2025, 8, 25),
                "end_date": datetime.date(2026, 5, 29),
                "eccd_1st_start": datetime.date(2025, 9, 1),
                "eccd_1st_end": datetime.date(2025, 9, 26),
                "eccd_2nd_start": datetime.date(2026, 1, 5),
                "eccd_2nd_end": datetime.date(2026, 1, 30),
                "eccd_3rd_start": datetime.date(2026, 5, 4),
                "eccd_3rd_end": datetime.date(2026, 5, 29),
                "is_deleted": False,
            }
        )
        hist_sy.is_active = False
        hist_sy.is_deleted = False
        hist_sy.save()

        # 2. Current Active Year (2026-2027)
        active_sy, created_act = SchoolYear.objects.get_or_create(
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
        active_sy.is_active = True
        active_sy.is_deleted = False
        active_sy.save()

        # Safely migrate any children & records attached to rogue school years like "2025-2026 Batch" or "2024-2025"
        rogue_sys = SchoolYear.objects.exclude(id__in=[hist_sy.id, active_sy.id])
        for rogue in rogue_sys:
            Child.objects.filter(school_year=rogue).update(school_year=hist_sy)
            AttendanceRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
            NutritionRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
            ECCDAssessment.objects.filter(school_year=rogue).update(school_year=hist_sy)
            BMIRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
            EngagementRecord.objects.filter(school_year=rogue).update(school_year=hist_sy)
            Activity.objects.filter(school_year=rogue).update(school_year=hist_sy)
            NoClassDay.objects.filter(school_year=rogue).update(school_year=hist_sy)
        deleted_rogue, _ = rogue_sys.delete()
        if deleted_rogue:
            self.stdout.write(self.style.WARNING(f"  [OK] Cleaned up {deleted_rogue} rogue / accidental school years."))

        # Strictly ensure only 2026-2027 is active
        SchoolYear.objects.exclude(id=active_sy.id).update(is_active=False)

        # 3. Check 2025-2026 archive count. If fewer than 60 pupils, re-seed the historical 60 pupils
        hist_count = Child.objects.filter(school_year=hist_sy).count()
        if hist_count < 60:
            self.stdout.write(self.style.NOTICE(f"  [->] 2025-2026 has {hist_count}/60 pupils. Seeding complete 60 archived pupils..."))
            seed_historical_school_year()
            hist_count = Child.objects.filter(school_year=hist_sy).count()
            self.stdout.write(self.style.SUCCESS(f"  [OK] 2025-2026 archive now populated with {hist_count} pupils."))

        # 4. Sky Dylan Villanueva (Sole Pupil in 2026-2027)
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

        self.stdout.write(self.style.SUCCESS(f"  [OK] Sky Dylan Villanueva in active {active_sy.name} ({'Created' if created_sky else 'Updated'})"))

        # 5. Ensure Sky Dylan is the ONLY pupil in the current batch (2026-2027)
        deleted_others, _ = Child.objects.filter(school_year=active_sy).exclude(id=sky.id).delete()
        if deleted_others:
            self.stdout.write(self.style.WARNING(f"  [OK] Removed {deleted_others} other child records from {active_sy.name}."))

        # 6. Remove Sky Dylan from 2025-2026 archive if accidentally copied
        Child.objects.filter(school_year=hist_sy, first_name="Sky Dylan").delete()

        # 7. Clean up parent demo accounts:
        # - Remove "Elena" or test names
        # - Reset all demo accounts (parent001 - parent080) to first_name="Parent", last_name=""
        demo_users = User.objects.filter(username__startswith="parent0", userprofile__is_teacher=False)
        for u in demo_users:
            u.first_name = "Parent"
            u.last_name = ""
            u.is_active = True
            u.save()
            if hasattr(u, 'userprofile'):
                u.userprofile.first_login = True
                u.userprofile.is_account_restricted = False
                u.userprofile.children.clear()
                u.userprofile.save()

        # Any other user with first_name 'Elena' who is not a teacher
        User.objects.filter(first_name__iexact="elena", userprofile__is_teacher=False).update(first_name="Parent", last_name="")

        self.stdout.write(self.style.SUCCESS(f"  [OK] Sanitized {demo_users.count()} demo parent accounts (first_name='Parent', first_login=True)."))
        self.stdout.write(self.style.SUCCESS(f"  [DONE] 2025-2026: Inactive Archive ({Child.objects.filter(school_year=hist_sy).count()} pupils)"))
        self.stdout.write(self.style.SUCCESS(f"  [DONE] 2026-2027: Active Batch ({Child.objects.filter(school_year=active_sy).count()} pupil: Sky Dylan Villanueva)"))

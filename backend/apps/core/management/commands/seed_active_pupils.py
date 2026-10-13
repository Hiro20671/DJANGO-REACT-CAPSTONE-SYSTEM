from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import SchoolYear, Child, UserProfile, AttendanceRecord, NutritionRecord, BMIRecord
import datetime

class Command(BaseCommand):
    help = "Seed or ensure Sky Dylan Villanueva, Denies Dador, and active cohort pupils in the active school year (2025-2026)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ensuring active pupils in current school year..."))

        active_sy = SchoolYear.objects.filter(name="2025-2026").first()
        if not active_sy:
            active_sy, _ = SchoolYear.objects.get_or_create(
                name="2025-2026",
                defaults={"is_active": True}
            )

        # Make sure 2025-2026 is active
        SchoolYear.objects.filter(id=active_sy.id).update(is_active=True)

        # 1. Sky Dylan Villanueva
        sky, created_sky = Child.objects.update_or_create(
            first_name="Sky Dylan",
            last_name="Villanueva",
            school_year=active_sy,
            defaults={
                "middle_initial": "T",
                "age": 3,
                "gender": "Male",
                "dob": datetime.date(2023, 3, 15),
                "shift": "Morning",
                "enrollment_status": "Enrolled",
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
        self.stdout.write(self.style.SUCCESS(f"  [OK] Sky Dylan Villanueva enrolled in {active_sy.name} ({'Created' if created_sky else 'Updated'})"))

        # 2. Denies Dador
        denies, created_denies = Child.objects.update_or_create(
            first_name="Denies",
            last_name="Dador",
            school_year=active_sy,
            defaults={
                "middle_initial": "M",
                "age": 4,
                "gender": "Female",
                "dob": datetime.date(2022, 5, 10),
                "shift": "Morning",
                "enrollment_status": "Enrolled",
                "allergies": "None",
                "health_conditions": "None",
                "father_first_name": "Dennis",
                "father_last_name": "Dador",
                "father_phone": "0918-555-0199",
                "barangay": "Market View",
                "city_municipality": "Lucena City",
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  [OK] Denies Dador enrolled in {active_sy.name} ({'Created' if created_denies else 'Updated'})"))

        # 3. Also populate sample cohort if empty so class list is lively
        current_count = Child.objects.filter(school_year=active_sy).count()
        if current_count < 10:
            sample_peers = [
                ("Mateo Luis", "Cruz", "Male", 4, "Morning", "2021-08-14"),
                ("Sofia Beatrice", "Garcia", "Female", 4, "Morning", "2021-09-20"),
                ("Lucas Antonio", "Bautista", "Male", 4, "Afternoon", "2021-04-18"),
                ("Chloe Althea", "Mendoza", "Female", 4, "Afternoon", "2021-11-03"),
                ("Gabriel Paulo", "Aquino", "Male", 4, "Morning", "2021-06-25"),
                ("Jasmine Nicole", "Flores", "Female", 4, "Afternoon", "2021-02-14"),
                ("Noah Elijah", "Castillo", "Male", 3, "Morning", "2022-01-30"),
                ("Althea Ysabel", "Ramos", "Female", 3, "Afternoon", "2022-03-22"),
            ]
            for fn, ln, gen, age, shf, dob_str in sample_peers:
                dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
                Child.objects.get_or_create(
                    first_name=fn,
                    last_name=ln,
                    school_year=active_sy,
                    defaults={
                        "gender": gen,
                        "age": age,
                        "shift": shf,
                        "dob": dob,
                        "enrollment_status": "Enrolled",
                        "barangay": "Market View",
                        "city_municipality": "Lucena City",
                    }
                )

        total_enrolled = Child.objects.filter(school_year=active_sy, enrollment_status="Enrolled").count()
        self.stdout.write(self.style.SUCCESS(f"  [DONE] Active School Year {active_sy.name} now has {total_enrolled} enrolled pupils."))

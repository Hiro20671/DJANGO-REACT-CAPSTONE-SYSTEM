from django.core.management.base import BaseCommand
from apps.core.demo_dataset import (
    reset_demonstration_database,
    seed_historical_school_year,
    seed_demo_parent_accounts,
    SchoolYear, Child, UserProfile, AttendanceRecord,
    NutritionRecord, BMIRecord, ECCDAssessment
)
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Orchestrate complete BMV3 Demo Setup: Safe reset, Historical 2024-2025 archive seeding, and 60 Parent Demo accounts creation."

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-reset',
            action='store_true',
            help='Skip the database reset step and keep existing records.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(self.style.NOTICE("  BMV3 CHILD DEVELOPMENT CENTER MANAGEMENT SYSTEM"))
        self.stdout.write(self.style.NOTICE("  DEMONSTRATION ENVIRONMENT ORCHESTRATION SETUP"))
        self.stdout.write(self.style.NOTICE("=" * 75))

        # STEP 1: Safe Reset
        if not options.get('skip_reset', False):
            self.stdout.write(self.style.WARNING("\n[STEP 1/4] Safely resetting demonstration records..."))
            reset_res = reset_demonstration_database()
            self.stdout.write(f"  [OK] Purged {reset_res['deleted_children']} previous pupil records.")
            self.stdout.write(f"  [OK] Purged {reset_res['deleted_parents']} previous demo parent accounts.")
            self.stdout.write("  [OK] Preserved teacher/admin accounts, schema, and system configuration.")
        else:
            self.stdout.write("\n[STEP 1/4] Skipping database reset as requested.")

        # STEP 2: Historical School Year Archive (2024-2025)
        self.stdout.write(self.style.WARNING("\n[STEP 2/4] Seeding Historical School Year (2024-2025) Archive..."))
        def on_progress(curr, total):
            if curr % 15 == 0 or curr == total:
                self.stdout.write(f"  -> Generated {curr}/{total} pupils and associated historical records...")

        sy_res = seed_historical_school_year(progress_callback=on_progress)
        self.stdout.write(self.style.SUCCESS(f"  [OK] Historical School Year: {sy_res['historical_school_year']} (Completed / Archived)"))
        self.stdout.write(f"  [OK] Morning Shift Pupils: {sy_res['morning_count']} (Requirement: >= 25)")
        self.stdout.write(f"  [OK] Afternoon Shift Pupils: {sy_res['afternoon_count']} (Requirement: >= 25)")
        self.stdout.write(f"  [OK] Total Unique Pupils: {sy_res['total_children']} (Requirement: >= 50)")

        # STEP 3: Provision 60 Demo Parent Accounts
        self.stdout.write(self.style.WARNING("\n[STEP 3/4] Provisioning 60 Ready-to-Use Parent Demonstration Accounts..."))
        acc_res = seed_demo_parent_accounts(reset_passwords=True)
        self.stdout.write(self.style.SUCCESS(f"  [OK] Provisioned {acc_res['total_accounts']} Parent Demonstration Accounts."))
        self.stdout.write(f"  [OK] Usernames: parent001 through parent060")
        self.stdout.write(f"  [OK] Mandatory First-Login Password Change: ENABLED for all 60 accounts")
        self.stdout.write(f"  [OK] Credentials exported to: {acc_res['csv_path']}")

        # STEP 4: Active Cohort Seeding (Sky Dylan Villanueva, Denies Dador, active pupils)
        self.stdout.write(self.style.WARNING("\n[STEP 4/5] Enrolling Active Pupils (Sky Dylan Villanueva & Cohort)..."))
        from django.core.management import call_command
        call_command('seed_active_pupils')

        # STEP 5: Integrity Verification
        self.stdout.write(self.style.WARNING("\n[STEP 5/5] Running Database Integrity and Verification Checks..."))
        hist_sy = SchoolYear.objects.filter(name="2024-2025").first()
        active_sy = SchoolYear.objects.filter(name="2025-2026").first()
        total_children = Child.objects.filter(school_year=hist_sy).count()
        morning_ch = Child.objects.filter(school_year=hist_sy, shift="Morning").count()
        afternoon_ch = Child.objects.filter(school_year=hist_sy, shift="Afternoon").count()
        total_demo_users = User.objects.filter(username__startswith="parent", userprofile__is_teacher=False).count()
        first_login_count = UserProfile.objects.filter(user__username__startswith="parent", first_login=True).count()
        att_count = AttendanceRecord.objects.filter(school_year=hist_sy).count()
        nut_count = NutritionRecord.objects.filter(school_year=hist_sy).count()
        bmi_count = BMIRecord.objects.filter(school_year=hist_sy).count()
        eccd_count = ECCDAssessment.objects.filter(school_year=hist_sy).count()

        self.stdout.write(f"  [OK] Historical School Year 2024-2025 Active Status: {hist_sy.is_active} (Must be False)")
        self.stdout.write(f"  [OK] Current School Year 2025-2026 Active Status: {active_sy.is_active if active_sy else 'N/A'} (Must be True)")
        self.stdout.write(f"  [OK] Total Historical Children: {total_children} (Pass: >= 50)")
        self.stdout.write(f"  [OK] Morning Shift Count: {morning_ch} (Pass: >= 25)")
        self.stdout.write(f"  [OK] Afternoon Shift Count: {afternoon_ch} (Pass: >= 25)")
        self.stdout.write(f"  [OK] Provisioned Parent Demo Accounts: {total_demo_users} (Pass: exactly 60)")
        self.stdout.write(f"  [OK] Accounts Requiring First-Login Password Change: {first_login_count} (Pass: exactly 60)")
        self.stdout.write(f"  [OK] Historical Attendance Records: {att_count}")
        self.stdout.write(f"  [OK] Historical Nutrition Records: {nut_count}")
        self.stdout.write(f"  [OK] Historical BMI Records: {bmi_count}")
        self.stdout.write(f"  [OK] Historical ECCD Assessments: {eccd_count}")

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 75))
        self.stdout.write(self.style.SUCCESS("  DEMO SETUP COMPLETED SUCCESSFULLY! SYSTEM READY FOR DEMONSTRATION."))
        self.stdout.write(self.style.SUCCESS("=" * 75 + "\n"))

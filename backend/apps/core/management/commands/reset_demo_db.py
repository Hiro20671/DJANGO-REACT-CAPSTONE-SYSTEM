from django.core.management.base import BaseCommand
from apps.core.demo_dataset import reset_demonstration_database

class Command(BaseCommand):
    help = "Safely reset the database by clearing demo pupil and parent records while preserving teachers, schema, migrations, and system settings."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bypass confirmation prompt.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=" * 70))
        self.stdout.write(self.style.WARNING("BMV3 DATABASE RESET (SAFE DEMO PURGE)"))
        self.stdout.write(self.style.WARNING("=" * 70))
        self.stdout.write("This command will safely remove existing demonstration child and parent records.")
        self.stdout.write("Teacher/Admin accounts, database schema, migrations, ECCD milestones, and system branding will be PRESERVED.\n")

        force = options.get('force', False)
        if not force:
            confirm = input("Are you sure you want to proceed with resetting demo data? (yes/no): ").strip().lower()
            if confirm != 'yes':
                self.stdout.write(self.style.NOTICE("Reset operation cancelled."))
                return

        result = reset_demonstration_database()
        self.stdout.write(self.style.SUCCESS("\nDatabase reset completed successfully!"))
        self.stdout.write(f"  - Deleted Demo Pupil Records: {result['deleted_children']}")
        self.stdout.write(f"  - Deleted Demo Parent Accounts: {result['deleted_parents']}")
        self.stdout.write("  - Teacher & Admin Accounts: PRESERVED")
        self.stdout.write("  - System Settings & ECCD Milestones: PRESERVED\n")

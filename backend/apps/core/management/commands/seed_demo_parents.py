from django.core.management.base import BaseCommand
from apps.core.demo_dataset import seed_demo_parent_accounts, seed_historical_school_year, Child, SchoolYear

class Command(BaseCommand):
    help = "Provision exactly 60 parent demonstration accounts (parent001 to parent060) linked to pupils with mandatory first-login password change."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-passwords',
            action='store_true',
            help='Reset passwords for existing demo accounts and set first_login back to True.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("BMV3 DEMO PARENT ACCOUNTS PROVISIONING"))
        self.stdout.write(self.style.NOTICE("=" * 70))

        # Check if historical children exist; if not, seed them first
        hist_sy = SchoolYear.objects.filter(name="2025-2026").first()
        child_count = Child.objects.filter(school_year=hist_sy).count() if hist_sy else 0

        if child_count < 50:
            self.stdout.write(self.style.WARNING("Historical pupils not found. Seeding 2025-2026 historical dataset first..."))
            seed_historical_school_year()

        reset_pw = options.get('reset_passwords', False)
        result = seed_demo_parent_accounts(reset_passwords=reset_pw)

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully provisioned {result['total_accounts']} Parent Demonstration Accounts!"))
        self.stdout.write(f"  - Newly Created: {result['created_count']}")
        self.stdout.write(f"  - Updated / Linked: {result['updated_count']}")
        self.stdout.write(f"  - Restricted Credentials File: {result['csv_path']}")
        self.stdout.write("  - Mandatory First-Login Password Change: ENABLED\n")

        self.stdout.write(self.style.NOTICE("-" * 70))
        self.stdout.write(f"{'Account':<8} | {'Username':<12} | {'Temporary Password':<18} | {'First Login Change'}")
        self.stdout.write(self.style.NOTICE("-" * 70))
        for row in result['accounts'][:10]:
            self.stdout.write(f"{row['Account']:<8} | {row['Username']:<12} | {row['Temporary Password']:<18} | {row['First Login Password Change']}")
        self.stdout.write(f"... and {result['total_accounts'] - 10} more accounts (refer to {result['csv_path']})")
        self.stdout.write(self.style.NOTICE("=" * 70))

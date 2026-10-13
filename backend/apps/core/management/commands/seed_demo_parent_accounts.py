import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from apps.core.models import UserProfile

from django.conf import settings

class Command(BaseCommand):
    help = "Provision exactly 80 built-in demonstration parent accounts (parent001 to parent080) without enrolled children and with mandatory first-login password change."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset credentials and first_login status for the 80 demo accounts.',
        )
        parser.add_argument(
            '--output-csv',
            type=str,
            default='',
            help='Custom output path for the credentials CSV file.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(self.style.NOTICE("BMV3 80 PRE-CREATED PARENT DEMO ACCOUNTS PROVISIONING"))
        self.stdout.write(self.style.NOTICE("=" * 75))

        reset_mode = options.get('reset', False)
        custom_csv = options.get('output_csv', '')

        if custom_csv:
            csv_paths = [Path(custom_csv)]
        else:
            # Workspace root: c:\Capstone\bmv3_80_demo_parent_credentials.csv
            root_dir = Path(settings.BASE_DIR).parent
            csv_paths = [
                root_dir / 'bmv3_80_demo_parent_credentials.csv',
                Path(settings.BASE_DIR) / 'bmv3_80_demo_parent_credentials.csv'
            ]

        accounts_data = []
        created_count = 0
        updated_count = 0
        preserved_count = 0

        with transaction.atomic():
            for i in range(1, 81):
                acc_num = f"{i:03d}"
                username = f"parent{acc_num}"
                temp_password = f"Bmv3!Parent{acc_num}#"
                email = f"parent{acc_num}@demo.bmv3.local"
                first_name = f"Parent"
                last_name = f"Demo{acc_num}"

                user = User.objects.filter(username=username).first()

                if user is None:
                    # Brand new user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=temp_password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.is_teacher = False
                    profile.first_login = True
                    profile.is_account_restricted = False
                    profile.home_address_text = f"Lucena City Demonstration Zone {acc_num}"
                    profile.save()
                    
                    # Ensure absolutely NO children are attached
                    profile.children.clear()

                    created_count += 1
                    status_str = "Must change password"
                    effective_pw = temp_password
                else:
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.is_teacher = False
                    profile.is_account_restricted = False

                    # Ensure empty child list for demo accounts
                    profile.children.clear()

                    if reset_mode:
                        user.set_password(temp_password)
                        user.save()
                        profile.first_login = True
                        profile.save()
                        updated_count += 1
                        status_str = "Must change password"
                        effective_pw = temp_password
                    else:
                        if profile.first_login:
                            # Reapply password in case it was not changed yet
                            user.set_password(temp_password)
                            user.save()
                            status_str = "Must change password"
                            effective_pw = temp_password
                            updated_count += 1
                        else:
                            # User has already changed password; preserve it safely
                            status_str = "Password already changed by user"
                            effective_pw = "[User Custom Password Preserved]"
                            preserved_count += 1

                accounts_data.append({
                    'Account No.': i,
                    'Username': username,
                    'Temporary Password': effective_pw,
                    'Initial Status': status_str
                })

        # Write restricted CSV credential report to configured paths
        for cp in csv_paths:
            try:
                with open(cp, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Account No.', 'Username', 'Temporary Password', 'Initial Status'])
                    writer.writeheader()
                    for row in accounts_data:
                        writer.writerow(row)
                self.stdout.write(self.style.SUCCESS(f"Saved credentials report to: {cp}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to write CSV file to {cp}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nProvisioning Complete:"))
        self.stdout.write(f"  - Total Configured Demo Accounts: 80")
        self.stdout.write(f"  - Newly Created Accounts: {created_count}")
        self.stdout.write(f"  - Updated / Synchronized: {updated_count}")
        self.stdout.write(f"  - Passwords Preserved (Already Changed): {preserved_count}")
        self.stdout.write(f"  - Linked Children: 0 (Pure empty parent accounts ready for enrollment)")
        self.stdout.write(f"  - Mandatory First-Login Password Change: ENABLED for all active temporary accounts\n")

        self.stdout.write(self.style.NOTICE("-" * 75))
        self.stdout.write(f"{'Account No.':<12} | {'Username':<12} | {'Temporary Password':<22} | {'Initial Status'}")
        self.stdout.write(self.style.NOTICE("-" * 75))
        for row in accounts_data[:10]:
            self.stdout.write(f"{row['Account No.']:<12} | {row['Username']:<12} | {row['Temporary Password']:<22} | {row['Initial Status']}")
        self.stdout.write(f"... and 70 more accounts (Full credential report in {csv_paths[0]})")
        self.stdout.write(self.style.NOTICE("=" * 75))

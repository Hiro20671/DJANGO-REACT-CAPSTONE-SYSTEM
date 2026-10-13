from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import sys

class Command(BaseCommand):
    help = "Send a test email via Brevo to verify Brevo API connectivity and email delivery."

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            default=getattr(settings, 'DEFAULT_FROM_EMAIL', 'jeremybryanvillanueva@gmail.com'),
            help='Recipient email address to test (default: settings.DEFAULT_FROM_EMAIL)',
        )

    def handle(self, *args, **options):
        recipient = options['to']
        self.stdout.write(self.style.NOTICE("=" * 65))
        self.stdout.write(self.style.NOTICE("  BREVO EMAIL CONNECTIVITY TEST"))
        self.stdout.write(self.style.NOTICE("=" * 65))

        backend = getattr(settings, 'EMAIL_BACKEND', 'Not configured')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'jeremybryanvillanueva@gmail.com')
        brevo_key = getattr(settings, 'BREVO_API_KEY', '') or getattr(settings, 'ANYMAIL', {}).get('BREVO_API_KEY', '')

        masked_key = f"{brevo_key[:10]}...{brevo_key[-6:]}" if len(brevo_key) > 16 else ("Configured" if brevo_key else "MISSING")

        self.stdout.write(f"  * EMAIL_BACKEND     : {backend}")
        self.stdout.write(f"  * DEFAULT_FROM_EMAIL: {from_email}")
        self.stdout.write(f"  * BREVO_API_KEY     : {masked_key}")
        self.stdout.write(f"  * Recipient Target  : {recipient}")
        self.stdout.write(self.style.NOTICE("-" * 65))

        subject = "[BMV3 Test] Brevo Notification System Online"
        text_body = (
            "Congratulations!\n\n"
            "This is a confirmation that your Brevo Email API service is configured properly "
            "and operating live on PythonAnywhere for BMV3 Child Development Center.\n\n"
            "Parent account credential deliveries and announcement textblasts are fully functional."
        )
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 580px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 16px;">
                <h2 style="color: #1e40af; margin: 0 0 6px 0;">BMV3 Child Development Center</h2>
                <span style="background: #10b981; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">
                    Brevo Test Passed
                </span>
            </div>
            <p style="color: #334155; font-size: 1rem; line-height: 1.5;">
                Hello <strong>{recipient}</strong>,
            </p>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                Your BMV3 notification engine has successfully dispatched this message via the <strong>Brevo HTTPS API (Port 443)</strong>.
            </p>
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 8px; margin: 18px 0;">
                <p style="margin: 0; color: #166534; font-weight: 600; font-size: 0.92rem;">
                    Parent credential alerts & announcement textblasts are fully operational!
                </p>
            </div>
            <p style="margin-top: 24px; color: #64748b; font-size: 0.85rem;">
                Barangay Market View 3, Lucena City | Automated Capstone Delivery Engine
            </p>
        </div>
        """

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=f"BMV3 Child Development Center <{from_email}>",
                to=[recipient]
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f"\n[SUCCESS] Test email successfully delivered to: {recipient}!"))
            self.stdout.write(self.style.SUCCESS("Check your inbox (and spam/promotions folder) to see the email.\n"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n[ERROR] Failed to send email via Brevo: {e}"))
            self.stdout.write(self.style.WARNING("\nTroubleshooting Suggestions:"))
            self.stdout.write(" 1. Verify that BREVO_API_KEY is exported in your environment or WSGI file.")
            self.stdout.write(" 2. Ensure your Brevo API key begins with 'xkeysib-'.")
            self.stdout.write(" 3. Verify sender email in Brevo: go to Brevo > Senders & IP and confirm the sender is verified.")
            sys.exit(1)

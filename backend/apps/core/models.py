from django.db import models
from django.contrib.auth.models import User

class Enrollment(models.Model):
    full_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Subject(models.Model):
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    
    def __str__(self):
        return self.subject_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='parent_profiles/', null=True, blank=True)
    first_login = models.BooleanField(default=True)
    home_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    home_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    home_address_text = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.user.username} - {'Teacher' if self.is_teacher else 'Parent'}"


class SchoolYear(models.Model):
    name = models.CharField(max_length=20, unique=True) # e.g. "2024-2025"
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # ECCD Assessment Period Dates
    eccd_1st_start = models.DateField(null=True, blank=True)
    eccd_1st_end = models.DateField(null=True, blank=True)
    eccd_2nd_start = models.DateField(null=True, blank=True)
    eccd_2nd_end = models.DateField(null=True, blank=True)
    eccd_3rd_start = models.DateField(null=True, blank=True)
    eccd_3rd_end = models.DateField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # deactivate all other school years
            SchoolYear.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
        
        # Automatically update any Draft assessment dates to align with the new school year evaluation start dates
        from apps.core.models import ECCDAssessment
        if self.eccd_1st_start:
            ECCDAssessment.objects.filter(school_year=self, assessment_period='1st', status='Draft').update(assessment_date=self.eccd_1st_start)
        if self.eccd_2nd_start:
            ECCDAssessment.objects.filter(school_year=self, assessment_period='2nd', status='Draft').update(assessment_date=self.eccd_2nd_start)
        if self.eccd_3rd_start:
            ECCDAssessment.objects.filter(school_year=self, assessment_period='3rd', status='Draft').update(assessment_date=self.eccd_3rd_start)

class Child(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    parents = models.ManyToManyField(UserProfile, related_name='children', blank=True)
    attendance_status = models.CharField(max_length=20, default='Present')
    date_added = models.DateTimeField(auto_now_add=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolled_children')
    enrollment_status = models.CharField(max_length=20, default='Pending')
    teacher_feedback = models.TextField(null=True, blank=True)
    
    # New fields to replace localStorage data
    dob = models.DateField(null=True, blank=True)
    doe = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    allergies = models.CharField(max_length=255, null=True, blank=True)
    health_conditions = models.CharField(max_length=255, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    mother_first_name = models.CharField(max_length=50, null=True, blank=True)
    mother_middle_initial = models.CharField(max_length=10, null=True, blank=True)
    mother_last_name = models.CharField(max_length=50, null=True, blank=True)
    mother_phone = models.CharField(max_length=50, null=True, blank=True)
    mother_email = models.EmailField(null=True, blank=True)
    mother_address = models.CharField(max_length=255, null=True, blank=True)
    
    father_first_name = models.CharField(max_length=50, null=True, blank=True)
    father_middle_initial = models.CharField(max_length=10, null=True, blank=True)
    father_last_name = models.CharField(max_length=50, null=True, blank=True)
    father_phone = models.CharField(max_length=50, null=True, blank=True)
    father_email = models.EmailField(null=True, blank=True)
    father_address = models.CharField(max_length=255, null=True, blank=True)
    
    other_guardian_first_name = models.CharField(max_length=50, null=True, blank=True)
    other_guardian_middle_initial = models.CharField(max_length=10, null=True, blank=True)
    other_guardian_last_name = models.CharField(max_length=50, null=True, blank=True)
    other_guardian_phone = models.CharField(max_length=50, null=True, blank=True)
    other_guardian_email = models.EmailField(null=True, blank=True)
    other_guardian_address = models.CharField(max_length=255, null=True, blank=True)
    
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    street = models.CharField(max_length=255, null=True, blank=True)
    barangay = models.CharField(max_length=100, null=True, blank=True)
    purok = models.CharField(max_length=100, null=True, blank=True)
    city_municipality = models.CharField(max_length=100, null=True, blank=True)
    
    img = models.ImageField(upload_to='child_profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='attendance_records')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='attendance_records', null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=20) # 'present', 'absent', 'late'
    absence_reason = models.CharField(max_length=255, blank=True, null=True)
    dropoff_time = models.CharField(max_length=50, blank=True, null=True)
    pickup_status = models.CharField(max_length=50, blank=True, null=True)
    authorized_guardian = models.CharField(max_length=100, blank=True, null=True)
    session = models.CharField(max_length=50, blank=True, null=True)

class MilestoneRecord(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='milestone_record')
    tasks = models.JSONField(default=dict)

class NutritionRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='nutrition_records')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='nutrition_records', null=True, blank=True)
    date = models.DateField()
    snack_status = models.CharField(
        max_length=50, 
        choices=[('Finished', 'Finished'), ('Some Left', 'Some Left'), ('Not Eaten', 'Not Eaten')], 
        null=True, blank=True
    )
    teacher_notes = models.TextField(blank=True, null=True)

class EngagementRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='engagement_records')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='engagement_records', null=True, blank=True)
    date = models.DateField()
    behavior = models.CharField(max_length=50, blank=True, null=True) # e.g. Positive, Needs Support
    notes = models.TextField(blank=True, null=True)

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        diff = now - self.created_at
        return diff <= datetime.timedelta(minutes=5)

class NoClassDay(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='no_class_days', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"No Class on {self.date}"

# ==========================================
# ECCD MILESTONE TRACKER MODELS
# ==========================================

class ECCDDomain(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fa-star') # FontAwesome class
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class ECCDMilestone(models.Model):
    domain = models.ForeignKey(ECCDDomain, on_delete=models.CASCADE, related_name='milestones')
    action_description = models.CharField(max_length=500)
    material_procedure = models.TextField(blank=True, null=True)
    age_bracket_min_months = models.IntegerField(default=0)
    age_bracket_max_months = models.IntegerField(default=72)
    order_number = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.domain.name}] {self.action_description}"

class ECCDAssessment(models.Model):
    PERIOD_CHOICES = [
        ('1st', '1st Assessment'),
        ('2nd', '2nd Assessment'),
        ('3rd', '3rd Assessment'),
    ]
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Finalized', 'Finalized'),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='eccd_assessments')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='eccd_assessments', null=True, blank=True)
    teacher = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    assessment_period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    import datetime
    assessment_date = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    
    # Recommendations & Summaries
    remarks = models.TextField(blank=True, null=True)
    strengths = models.TextField(blank=True, null=True)
    concerns = models.TextField(blank=True, null=True)
    follow_up_action = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ECCD - {self.child.first_name} ({self.assessment_period})"

    def save(self, *args, **kwargs):
        if not self.school_year:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                self.school_year = active_year
        super().save(*args, **kwargs)

class ECCDMilestoneScore(models.Model):
    SCORE_CHOICES = [
        (0, 'Not Yet Observed'),
        (1, 'Emerging'),
        (2, 'Consistently Demonstrated'),
    ]

    assessment = models.ForeignKey(ECCDAssessment, on_delete=models.CASCADE, related_name='scores')
    milestone = models.ForeignKey(ECCDMilestone, on_delete=models.CASCADE)
    
    teacher_score = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True)
    parent_score = models.IntegerField(choices=SCORE_CHOICES, null=True, blank=True)
    
    teacher_observation = models.TextField(blank=True, null=True)
    parent_observation = models.TextField(blank=True, null=True)
    
    date_checked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'milestone')

    def __str__(self):
        return f"Score: {self.milestone.action_description[:20]}..."

class ScoringAccessRequest(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='scoring_requests')
    parent = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='scoring_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request for {self.child.first_name} by {self.parent.user.username} - {self.status}"

class Activity(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

class StudentActivityCompletion(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='activity_completions')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='completions')
    completed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('child', 'activity')

    def __str__(self):
        return f"{self.child} - {self.activity.name} - {'Yes' if self.completed else 'No'}"

class BMIRecord(models.Model):
    QUARTER_CHOICES = [
        ('1st', '1st Quarter'),
        ('2nd', '2nd Quarter'),
        ('3rd', '3rd Quarter'),
    ]
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Finalized', 'Finalized'),
    ]
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='bmi_records')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='bmi_records', null=True, blank=True)
    quarter = models.CharField(max_length=10, choices=QUARTER_CHOICES)
    weight = models.FloatField()
    height = models.FloatField()
    import datetime
    measurement_date = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('child', 'school_year', 'quarter')

    def save(self, *args, **kwargs):
        if not self.school_year:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                self.school_year = active_year
        super().save(*args, **kwargs)
        
        # Update current weight/height on the Child model
        latest_record = BMIRecord.objects.filter(child=self.child, school_year=self.school_year).order_by('quarter').last()
        if latest_record:
            Child.objects.filter(pk=self.child.pk).update(weight=latest_record.weight, height=latest_record.height)

    def __str__(self):
        return f"{self.child.first_name} - {self.quarter} ({self.status})"

# ==========================================
# PUBLIC LANDING PAGE & ANNOUNCEMENT MODELS
# ==========================================

class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Enrollment', 'Enrollment'),
        ('Important Notice', 'Important Notice'),
        ('Schedule', 'Schedule'),
        ('Daycare Suspension', 'Daycare Suspension'),
        ('Parent Reminder', 'Parent Reminder'),
        ('Activities', 'Activities'),
        ('Events', 'Events'),
        ('Health & Safety', 'Health & Safety'),
        ('Program Highlights', 'Program Highlights'),
    ]
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Scheduled', 'Scheduled'),
        ('Expired', 'Expired'),
        ('Archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    image = models.ImageField(upload_to='announcements/', null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Published')
    is_featured = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.category}] {self.title} ({self.status})"

class EnrollmentInfo(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollment_info')
    program_name = models.CharField(max_length=150, default='Child Development Program')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    age_requirement = models.CharField(max_length=100, default='3 to 4.11 years old')
    available_slots = models.IntegerField(default=30)
    requirements_text = models.TextField(blank=True, null=True, default="• Photocopy of PSA Birth Certificate\n• 2x2 ID Photo of Child (2 copies)\n• Barangay Certificate of Residency\n• Parent/Guardian Government Issued ID\n• Child Health / Immunization Record")
    instructions_text = models.TextField(blank=True, null=True, default="Please visit the Barangay Market View 3 Child Development Center to submit requirements or contact center administration for enrollment details.")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Enrollment ({self.program_name})"

class ProgramHighlight(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='program_highlights/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PublicReminder(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, default='General Reminder')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CenterSettings(models.Model):
    center_name = models.CharField(max_length=150, default="Barangay Market View 3 Child Development Center")
    short_name = models.CharField(max_length=50, default="BMV3")
    system_title = models.CharField(max_length=150, default="Child Care Management System")
    tagline = models.CharField(max_length=255, default="Nurturing Early Childhood Development")
    logo = models.ImageField(upload_to='center_branding/', null=True, blank=True)
    center_latitude = models.DecimalField(max_digits=12, decimal_places=7, default=13.9380)
    center_longitude = models.DecimalField(max_digits=12, decimal_places=7, default=121.6146)

    address_text = models.TextField(default="Barangay Market View 3, Lucena City")
    contact_phone = models.CharField(max_length=50, blank=True, default="(042) 710-1234")
    contact_email = models.EmailField(blank=True, default="center@bmv3.edu.ph")
    semaphore_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Semaphore SMS Gateway API key")
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.center_name

    @classmethod
    def get_settings(cls):
        settings_obj, _ = cls.objects.get_or_create(id=1)
        return settings_obj


class TextblastLog(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=50, default='General Announcement')
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=True)
    target_group = models.CharField(max_length=100, default='All Active Parents')
    emails_sent_count = models.IntegerField(default=0)
    sms_sent_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"



import datetime
import random
from django.core.management.base import BaseCommand
from apps.core.models import SchoolYear, Child, Activity, StudentActivityCompletion

class Command(BaseCommand):
    help = "Seeds historical daily activities and student completions from July 1, 2026 to November 3, 2026."

    def handle(self, *args, **options):
        active_sy = SchoolYear.objects.filter(is_active=True).first()
        if not active_sy:
            active_sy, _ = SchoolYear.objects.get_or_create(
                name="2026-2027",
                defaults={"is_active": True, "start_date": "2026-07-01", "end_date": "2027-04-30"}
            )

        children = list(Child.objects.filter(school_year=active_sy, enrollment_status="Enrolled"))
        if not children:
            children = list(Child.objects.all()[:81])

        self.stdout.write(f"Seeding activities for {len(children)} students...")

        learning_templates = [
            ("Alphabet Tracing & Phonics", "Writing practice for letters and recognition of phonics sounds."),
            ("Number Counting & Sorting", "Hands-on counting from 1-20 using colorful counting bears."),
            ("Storytelling: Ang Alamat ng Pinya", "Interactive listening session focusing on respect and obedience."),
            ("Shapes & Primary Colors Matching", "Cognitive identification of circle, square, triangle, and rectangle."),
            ("Parts of the Body Identification", "Interactive song and naming head, shoulders, knees, and toes."),
            ("Community Helpers & Occupations", "Role playing as doctors, teachers, police, and firefighters."),
            ("Basic Rhymes & Poetry Recitation", "Language and auditory memory exercise with Tagalog nursery rhymes."),
            ("Days of the Week & Calendar Time", "Morning routine learning today, yesterday, and tomorrow."),
            ("Weather & Nature Exploration", "Observing the sky and classifying sunny, rainy, and cloudy days."),
            ("Size & Sequence Concept Sorting", "Big, medium, small object classification and sequencing."),
        ]

        snack_templates = [
            ("Morning Healthy Snack: Arroz Caldo", "Nutritious warm rice porridge with shredded chicken and hardboiled egg."),
            ("Morning Healthy Snack: Veggie Sopas", "Macaroni soup enriched with carrots, cabbage, and fortified milk."),
            ("Morning Healthy Snack: Champorado & Milk", "Traditional cocoa porridge paired with calcium-rich milk."),
            ("Morning Healthy Snack: Ginataang Bilo-bilo", "Coconut milk sweet soup with glutinous rice balls and sweet potato."),
            ("Morning Healthy Snack: Fresh Sliced Papaya & Milk", "Vitamin A & C rich fruit snack promoting digestive health."),
            ("Afternoon Snack: Banana Cue & Vitamin Drink", "Saba banana snack with fortified orange vitamin juice."),
            ("Afternoon Snack: Boiled Sweet Potato & Milk", "Complex carbohydrate snack providing energy for playtime."),
            ("Afternoon Snack: Lugaw with Malunggay", "Iron-rich rice porridge cooked with fresh garden malunggay."),
        ]

        motor_templates = [
            ("Gross Motor: Animal Dance & Action", "Gross motor coordination imitating hopping frog and flying birds."),
            ("Fine Motor: Playdough & Clay Sculpting", "Hand and finger muscle development by rolling and shaping dough."),
            ("Gross Motor: Balance Beam & Obstacle Fun", "Balance and spatial navigation along safe soft obstacles."),
            ("Fine Motor: Scissor Cutting & Collage", "Safe paper cutting along straight and wavy lines."),
            ("Gross Motor: Parachute & Group Ball Play", "Social cooperation and upper body movement with classroom parachute."),
            ("Art & Music: Finger Painting Primary Colors", "Sensory color mixing and expressive creative self-expression."),
        ]

        remarks_pool = [
            "Participated enthusiastically!",
            "Completed task independently with neat output.",
            "Shared materials nicely with classmates.",
            "Finished entire serving of snack with good appetite.",
            "Listened attentively during storytelling.",
            "Followed teacher directions carefully.",
            "Showed great improvement in pencil grip.",
            "Very energetic during movement songs.",
        ]

        start_date = datetime.date(2026, 7, 1)
        end_date = datetime.date(2026, 11, 3) # Today

        curr = start_date
        total_activities = 0
        total_completions = 0

        while curr <= end_date:
            # Mon = 0, Tue = 1, Wed = 2, Thu = 3 (Friday = 4, Sat = 5, Sun = 6)
            if curr.weekday() in [0, 1, 2, 3]:
                # Pick 1 learning, 1 snack, and optionally 1 motor
                day_seed = curr.timetuple().tm_yday
                learn_tpl = learning_templates[day_seed % len(learning_templates)]
                snack_tpl = snack_templates[(day_seed * 2) % len(snack_templates)]
                motor_tpl = motor_templates[(day_seed * 3) % len(motor_templates)]

                day_acts = [
                    (learn_tpl[0], learn_tpl[1]),
                    (snack_tpl[0], snack_tpl[1]),
                    (motor_tpl[0], motor_tpl[1]),
                ]

                for name, desc in day_acts:
                    act, created = Activity.objects.get_or_create(
                        name=name,
                        date=curr,
                        defaults={
                            "description": desc,
                            "school_year": active_sy
                        }
                    )
                    if created:
                        total_activities += 1

                    # Seed completions for all enrolled children
                    completions_to_create = []
                    for child in children:
                        # Check existing
                        if not StudentActivityCompletion.objects.filter(child=child, activity=act).exists():
                            # Default ~94% completion rate
                            is_at_risk = (
                                "Carlos Miguel" in f"{child.first_name} {child.last_name}" or
                                "Liam Nathan" in f"{child.first_name} {child.last_name}"
                            )
                            comp_chance = 0.70 if is_at_risk else 0.94
                            completed = (random.random() < comp_chance)
                            remark = random.choice(remarks_pool) if completed and random.random() < 0.4 else ""

                            completions_to_create.append(
                                StudentActivityCompletion(
                                    child=child,
                                    activity=act,
                                    completed=completed,
                                    remarks=remark
                                )
                            )

                    if completions_to_create:
                        StudentActivityCompletion.objects.bulk_create(completions_to_create)
                        total_completions += len(completions_to_create)

            curr += datetime.timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {total_activities} activities and {total_completions} student completions!"
        ))

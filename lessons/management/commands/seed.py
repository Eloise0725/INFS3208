import datetime
from random import randint

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.contrib.auth.models import Group
from faker import Faker

from lessons.models import (
    Bank,
    CustomUser as User,
    Request,
    Booking,
    Child,
    SchoolTerm,
)


class Command(BaseCommand):
    """
    Idempotent seeder:
    - Safe to run multiple times.
    - Uses get_or_create / update_or_create to avoid duplicates.
    - Bulk random users use faker.unique.email() to avoid collisions.
    """
    PASSWORD = "Password123"
    USER_COUNT = 100  # number of random students to create

    def __init__(self):
        super().__init__()
        # Australia locale to match your AU branding
        self.faker = Faker("en_AU")

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.NOTICE("Seeding fixed data..."))
            self._seed_fixed_users_and_groups()
            self._seed_school_terms()

        self.stdout.write(self.style.NOTICE(f"Seeding {Command.USER_COUNT} random students..."))
        created = self._seed_random_students(Command.USER_COUNT)
        self.stdout.write(self.style.SUCCESS(f"Random students created: {created}"))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    # ---------------------------
    # Fixed data (safe/idempotent)
    # ---------------------------
    def _seed_fixed_users_and_groups(self):
        # Groups
        director_group, _ = Group.objects.get_or_create(name="Director")
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        student_group, _ = Group.objects.get_or_create(name="Student")

        # Core accounts
        user, _ = User.objects.get_or_create(
            email="john.doe@example.org",
            defaults=dict(first_name="John", last_name="Doe"),
        )
        if not user.has_usable_password():
            user.set_password(Command.PASSWORD)
            user.save(update_fields=["password"])
        student_group.user_set.add(user)
        self._ensure_bank(user)

        # Sample requests/bookings/children for the student (guarded to avoid duplicates)
        self._ensure_request(
            user=user,
            day="FRI",
            number="6",
            interval="2 WEEKS",
            duration="60 Minutes",
        )

        # Two children + linked bookings
        alice, _ = Child.objects.get_or_create(student=user, first_name="Alice", last_name="Doe")
        bob, _ = Child.objects.get_or_create(student=user, first_name="Bob", last_name="Doe")

        self._ensure_booking(
            user=user,
            child=None,
            day="FRI",
            time=datetime.time(16, 0, 0),
            teacher="Smith Jane",
            start_date=datetime.date(2022, 12, 2),
            duration="60 Minutes",
            interval="2 WEEKS",
            number_of_lessons="6",
            full_price=150,
            payment_made=150,
        )
        self._ensure_booking(
            user=user,
            child=alice,
            day="FRI",
            time=datetime.time(16, 0, 0),
            teacher="Smith Jane",
            start_date=datetime.date(2022, 12, 2),
            duration="60 Minutes",
            interval="2 WEEKS",
            number_of_lessons="6",
            full_price=150,
            payment_made=150,
        )
        self._ensure_booking(
            user=user,
            child=bob,
            day="FRI",
            time=datetime.time(16, 0, 0),
            teacher="Smith Jane",
            start_date=datetime.date(2022, 12, 2),
            duration="60 Minutes",
            interval="2 WEEKS",
            number_of_lessons="6",
            full_price=150,
            payment_made=150,
        )

        # Admins/Director
        admin_user, _ = User.objects.get_or_create(
            email="petra.pickles@example.org",
            defaults=dict(first_name="Petra", last_name="Pickles"),
        )
        if not admin_user.has_usable_password():
            admin_user.set_password(Command.PASSWORD)
            admin_user.save(update_fields=["password"])
        admin_group.user_set.add(admin_user)
        self._ensure_bank(admin_user)

        admin_user2, _ = User.objects.get_or_create(
            email="jane.smith@example.org",
            defaults=dict(first_name="Jane", last_name="Smith"),
        )
        if not admin_user2.has_usable_password():
            admin_user2.set_password(Command.PASSWORD)
            admin_user2.save(update_fields=["password"])
        admin_group.user_set.add(admin_user2)
        self._ensure_bank(admin_user2)

        director_user, _ = User.objects.get_or_create(
            email="marty.major@example.org",
            defaults=dict(first_name="Marty", last_name="Major"),
        )
        if not director_user.has_usable_password():
            director_user.set_password(Command.PASSWORD)
            director_user.save(update_fields=["password"])
        director_group.user_set.add(director_user)
        self._ensure_bank(director_user)

    def _ensure_bank(self, user: User):
        # Only create a Bank account if none exists for this user
        if not Bank.objects.filter(user=user).exists():
            # create_bank() is assumed to initialize a bank record for the user
            Bank.objects.create_bank(user)

    def _ensure_request(self, user: User, day: str, number: str, interval: str, duration: str, child: Child | None = None):
        # Avoid duplicate sample request: use a minimal uniqueness guard
        if not Request.objects.filter(
            user=user,
            child=child,
            daysAvailable=day,
            durationOfLessons=duration,
            numberOfLessons=number,
            intervalBetweenLessons=interval,
        ).exists():
            Request.objects.create(
                user=user,
                child=child,
                daysAvailable=day,
                durationOfLessons=duration,
                numberOfLessons=number,
                intervalBetweenLessons=interval,
            )

    def _ensure_booking(
        self,
        user: User,
        day: str,
        time: datetime.time,
        teacher: str,
        start_date: datetime.date,
        duration: str,
        interval: str,
        number_of_lessons: str,
        full_price: int,
        payment_made: int,
        child: Child | None = None,
    ):
        # Use a conservative uniqueness guard to avoid duplicates
        if not Booking.objects.filter(
            user=user,
            child=child,
            day=day,
            time=time,
            start_date=start_date,
            teacher=teacher,
        ).exists():
            Booking.objects.create(
                user=user,
                child=child,
                day=day,
                time=time,
                teacher=teacher,
                start_date=start_date,
                duration=duration,
                interval=interval,
                number_of_lessons=number_of_lessons,
                full_price=full_price,
                payment_made=payment_made,
            )

    # ---------------------------
    # School terms (idempotent)
    # ---------------------------
    def _seed_school_terms(self):
        terms = [
            ("one",  datetime.date(2022, 9, 1),  datetime.date(2022, 10, 21)),
            ("two",  datetime.date(2022, 10, 31), datetime.date(2022, 12, 16)),
            ("three",datetime.date(2023, 1, 3),  datetime.date(2023, 2, 10)),
            ("four", datetime.date(2023, 2, 20), datetime.date(2023, 3, 31)),
            ("five", datetime.date(2023, 4, 17), datetime.date(2023, 5, 26)),
            ("six",  datetime.date(2023, 6, 5),  datetime.date(2023, 7, 21)),
        ]
        for term_number, start, end in terms:
            SchoolTerm.objects.update_or_create(
                term_number=term_number,
                defaults=dict(start_date=start, end_date=end),
            )

    # ---------------------------
    # Random students (unique)
    # ---------------------------
    def _seed_random_students(self, target: int) -> int:
        created = 0
        student_group, _ = Group.objects.get_or_create(name="Student")

        # Reset faker uniqueness per run
        self.faker.unique.clear()

        while created < target:
            try:
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                email = self.faker.unique.email()

                user, was_created = User.objects.get_or_create(
                    email=email,
                    defaults=dict(first_name=first_name, last_name=last_name),
                )
                if was_created:
                    user.set_password(Command.PASSWORD)
                    user.save(update_fields=["password"])
                    student_group.user_set.add(user)
                    self._ensure_bank(user)

                    # Random related objects for this NEW user only
                    if randint(0, 100) <= 20:
                        self._ensure_request(
                            user=user,
                            day="FRI",
                            number="6",
                            interval="2 WEEKS",
                            duration="60 Minutes",
                        )

                    if randint(0, 100) <= 20:
                        Booking.objects.create(
                            day="FRI",
                            time=datetime.time(16, 0, 0),
                            teacher="Smith Jane",
                            start_date=datetime.date(2022, 12, 2),
                            duration="60 Minutes",
                            interval="2 WEEKS",
                            number_of_lessons="6",
                            full_price=150,
                            payment_made=self._payment_made_value(),
                            user=user,
                        )

                    if randint(0, 100) >= 30:
                        child = Child.objects.create(
                            student=user,
                            first_name=self.faker.first_name(),
                            last_name=self.faker.last_name(),
                        )

                        if randint(0, 100) >= 30:
                            Booking.objects.create(
                                day="FRI",
                                time=datetime.time(16, 0, 0),
                                teacher="Smith Jane",
                                start_date=datetime.date(2022, 12, 2),
                                duration="60 Minutes",
                                interval="2 WEEKS",
                                number_of_lessons="6",
                                full_price=150,
                                payment_made=self._payment_made_value(),
                                user=user,
                                child=child,
                            )

                        if randint(0, 100) <= 30:
                            self._ensure_request(
                                user=user,
                                child=child,
                                day="FRI",
                                number="6",
                                interval="2 WEEKS",
                                duration="60 Minutes",
                            )

                    created += 1

            except IntegrityError:
                # In the unlikely event of a unique collision, just try again
                continue

        return created

    # ---------------------------
    # Helpers
    # ---------------------------
    def _payment_made_value(self) -> int:
        r = randint(0, 40)
        if r <= 10:
            return 0
        elif r <= 20:
            return randint(1, 150)
        elif r <= 30:
            return 150
        else:
            return randint(151, 200)

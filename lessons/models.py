from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, first_name, last_name, password=None, **extra_fields):
        # (password= none) allows you to not define a password when creating a user.
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        # the domain part is case-insensitive , Normalizing will make two equivalent email strings normalize to the same thing.
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()


DAY_OF_THE_WEEK = [
    ('MON', "Monday"),
    ('TUE', "Tuesday"),
    ('WED', "Wednesday"),
    ('THU', "Thursday"),
    ('FRI', "Friday"),
    ('SAT', "Saturday"),
    ('SUN', "Sunday"),
]

DURATION = [
    ('30 Minutes', '30 minutes'),
    ('45 Minutes', '45 minutes'),
    ('60 Minutes', '60 minutes')
]

INTERVAL = [
    ('1 WEEK', '1 Week'),
    ('2 WEEKS', '2 Weeks')
]

NUMBER_OF_LESSONS = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7')
]


class Child(models.Model):
    student = models.ForeignKey(CustomUser, related_name="children", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Request(models.Model):
    daysAvailable = models.CharField(max_length=7, choices=DAY_OF_THE_WEEK, blank=False)
    numberOfLessons = models.CharField(max_length=7, choices=NUMBER_OF_LESSONS, blank=False)
    intervalBetweenLessons = models.CharField(max_length=7, choices=INTERVAL, blank=False)
    durationOfLessons = models.CharField(max_length=15, choices=DURATION, blank=False)
    furtherInformation = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, related_name="requests", on_delete=models.CASCADE, null=True, blank=True)

class Booking(models.Model):
    day = models.CharField(max_length=7, choices=DAY_OF_THE_WEEK, blank=False)
    time = models.TimeField(blank=False)
    teacher = models.CharField(blank=False, max_length=30)
    start_date = models.DateField(blank=False)
    duration = models.CharField(max_length=15, choices=DURATION, blank=False)
    interval = models.CharField(max_length=7, choices=INTERVAL, blank=False)
    number_of_lessons = models.CharField(max_length=7, choices=NUMBER_OF_LESSONS, blank=False)
    price_per_lesson = models.IntegerField(blank=False, default=50)
    full_price = models.IntegerField(blank=True, default=0)
    payment_made = models.IntegerField(blank=True, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True)


class Transaction(models.Model):
    invoice_id = models.IntegerField(blank=False)
    transfer_date = models.DateField(blank=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class BankManager(models.Manager):
    def create_bank(self, user):
        bank = self.create(user=user)
        return bank


class Bank(models.Model):
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    objects = BankManager()


TERMS = [
    ('one', '1'),
    ('two', '2'),
    ('three', '3'),
    ('four', '4'),
    ('five', '5'),
    ('six', '6')
]


class SchoolTerm(models.Model):
    term_number = models.CharField(blank=False, max_length=6, choices=TERMS)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    class Meta:
        ordering = ['start_date']

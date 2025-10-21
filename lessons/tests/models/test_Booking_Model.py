from django.test import TestCase 
from lessons.models import Booking
from django.core.exceptions import ValidationError
from lessons.models import Child, CustomUser as User


class BookingModelTest(TestCase):
    def setUp(self): 
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )

        self.child = Child.objects.create(
            student=self.user,
            first_name='Alice',
            last_name='Doe'
        ) 
        
        self.booking_user = Booking.objects.create(
            day = 'MON',
            time = '09:00',
            teacher = 'Mr Green',
            start_date = '2022-12-01',
            number_of_lessons = '2',
            interval =  '1 WEEK',
            duration = '30 Minutes',
            price_per_lesson = '50',
            full_price = '10',
            user = self.user,
            child = self.child)
    
    def test_valid_booking(self):
        try:
            self.booking_user.full_clean()
        except ValidationError:
            self.fail("Request should be valid")
            
    def test_days_must_not_be_blank(self):
        self.booking_user.day = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
    
    def test_time_must_not_be_blank(self):
        self.booking_user.time = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
            
    def test_teacher_must_not_be_blank(self):
        self.booking_user.teacher = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
            
    def test_teacher_must_not_contain_more_than_30_characters(self):
        self.booking_user.teacher = 'x' * 31
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
            
    def test_start_date_must_not_be_blank(self):
        self.booking_user.start_date = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()

    def test_number_of_lessons_must_not_be_blank(self):
        self.booking_user.number_of_lessons = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()

    def test_interval_must_not_be_blank(self):
        self.booking_user.interval = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
    
    def test_duration_must_not_be_blank(self):
        self.booking_user.duration = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
    
    def test_price_per_lesson_must_not_be_blank(self):
        self.booking_user.price_per_lesson = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
        
    def test_full_price_can_be_blank(self):
        self.booking_user.full_price = None
        try:
            self.booking_user.full_clean()
        except ValidationError:
            self.fail("Booking should be valid")\
                
    def test_payment_made_should_default_to_zero(self):
        self.assertTrue(Booking.payment_made, 0)
                    
    def test_user_must_not_be_blank(self):
        self.booking_user.user = None
        with self.assertRaises(ValidationError):
            self.booking_user.full_clean()
            
    def test_user_should_be_the_correct_user(self):
        givenUser = self.booking_user.user
        self.assertEqual(self.user, givenUser, 'User should be John')

    def test_child_should_be_correct(self):
        givenChild = self.booking_user.child
        self.assertEqual(self.child, givenChild)
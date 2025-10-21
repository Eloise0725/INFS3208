from django.test import TestCase
from lessons.models import Request as RequestTestCase
from django.core.exceptions import ValidationError
from lessons.models import CustomUser as User

class RequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )
        self.request_user = RequestTestCase.objects.create(
            daysAvailable='MON',
            numberOfLessons='2',
            intervalBetweenLessons='1 WEEK',
            durationOfLessons='30 Minutes',
            furtherInformation='Piano, Mr Green',
            user=self.user, )

    def test_valid_request(self):
        try:
            self.request_user.full_clean()
        except ValidationError:
            self.fail("Request should be valid")

    def test_daysAvailable_must_not_be_blank(self):
        self.request_user.daysAvailable = None
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_numberOfLessons_must_not_be_blank(self):
        self.request_user.numberOfLessons = None
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_intervalBetweenLessons_must_not_be_blank(self):
        self.request_user.intervalBetweenLessons = None
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_durationOfLesson_must_not_be_blank(self):
        self.request_user.durationOfLessons = None
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_furtherInformation_can_be_blank(self):
        try:
            self.request_user.full_clean()
        except ValidationError:
            self.fail("Request should be valid")

    def test_furtherInformation_must_not_contain_more_than_100_characters(self):
        self.request_user.furtherInformation = 'x' * 101
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_user_must_not_be_blank(self):
        self.request_user.user = None
        with self.assertRaises(ValidationError):
            self.request_user.full_clean()

    def test_user_should_be_the_correct_user(self):
        givenUser = self.request_user.user
        self.assertEqual(self.user, givenUser, 'User should be John')

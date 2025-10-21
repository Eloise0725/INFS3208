from django.test import TestCase
from django import forms
from lessons.forms import RequestForm
from lessons.models import CustomUser as User

class RequestFormTestCase(TestCase):
    fixtures = ['lessons/tests/fixtures/default_user.json']
    def setUp(self):
        self.user=User.objects.get(pk=1)
        self.form_input = {'daysAvailable': 'MON',
                           'numberOfLessons': '2',
                           'intervalBetweenLessons': '1 WEEK',
                           'durationOfLessons': '30 Minutes',
                           'furtherInformation': 'maths'
                           }

    def test_valid_request_form(self):
        form = RequestForm(data=self.form_input, user=self.user)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RequestForm(user=self.user)
        self.assertIn('daysAvailable', form.fields)
        self.assertIn('numberOfLessons', form.fields)
        self.assertIn('intervalBetweenLessons', form.fields)
        self.assertIn('durationOfLessons', form.fields)
        self.assertIn('furtherInformation', form.fields)

    def test_form_uses_model_validation(self):
        self.form_input['furtherInformation'] = 'x' * 101
        form = RequestForm(user=self.user)
        self.assertFalse(form.is_valid())
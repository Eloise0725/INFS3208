from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
from lessons.models import CustomUser as user
from lessons.tests.helpers import LogInTester
from django.contrib import messages


class LogInViewTestCase(LogInTester, TestCase):
    """Tests of the log in view."""
    fixtures = ['lessons/tests/fixtures/default_user.json']
    def setUp(self):
        self.url = reverse('log_in')
        self.user = user.objects.get(pk=1)
    
    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')
        
    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccesful_log_in(self):
        form_input = { 'email': 'johndoe123@gmail.com', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_username(self):
        form_input = { 'email': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        
    def test_log_in_with_blank_password(self):
        form_input = { 'email': 'johndoe@example.org', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
    
    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = { 'email': 'johndoe@example.org', 'password': 'pbkdf2_sha256$260000$4BNvFuAWoTT1XVU8D6hCay$KqDCG+bHl8TwYcvA60SGhOMluAheVOnF1PMz0wClilc=' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

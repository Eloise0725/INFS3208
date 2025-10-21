"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import CustomUser,Request
from lessons.tests.helpers import LogInTester


class LogOutViewTestCase(LogInTester, TestCase):
    """Tests of the log out view."""

    def setUp(self):
        self.url = reverse('log_out')
        self.user = CustomUser.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )

    def test_user_is_created(self):
        user = CustomUser.objects.get(email='johndoe@example.org')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'johndoe@example.org')

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_get_log_out(self):
       self.client.login(email='johndoe@example.org', password='Password123')
       self.assertTrue(self._is_logged_in())
       response = self.client.get(self.url, follow=True)
       response_url = reverse('home')
       self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
       self.assertTemplateUsed(response, 'home.html')
       self.assertFalse(self._is_logged_in())

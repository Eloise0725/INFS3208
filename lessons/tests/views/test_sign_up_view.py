"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import SignUpForm
from lessons.models import CustomUser as User


from lessons.models import CustomUser

class SignUpViewTestCase(TestCase):
    """Tests of the sign up view."""

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.org',
            'password1': 'Password123',
            'password2': 'Password123',
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_sign_up(self):
        self.form_input['email'] = 'BAD_email'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('student')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student.html')
        user = CustomUser.objects.get(email='johndoe@example.org')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'johndoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

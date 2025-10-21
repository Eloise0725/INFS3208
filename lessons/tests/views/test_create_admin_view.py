from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import SignUpForm
from lessons.models import CustomUser, Bank
from django.contrib.auth.models import Group


class CreateAdminViewTestCase(TestCase):
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('create_admin')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.com',
            'password1': 'Password123',
            'password2': 'Password123',
        }
        self.user = CustomUser.objects.get(email="johndoe@example.org")
        director, created = Group.objects.get_or_create(name='Director')
        director.user_set.add(self.user)
        self.other_user = CustomUser.objects.get(email='petrapickles@example.org')
        student, created = Group.objects.get_or_create(name='Student')
        student.user_set.add(self.other_user)
        bank = Bank.objects.create_bank(self.other_user)

    def test_create_admin_url(self):
        self.assertEqual(self.url, '/create_admin/')

    def test_get_create_admin_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_admin.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))

    def test_get_create_admin_with_invalid_id(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('student')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_admin_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_admin_creation(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'BAD_EMAIL'
        before_count = CustomUser.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = CustomUser.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_admin.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_succesful_admin_creation(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = CustomUser.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = CustomUser.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('create_admin')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_admin.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        new_user = CustomUser.objects.get(email = 'janedoe@example.org')
        self.assertEqual(new_user.first_name, 'Jane')
        self.assertEqual(new_user.last_name, 'Doe')
        self.assertEqual(new_user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', new_user.password)
        self.assertTrue(is_password_correct)

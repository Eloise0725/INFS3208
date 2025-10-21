from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import EditAdminForm
from lessons.models import CustomUser
from django.contrib.auth.models import Group


class EditUserTest(TestCase):
    """Test suite for the edit user view."""

    fixtures = [
        'lessons/tests/fixtures/default_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = CustomUser.objects.get(email='johndoe@example.org')
        director, created = Group.objects.get_or_create(name='Director')
        director.user_set.add(self.user)

        self.other_user = CustomUser.objects.get(email='janedoe@example.org')
        admin, created = Group.objects.get_or_create(name='Admin')
        admin.user_set.add(self.user)

        self.url = reverse('edit_user', kwargs={'user_id': self.other_user.id})
        self.form_input = {
            'first_name': self.other_user.first_name,
            'last_name': self.other_user.last_name,
            'email': self.other_user.email,
        }

    def test_edit_user_url(self):
        self.assertEqual(self.url, f'/edit/{self.other_user.id}')

    def test_get_edit_user_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAdminForm))

    def test_get_edit_user_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_change(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'janedow@example.org'
        self.form_input['last_name'] = 'dow'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAdminForm))
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.email, 'janedow@example.org')
        self.assertEqual(self.other_user.last_name, 'dow')

    def test_change_unsuccesful_email_already_taken(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'johndoe@example.org'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAdminForm))
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.email, 'janedoe@example.org')

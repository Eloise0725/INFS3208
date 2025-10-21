from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import SchoolTermForm
from lessons.models import CustomUser, SchoolTerm, Bank
from django.contrib.auth.models import Group
import datetime


class EditSchoolTermTest(TestCase):
    fixtures = [
        'lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json',
        'lessons/tests/fixtures/school_terms.json', 'lessons/tests/fixtures/other_school_terms.json']

    def setUp(self):
        self.user = CustomUser.objects.get(email='johndoe@example.org')
        admin, created = Group.objects.get_or_create(name='Admin')
        admin.user_set.add(self.user)

        self.other_user = CustomUser.objects.get(email='janedoe@example.org')
        student, created = Group.objects.get_or_create(name='Student')
        student.user_set.add(self.other_user)
        bank = Bank.objects.create_bank(self.other_user)
        self.first_term = SchoolTerm.objects.get(id='1')

        self.url = reverse('edit_term', kwargs={'term_id': 1})
        self.form_input = {
            "term_number": "one",
            "start_date": datetime.date(2022, 9, 1),
            "end_date": datetime.date(2022, 10, 21)
        }

    def test_edit_term_url(self):
        self.assertEqual(self.url, f'/edit_term/1')

    def test_get_edit_term_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_term.html')

    def test_get_edit_term_with_invalid_id(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('student')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_edit_term_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_change(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['term_number'] = 'two'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('school_term')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.first_term.refresh_from_db()
        self.assertEqual(self.first_term.term_number, 'two')
        self.assertEqual(self.first_term.start_date, datetime.date(2022, 9, 1))
        self.assertEqual(self.first_term.end_date, datetime.date(2022, 10, 21))
        self.assertEqual(self.first_term.id, 1)

    def test_change_unsuccesful_repeat_term(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['term_number'] = 'six'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.first_term.refresh_from_db()
        self.assertEqual(self.first_term.term_number, 'one')
        self.assertEqual(self.first_term.start_date, datetime.date(2022, 9, 1))
        self.assertEqual(self.first_term.end_date, datetime.date(2022, 10, 21))
        self.assertEqual(self.first_term.id, 1)

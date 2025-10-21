from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm, CustomUser, Bank
from django.contrib.auth.models import Group
from lessons.forms import SchoolTermForm
import datetime


class SchoolTermTest(TestCase):
    fixtures = ['lessons/tests/fixtures/school_terms.json', 'lessons/tests/fixtures/other_school_terms.json', 'lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('school_term')
        self.user = CustomUser.objects.get(email='johndoe@example.org')
        admin, created = Group.objects.get_or_create(name='Admin')
        admin.user_set.add(self.user)
        self.other_user = CustomUser.objects.get(email="janedoe@example.org")
        student, created = Group.objects.get_or_create(name='Student')
        student.user_set.add(self.other_user)
        bank = Bank.objects.create_bank(self.other_user)
        self.remove = {'delete': '1'}
        self.form_input = {
            'term_number': 'two',
            'start_date': datetime.date(2022, 10, 31),
            'end_date': datetime.date(2022, 12, 16)
        }

    def test_school_term_url(self):
        self.assertEqual(self.url, '/school_term/')

    def test_get_school_term_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'school_term.html')

    def test_get_school_term_with_invalid_id(self):
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('student')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_school_term_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_school_term_shows_all_terms(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'school_term.html')
        self.assertEqual(len(response.context['term_dates']), 2)
        for term_id in range(1,2):
            term_url = reverse('edit_term', kwargs={'term_id': term_id})
            self.assertContains(response, term_url)

        self.assertContains(response, 'Term one')
        self.assertContains(response, 'Term six')
        self.assertContains(response, 'Sept. 1, 2022')
        self.assertContains(response, 'Oct. 21, 2022')
        self.assertContains(response, 'June 5, 2023')
        self.assertContains(response, 'July 21, 2023')

    def test_delete_terms(self):
        self.client.login(email = self.user.email, password='Password123')
        terms_before = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.remove, follow = True)
        terms_after = SchoolTerm.objects.count()
        response_url = reverse('school_term')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'school_term.html')
        self.assertEqual(terms_before, terms_after+1)
    
    def test_unsuccesful_term_creation(self):
        self.client.login(email = self.user.email, password='Password123')
        self.form_input['term_number'] = 'one'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.assertTrue(form.is_bound)

    def test_succesful_term_creation(self):
        self.client.login(email = self.user.email, password='Password123')
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True,)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('school_term')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'school_term.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SchoolTermForm))
        self.assertFalse(form.is_bound)
        new_term = SchoolTerm.objects.get(id = '3')
        self.assertEqual(new_term.start_date, datetime.date(2022,10,31))
        self.assertEqual(new_term.end_date,datetime.date(2022,12,16))
        self.assertEqual(new_term.term_number, 'two')

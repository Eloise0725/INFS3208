from django import forms
from django.test import TestCase
from lessons.forms import SchoolTermForm
from lessons.models import SchoolTerm
import datetime


class SchoolTermFormTestCase(TestCase):
    fixtures = ['lessons/tests/fixtures/school_terms.json', 'lessons/tests/fixtures/other_school_terms.json']

    def setUp(self):
        self.form_input = {
            'term_number': 'two',
            'start_date': datetime.date(2022, 10, 31),
            'end_date': datetime.date(2022, 12, 16)
        }

    def test_valid_school_term_form(self):
        form = SchoolTermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SchoolTermForm()
        self.assertIn('term_number', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        start_field = form.fields['start_date'].widget
        self.assertTrue(isinstance(start_field, forms.DateInput))
        end_field = form.fields['end_date'].widget
        self.assertTrue(isinstance(end_field, forms.DateInput))

    def test_form_uses_model_validation(self):
        self.form_input['term_number'] = 'badterm'
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_end_date_must_be_greater_than_start_date(self):
        self.form_input['start_date'] = datetime.date(2022, 12, 17)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_and_end_date_cannot_be_the_same(self):
        self.form_input['start_date'] = datetime.date(2022, 12, 16)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_term_dates_cannot_overlap(self):
        self.form_input['start_date'] = datetime.date(2022, 10, 10)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.form_input['end_date'] = datetime.date(2022, 10, 20)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_no_school_term_in_august(self):
        self.form_input['start_date'] = datetime.date(2022, 7, 1)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.form_input['start_date'] = datetime.date(2022, 8, 1)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_six_different_terms_in_a_school_year(self):
        self.form_input['term_number'] = 'one'
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.form_input['start_date'] = datetime.date(2023, 1, 3)
        self.form_input['end_date'] = datetime.date(2023, 2, 10)
        form = SchoolTermForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.form_input['start_date'] = datetime.date(2023, 9, 1)
        self.form_input['end_date'] = datetime.date(2023, 10, 21)
        form = SchoolTermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form = SchoolTermForm(data=self.form_input)
        before_count = SchoolTerm.objects.count()
        form.save()
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count + 1)
        term = SchoolTerm.objects.get(id='3')
        self.assertEqual(term.start_date, datetime.date(2022, 10, 31))
        self.assertEqual(term.end_date, datetime.date(2022, 12, 16))
        self.assertEqual(term.term_number, 'two')

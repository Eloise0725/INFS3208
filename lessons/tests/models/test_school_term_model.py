from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import SchoolTerm


class SchoolTermTest(TestCase):
    fixtures = ['lessons/tests/fixtures/school_terms.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.term = SchoolTerm.objects.get(id=1)

    def test_valid_term(self):
        try:
            self.term.full_clean()
        except ValidationError:
            self.fail("Term should be valid")

    def test_term_number_must_not_be_blank(self):
        self.term.term_number = None
        with self.assertRaises(ValidationError):
            self.term.full_clean()

    def test_start_date_must_not_be_blank(self):
        self.term.start_date = None
        with self.assertRaises(ValidationError):
            self.term.full_clean()

    def test_end_date_must_not_be_blank(self):
        self.term.end_date = None
        with self.assertRaises(ValidationError):
            self.term.full_clean()

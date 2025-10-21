from django.test import TestCase 
from lessons.models import Child
from django.core.exceptions import ValidationError
from lessons.models import CustomUser as User


class BankModelTest(TestCase):
    def setUp(self): 
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123'
        )
        
        self.child = Child.objects.create(
            student = self.user,
            first_name = 'John',
            last_name = 'Doe',           
        )
        
    def test_valid_child(self):
        try:
            self.child.full_clean()
        except ValidationError:
            self.fail("Child should be valid")
    
    def test_first_name_must_not_be_blank(self):
        self.child.first_name = None
        with self.assertRaises(ValidationError):
            self.child.full_clean()
            
    def test_first_name_should_not_be_more_than_50_characters(self):
        self.child.first_name = 'x' * 51
        with self.assertRaises(ValidationError):
            self.child.full_clean()
            
    def test_last_name_must_not_be_blank(self):
        self.child.last_name = None
        with self.assertRaises(ValidationError):
            self.child.full_clean()
    
    def test_last_name_should_not_be_more_than_50_characters(self):
        self.child.last_name = 'x' * 51
        with self.assertRaises(ValidationError):
            self.child.full_clean()
            
    def test_user_must_not_be_blank(self):
        self.child.student = None
        with self.assertRaises(ValidationError):
            self.child.full_clean()
    
    def test_user_should_be_the_correct_user(self):
        givenUser = self.child.student
        self.assertEqual(self.user, givenUser, 'User should be John')
from django.test import TestCase 
from lessons.models import Bank
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
        
        self.bank = Bank.objects.create(
            balance = '5.00',
            user = self.user
        )
        
    def test_valid_bank(self):
        try:
            self.bank.full_clean()
        except ValidationError:
            self.fail("Bank should be valid")
    
    def test_balance_must_not_have_more_than_6_digit(self):
        self.bank.balance = '1' * 7
        with self.assertRaises(ValidationError):
            self.bank.full_clean()
        
    def test_balance_can_be_zero(self):
        try:
            self.bank.full_clean()
        except ValidationError:
            self.fail("Bank should be valid")
            
    def test_user_must_not_be_blank(self):
        self.bank.user = None
        with self.assertRaises(ValidationError):
            self.bank.full_clean()
            
    def test_user_should_be_the_correct_user(self):
        givenUser = self.bank.user
        self.assertEqual(self.user, givenUser, 'User should be John')
    
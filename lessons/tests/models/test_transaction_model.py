from django.test import TestCase 
from lessons.models import Transaction
from django.core.exceptions import ValidationError
from lessons.models import CustomUser as User

class TransactionsModelTest(TestCase):
    def setUp(self): 
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )
        
        self.transactions = Transaction.objects.create(
            invoice_id = '0001',
            transfer_date = '2022-12-02',
            amount = '5.00',
            user = self.user            
        )
        
    def test_valid_booking(self):
        try:
            self.transactions.full_clean()
        except ValidationError:
            self.fail("Booking should be valid")
    
    def test_invoice_id_must_not_be_blank(self):
        self.transactions.invoice_id = None
        with self.assertRaises(ValidationError):
            self.transactions.full_clean()
            
    def test_transfer_date_must_not_be_blank(self):
        self.transactions.transfer_date = None
        with self.assertRaises(ValidationError):
            self.transactions.full_clean()
            
    def test_invoice_id_must_not_be_blank(self):
        self.transactions.invoice_id = None
        with self.assertRaises(ValidationError):
            self.transactions.full_clean()
    
    def test_amount_must_not_have_more_than_6_digits(self):
        self.transactions.amount = '1' * 7
        with self.assertRaises(ValidationError):
            self.transactions.full_clean()
            
    def test_amount_can_be_zero(self):
        try:
            self.transactions.full_clean()
        except ValidationError:
            self.fail("Booking should be valid")
    
    def test_user_must_not_be_blank(self):
        self.transactions.user = None
        with self.assertRaises(ValidationError):
            self.transactions.full_clean()
            
    def test_user_should_be_the_correct_user(self):
        givenUser = self.transactions.user
        self.assertEqual(self.user, givenUser, 'User should be John')
    
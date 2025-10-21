from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Q
from lessons.models import CustomUser, Request, Bank, Child, Booking, SchoolTerm, Transaction

class LogInForm(forms.Form):
    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):
    """    A Custom form for creating new users.    """

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        new_password = forms.CharField(
            label='Password',
            widget=forms.PasswordInput(),
        )


class RequestForm(forms.ModelForm):
    child = forms.ModelChoiceField(queryset=None, empty_label="-------")

    class Meta:
        model = Request
        fields = (
            'daysAvailable', 'numberOfLessons', 'intervalBetweenLessons', 'durationOfLessons', 'furtherInformation')
        labels = {
            'daysAvailable': 'Days Available',
            'numberOfLessons': 'Number Of Lessons',
            'intervalBetweenLessons': 'Interval Between Lessons',
            'durationOfLessons': 'Duration Of Each Lesson',
            'furtherInformation': 'Further Information',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['child'].queryset = user.children.all()
        self.fields['child'].required = False

    def save(self, user=None):
        if user is None:
            return super().save()
        super().save(commit=False)
        request = Request.objects.create(
            daysAvailable=self.cleaned_data.get('daysAvailable'),
            numberOfLessons=self.cleaned_data.get('numberOfLessons'),
            intervalBetweenLessons=self.cleaned_data.get('intervalBetweenLessons'),
            durationOfLessons=self.cleaned_data.get('durationOfLessons'),
            furtherInformation=self.cleaned_data.get('furtherInformation'),
            user=user,
            child=self.cleaned_data.get('child')
        )
        return request


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['day', 'time', 'teacher', 'start_date', 'duration', 'interval', 'number_of_lessons',
                  'price_per_lesson']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def save(self, user=None):
        if user is None:
            return super().save()
        super().save(commit=False)
        total_price = int(self.cleaned_data.get('number_of_lessons')) * int(self.cleaned_data.get('price_per_lesson'))
        new_booking = Booking.objects.create(day=self.cleaned_data.get('day'),
                                            time=self.cleaned_data.get('time'),
                                            teacher=self.cleaned_data.get('teacher'),
                                            start_date=self.cleaned_data.get('start_date'),
                                            duration=self.cleaned_data.get('duration'),
                                            interval=self.cleaned_data.get('interval'),
                                            number_of_lessons=self.cleaned_data.get('number_of_lessons'),
                                            price_per_lesson=self.cleaned_data.get('price_per_lesson'),
                                            full_price = total_price,
                                            user=user
                                        )
        return new_booking


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['invoice_id', 'transfer_date', 'amount']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def save(self, user=None):
        if user is None:
            return super().save()
        super().save(commit=False)
        new_invoice = Transaction.objects.create(invoice_id=self.cleaned_data.get('invoice_id'),
                                                transfer_date=self.cleaned_data.get('transfer_date'),
                                                amount=self.cleaned_data.get('amount'),
                                                user=user
                                            )
        return new_invoice


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['balance']
        labels = {'balance': 'Amount'}


class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name']

    def save(self, student):
        super().save(commit=False)
        Child.objects.create(
            student=student,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),

        )


class EditAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']


class SchoolTermForm(forms.ModelForm):
    class Meta:
        model = SchoolTerm
        fields = ['term_number', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        term_number = cleaned_data.get('term_number')
        term_id = cleaned_data.get('id')

        exclude_value = SchoolTerm.objects.filter(~Q(id=term_id))

        if end_date <= start_date:
            self.add_error('end_date', 'End date should be greater than the start date.')

        checker = False
        for existing_terms in exclude_value:
            if (existing_terms.end_date >= start_date and existing_terms.start_date <= end_date):
                checker = True
        if checker:
            self.add_error('start_date', 'Term dates cannot overlap.')

        if (start_date.month <= 8 and end_date.month >= 8):
            self.add_error('start_date',
                           'There should not be a school term in August. The academic school year starts in September and ends in July.')
        else:
            another_checker = False
            for existing_terms in exclude_value:
                if existing_terms.start_date.month >= 9 and existing_terms.start_date.month <= 12:
                    if start_date.month >= 9 and start_date.month <= 12:
                        if existing_terms.term_number == term_number and existing_terms.start_date.year == start_date.year:
                            another_checker = True
                    else:
                        if existing_terms.term_number == term_number and existing_terms.start_date.year + 1 == start_date.year:
                            another_checker = True
                else:
                    if not (start_date.month >= 9 and start_date.month <= 12):
                        if existing_terms.term_number == term_number and existing_terms.start_date.year == start_date.year:
                            another_checker = True
                    else:
                        if existing_terms.term_number == term_number and existing_terms.start_date.year - 1 == start_date.year:
                            another_checker = True
            if another_checker:
                self.add_error('term_number', f'Term {term_number} already exists for this academic year.')

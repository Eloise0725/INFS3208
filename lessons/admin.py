from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Request, Bank, Child, Booking, Transaction, SchoolTerm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('daysAvailable',
                    'numberOfLessons',
                    'intervalBetweenLessons',
                    'durationOfLessons',
                    'furtherInformation',
                    'user')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('day', 'time', 'teacher', 'start_date', 'duration',
                    'interval', 'number_of_lessons', 'price_per_lesson')


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('balance',
                    'user')


@admin.register(Child)
class ChildAdmmin(admin.ModelAdmin):
    list_display = ('student',
                    'first_name',
                    'last_name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('invoice_id',
    'transfer_date',
    'amount',
    'user')

@admin.register(SchoolTerm)
class SchoolTermAdmin(admin.ModelAdmin):
    list_display = ('term_number',
    'start_date',
    'end_date')
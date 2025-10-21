"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('student/', views.student, name='student'),
    path('add_children/', views.add_children, name='add_children'),
    path('request/', views.make_request, name='request'),
    path('transactions/', views.transactions, name='transactions'),
    path('balance/', views.update_balance, name='balance'),
    path('create_admin/', views.create_admin, name='create_admin'),
    path('administrator/', views.administrators, name='administrators'),
    path('all_transactions/', views.all_transactions, name='all_transactions'),
    path('director/', views.admin_list, name="admin_list"),
    path('edit/<int:user_id>', views.edit_user, name='edit_user'),
    path('school_term/', views.school_term, name='school_term'),
    path('edit_term/<int:term_id>', views.edit_term, name="edit_term"),
    path('booking/<int:request_id>', views.booking, name='booking'),
    path('edit_booking/<int:booking_id>', views.edit_booking, name='edit_booking'),
    path('edit_request/<int:request_id>', views.edit_request, name='edit_request'),
]

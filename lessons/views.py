from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from lessons.forms import LogInForm, SignUpForm, RequestForm, ChildrenForm, BalanceForm, EditAdminForm, BookingForm, SchoolTermForm, TransactionForm
from django.contrib.auth.models import Group
from lessons.models import CustomUser, Bank, Request, Booking, SchoolTerm, Transaction
from .helpers import group_required, login_prohibited, login_required

@login_prohibited
def log_in(request):
    if request.method == 'POST': #checks if user submits form
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                if user.groups.filter(name='Director').exists(): #logs the user into different pages based on their group
                    return redirect('admin_list')
                elif user.groups.filter(name='Admin').exists():
                    return redirect('administrators')
                else:
                    return redirect('student')
            # Add error message
            messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            bank = Bank.objects.create_bank(user) #create a balance for each user
            bank.save()
            student, created = Group.objects.get_or_create(name='Student')
            student.user_set.add(user) #add user into student group
            login(request, user)
            return redirect('log_in')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('home')

@login_prohibited
def home(request):
    return render(request, 'home.html')

@group_required('Student')
def make_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, user=request.user) #stores the current user
        if form.is_valid():
            form.save(request.user)
            messages.add_message(request, messages.INFO, 'Request created.')
            return redirect('student')  # studentpage
            # have to use this information to store in database.
    else:
        form = RequestForm(user=request.user)
    return render(request, 'request.html', {'form': form})


@group_required('Admin')
def administrators(request):
    if request.method == 'POST':
        if request.POST.get("delete"): #checks if user clicks on the delete button
            booking_id = request.POST.get("delete")
            Booking.objects.get(id=booking_id).delete()
            messages.add_message(request, messages.INFO, 'Booking has been deleted.')
            return redirect('administrators')
    requests = Request.objects.all()
    bookings = Booking.objects.all()
    return render(request, 'administrators.html', {'request': requests, 'booking': bookings})


@group_required('Admin')
def booking(request, request_id):
    try:
        requests = Request.objects.get(id=request_id)
    except ObjectDoesNotExist:
        return redirect('administrators')
    else:
        input = { #make the initial values of the booking form same as the request values
            'day': requests.daysAvailable,
            'number_of_lessons': requests.numberOfLessons,
            'interval': requests.intervalBetweenLessons,
            'duration': requests.durationOfLessons
        }
        if request.method == 'POST':
            form = BookingForm(request.POST, input)
            if form.is_valid():
                form.save(requests.user)
                Request.objects.get(id=request_id).delete()
                messages.add_message(request, messages.INFO, 'Booking has been made.')
                return redirect('administrators')
        else:
            form = BookingForm(input)
    return render(request, 'booking.html', {'form': form, 'request_id': request_id})


@group_required('Admin')
def edit_booking(request, booking_id):
    try:
        bookings = Booking.objects.get(id=booking_id)
    except ObjectDoesNotExist:
        return redirect('administrators')
    else:
        if request.method == 'POST':
            form = BookingForm(request.POST, instance=bookings) #initial values are the values of the current booking
            if form.is_valid():
                bookings.delete()
                bookings = form.save(bookings.user)
                messages.add_message(request, messages.INFO, 'Booking has been successfully edited.')
                return redirect('administrators')
        else:
            form = BookingForm(instance=bookings)
    return render(request, 'edit_booking.html', {'form': form, 'booking_id': booking_id})


@group_required('Director')
def create_admin(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            admin, created = Group.objects.get_or_create(name='Admin') #make new user an admin
            admin.user_set.add(user)
            messages.add_message(request, messages.INFO, 'User created.')
    else:
        form = SignUpForm()
    return render(request, 'create_admin.html', {'form': form})


@group_required('Director')
def admin_list(request):
    admin = []
    for user in CustomUser.objects.all():
        if user.groups.filter(name='Admin').exists(): #find all the admin users
            admin.append(user)
    if request.method == 'POST':
        if request.POST.get("edit"): #check if user clicks on the edit, delete or super admin button
            user_email = request.POST.get("edit")
            user = CustomUser.objects.get(email=user_email)
            return redirect('edit_user', user_id=user.id)
        if request.POST.get("delete"):
            user_email = request.POST.get("delete")
            CustomUser.objects.get(email=user_email).delete()
            messages.add_message(request, messages.INFO, 'User has been deleted.')
        if request.POST.get('super_admin'):
            user_email = request.POST.get("super_admin")
            user = CustomUser.objects.get(email=user_email)
            director, created = Group.objects.get_or_create(name='Director')
            if (user.groups.filter(name="Director").exists()): #check if user is already a director
                group_id = Group.objects.get(name="Director") #if user is a director, remove the director privileges
                user.groups.remove(group_id)
            else:
                director.user_set.add(user) #make the user a director
        return redirect('admin_list')
    return render(request, 'admin_list.html', {'admin': admin})


@login_required
def edit_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return redirect('admin_list')
    else:
        if request.method == 'POST':
            form = EditAdminForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save()
                messages.add_message(request, messages.INFO, 'Update Successful.')
        else:
            form = EditAdminForm(instance=user)
        return render(request, 'edit_user.html', {'form': form, 'user_id': user_id})

@group_required('Student')
def edit_request(request, request_id):
    try:
        reqs = Request.objects.get(id=request_id)
    except ObjectDoesNotExist:
        return redirect('student')
    else:
        if request.method == 'POST':
            form = RequestForm(request.POST, instance=reqs)
            if form.is_valid():
                reqs = form.save()
                messages.add_message(request, messages.INFO, 'Request has been successfully edited.')
                return redirect('student')
        else:
            form = RequestForm(instance=reqs)
    return render(request, 'edit_request.html', {'form': form, 'request_id': request_id})

@group_required('Student')
def edit_request(request, request_id):
    try:
        reqs = Request.objects.get(id=request_id)
    except ObjectDoesNotExist:
        return redirect('student')
    else:
        if request.method == 'POST':
            form = RequestForm(request.POST, instance=reqs, user=request.user)
            if form.is_valid():
                reqs = form.save()
                messages.add_message(request, messages.INFO, 'Request has been successfully edited.')
                return redirect('student')
        else:
            form = RequestForm(instance=reqs, user=request.user)
    return render(request, 'edit_request.html', {'form': form, 'request_id': request_id})

@group_required('Student')
def student(request):
    current_user = request.user
    user_id = current_user.id
    account = Bank.objects.get(user=current_user)
    all_requests = Request.objects.filter(user=current_user)
    all_bookings = Booking.objects.filter(user=current_user)
    balance = account.balance
    if request.method == 'POST':
        if request.POST.get("delete"):
            request_id = request.POST.get("delete")
            Request.objects.get(id=request_id).delete()
            messages.add_message(request, messages.INFO, 'Request has been deleted.')
            return redirect('student')
        if request.POST.get("edit"):
            request_id = request.POST.get("edit")
            return redirect('edit_request', request_id=request_id)
    context = {'user': current_user, 'user_id': user_id, 'balance': balance, 'requests': all_requests,
               'bookings': all_bookings}
    return render(request, 'student.html', context)

@group_required('Student')
def transactions(request):
    account = Bank.objects.get(user=request.user)
    balance = account.balance
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            new_invoice = form.save(request.user)
            if Booking.objects.filter(id=new_invoice.invoice_id).exists():
                current_booking = Booking.objects.get(id=new_invoice.invoice_id)
                if current_booking.payment_made <= current_booking.full_price:
                    if balance >= new_invoice.amount: #automatically deduct the price of invoice if there is sufficient amount in balance
                        account.balance -= int(float(new_invoice.amount))
                        current_booking.payment_made += new_invoice.amount
                        current_booking.save()
                        account.save()
                    else:
                        new_invoice.delete()
                        redirect('student')
                        messages.add_message(request, messages.ERROR, "ERROR: Account balance is insufficient")
                else: #payment has been made
                    new_invoice.delete()
                    redirect('student')
                    messages.add_message(request, messages.ERROR, "ERROR: Transaction for invoice ID already made")
            else:
                new_invoice.delete()
                redirect('student')
                messages.add_message(request, messages.ERROR, "ERROR: Invoice ID does not exist")
    else:
        form = TransactionForm()
    return render(request, 'transactions.html', {'form': form})

@group_required('Admin')
def all_transactions(request):
    all_transactions = Transaction.objects.all()
    return render(request, 'all_transactions.html', {'transactions': all_transactions})

@group_required('Student')
def update_balance(request):
    account = Bank.objects.get(user=request.user)
    if request.method == 'POST':
        form = BalanceForm(request.POST, instance=account)
        form.account = Bank.objects.get(user=request.user)
        amount = request.POST.get('balance')
        form.account.balance += int(float(amount))
        if form.is_valid():
            form.account.save()
            return redirect('student')
    else:
        form = BalanceForm(instance=account)
    balance = account.balance
    context = {'balance': balance, 'form': form}
    return render(request, 'update_balance.html', context)

@group_required('Student')
def add_children(request):
    if request.method == 'POST':
        form = ChildrenForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('add_children')
    else:
        form = ChildrenForm()
    children = request.user.children.all()
    return render(request, 'add_children.html', {'form': form, 'children': children})


@group_required('Admin')
def school_term(request):
    if request.method == 'POST':
        form = SchoolTermForm(request.POST)
        if request.POST.get("delete"):
            term_id = request.POST.get("delete")
            SchoolTerm.objects.get(id=term_id).delete()
            return redirect('school_term')
        else:
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'New term created.')
                return redirect('school_term')
    else:
        form = SchoolTermForm()
    term_dates = SchoolTerm.objects.all()
    return render(request, 'school_term.html', {'form': form, 'term_dates': term_dates})


@group_required('Admin')
def edit_term(request, term_id):
    try:
        term = SchoolTerm.objects.get(id=term_id)
    except ObjectDoesNotExist:
        return redirect('school_term')
    else:
        if request.method == 'POST':
            original = SchoolTermForm(instance=term).save(commit=False)
            form = SchoolTermForm(request.POST, instance=term)
            term.delete()  #delete term so that validation can exclude the values of this term
            if form.is_valid():
                term = form.save(commit=False)
                term.id = term_id #make the new term have the same id as the initial one
                term.save()
                messages.add_message(request, messages.INFO, 'Update Successful.')
                return redirect('school_term')
            else:
                original.id = term_id
                original.save() #if form is not valid create the same term object again
        else:
            form = SchoolTermForm(instance=term)
        return render(request, 'edit_term.html', {'form': form, 'term_id': term_id})

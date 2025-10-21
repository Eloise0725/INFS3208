from django.shortcuts import redirect
from django.contrib.auth.models import Group


def group_required(group):
    def decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            if request.user.groups.filter(name=group).exists() or (request.user.groups.filter(name='Director') and group=='Admin'):
                return view_function(request, *args, **kwargs)
            else:
                if request.user.groups.filter(name='Admin').exists():
                    return redirect('administrators')
                if request.user.groups.filter(name='Director').exists():
                    return redirect('admin_list')
                if request.user.groups.filter(name='Student').exists():
                    return redirect('student')
                else:
                    return redirect('log_in')

        return modified_view_function

    return decorator

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Admin').exists():
                return redirect('administrators')
            if request.user.groups.filter(name='Director').exists():
                return redirect('admin_list')
            else:
                return redirect('student')
        else:
            return view_function(request)
    return modified_view_function


def login_required(view_function, **kwargs):
    def modified_view_function(request, **kwargs):
        if request.user.is_authenticated:
            return view_function(request, **kwargs)
        else:
            return redirect('log_in')
    return modified_view_function

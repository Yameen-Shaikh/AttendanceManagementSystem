from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from student.models import CustomUser
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'Teacher':
            return redirect('teacher:teacher_dashboard')
        elif request.user.role == 'Student':
            return redirect('student:student_dashboard')
        else:
            return redirect('/admin/')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                if not user.is_active:
                    messages.error(request, 'Invalid username or password/Approval pending.')
                    return redirect('login')
                login(request, user)
                if user.role == 'Teacher':
                    return redirect('teacher:teacher_dashboard')
                elif user.role == 'Student':
                    return redirect('student:student_dashboard')
                else:
                    return redirect('/admin/')
            else:
                messages.error(request, 'Invalid username or password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

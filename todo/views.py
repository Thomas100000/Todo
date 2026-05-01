from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Task

@login_required(login_url='login')
def index(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'todo/index.html', {'tasks': tasks})

@login_required(login_url='login')
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Task.objects.create(title=title, user=request.user)
    return redirect('index')

@login_required(login_url='login')
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    return redirect('index')

@login_required(login_url='login')
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return redirect('index')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('signup')
        user = User.objects.create_user(username=email, email=email, password=password)
        login(request, user)
        return redirect('index')
    return render(request, 'todo/signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'todo/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def statistics_view(request):
    completed = Task.objects.filter(user=request.user, is_completed=True).count()
    pending = Task.objects.filter(user=request.user, is_completed=False).count()
    return render(request, 'todo/statistics.html', {'completed': completed, 'pending': pending})

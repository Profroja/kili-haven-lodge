from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def login_view(request):
    """Handle user login with role-based redirection"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirect based on user role
            if user.role == 'manager':
                return redirect('manager_dashboard')
            else:  # lodge_attendant or any other role
                return redirect('staff_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auths/login.html')

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('/')  # Redirect to homepage after logout
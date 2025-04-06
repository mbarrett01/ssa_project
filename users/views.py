from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .forms import TopUpForm
from .models import Profile, Transaction
from django.contrib.auth.models import User

@login_required(login_url='users:login')
def user(request):
    return render(request, "users/user.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', reverse("users:user"))
            return HttpResponseRedirect(next_url)
        else:
            messages.error(request, "Invalid Credentials.")
    return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('users:login')




def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created! You can now log in.")
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user(request):
    profile = request.user.profile
    return render(request, 'users/user.html', {
        'user': request.user,
        'balance': profile.balance
    })

@login_required
def TopUpBalance(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == "POST":
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']

                profile = request.user.profile
                profile.balance += amount
                profile.save()

                Transaction.objects.create(user=request.user, amount=amount)

                # Send success message
                messages.success(request, f"Your balance has been topped up by ${amount}.")
                
                return redirect('users:user')  # Redirect to user dashboard
    else:
            form = TopUpForm()

            context = {
                'form': form,
                'user_balance': request.user.profile.balance,
                'welcome_message': f"Welcome back, {request.user.first_name}!",
            }

    return render(request, 'chipin/top_up.html', {'form': form})
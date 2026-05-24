from rest_framework import viewsets
from .models import Income, Expense, Goal, Category
from .serializers import *

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Create your views here.
# frontend views 
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# ---------------- REGISTER ----------------

def register_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if username already exists
        if User.objects.filter(username=username).exists():

            return render(request,
                          'register.html',
                          {'error': 'Username already exists'})

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('/login/')

    return render(request, 'register.html')


# ---------------- LOGIN ----------------

def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

        else:

            return render(
                request,
                'login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'login.html')


# ---------------- DASHBOARD ----------------

@login_required
def dashboard(request):

    return render(request, 'dashboard.html')


# ---------------- LOGOUT ----------------

def logout_view(request):

    logout(request)

    return redirect('/')

# ---------------- Home Page ----------------

def home_view(request):

    return render(request,'home_page.html')

from .models import Income
from django.contrib.auth.decorators import login_required

# ---------------- Add_income Page ----------------

@login_required
def add_income(request):

    if request.method == 'POST':

        amount = request.POST['amount']

        source = request.POST['source']

        date = request.POST['date']

        Income.objects.create(

            user=request.user,

            amount=amount,

            source=source,

            date=date

        )

        return render(
            request,
            'add_income.html',
            {'success': True}
        )

    return render(
        request,
        'add_income.html'
    )
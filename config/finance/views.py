from rest_framework import viewsets
from .models import Income, Expense, Goal, Category
from django.db.models import Sum
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
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Income, Expense, Goal


@login_required
def dashboard(request):

    # ---------- TOTAL INCOME ----------

    total_income = Income.objects.filter(

        user=request.user

    ).aggregate(

        Sum('amount')

    )['amount__sum']


    # ---------- TOTAL EXPENSE ----------

    total_expense = Expense.objects.filter(

        user=request.user

    ).aggregate(

        Sum('amount')

    )['amount__sum']


    # ---------- HANDLE NONE VALUES ----------

    if total_income is None:

        total_income = 0


    if total_expense is None:

        total_expense = 0


    # ---------- SAVINGS ----------

    savings = total_income - total_expense


    # ---------- ACTIVE GOALS ----------

    active_goals = Goal.objects.filter(

        user=request.user

    ).count()


    # ---------- SEND DATA TO TEMPLATE ----------

    context = {

        'total_income': total_income,

        'total_expense': total_expense,

        'savings': savings,

        'active_goals': active_goals

    }


    return render(

        request,

        'dashboard.html',

        context

    )


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
# ---------------- View _income Page ----------------

@login_required
def view_income(request):

    incomes = Income.objects.filter(

        user=request.user

    ).order_by('-date')


    total_income = incomes.aggregate(

        Sum('amount')

    )['amount__sum']


    if total_income is None:

        total_income = 0


    return render(request,'view_income.html',{
            'incomes': incomes,
            'total_income': total_income})

# ---------------- Add_expense Page ----------------
@login_required
def add_expense(request):

    categories = Category.objects.all()

    if request.method == 'POST':

        amount = request.POST['amount']

        category_id = request.POST['category']

        date = request.POST['date']

        category = Category.objects.get(
            id=category_id
        )

        Expense.objects.create(

            user=request.user,

            amount=amount,

            category=category,

            date=date

        )

        return render(

            request,

            'add_expense.html',

            {

                'success': True,

                'categories': categories

            }

        )

    return render(

        request,

        'add_expense.html',

        {

            'categories': categories

        }

    )
    
# ----------------View_expense Page ----------------
@login_required
def view_expenses(request):

    expenses = Expense.objects.filter(

        user=request.user

    ).order_by('-date')


    total_expense = expenses.aggregate(

        Sum('amount')

    )['amount__sum']


    if total_expense is None:

        total_expense = 0


    return render(

        request,

        'view_expense.html',

        {

            'expenses': expenses,

            'total_expense': total_expense

        }

    )
    
#----------------SET GOAL Page---------------
from .models import Goal


@login_required
def set_goal(request):

    if request.method == 'POST':

        name = request.POST['name']

        target_amount = request.POST['target_amount']

        saved_amount = request.POST['saved_amount']


        Goal.objects.create(

            user=request.user,

            name=name,

            target_amount=target_amount,

            saved_amount=saved_amount

        )


        return render(

            request,

            'set_goal.html',

            {

                'success': True

            }

        )


    return render(

        request,

        'set_goal.html'

    )
    
    # ---------------view goals ---------------------
@login_required
def view_goals(request):

    goals = Goal.objects.filter(

        user=request.user

    )

    goal_data = []

    for goal in goals:

        progress = (

            goal.saved_amount /

            goal.target_amount

        ) * 100


        remaining = (

            goal.target_amount -

            goal.saved_amount

        )


        goal.progress = round(progress, 2)

        goal.remaining = remaining


        goal_data.append(goal)


    return render(

        request,

        'view_goals.html',

        {

            'goals': goal_data

        }

    )